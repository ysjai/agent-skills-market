'use client';

import { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';

export interface MarketFileNode {
  id: string;
  name: string;
  path: string;
  type: 'blob' | 'tree';
  blob_id?: string;
  children: MarketFileNode[];
  isExpanded: boolean;
  depth: number;
}

interface UseMarketFileTreeOptions {
  sharedSkillId: string;
}

export function useMarketFileTree({ sharedSkillId }: UseMarketFileTreeOptions) {
  const [nodes, setNodes] = useState<MarketFileNode[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPath, setSelectedPath] = useState('');
  const [selectedBlobId, setSelectedBlobId] = useState('');

  const buildTree = useCallback(
    (entries: Array<{ path: string; blob_id: string | null; type: string }>): MarketFileNode[] => {
      const root: MarketFileNode[] = [];
      const map = new Map<string, MarketFileNode>();

      const sorted = [...entries].sort((a, b) => {
        if (a.type !== b.type) return a.type === 'tree' ? -1 : 1;
        return a.path.localeCompare(b.path);
      });

      for (const entry of sorted) {
        const parts = entry.path.split('/');
        const name = parts[parts.length - 1];
        const depth = parts.length - 1;

        const node: MarketFileNode = {
          id: entry.path,
          name,
          path: entry.path,
          type: entry.type as 'blob' | 'tree',
          blob_id: entry.blob_id || undefined,
          children: [],
          isExpanded: depth === 0,
          depth,
        };

        map.set(entry.path, node);

        if (parts.length === 1) {
          root.push(node);
        } else {
          const parentPath = parts.slice(0, -1).join('/');
          const parent = map.get(parentPath);
          if (parent) {
            parent.children.push(node);
          }
        }
      }

      return root;
    },
    []
  );

  useEffect(() => {
    if (!sharedSkillId) return;

    let cancelled = false;
    setLoading(true);
    setError(null);

    api
      .getMarketSkillTree(sharedSkillId)
      .then((data) => {
        if (!cancelled) {
          setNodes(buildTree(data.entries));
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load file tree');
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [sharedSkillId, buildTree]);

  const toggleNode = useCallback((path: string) => {
    setNodes((prev) => {
      const toggle = (items: MarketFileNode[]): MarketFileNode[] =>
        items.map((item) => {
          if (item.path === path) {
            return { ...item, isExpanded: !item.isExpanded };
          }
          if (item.children.length > 0) {
            return { ...item, children: toggle(item.children) };
          }
          return item;
        });
      return toggle(prev);
    });
  }, []);

  const selectNode = useCallback((path: string, blobId?: string) => {
    setSelectedPath(path);
    setSelectedBlobId(blobId || '');
  }, []);

  return {
    nodes,
    loading,
    error,
    selectedPath,
    selectedBlobId,
    toggleNode,
    selectNode,
  };
}
