export interface TreeEntry {
  path: string;
  blob_id?: string;
  type: 'blob' | 'tree';
  name?: string;
  children?: TreeEntry[];
}

export interface TreeStructure {
  id: string;
  entries: TreeEntry[];
  created_at: string;
}

export interface FileTreeNode extends TreeEntry {
  id: string;
  isExpanded?: boolean;
  isEditing?: boolean;
  depth: number;
  children?: FileTreeNode[];
}

export interface CreateFileRequest {
  path: string;
  content?: string;
  type: 'blob' | 'tree';
}

export interface RenameFileRequest {
  oldPath: string;
  newPath: string;
}

export interface FileOperation {
  type: 'create' | 'delete' | 'rename';
  path: string;
  newPath?: string;
  fileType?: 'blob' | 'tree';
}
