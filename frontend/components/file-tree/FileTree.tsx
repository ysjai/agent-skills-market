'use client';

import * as React from 'react';
import { forwardRef, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { FolderTree, FilePlus, FolderPlus } from 'lucide-react';

import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { useToast } from '@/components/ui/Toast';
import { useFileTree } from '@/hooks/useFileTree';
import { useFileTreeDialogs } from '@/hooks/useFileTreeDialogs';
import { useFileUpload } from '@/hooks/useFileUpload';
import { useFolderDownload } from '@/hooks/useFolderDownload';
import { api } from '@/lib/api';
import { findNodeByPath } from '@/lib/file-tree-utils';

import { FileTreeDialogs } from './FileTreeDialogs';
import { FileTreeWarnings } from './FileTreeWarnings';
import { FileTreeDragOverlay } from './FileTreeDragOverlay';
import { FileTreeToolbar } from './FileTreeToolbar';
import { FileTreeItem } from './FileTreeItem';

interface FileTreeProps {
  treeId?: string;
  onFileSelect?: (path: string, blobId?: string) => void | Promise<boolean>;
  className?: string;
  selectedFilePath?: string;
  onFileReload?: (path: string, blobId: string) => void;
  onFileDownload?: (path: string, blobId: string, fileName: string) => void;
}

export interface FileTreeRef {
  updateBlobId: (path: string, newBlobId: string) => void;
  selectFile: (path: string, blobId?: string) => void;
}

export const FileTree = forwardRef<FileTreeRef, FileTreeProps>(function FileTree(
  { treeId, onFileSelect, className, selectedFilePath, onFileReload, onFileDownload },
  ref
) {
  const t = useTranslations('files');
  const { showToast } = useToast();

  const {
    nodes,
    selectedPath,
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
    setSelectedPath,
    saveSelectedPath,
    ref: treeRef,
  } = useFileTree({ treeId, onFileSelect });

  const {
    isDragging,
    setIsDragging,
    conflictDialogOpen,
    conflictFileName,
    handleDrop: originalHandleDrop,
    handleFileInputChange: originalHandleFileInputChange,
    handleFolderInputChange: originalHandleFolderInputChange,
    handleConflictResolution,
    progressDialogOpen,
    progressItems,
    progressCurrent,
    progressTotal,
    progressCurrentFile,
    batchConflictDialogOpen,
    batchConflictItems,
    handleBatchConflictResolve,
    handleBatchConflictCancel,
    handleProgressCancel,
    handleProgressClose,
    windowsWarningFiles,
    windowsConfirmDialogOpen,
    windowsConfirmFiles,
    handleWindowsConfirm,
    handleWindowsCancel,
  } = useFileUpload({
    treeId,
    nodes,
    onFileSelect,
    onFileReload,
    selectedFilePath,
    fetchTree,
    addNode,
    removeNode,
    showToast,
    setSelectedPath,
    saveSelectedPath,
    expandPath,
  });

  const { downloadFolder, downloadFolderAsZip, checkWindowsCompatibility } = useFolderDownload({
    treeId,
    nodes,
    showToast,
  });

  React.useImperativeHandle(ref, () => treeRef.current, [treeRef]);

  const onFileReloadRef = React.useRef(onFileReload);

  React.useEffect(() => {
    onFileReloadRef.current = onFileReload;
  }, [onFileReload]);

  const [dragSource, setDragSource] = React.useState<string | null>(null);
  const [dragOverTarget, setDragOverTarget] = React.useState<string | null>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);
  const folderFileInputRef = React.useRef<HTMLInputElement>(null);
  const folderUploadInputRef = React.useRef<HTMLInputElement>(null);
  const [targetFolderPath, setTargetFolderPath] = React.useState<string>('');
  const [downloadWarningOpen, setDownloadWarningOpen] = React.useState(false);
  const [downloadWarningFiles, setDownloadWarningFiles] = React.useState<string[]>([]);
  const [pendingDownloadFolder, setPendingDownloadFolder] = React.useState<{ path: string; name: string } | null>(null);

  const {
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
  } = useFileTreeDialogs({
    treeId,
    nodes,
    selectedPath,
    checkNameExists,
    addNode,
    removeNode,
    findNodeByPath,
    t,
    showToast,
  });

  const handleAddFile = useCallback((parentPath: string) => {
    openAddDialog('file', parentPath);
  }, [openAddDialog]);

  const handleAddFolder = useCallback((parentPath: string) => {
    openAddDialog('folder', parentPath);
  }, [openAddDialog]);

  const handleDialogConfirmWrapper = async (name: string) => {
    await handleDialogConfirm(name);
    const fileName = dialogType === 'file' && name && !name.includes('.') ? `${name}.md` : name;
    const newPath = dialogParentPath ? `${dialogParentPath}/${fileName}` : fileName;
    const node = findNodeByPath(nodes, newPath);
    if (node && node.type === 'blob') {
      treeRef.current?.selectFile(newPath, node.blob_id);
    }
  };

  const handleRename = useCallback(async (oldPath: string, newPath: string): Promise<boolean> => {
    const parentPath = oldPath.includes('/')
      ? oldPath.substring(0, oldPath.lastIndexOf('/'))
      : '';
    const newName = newPath.split('/').pop() || '';

    if (newPath === oldPath) {
      return true;
    }

    const exists = checkNameExists(parentPath, newName, oldPath);
    if (exists) {
      return false;
    }

    try {
      const response = await api.put<{
        id: string;
        entries: Array<{
          path: string;
          blob_id: string | null;
          type: string;
        }>;
        created_at: string;
      }>(`/trees/${treeId}/files/rename`, {
        old_path: oldPath,
        new_path: newPath,
      });

      const renamedEntry = response.entries.find((e) => e.path === newPath);
      const newBlobId = renamedEntry?.blob_id || null;
      updateNode(oldPath, newPath, newBlobId || undefined);
      return true;
    } catch {
      return false;
    }
  }, [checkNameExists, treeId, updateNode]);

  const handleMove = useCallback(async (source: string, targetDir: string) => {
    if (!treeId || source === targetDir) return;

    const fileName = source.split('/').pop();
    if (!fileName) return;
    
    const targetPath = targetDir ? `${targetDir}/${fileName}` : fileName;
    
    try {
      const response = await api.put<{
        id: string;
        entries: Array<{
          path: string;
          blob_id: string | null;
          type: string;
        }>;
        created_at: string;
      }>(`/trees/${treeId}/files/move`, {
        source,
        target: targetPath,
      });

      const movedEntry = response.entries.find((e) => e.path === targetPath);
      const newBlobId = movedEntry?.blob_id || null;
      removeNode(source);
      addNode({
        path: targetPath,
        blob_id: newBlobId || undefined,
        type: movedEntry?.type as 'blob' | 'tree' || 'blob',
      });
    } catch (err) {
      showToast(err instanceof Error ? err.message : t('moveFailed'), 'error');
    }
  }, [treeId, removeNode, addNode, showToast, t]);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
    setDragSource(null);
    setDragOverTarget(null);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.currentTarget === e.target) {
      setIsDragging(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleCreateRootFile = () => {
    handleAddFile('');
  };

  const handleCreateRootFolder = () => {
    handleAddFolder('');
  };

  const handleDeleteWithConfirm = useCallback((path: string) => {
    handleDelete(path);
  }, [handleDelete]);

  const handleDownloadWithConfirm = useCallback((path: string, blobId: string, fileName: string) => {
    if (onFileDownload) {
      onFileDownload(path, blobId, fileName);
    }
  }, [onFileDownload]);

  const handleDownloadFolderWithCheck = useCallback((folderPath: string, folderName: string) => {
    const { hasIllegalChars, affectedFiles } = checkWindowsCompatibility(folderPath);

    if (!hasIllegalChars) {
      void downloadFolder(folderPath, folderName);
      return;
    }

    setDownloadWarningFiles(affectedFiles);
    setPendingDownloadFolder({ path: folderPath, name: folderName });
    setDownloadWarningOpen(true);
  }, [checkWindowsCompatibility, downloadFolder]);

  const handleDownloadWithAutoRename = useCallback(() => {
    setDownloadWarningOpen(false);
    if (pendingDownloadFolder) {
      void downloadFolder(pendingDownloadFolder.path, pendingDownloadFolder.name, false);
    }
  }, [pendingDownloadFolder, downloadFolder]);

  const handleDownloadAsZip = useCallback(() => {
    setDownloadWarningOpen(false);
    if (pendingDownloadFolder) {
      void downloadFolderAsZip(pendingDownloadFolder.path, pendingDownloadFolder.name);
    }
  }, [pendingDownloadFolder, downloadFolderAsZip]);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleUploadFileToFolder = useCallback((folderPath: string) => {
    setTargetFolderPath(folderPath);
    folderFileInputRef.current?.click();
  }, []);

  const handleUploadFolderToFolder = useCallback((folderPath: string) => {
    setTargetFolderPath(folderPath);
    folderUploadInputRef.current?.click();
  }, []);

  const handleUploadFolderToRoot = () => {
    setTargetFolderPath('');
    folderUploadInputRef.current?.click();
  };

  const handleFolderFileInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    await originalHandleFileInputChange(e, targetFolderPath);
    setTargetFolderPath('');
  };

  const handleFolderUploadInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    await originalHandleFolderInputChange(e, targetFolderPath);
    setTargetFolderPath('');
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    if (!treeId) return;

    const files = Array.from(e.dataTransfer.files);

    if (files.length > 0) {
      await originalHandleDrop(e);
    }
  };

  const handleFileInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!treeId || !e.target.files) return;

    const files = Array.from(e.target.files);

    if (files.length > 0) {
      await originalHandleFileInputChange(e);
    } else {
      e.target.value = '';
    }
  };

  if (!treeId) {
    return (
      <Card className={cn('h-full', className)}>
        <CardContent className="flex h-full items-center justify-center p-8">
          <p className="text-gray-500">{t('selectSkill')}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card
        className={cn(
          'flex h-full flex-col transition-colors',
          isDragging && 'ring-2 ring-blue-500 ring-offset-2',
          className
        )}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
          <CardTitle className="flex items-center gap-2 text-base font-semibold">
            <FolderTree className="h-5 w-5 text-gray-600" />
            {t('title')}
          </CardTitle>
          <FileTreeToolbar
            onNewFile={handleCreateRootFile}
            onNewFolder={handleCreateRootFolder}
            onUpload={handleUploadClick}
            onRefresh={handleUploadFolderToRoot}
          />
        </CardHeader>

        <CardContent className="flex-1 overflow-auto py-2">
          <input
            ref={fileInputRef}
            type="file"
            multiple
            className="hidden"
            onChange={handleFileInputChange}
          />
          <input
            ref={folderFileInputRef}
            type="file"
            multiple
            className="hidden"
            onChange={handleFolderFileInputChange}
          />
          <input
            ref={folderUploadInputRef}
            type="file"
            // @ts-expect-error webkitdirectory is non-standard but widely supported
            webkitdirectory=""
            className="hidden"
            onChange={handleFolderUploadInputChange}
          />

          <FileTreeDragOverlay isDragging={isDragging} />

          {error && (
            <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">
              {error === 'loadTreeFailed' ? t('loadTreeFailed') : error}
            </div>
          )}

          <FileTreeWarnings windowsWarningFiles={windowsWarningFiles} />

          {nodes.length === 0 && !loading ? (
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <FolderTree className="h-12 w-12 text-gray-300" />
              <p className="mt-2 text-sm text-gray-500">{t('noFiles')}</p>
              <div className="mt-4 flex gap-2">
                <Button variant="outline" size="sm" onClick={handleCreateRootFile}>
                  <FilePlus className="mr-1 h-4 w-4" />
                  {t('newFile')}
                </Button>
                <Button variant="outline" size="sm" onClick={handleCreateRootFolder}>
                  <FolderPlus className="mr-1 h-4 w-4" />
                  {t('newFolder')}
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-0.5">
              {nodes.map((node) => (
                <FileTreeItem
                  key={node.id}
                  node={node}
                  onToggle={toggleNode}
                  onSelect={selectNode}
                  onAddFile={handleAddFile}
                  onAddFolder={handleAddFolder}
                  onDelete={handleDeleteWithConfirm}
                  onRename={handleRename}
                  onMove={handleMove}
                  onDragStart={setDragSource}
                  onDragOver={setDragOverTarget}
                  dragSource={dragSource}
                  dragOverTarget={dragOverTarget}
                  selectedPath={selectedPath}
                  onDownload={handleDownloadWithConfirm}
                  onDownloadFolder={handleDownloadFolderWithCheck}
                  onUploadFile={handleUploadFileToFolder}
                  onUploadFolder={handleUploadFolderToFolder}
                />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <FileTreeDialogs
        // Input Dialog
        dialogOpen={dialogOpen}
        dialogType={dialogType}
        dialogError={dialogError}
        onDialogConfirm={handleDialogConfirmWrapper}
        onDialogCancel={closeAddDialog}
        // Delete Confirm Dialog
        deleteConfirmOpen={deleteConfirmOpen}
        deleteTargetName={deleteTargetName}
        deleteTargetPath={deleteTargetPath}
        isDeleting={isDeleting}
        deleteError={deleteError}
        onDeleteConfirm={executeDelete}
        onDeleteCancel={closeDeleteDialog}
        // Conflict Dialog
        conflictDialogOpen={conflictDialogOpen}
        conflictFileName={conflictFileName}
        onConflictResolve={handleConflictResolution}
        // Progress Dialog
        progressDialogOpen={progressDialogOpen}
        progressItems={progressItems}
        progressCurrent={progressCurrent}
        progressTotal={progressTotal}
        progressCurrentFile={progressCurrentFile}
        onProgressCancel={handleProgressCancel}
        onProgressClose={handleProgressClose}
        // Batch Conflict Dialog
        batchConflictDialogOpen={batchConflictDialogOpen}
        batchConflictItems={batchConflictItems}
        onBatchConflictResolve={handleBatchConflictResolve}
        onBatchConflictCancel={handleBatchConflictCancel}
        // Download Warning Dialog
        downloadWarningOpen={downloadWarningOpen}
        downloadWarningFiles={downloadWarningFiles}
        pendingDownloadFolder={pendingDownloadFolder}
        onDownloadWarningClose={() => setDownloadWarningOpen(false)}
        onDownloadWithAutoRename={handleDownloadWithAutoRename}
        onDownloadAsZip={handleDownloadAsZip}
        // Windows Upload Confirm Dialog
        windowsConfirmDialogOpen={windowsConfirmDialogOpen}
        windowsConfirmFiles={windowsConfirmFiles}
        onWindowsConfirm={handleWindowsConfirm}
        onWindowsCancel={handleWindowsCancel}
      />
    </>
  );
});
