import { useCallback } from 'react';
import type { FileTreeNode } from '@/types/file-tree';
import { findNodeByPath } from '@/lib/file-tree-utils';
import type { OnFileSelectCallback } from './useTreeState';

export interface UseTreeSelectionOptions {
  selectedPath: string | undefined;
  setSelectedPath: React.Dispatch<React.SetStateAction<string | undefined>>;
  onFileSelectRef: React.RefObject<OnFileSelectCallback | undefined>;
  saveSelectedPath: (path: string | undefined) => void;
}

export interface UseTreeSelectionReturn {
  selectNode: (node: FileTreeNode) => Promise<void>;
  handleAutoSelect: (path: string, blobId?: string) => void;
}

export function useTreeSelection({
  selectedPath,
  setSelectedPath,
  onFileSelectRef,
  saveSelectedPath,
}: UseTreeSelectionOptions): UseTreeSelectionReturn {
  const selectNode = useCallback(async (node: FileTreeNode) => {
    const previousPath = selectedPath;
    setSelectedPath(node.path);
    saveSelectedPath(node.path);
    if (node.type === 'blob' && onFileSelectRef.current) {
      const result = await onFileSelectRef.current(node.path, node.blob_id);
      if (result === false) {
        setSelectedPath(previousPath);
        saveSelectedPath(previousPath);
      }
    }
  }, [selectedPath, setSelectedPath, saveSelectedPath, onFileSelectRef]);

  const handleAutoSelect = useCallback((path: string, blobId?: string) => {
    setSelectedPath(path);
    saveSelectedPath(path);
    onFileSelectRef.current?.(path, blobId);
  }, [setSelectedPath, saveSelectedPath, onFileSelectRef]);

  return {
    selectNode,
    handleAutoSelect,
  };
}

export function findNodeInTree(nodeList: FileTreeNode[], path: string): FileTreeNode | null {
  return findNodeByPath(nodeList, path);
}

export function findSkillMdNode(nodeList: FileTreeNode[]): FileTreeNode | null {
  for (const node of nodeList) {
    if (node.path === 'SKILL.md' && node.type === 'blob') return node;
    if (node.children) {
      const found = findSkillMdNode(node.children as FileTreeNode[]);
      if (found) return found;
    }
  }
  return null;
}
