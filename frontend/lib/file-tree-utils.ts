import type { TreeEntry, FileTreeNode } from '@/types/file-tree';

export const generateId = () => Math.random().toString(36).substring(2, 9);

export function normalizePath(path: string): string {
  return path.endsWith('/') ? path.slice(0, -1) : path;
}

export function buildTree(entries: TreeEntry[]): FileTreeNode[] {
  if (!entries || entries.length === 0) return [];
  
  const root: FileTreeNode[] = [];
  const nodeMap = new Map<string, FileTreeNode>();

  entries.forEach((entry) => {
    const normalizedPath = entry.type === 'tree' ? normalizePath(entry.path) : entry.path;
    const name = entry.name || normalizedPath.split('/').pop() || normalizedPath;
    const node: FileTreeNode = {
      path: normalizedPath,
      blob_id: entry.blob_id,
      type: entry.type,
      name,
      id: generateId(),
      isExpanded: false,
      depth: 0,
      children: entry.type === 'tree' ? [] : undefined,
    };
    nodeMap.set(normalizedPath, node);
  });

  entries.forEach((entry) => {
    const normalizedPath = entry.type === 'tree' ? normalizePath(entry.path) : entry.path;
    const node = nodeMap.get(normalizedPath)!;
    const lastSlash = normalizedPath.lastIndexOf('/');

    if (lastSlash === -1) {
      root.push(node);
    } else {
      const parentPath = normalizedPath.substring(0, lastSlash);
      const parent = nodeMap.get(parentPath);
      if (parent && parent.children) {
        node.depth = parent.depth + 1;
        parent.children.push(node);
      }
    }
  });

  const sortNodes = (nodes: FileTreeNode[]) => {
    nodes.sort((a, b) => {
      if (a.type === b.type) {
        return (a.name || '').localeCompare(b.name || '');
      }
      return a.type === 'tree' ? -1 : 1;
    });
    nodes.forEach((node) => {
      if (node.children) {
        sortNodes(node.children as FileTreeNode[]);
      }
    });
  };
  sortNodes(root);

  return root;
}

export const findNodeByPath = (nodeList: FileTreeNode[], targetPath: string): FileTreeNode | null => {
  for (const node of nodeList) {
    if (node.path === targetPath) return node;
    if (node.children) {
      const found = findNodeByPath(node.children as FileTreeNode[], targetPath);
      if (found) return found;
    }
  }
  return null;
};

export const findFirstFileInDirectory = (targetPath: string, nodeList: FileTreeNode[]): { path: string; blobId: string } | null => {
  const parentPath = targetPath.includes('/') 
    ? targetPath.substring(0, targetPath.lastIndexOf('/'))
    : '';

  const findInNodes = (nodes: FileTreeNode[]): { path: string; blobId: string } | null => {
    for (const node of nodes) {
      if (node.type === 'blob') {
        if (parentPath === '') {
          const nodeDir = node.path.includes('/') 
            ? node.path.substring(0, node.path.lastIndexOf('/'))
            : '';
          if (nodeDir === parentPath) {
            return { path: node.path, blobId: node.blob_id || '' };
          }
        } else if (node.path.startsWith(parentPath + '/')) {
          const relativePath = node.path.substring(parentPath.length + 1);
          if (!relativePath.includes('/')) {
            return { path: node.path, blobId: node.blob_id || '' };
          }
        }
      }
      if (node.children) {
        const result = findInNodes(node.children as FileTreeNode[]);
        if (result) return result;
      }
    }
    return null;
  };

  return findInNodes(nodeList);
};

export const applyExpandedState = (nodeList: FileTreeNode[], expandedPaths: string[]): FileTreeNode[] => {
  return nodeList.map((node) => {
    const newNode = { ...node };
    if (expandedPaths.includes(node.path) && node.type === 'tree') {
      newNode.isExpanded = true;
    }
    if (node.children) {
      newNode.children = applyExpandedState(node.children as FileTreeNode[], expandedPaths);
    }
    return newNode;
  });
};

export const findSiblingFiles = (nodeList: FileTreeNode[], targetPath: string): FileTreeNode[] => {
  const parentPath = targetPath.includes('/') 
    ? targetPath.substring(0, targetPath.lastIndexOf('/'))
    : '';

  const siblings: FileTreeNode[] = [];

  const findInNodes = (nodes: FileTreeNode[]): void => {
    for (const node of nodes) {
      if (node.type === 'blob') {
        const nodeParentPath = node.path.includes('/') 
          ? node.path.substring(0, node.path.lastIndexOf('/'))
          : '';
        if (nodeParentPath === parentPath) {
          siblings.push(node);
        }
      }
      if (node.children) {
        findInNodes(node.children as FileTreeNode[]);
      }
    }
  };

  findInNodes(nodeList);
  return siblings.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
};

export const findNextFileAfterDelete = (
  nodeList: FileTreeNode[],
  deletedPath: string,
  currentSelectedPath: string | undefined
): { path: string | null; blobId: string | null; selectDirectory: boolean } => {
  if (deletedPath !== currentSelectedPath) {
    return { path: null, blobId: null, selectDirectory: false };
  }

  const siblings = findSiblingFiles(nodeList, deletedPath);
  const deletedIndex = siblings.findIndex((node) => node.path === deletedPath);

  const getParentPath = (path: string) => path.includes('/') 
    ? path.substring(0, path.lastIndexOf('/'))
    : '';

  if (siblings.length === 0 || deletedIndex === -1 || siblings.length === 1) {
    const parentPath = getParentPath(deletedPath);
    return { path: parentPath || null, blobId: null, selectDirectory: true };
  }

  const nextIndex = (deletedIndex + 1) % siblings.length;
  const nextFile = siblings[nextIndex];
  return { path: nextFile.path, blobId: nextFile.blob_id || null, selectDirectory: false };
};
