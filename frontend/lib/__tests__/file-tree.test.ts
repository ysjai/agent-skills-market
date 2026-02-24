import { describe, expect, it } from 'bun:test';
import { buildTree, findNodeByPath, findFirstFileInDirectory, applyExpandedState } from '../file-tree-utils';

describe('buildTree', () => {
  it('builds correct directory structure from Git entries', () => {
    const entries = [
      { path: 'src', type: 'tree', name: 'src' },
      { path: 'src/index.ts', type: 'blob', name: 'index.ts', blob_id: 'abc123' },
    ];
    const result = buildTree(entries);
    expect(result).toHaveLength(1);
    expect(result[0].name).toBe('src');
    expect(result[0].children).toHaveLength(1);
    expect(result[0].children![0].name).toBe('index.ts');
  });
  it('returns empty array for empty input', () => {
    expect(buildTree([])).toEqual([]);
    expect(buildTree(null as any)).toEqual([]);
  });
  it('sorts directories first then alphabetically', () => {
    const entries = [
      { path: 'z-file.ts', type: 'blob', name: 'z-file.ts' },
      { path: 'a-dir', type: 'tree', name: 'a-dir' },
      { path: 'b-file.ts', type: 'blob', name: 'b-file.ts' },
    ];
    const result = buildTree(entries);
    expect(result[0].name).toBe('a-dir');
    expect(result[1].name).toBe('b-file.ts');
    expect(result[2].name).toBe('z-file.ts');
  });
  it('correctly constructs nested directories', () => {
    const entries = [
      { path: 'a', type: 'tree', name: 'a' },
      { path: 'a/b', type: 'tree', name: 'b' },
      { path: 'a/b/c.ts', type: 'blob', name: 'c.ts', blob_id: 'xyz' },
    ];
    const result = buildTree(entries);
    expect(result[0].children![0].children![0].name).toBe('c.ts');
    expect(result[0].children![0].children![0].depth).toBe(2);
  });
});
describe('findNodeByPath', () => {
  it('finds node by exact path', () => {
    const entries = [
      { path: 'src', type: 'tree', name: 'src' },
      { path: 'src/utils.ts', type: 'blob', name: 'utils.ts', blob_id: 'def456' },
    ];
    const tree = buildTree(entries);
    expect(findNodeByPath(tree, 'src/utils.ts')?.name).toBe('utils.ts');
    expect(findNodeByPath(tree, 'nonexistent')).toBeNull();
  });
});
describe('findFirstFileInDirectory', () => {
  it('finds first file in same directory', () => {
    const entries = [
      { path: 'src', type: 'tree', name: 'src' },
      { path: 'src/a.ts', type: 'blob', name: 'a.ts', blob_id: 'aaa' },
      { path: 'src/b.ts', type: 'blob', name: 'b.ts', blob_id: 'bbb' },
    ];
    const result = findFirstFileInDirectory('src/a.ts', buildTree(entries));
    expect(result?.path).toBe('src/a.ts');
    expect(result?.blobId).toBe('aaa');
  });
  it('finds file in root directory', () => {
    const entries = [
      { path: 'root.ts', type: 'blob', name: 'root.ts', blob_id: 'root123' },
      { path: 'other.ts', type: 'blob', name: 'other.ts', blob_id: 'other456' },
    ];
    const result = findFirstFileInDirectory('root.ts', buildTree(entries));
    expect(result).not.toBeNull();
    expect(result?.blobId).toBeDefined();
  });
});
describe('applyExpandedState', () => {
  it('applies expanded state to matching paths', () => {
    const entries = [{ path: 'src', type: 'tree', name: 'src' }];
    const expanded = applyExpandedState(buildTree(entries), ['src']);
    expect(expanded[0].isExpanded).toBe(true);
  });
  it('does not expand non-matching paths', () => {
    const entries = [{ path: 'src', type: 'tree', name: 'src' }];
    const expanded = applyExpandedState(buildTree(entries), ['other']);
    expect(expanded[0].isExpanded).toBe(false);
  });
});

import { findSiblingFiles, findNextFileAfterDelete } from '../file-tree-utils';

describe('findSiblingFiles', () => {
  it('returns all files in the same directory', () => {
    const entries = [
      { path: 'src', type: 'tree', name: 'src' },
      { path: 'src/a.ts', type: 'blob', name: 'a.ts', blob_id: 'aaa' },
      { path: 'src/b.ts', type: 'blob', name: 'b.ts', blob_id: 'bbb' },
      { path: 'src/c.ts', type: 'blob', name: 'c.ts', blob_id: 'ccc' },
    ];
    const tree = buildTree(entries);
    const siblings = findSiblingFiles(tree, 'src/a.ts');
    
    expect(siblings).toHaveLength(3);
    expect(siblings.map(s => s.name)).toEqual(['a.ts', 'b.ts', 'c.ts']);
  });

  it('returns files from root directory', () => {
    const entries = [
      { path: 'file1.ts', type: 'blob', name: 'file1.ts', blob_id: '1' },
      { path: 'file2.ts', type: 'blob', name: 'file2.ts', blob_id: '2' },
    ];
    const tree = buildTree(entries);
    const siblings = findSiblingFiles(tree, 'file1.ts');
    
    expect(siblings).toHaveLength(2);
  });

  it('returns empty array when no siblings exist', () => {
    const entries = [
      { path: 'src', type: 'tree', name: 'src' },
      { path: 'src/only.ts', type: 'blob', name: 'only.ts', blob_id: '1' },
    ];
    const tree = buildTree(entries);
    // Searching for a file in a different directory
    const siblings = findSiblingFiles(tree, 'other/file.ts');
    expect(siblings).toEqual([]);
  });

  it('sorts siblings alphabetically', () => {
    const entries = [
      { path: 'src', type: 'tree', name: 'src' },
      { path: 'src/z.ts', type: 'blob', name: 'z.ts', blob_id: 'z' },
      { path: 'src/a.ts', type: 'blob', name: 'a.ts', blob_id: 'a' },
      { path: 'src/m.ts', type: 'blob', name: 'm.ts', blob_id: 'm' },
    ];
    const tree = buildTree(entries);
    const siblings = findSiblingFiles(tree, 'src/m.ts');
    
    expect(siblings.map(s => s.name)).toEqual(['a.ts', 'm.ts', 'z.ts']);
  });

  it('handles nested directories correctly', () => {
    const entries = [
      { path: 'src', type: 'tree', name: 'src' },
      { path: 'src/utils', type: 'tree', name: 'utils' },
      { path: 'src/utils/helper.ts', type: 'blob', name: 'helper.ts', blob_id: 'h1' },
      { path: 'src/utils/format.ts', type: 'blob', name: 'format.ts', blob_id: 'f1' },
      { path: 'src/main.ts', type: 'blob', name: 'main.ts', blob_id: 'm1' },
    ];
    const tree = buildTree(entries);
    const siblings = findSiblingFiles(tree, 'src/utils/helper.ts');
    
    expect(siblings).toHaveLength(2);
    expect(siblings.map(s => s.name)).toEqual(['format.ts', 'helper.ts']);
  });
});

describe('findNextFileAfterDelete', () => {
  it('returns null when deleted file is not the selected one', () => {
    const entries = [
      { path: 'src', type: 'tree', name: 'src' },
      { path: 'src/a.ts', type: 'blob', name: 'a.ts', blob_id: 'aaa' },
      { path: 'src/b.ts', type: 'blob', name: 'b.ts', blob_id: 'bbb' },
    ];
    const tree = buildTree(entries);
    const result = findNextFileAfterDelete(tree, 'src/a.ts', 'src/b.ts');
    
    expect(result.path).toBeNull();
    expect(result.selectDirectory).toBe(false);
  });

  it('returns parent directory when only one file exists', () => {
    const entries = [
      { path: 'src', type: 'tree', name: 'src' },
      { path: 'src/only.ts', type: 'blob', name: 'only.ts', blob_id: '1' },
    ];
    const tree = buildTree(entries);
    const result = findNextFileAfterDelete(tree, 'src/only.ts', 'src/only.ts');
    
    expect(result.path).toBe('src');
    expect(result.selectDirectory).toBe(true);
  });

  it('returns next sibling when multiple files exist', () => {
    const entries = [
      { path: 'src', type: 'tree', name: 'src' },
      { path: 'src/a.ts', type: 'blob', name: 'a.ts', blob_id: 'a' },
      { path: 'src/b.ts', type: 'blob', name: 'b.ts', blob_id: 'b' },
      { path: 'src/c.ts', type: 'blob', name: 'c.ts', blob_id: 'c' },
    ];
    const tree = buildTree(entries);
    // Deleting 'a.ts' while it's selected - should go to 'b.ts'
    const result = findNextFileAfterDelete(tree, 'src/a.ts', 'src/a.ts');
    
    expect(result.path).toBe('src/b.ts');
    expect(result.blobId).toBe('b');
    expect(result.selectDirectory).toBe(false);
  });

  it('wraps around to first file when deleting last file', () => {
    const entries = [
      { path: 'src', type: 'tree', name: 'src' },
      { path: 'src/a.ts', type: 'blob', name: 'a.ts', blob_id: 'a' },
      { path: 'src/b.ts', type: 'blob', name: 'b.ts', blob_id: 'b' },
    ];
    const tree = buildTree(entries);
    // Deleting 'b.ts' (last) while it's selected - should wrap to 'a.ts'
    const result = findNextFileAfterDelete(tree, 'src/b.ts', 'src/b.ts');
    
    expect(result.path).toBe('src/a.ts');
    expect(result.blobId).toBe('a');
  });

  it('returns null path when deleting file from root with no siblings', () => {
    const entries = [
      { path: 'only.ts', type: 'blob', name: 'only.ts', blob_id: '1' },
    ];
    const tree = buildTree(entries);
    const result = findNextFileAfterDelete(tree, 'only.ts', 'only.ts');
    
    expect(result.path).toBeNull();
    expect(result.selectDirectory).toBe(true);
  });

  it('handles deeply nested directories', () => {
    const entries = [
      { path: 'src', type: 'tree', name: 'src' },
      { path: 'src/utils', type: 'tree', name: 'utils' },
      { path: 'src/utils/helpers', type: 'tree', name: 'helpers' },
      { path: 'src/utils/helpers/a.ts', type: 'blob', name: 'a.ts', blob_id: 'a' },
      { path: 'src/utils/helpers/b.ts', type: 'blob', name: 'b.ts', blob_id: 'b' },
    ];
    const tree = buildTree(entries);
    const result = findNextFileAfterDelete(tree, 'src/utils/helpers/a.ts', 'src/utils/helpers/a.ts');
    
    expect(result.path).toBe('src/utils/helpers/b.ts');
  });
});
