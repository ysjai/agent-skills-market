import { describe, it, expect, beforeEach, mock } from 'bun:test';

import type { FileTreeNode } from '@/types/file-tree';

// Create a mock storage
const createMockStorage = () => {
  const storage = new Map<string, string>();
  return {
    getItem: (key: string) => storage.get(key) || null,
    setItem: (key: string, value: string) => storage.set(key, value),
    removeItem: (key: string) => storage.delete(key),
  };
};

describe('file-tree-storage', () => {
  let mockStorage: ReturnType<typeof createMockStorage>;
  let getItemSpy: ReturnType<typeof mock>;
  let setItemSpy: ReturnType<typeof mock>;
  let removeItemSpy: ReturnType<typeof mock>;

  // Import the module fresh for each test
  const importModule = async () => {
    const mod = await import('../file-tree-storage');
    return mod;
  };

  beforeEach(() => {
    mockStorage = createMockStorage();
    getItemSpy = mock((key: string) => mockStorage.getItem(key));
    setItemSpy = mock((key: string, value: string) => mockStorage.setItem(key, value));
    removeItemSpy = mock((key: string) => mockStorage.removeItem(key));

    // Mock localStorage on global
    Object.defineProperty(global, 'localStorage', {
      value: {
        getItem: getItemSpy,
        setItem: setItemSpy,
        removeItem: removeItemSpy,
      },
      writable: true,
      configurable: true,
    });
  });

  describe('getExpandedStateKey', () => {
    it('传入treeId返回正确key', async () => {
      const { getExpandedStateKey } = await importModule();
      expect(getExpandedStateKey('my-tree')).toBe('filetree_expanded_my-tree');
    });

    it('不传treeId返回default key', async () => {
      const { getExpandedStateKey } = await importModule();
      expect(getExpandedStateKey()).toBe('filetree_expanded_default');
    });

    it('传入空字符串返回default key', async () => {
      const { getExpandedStateKey } = await importModule();
      expect(getExpandedStateKey('')).toBe('filetree_expanded_default');
    });
  });

  describe('getSelectedPathKey', () => {
    it('传入treeId返回正确key', async () => {
      const { getSelectedPathKey } = await importModule();
      expect(getSelectedPathKey('my-tree')).toBe('filetree_selected_my-tree');
    });

    it('不传treeId返回default key', async () => {
      const { getSelectedPathKey } = await importModule();
      expect(getSelectedPathKey()).toBe('filetree_selected_default');
    });

    it('传入空字符串返回default key', async () => {
      const { getSelectedPathKey } = await importModule();
      expect(getSelectedPathKey('')).toBe('filetree_selected_default');
    });
  });

  describe('saveSelectedPath', () => {
    it('传入path调用setItem', async () => {
      const { saveSelectedPath } = await importModule();
      saveSelectedPath('/path/to/file', 'test-key');
      expect(setItemSpy).toHaveBeenCalledWith('test-key', '/path/to/file');
    });

    it('传入undefined调用removeItem', async () => {
      const { saveSelectedPath } = await importModule();
      saveSelectedPath(undefined, 'test-key');
      expect(removeItemSpy).toHaveBeenCalledWith('test-key');
    });
  });

  describe('loadSelectedPath', () => {
    it('key存在返回path', async () => {
      mockStorage.setItem('test-key', '/saved/path');
      const { loadSelectedPath } = await importModule();
      expect(loadSelectedPath('test-key')).toBe('/saved/path');
      expect(getItemSpy).toHaveBeenCalledWith('test-key');
    });

    it('key不存在返回undefined', async () => {
      const { loadSelectedPath } = await importModule();
      expect(loadSelectedPath('non-existent-key')).toBeUndefined();
    });

    it('异常时返回undefined', async () => {
      getItemSpy.mockImplementation(() => {
        throw new Error('Storage error');
      });
      const { loadSelectedPath } = await importModule();
      expect(loadSelectedPath('test-key')).toBeUndefined();
    });
  });

  describe('saveExpandedState', () => {
    it('递归收集展开的树节点path', async () => {
      const { saveExpandedState } = await importModule();
      const nodes: FileTreeNode[] = [
        {
          name: 'folder1',
          path: '/folder1',
          type: 'tree',
          isExpanded: true,
          id: '1',
          depth: 0,
          children: [
            {
              name: 'subfolder',
              path: '/folder1/subfolder',
              type: 'tree',
              isExpanded: true,
              id: '2',
              depth: 1,
            } as FileTreeNode,
          ],
        } as FileTreeNode,
      ];
      saveExpandedState(nodes, 'expanded-key');
      expect(setItemSpy).toHaveBeenCalledWith('expanded-key', '["/folder1","/folder1/subfolder"]');
    });

    it('保存JSON到localStorage', async () => {
      const { saveExpandedState } = await importModule();
      const nodes: FileTreeNode[] = [
        {
          name: 'folder',
          path: '/folder',
          type: 'tree',
          isExpanded: true,
          id: '1',
          depth: 0,
        } as FileTreeNode,
      ];
      saveExpandedState(nodes, 'json-key');
      expect(setItemSpy).toHaveBeenCalledWith('json-key', '["/folder"]');
    });

    it('无展开节点保存空数组', async () => {
      const { saveExpandedState } = await importModule();
      const nodes: FileTreeNode[] = [
        {
          name: 'folder',
          path: '/folder',
          type: 'tree',
          isExpanded: false,
          id: '1',
          depth: 0,
        } as FileTreeNode,
        {
          name: 'file',
          path: '/file.txt',
          type: 'blob',
          isExpanded: true,
          id: '2',
          depth: 0,
        } as FileTreeNode,
      ];
      saveExpandedState(nodes, 'empty-key');
      expect(setItemSpy).toHaveBeenCalledWith('empty-key', '[]');
    });

    it('blob类型不收集', async () => {
      const { saveExpandedState } = await importModule();
      const nodes: FileTreeNode[] = [
        {
          name: 'file',
          path: '/file.txt',
          type: 'blob',
          isExpanded: true,
          id: '1',
          depth: 0,
        } as FileTreeNode,
      ];
      saveExpandedState(nodes, 'blob-key');
      expect(setItemSpy).toHaveBeenCalledWith('blob-key', '[]');
    });
  });

  describe('loadExpandedState', () => {
    it('正确解析JSON', async () => {
      mockStorage.setItem('load-key', '["/path1","/path2"]');
      const { loadExpandedState } = await importModule();
      const result = loadExpandedState('load-key');
      expect(result).toEqual(['/path1', '/path2']);
    });

    it('无数据返回空数组', async () => {
      const { loadExpandedState } = await importModule();
      const result = loadExpandedState('non-existent-key');
      expect(result).toEqual([]);
    });

    it('解析失败返回空数组', async () => {
      mockStorage.setItem('bad-key', 'invalid json');
      const { loadExpandedState } = await importModule();
      const result = loadExpandedState('bad-key');
      expect(result).toEqual([]);
    });
  });
});
