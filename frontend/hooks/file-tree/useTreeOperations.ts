import { useCallback } from 'react';
import type { FileTreeNode, TreeEntry } from '@/types/file-tree';
import { generateId, findFirstFileInDirectory } from '@/lib/file-tree-utils';
import type { OnFileSelectCallback } from './useTreeState';

export interface UseTreeOperationsOptions {
  nodes: FileTreeNode[];
  setNodes: React.Dispatch<React.SetStateAction<FileTreeNode[]>>;
  selectedPath: string | undefined;
  setSelectedPath: React.Dispatch<React.SetStateAction<string | undefined>>;
  onFileSelectRef: React.RefObject<OnFileSelectCallback | undefined>;
  saveSelectedPath: (path: string | undefined) => void;
  saveExpandedState: (nodes: FileTreeNode[]) => void;
}

export interface UseTreeOperationsReturn {
  addNode: (entry: TreeEntry, autoSelect?: boolean) => void;
  removeNode: (path: string, isDirectory?: boolean, nextSelection?: { path: string; blobId?: string; selectDirectory?: boolean }) => void;
  updateNode: (oldPath: string, newPath: string, newBlobId?: string) => void;
  toggleNode: (node: FileTreeNode) => void;
  expandPath: (path: string) => void;
  checkNameExists: (parentPath: string, name: string, excludePath?: string) => boolean;
  updateBlobId: (path: string, newBlobId: string) => void;
}

export function useTreeOperations({
  nodes,
  setNodes,
  selectedPath,
  setSelectedPath,
  onFileSelectRef,
  saveSelectedPath,
  saveExpandedState,
}: UseTreeOperationsOptions): UseTreeOperationsReturn {
  const toggleNode = useCallback((node: FileTreeNode) => {
    setNodes((prevNodes) => {
      const updateNode = (nodes: FileTreeNode[]): FileTreeNode[] => {
        return nodes.map((n) => {
          if (n.id === node.id) {
            return { ...n, isExpanded: !n.isExpanded };
          }
          if (n.children) {
            return { ...n, children: updateNode(n.children as FileTreeNode[]) };
          }
          return n;
        });
      };
      const updatedNodes = updateNode(prevNodes);
      setTimeout(() => saveExpandedState(updatedNodes), 0);
      return updatedNodes;
    });
  }, [setNodes, saveExpandedState]);

  const expandPath = useCallback((path: string) => {
    setNodes((prevNodes) => {
      const updateNode = (nodes: FileTreeNode[]): FileTreeNode[] => {
        return nodes.map((n) => {
          if (n.path === path && n.type === 'tree') {
            return { ...n, isExpanded: true };
          }
          if (n.children) {
            return { ...n, children: updateNode(n.children as FileTreeNode[]) };
          }
          return n;
        });
      };
      const updatedNodes = updateNode(prevNodes);
      setTimeout(() => saveExpandedState(updatedNodes), 0);
      return updatedNodes;
    });
  }, [setNodes, saveExpandedState]);

  const addNode = useCallback((entry: TreeEntry, autoSelect: boolean = false) => {
    const name = entry.name || entry.path.split('/').pop() || entry.path;
    const newNode: FileTreeNode = {
      path: entry.path,
      blob_id: entry.blob_id,
      type: entry.type,
      name,
      id: generateId(),
      isExpanded: entry.type === 'tree',
      depth: 0,
      children: entry.type === 'tree' ? [] : undefined,
    };

    setNodes((prevNodes) => {
      const parentPath = entry.path.includes('/')
        ? entry.path.substring(0, entry.path.lastIndexOf('/'))
        : '';

      if (!parentPath) {
        const newNodes = [...prevNodes, newNode];
        newNodes.sort((a, b) => {
          if (a.type === b.type) {
            return (a.name || '').localeCompare(b.name || '');
          }
          return a.type === 'tree' ? -1 : 1;
        });
        return newNodes;
      }

      const addToParent = (nodes: FileTreeNode[]): FileTreeNode[] => {
        return nodes.map((n) => {
          if (n.path === parentPath && n.children) {
            const newChildren = [...n.children, { ...newNode, depth: n.depth + 1 }];
            newChildren.sort((a, b) => {
              if (a.type === b.type) {
                return (a.name || '').localeCompare(b.name || '');
              }
              return a.type === 'tree' ? -1 : 1;
            });
            return { ...n, isExpanded: true, children: newChildren };
          }
          if (n.children) {
            return { ...n, children: addToParent(n.children as FileTreeNode[]) };
          }
          return n;
        });
      };

      return addToParent(prevNodes);
    });

    if (autoSelect && entry.type === 'blob') {
      setSelectedPath(entry.path);
      saveSelectedPath(entry.path);
      onFileSelectRef.current?.(entry.path, entry.blob_id);
    }
  }, [setNodes, setSelectedPath, saveSelectedPath, onFileSelectRef]);

  const removeNode = useCallback((path: string, isDirectory = false, nextSelection?: { path: string; blobId?: string; selectDirectory?: boolean }) => {
    let currentNodes: FileTreeNode[] = [];
    setNodes((prevNodes) => {
      currentNodes = prevNodes;
      const removeFromNodes = (nodes: FileTreeNode[]): FileTreeNode[] => {
        return nodes
          .filter((n) => {
            if (n.path === path) return false;
            if (isDirectory && n.path.startsWith(`${path}/`)) return false;
            return true;
          })
          .map((n) => {
            if (n.children) {
              return { ...n, children: removeFromNodes(n.children as FileTreeNode[]) };
            }
            return n;
          });
      };
      return removeFromNodes(prevNodes);
    });

    if (selectedPath === path || (isDirectory && selectedPath?.startsWith(`${path}/`))) {
      if (nextSelection?.path) {
        setSelectedPath(nextSelection.path);
        saveSelectedPath(nextSelection.path);
        if (!nextSelection.selectDirectory) {
          onFileSelectRef.current?.(nextSelection.path, nextSelection.blobId);
        }
      } else {
        setTimeout(() => {
          const fallback = findFirstFileInDirectory(path, currentNodes);
          if (fallback) {
            setSelectedPath(fallback.path);
            saveSelectedPath(fallback.path);
            onFileSelectRef.current?.(fallback.path, fallback.blobId);
          } else {
            setSelectedPath(undefined);
            saveSelectedPath(undefined);
          }
        }, 0);
      }
    }
  }, [selectedPath, setSelectedPath, setNodes, saveSelectedPath, onFileSelectRef]);

  const updateNode = useCallback((oldPath: string, newPath: string, newBlobId?: string) => {
    setNodes((prevNodes) => {
      const updatePath = (nodes: FileTreeNode[]): FileTreeNode[] => {
        return nodes.map((n) => {
          if (n.path === oldPath) {
            const newName = newPath.split('/').pop() || newPath;
            return {
              ...n,
              path: newPath,
              name: newName,
              blob_id: newBlobId || n.blob_id,
            };
          }
          if (n.children) {
            return { ...n, children: updatePath(n.children as FileTreeNode[]) };
          }
          return n;
        });
      };
      return updatePath(prevNodes);
    });
    if (selectedPath === oldPath) {
      setSelectedPath(newPath);
    }
  }, [selectedPath, setSelectedPath, setNodes]);

  const checkNameExists = useCallback((parentPath: string, name: string, excludePath?: string): boolean => {
    const newPath = parentPath ? `${parentPath}/${name}` : name;
    const findPath = (nodeList: FileTreeNode[]): boolean => {
      for (const node of nodeList) {
        if (excludePath && node.path === excludePath) continue;
        if (node.path === newPath) return true;
        if (node.children && findPath(node.children as FileTreeNode[])) return true;
      }
      return false;
    };
    return findPath(nodes);
  }, [nodes]);

  const updateBlobId = useCallback((path: string, newBlobId: string) => {
    setNodes((prevNodes) => {
      const updateNodeRecursive = (nodes: FileTreeNode[]): FileTreeNode[] => {
        return nodes.map((n) => {
          if (n.path === path) {
            return { ...n, blob_id: newBlobId };
          }
          if (n.children) {
            return { ...n, children: updateNodeRecursive(n.children as FileTreeNode[]) };
          }
          return n;
        });
      };
      return updateNodeRecursive(prevNodes);
    });
  }, [setNodes]);

  return {
    addNode,
    removeNode,
    updateNode,
    toggleNode,
    expandPath,
    checkNameExists,
    updateBlobId,
  };
}
