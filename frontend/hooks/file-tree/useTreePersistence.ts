import { useCallback } from 'react';
import type { FileTreeNode } from '@/types/file-tree';
import {
  getExpandedStateKey,
  getSelectedPathKey,
  saveSelectedPath as storageSaveSelectedPath,
  loadSelectedPath as storageLoadSelectedPath,
  saveExpandedState as storageSaveExpandedState,
  loadExpandedState as storageLoadExpandedState,
} from '@/lib/file-tree-storage';

export interface UseTreePersistenceOptions {
  treeId?: string;
}

export interface UseTreePersistenceReturn {
  saveSelectedPath: (path: string | undefined) => void;
  loadSelectedPath: () => string | undefined;
  saveExpandedState: (nodes: FileTreeNode[]) => void;
  loadExpandedState: () => string[];
}

export function useTreePersistence({ treeId }: UseTreePersistenceOptions): UseTreePersistenceReturn {
  const saveSelectedPath = useCallback((path: string | undefined) => {
    if (!treeId) return;
    const key = getSelectedPathKey(treeId);
    storageSaveSelectedPath(path, key);
  }, [treeId]);

  const loadSelectedPath = useCallback((): string | undefined => {
    if (!treeId) return undefined;
    const key = getSelectedPathKey(treeId);
    return storageLoadSelectedPath(key);
  }, [treeId]);

  const saveExpandedState = useCallback((nodeList: FileTreeNode[]) => {
    if (!treeId) return;
    const key = getExpandedStateKey(treeId);
    storageSaveExpandedState(nodeList, key);
  }, [treeId]);

  const loadExpandedState = useCallback((): string[] => {
    if (!treeId) return [];
    const key = getExpandedStateKey(treeId);
    return storageLoadExpandedState(key);
  }, [treeId]);

  return {
    saveSelectedPath,
    loadSelectedPath,
    saveExpandedState,
    loadExpandedState,
  };
}
