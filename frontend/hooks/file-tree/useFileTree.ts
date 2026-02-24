import { useCallback, useRef, useEffect } from 'react';
import type { FileTreeNode, TreeStructure } from '@/types/file-tree';
import { api } from '@/lib/api';
import { buildTree, findFirstFileInDirectory, applyExpandedState } from '@/lib/file-tree-utils';
import { useTreeState } from './useTreeState';
import { useTreePersistence } from './useTreePersistence';
import { useTreeSelection, findNodeInTree, findSkillMdNode } from './useTreeSelection';
import { useTreeOperations } from './useTreeOperations';

export interface FileTreeRef {
  updateBlobId: (path: string, newBlobId: string) => void;
  selectFile: (path: string, blobId?: string) => void;
}

export interface UseFileTreeOptions {
  treeId?: string;
  onFileSelect?: (path: string, blobId?: string) => void | Promise<boolean>;
}

export interface UseFileTreeReturn {
  nodes: FileTreeNode[];
  selectedPath: string | undefined;
  setSelectedPath: React.Dispatch<React.SetStateAction<string | undefined>>;
  saveSelectedPath: (path: string | undefined) => void;
  loading: boolean;
  error: string | null;
  fetchTree: () => Promise<void>;
  addNode: (entry: import('@/types/file-tree').TreeEntry, autoSelect?: boolean) => void;
  removeNode: (path: string, isDirectory?: boolean, nextSelection?: { path: string; blobId?: string; selectDirectory?: boolean }) => void;
  updateNode: (oldPath: string, newPath: string, newBlobId?: string) => void;
  toggleNode: (node: FileTreeNode) => void;
  expandPath: (path: string) => void;
  selectNode: (node: FileTreeNode) => Promise<void>;
  checkNameExists: (parentPath: string, name: string, excludePath?: string) => boolean;
  ref: React.RefObject<FileTreeRef>;
}

export function useFileTree({ treeId, onFileSelect }: UseFileTreeOptions): UseFileTreeReturn {
  const {
    nodes,
    setNodes,
    selectedPath,
    setSelectedPath,
    loading,
    setLoading,
    error,
    setError,
    onFileSelectRef,
  } = useTreeState({ onFileSelect });

  const {
    saveSelectedPath,
    loadSelectedPath,
    saveExpandedState,
    loadExpandedState,
  } = useTreePersistence({ treeId });

  const { selectNode, handleAutoSelect } = useTreeSelection({
    selectedPath,
    setSelectedPath,
    onFileSelectRef,
    saveSelectedPath,
  });

  const {
    addNode,
    removeNode,
    updateNode,
    toggleNode,
    expandPath,
    checkNameExists,
    updateBlobId,
  } = useTreeOperations({
    nodes,
    setNodes,
    selectedPath,
    setSelectedPath,
    onFileSelectRef,
    saveSelectedPath,
    saveExpandedState,
  });

  const fetchTree = useCallback(async () => {
    if (!treeId) return;

    setLoading(true);
    setError(null);
    try {
      const treeData = await api.get<TreeStructure>(`/trees/${treeId}`);
      const entries = treeData.entries ?? [];
      const treeNodes = buildTree(entries);

      const expandedPaths = loadExpandedState();
      const finalNodes = applyExpandedState(treeNodes, expandedPaths);
      setNodes(finalNodes);

      const savedPath = loadSelectedPath();
      if (savedPath) {
        const foundNode = findNodeInTree(finalNodes, savedPath);
        if (foundNode && foundNode.type === 'blob') {
          setSelectedPath(savedPath);
          onFileSelectRef.current?.(savedPath, foundNode.blob_id);
        } else {
          const fallback = findFirstFileInDirectory(savedPath, finalNodes);
          if (fallback) {
            handleAutoSelect(fallback.path, fallback.blobId);
          } else {
            saveSelectedPath(undefined);
          }
        }
      } else {
        const skillMdNode = findSkillMdNode(finalNodes);
        if (skillMdNode && skillMdNode.type === 'blob') {
          handleAutoSelect('SKILL.md', skillMdNode.blob_id);
        }
      }
    } catch (err) {
      const errorMessage = err instanceof Error
        ? err.message
        : err && typeof err === 'object' && 'message' in err
          ? String((err as { message: unknown }).message)
          : 'loadTreeFailed';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [treeId, loadExpandedState, loadSelectedPath, saveSelectedPath, setLoading, setError, setNodes, setSelectedPath, onFileSelectRef, handleAutoSelect]);

  useEffect(() => {
    fetchTree();
  }, [fetchTree]);

  const ref = useRef<FileTreeRef>({
    updateBlobId: () => {},
    selectFile: () => {},
  });

  useEffect(() => {
    ref.current = {
      updateBlobId: (path: string, newBlobId: string) => {
        updateBlobId(path, newBlobId);
      },
      selectFile: (path: string, blobId?: string) => {
        setSelectedPath(path);
        saveSelectedPath(path);
        if (blobId) {
          onFileSelectRef.current?.(path, blobId);
        } else {
          const node = findNodeInTree(nodes, path);
          if (node && node.type === 'blob') {
            onFileSelectRef.current?.(path, node.blob_id);
          }
        }
      },
    };
  }, [updateBlobId, setSelectedPath, saveSelectedPath, onFileSelectRef, nodes]);

  return {
    nodes,
    selectedPath,
    setSelectedPath,
    saveSelectedPath,
    loading,
    error,
    fetchTree,
    addNode,
    removeNode,
    updateNode,
    toggleNode,
    expandPath,
    selectNode,
    checkNameExists,
    ref,
  };
}
