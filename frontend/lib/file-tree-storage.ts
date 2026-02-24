import type { FileTreeNode } from '@/types/file-tree';

export const getExpandedStateKey = (treeId?: string): string => {
  return `filetree_expanded_${treeId || 'default'}`;
};

export const getSelectedPathKey = (treeId?: string): string => {
  return `filetree_selected_${treeId || 'default'}`;
};

export const saveSelectedPath = (path: string | undefined, key: string): void => {
  if (path) {
    localStorage.setItem(key, path);
  } else {
    localStorage.removeItem(key);
  }
};

export const loadSelectedPath = (key: string): string | undefined => {
  try {
    return localStorage.getItem(key) || undefined;
  } catch {
    return undefined;
  }
};

const collectExpandedPaths = (nodes: FileTreeNode[]): string[] => {
  const paths: string[] = [];
  for (const node of nodes) {
    if (node.isExpanded && node.type === 'tree') {
      paths.push(node.path);
    }
    if (node.children) {
      paths.push(...collectExpandedPaths(node.children as FileTreeNode[]));
    }
  }
  return paths;
};

export const saveExpandedState = (nodes: FileTreeNode[], key: string): void => {
  const expandedPaths = collectExpandedPaths(nodes);
  localStorage.setItem(key, JSON.stringify(expandedPaths));
};

export const loadExpandedState = (key: string): string[] => {
  try {
    const saved = localStorage.getItem(key);
    if (saved) {
      return JSON.parse(saved) as string[];
    }
  } catch {
  }
  return [];
};
