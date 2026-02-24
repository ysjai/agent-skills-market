import { useState, useRef, useEffect } from 'react';
import type { FileTreeNode } from '@/types/file-tree';

export interface OnFileSelectCallback {
  (path: string, blobId?: string): void | Promise<boolean>;
}

export interface UseTreeStateOptions {
  onFileSelect?: OnFileSelectCallback;
}

export interface UseTreeStateReturn {
  nodes: FileTreeNode[];
  setNodes: React.Dispatch<React.SetStateAction<FileTreeNode[]>>;
  selectedPath: string | undefined;
  setSelectedPath: React.Dispatch<React.SetStateAction<string | undefined>>;
  loading: boolean;
  setLoading: React.Dispatch<React.SetStateAction<boolean>>;
  error: string | null;
  setError: React.Dispatch<React.SetStateAction<string | null>>;
  onFileSelectRef: React.RefObject<OnFileSelectCallback | undefined>;
}

export function useTreeState({ onFileSelect }: UseTreeStateOptions): UseTreeStateReturn {
  const [nodes, setNodes] = useState<FileTreeNode[]>([]);
  const [selectedPath, setSelectedPath] = useState<string | undefined>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onFileSelectRef = useRef(onFileSelect);

  useEffect(() => {
    onFileSelectRef.current = onFileSelect;
  }, [onFileSelect]);

  return {
    nodes,
    setNodes,
    selectedPath,
    setSelectedPath,
    loading,
    setLoading,
    error,
    setError,
    onFileSelectRef,
  };
}
