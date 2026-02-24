import { useState, useCallback } from 'react';
import type { FileTreeNode, TreeEntry } from '@/types/file-tree';
import { api } from '@/lib/api';
import { logger } from '@/lib/logger';
import { findNodeByPath, findNextFileAfterDelete } from '@/lib/file-tree-utils';

export interface UseFileTreeDialogsOptions {
  treeId?: string;
  nodes: FileTreeNode[];
  selectedPath: string | undefined;
  checkNameExists: (parentPath: string, name: string, excludePath?: string) => boolean;
  addNode: (entry: TreeEntry, autoSelect?: boolean) => void;
  removeNode: (path: string, isDirectory?: boolean, nextSelection?: { path: string; blobId?: string; selectDirectory?: boolean }) => void;
  findNodeByPath: typeof findNodeByPath;
  t: (key: string) => string;
  showToast: (message: string, type: 'success' | 'error' | 'info') => void;
}

export interface UseFileTreeDialogsReturn {
  dialogOpen: boolean;
  dialogType: 'file' | 'folder';
  dialogParentPath: string;
  dialogError: string | undefined;
  deleteConfirmOpen: boolean;
  deleteTargetPath: string;
  deleteTargetName: string;
  isDeleting: boolean;
  deleteError: string | null;
  openAddDialog: (type: 'file' | 'folder', parentPath: string) => void;
  closeAddDialog: () => void;
  handleDialogConfirm: (name: string) => Promise<void>;
  handleDelete: (path: string) => void;
  closeDeleteDialog: () => void;
  executeDelete: () => Promise<void>;
}

export function useFileTreeDialogs({
  treeId,
  nodes,
  selectedPath,
  checkNameExists,
  addNode,
  removeNode,
  findNodeByPath: findNodeByPathFn,
  t,
  showToast,
}: UseFileTreeDialogsOptions): UseFileTreeDialogsReturn {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogType, setDialogType] = useState<'file' | 'folder'>('file');
  const [dialogParentPath, setDialogParentPath] = useState('');
  const [dialogError, setDialogError] = useState<string | undefined>();

  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [deleteTargetPath, setDeleteTargetPath] = useState('');
  const [deleteTargetName, setDeleteTargetName] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const openAddDialog = useCallback((type: 'file' | 'folder', parentPath: string) => {
    setDialogType(type);
    setDialogParentPath(parentPath);
    setDialogError(undefined);
    setDialogOpen(true);
  }, []);

  const closeAddDialog = useCallback(() => {
    setDialogOpen(false);
    setDialogError(undefined);
  }, []);

  const handleDialogConfirm = useCallback(async (name: string) => {
    let fileName = name.trim();

    if (dialogType === 'file' && fileName && !fileName.includes('.')) {
      fileName = `${fileName}.md`;
    }

    const exists = checkNameExists(dialogParentPath, fileName);
    if (exists) {
      setDialogError(t(dialogType === 'file' ? 'fileExists' : 'folderExists'));
      return;
    }

    const newPath = dialogParentPath ? `${dialogParentPath}/${fileName}` : fileName;

    try {
      const response = await api.post<{
        id: string;
        entries: Array<{
          path: string;
          blob_id: string | null;
          type: string;
        }>;
        created_at: string;
      }>(`/trees/${treeId}/files`, {
        path: newPath,
        type: dialogType === 'file' ? 'blob' : 'tree',
        content: dialogType === 'file' ? '' : undefined,
      });

      const newEntry = response.entries.find((e) => e.path === newPath);
      if (newEntry) {
        const isFile = newEntry.type === 'blob';
        addNode({
          path: newEntry.path,
          blob_id: newEntry.blob_id || undefined,
          type: newEntry.type as 'blob' | 'tree',
        }, isFile);
      }
      setDialogOpen(false);
    } catch (err) {
      const errorMessage = err instanceof Error
        ? err.message
        : err && typeof err === 'object' && 'message' in err
          ? String((err as { message: unknown }).message)
          : dialogType === 'file' ? t('createFileFailed') : t('createFolderFailed');
      setDialogError(errorMessage);
    }
  }, [checkNameExists, dialogParentPath, dialogType, treeId, addNode]);

  const handleDelete = useCallback((path: string) => {
    if (path === 'SKILL.md') {
      showToast(t('cannotDeleteSkillMd'), 'error');
      return;
    }

    const node = findNodeByPathFn(nodes, path);
    const nodeName = node?.name || path;
    setDeleteTargetPath(path);
    setDeleteTargetName(nodeName);
    setDeleteError(null);
    setDeleteConfirmOpen(true);
  }, [nodes, findNodeByPathFn, t, showToast]);

  const executeDelete = useCallback(async () => {
    if (!deleteTargetPath) return;

    setIsDeleting(true);
    setDeleteError(null);

    try {
      const node = findNodeByPathFn(nodes, deleteTargetPath);
      const isDirectory = node?.type === 'tree';
      const deletePath = deleteTargetPath.replace(/\/$/, '');

      const nextSelection = findNextFileAfterDelete(nodes, deletePath, selectedPath);

      await api.delete(`/trees/${treeId}/files`, { path: deletePath });
      removeNode(deletePath, isDirectory, nextSelection.path ? {
        path: nextSelection.path,
        blobId: nextSelection.blobId || undefined,
        selectDirectory: nextSelection.selectDirectory,
      } : undefined);
      setDeleteConfirmOpen(false);
      setDeleteTargetPath('');
      setDeleteTargetName('');
    } catch (err) {
      logger.error('Delete error:', err);
      let errorMessage: string;
      if (err instanceof Error) {
        errorMessage = err.message;
      } else if (err && typeof err === 'object') {
        errorMessage = JSON.stringify(err);
      } else {
        errorMessage = String(err);
      }
      setDeleteError(`Delete failed: ${errorMessage}`);
    } finally {
      setIsDeleting(false);
    }
  }, [deleteTargetPath, treeId, nodes, selectedPath, findNodeByPathFn, removeNode]);

  const closeDeleteDialog = useCallback(() => {
    if (!isDeleting) {
      setDeleteConfirmOpen(false);
      setDeleteTargetPath('');
      setDeleteTargetName('');
      setDeleteError(null);
    }
  }, [isDeleting]);

  return {
    dialogOpen,
    dialogType,
    dialogParentPath,
    dialogError,
    deleteConfirmOpen,
    deleteTargetPath,
    deleteTargetName,
    isDeleting,
    deleteError,
    openAddDialog,
    closeAddDialog,
    handleDialogConfirm,
    handleDelete,
    closeDeleteDialog,
    executeDelete,
  };
}
