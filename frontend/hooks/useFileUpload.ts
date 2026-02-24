import { useState, useRef, useCallback, useEffect } from 'react';
import type { FileTreeNode, TreeEntry } from '@/types/file-tree';
import type { ProgressItem } from '@/components/ui/ProgressDialog';
import type { ConflictItem, ConflictAction } from '@/components/ui/BatchConflictDialog';
import type { ConflictAction as SingleConflictAction } from '@/components/ui/ConflictDialog';
import { api } from '@/lib/api';
import { getFileType } from '@/lib/file-utils';
import { logger } from '@/lib/logger';
import { hasWindowsReservedChars } from '@/lib/windows-fs';

export interface UseFileUploadOptions {
  treeId?: string;
  nodes: FileTreeNode[];
  onFileSelect?: (path: string, blobId?: string) => void;
  onFileReload?: (path: string, blobId: string) => void;
  selectedFilePath?: string;
  fetchTree: () => Promise<void>;
  addNode: (entry: TreeEntry, autoSelect?: boolean) => void;
  removeNode: (path: string, isDirectory?: boolean) => void;
  showToast: (message: string, type?: 'success' | 'error' | 'info') => void;
  setSelectedPath: React.Dispatch<React.SetStateAction<string | undefined>>;
  saveSelectedPath: (path: string | undefined) => void;
  expandPath: (path: string) => void;
}

export interface UseFileUploadReturn {
  isDragging: boolean;
  setIsDragging: (val: boolean) => void;
  pendingUploadFiles: File[];
  currentUploadIndex: number;
  conflictDialogOpen: boolean;
  conflictFileName: string;

  progressDialogOpen: boolean;
  progressItems: ProgressItem[];
  progressCurrent: number;
  progressTotal: number;
  progressCurrentFile: string;

  batchConflictDialogOpen: boolean;
  batchConflictItems: ConflictItem[];

  uploadBinaryFile: (file: File) => Promise<string>;
  processFileUpload: (files: File[], index?: number, targetFolder?: string) => Promise<void>;
  handleConflictResolution: (action: SingleConflictAction, newName?: string) => Promise<void>;
  handleFileInputChange: (e: React.ChangeEvent<HTMLInputElement>, targetFolder?: string) => Promise<void>;
  handleFolderInputChange: (e: React.ChangeEvent<HTMLInputElement>, targetFolder?: string) => Promise<void>;
  handleBatchConflictResolve: (resolutions: Map<string, ConflictAction>) => Promise<void>;
  handleBatchConflictCancel: () => void;
  handleProgressCancel: () => void;
  handleProgressClose: () => void;
  checkFileExists: (fileName: string) => boolean;
  checkFilesExist: (paths: string[]) => string[];
  handleDrop: (e: React.DragEvent) => Promise<void>;
  windowsWarningFiles: string[];
  windowsConfirmDialogOpen: boolean;
  windowsConfirmFiles: string[];
  pendingUploadTargetFolder: string;
  handleWindowsConfirm: () => void;
  handleWindowsCancel: () => void;
}

export function useFileUpload({
  treeId,
  nodes,
  onFileSelect,
  onFileReload,
  selectedFilePath,
  fetchTree,
  addNode: addNodeCallback,
  removeNode: _removeNode,
  showToast,
  setSelectedPath,
  saveSelectedPath,
  expandPath,
}: UseFileUploadOptions): UseFileUploadReturn {
  const [isDragging, setIsDragging] = useState(false);
  const [pendingUploadFiles, setPendingUploadFiles] = useState<File[]>([]);
  const [currentUploadIndex, setCurrentUploadIndex] = useState(0);
  const [conflictDialogOpen, setConflictDialogOpen] = useState(false);
  const [conflictFileName, setConflictFileName] = useState('');

  const [progressDialogOpen, setProgressDialogOpen] = useState(false);
  const [progressItems, setProgressItems] = useState<ProgressItem[]>([]);
  const [progressCurrent, setProgressCurrent] = useState(0);
  const [progressTotal, setProgressTotal] = useState(0);
  const [progressCurrentFile, setProgressCurrentFile] = useState('');

  const [batchConflictDialogOpen, setBatchConflictDialogOpen] = useState(false);
  const [batchConflictItems, setBatchConflictItems] = useState<ConflictItem[]>([]);
  const [windowsWarningFiles, setWindowsWarningFiles] = useState<string[]>([]);
  const [windowsConfirmDialogOpen, setWindowsConfirmDialogOpen] = useState(false);
  const [windowsConfirmFiles, setWindowsConfirmFiles] = useState<string[]>([]);
  const [pendingUploadTargetFolder, setPendingUploadTargetFolder] = useState<string>('');
  const pendingFilesRef = useRef<File[]>([]);
  const pendingFolderUploadRef = useRef<{
    entries: Array<{ path: string; type: 'blob' | 'tree'; content?: string; blob_id?: string }>;
    targetFolder: string;
  } | null>(null);

  const lastUploadedFileRef = useRef<{ path: string; blobId: string } | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const currentTargetFolderRef = useRef<string | undefined>(undefined);
  const nodesRef = useRef<FileTreeNode[]>(nodes);
  useEffect(() => {
    nodesRef.current = nodes;
  }, [nodes]);

  const checkWindowsWarning = useCallback((fileNames: string[]): string[] => {
    return fileNames.filter(name => hasWindowsReservedChars(name));
  }, []);

  const checkFileExists = useCallback((fileName: string): boolean => {
    const findFile = (nodeList: FileTreeNode[]): boolean => {
      for (const node of nodeList) {
        if (node.path === fileName && node.type === 'blob') return true;
        if (node.children && findFile(node.children as FileTreeNode[])) return true;
      }
      return false;
    };
    return findFile(nodes);
  }, [nodes]);

  const checkFilesExist = useCallback((paths: string[]): string[] => {
    return paths.filter((path) => checkFileExists(path));
  }, [checkFileExists]);

  const uploadBinaryFile = useCallback(async (file: File): Promise<string> => {
    if (abortControllerRef.current?.signal.aborted) {
      throw new Error('Upload cancelled');
    }

    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<{
      id: string;
      content_hash: string;
      size: number;
      compressed: boolean;
      created_at: string;
    }>('/blobs', formData);

    return response.id;
  }, []);

  const processFileUpload = useCallback(async (files: File[], index: number = 0, targetFolder?: string) => {
    currentTargetFolderRef.current = targetFolder;

    if (index === 0) {
      setProgressDialogOpen(true);
      setProgressItems(files.map((f) => ({ name: f.name, status: 'pending' })));
      setProgressTotal(files.length);
      setProgressCurrent(0);
      abortControllerRef.current = new AbortController();
      const warnings = checkWindowsWarning(files.map(f => f.name));
      setWindowsWarningFiles(warnings);
    }

    if (abortControllerRef.current?.signal.aborted) {
      setProgressDialogOpen(false);
      setPendingUploadFiles([]);
      setCurrentUploadIndex(0);
      return;
    }

    if (index >= files.length) {
      setProgressCurrent(files.length);
      setPendingUploadFiles([]);
      setCurrentUploadIndex(0);
      await fetchTree();

      if (lastUploadedFileRef.current) {
        const uploadedPath = lastUploadedFileRef.current.path;
        setSelectedPath(uploadedPath);
        saveSelectedPath(uploadedPath);
        onFileSelect?.(uploadedPath, lastUploadedFileRef.current.blobId);

        const lastSlashIndex = uploadedPath.lastIndexOf('/');
        if (lastSlashIndex > 0) {
          const parentPath = uploadedPath.substring(0, lastSlashIndex);
          expandPath(parentPath);
        }

        lastUploadedFileRef.current = null;
      }

      setTimeout(() => {
        if (!progressItems.some((item) => item.status === 'error')) {
          setProgressDialogOpen(false);
        }
      }, 1500);
      return;
    }

    setCurrentUploadIndex(index);
    const file = files[index];
    const filePath = targetFolder ? `${targetFolder}/${file.name}` : file.name;

    setProgressCurrentFile(filePath);
    setProgressItems((prev) =>
      prev.map((item, i) => (i === index ? { ...item, status: 'processing' } : item))
    );

    if (checkFileExists(filePath)) {
      setConflictFileName(filePath);
      setProgressDialogOpen(false);
      setConflictDialogOpen(true);
      setProgressItems((prev) =>
        prev.map((item, i) => (i === index ? { ...item, status: 'pending' } : item))
      );
      return;
    }

    try {
      const fileType = getFileType(file.name);
      let requestBody: { path: string; type: string; content?: string; blob_id?: string };

      if (fileType === 'text') {
        const content = await file.text();
        requestBody = {
          path: filePath,
          type: 'blob',
          content,
        };
      } else {
        const blobId = await uploadBinaryFile(file);
        requestBody = {
          path: filePath,
          type: 'blob',
          blob_id: blobId,
        };
      }

      const response = await api.post<{
        id: string;
        entries: Array<{
          path: string;
          blob_id: string | null;
          type: string;
        }>;
        created_at: string;
      }>(`/trees/${treeId}/files`, requestBody);

      const uploadedEntry = response.entries.find((e) => e.path === filePath);
      if (uploadedEntry?.blob_id) {
        lastUploadedFileRef.current = { path: filePath, blobId: uploadedEntry.blob_id };
      }

      // Immediately add node to tree to avoid race condition with fetchTree
      addNodeCallback({
        path: filePath,
        blob_id: uploadedEntry?.blob_id || undefined,
        type: 'blob',
      }, false);

      setProgressItems((prev) =>
        prev.map((item, i) => (i === index ? { ...item, status: 'success' } : item))
      );
      setProgressCurrent(index + 1);
    } catch (err) {
      logger.error('Failed to upload file:', err);
      const errorMessage = err instanceof Error ? err.message : String(err);
      setProgressItems((prev) =>
        prev.map((item, i) =>
          i === index ? { ...item, status: 'error', error: errorMessage } : item
        )
      );
    }

    await processFileUpload(files, index + 1, targetFolder);
  }, [treeId, checkFileExists, uploadBinaryFile, fetchTree, onFileSelect, showToast, saveSelectedPath, setSelectedPath, expandPath]);

  const handleConflictResolution = useCallback(async (action: SingleConflictAction, newName?: string) => {
    setConflictDialogOpen(false);
    setProgressDialogOpen(true);

    const file = pendingUploadFiles[currentUploadIndex];
    if (!file) return;

    const originalFilePath = conflictFileName;
    const filePath = action === 'rename' && newName ? newName : originalFilePath;

    if (action === 'skip') {
      setProgressItems((prev) =>
        prev.map((item, i) =>
          i === currentUploadIndex ? { ...item, status: 'error', error: 'Skipped' } : item
        )
      );
      setProgressCurrent(currentUploadIndex + 1);
    } else {
      setProgressItems((prev) =>
        prev.map((item, i) =>
          i === currentUploadIndex ? { ...item, status: 'processing' } : item
        )
      );

      try {
        if (action === 'overwrite') {
          await api.delete(`/trees/${treeId}/files`, { path: originalFilePath });
        }

        const fileType = getFileType(file.name);
        let requestBody: { path: string; type: string; content?: string; blob_id?: string };

        if (fileType === 'text') {
          const content = await file.text();
          requestBody = {
            path: filePath,
            type: 'blob',
            content,
          };
        } else {
          const blobId = await uploadBinaryFile(file);
          requestBody = {
            path: filePath,
            type: 'blob',
            blob_id: blobId,
          };
        }

        const response = await api.post<{
          id: string;
          entries: Array<{
            path: string;
            blob_id: string | null;
            type: string;
          }>;
          created_at: string;
        }>(`/trees/${treeId}/files`, requestBody);

        const updatedEntry = response.entries.find((e) => e.path === filePath);
        if (updatedEntry?.blob_id) {
          lastUploadedFileRef.current = { path: filePath, blobId: updatedEntry.blob_id };
        }

        if (selectedFilePath === originalFilePath) {
          if (updatedEntry?.blob_id) {
            onFileReload?.(filePath, updatedEntry.blob_id);
          }
        }

        setProgressItems((prev) =>
          prev.map((item, i) =>
            i === currentUploadIndex ? { ...item, status: 'success' } : item
          )
        );
        setProgressCurrent(currentUploadIndex + 1);
      } catch (err) {
        logger.error(`Failed to ${action} file:`, err);
        const errorMessage = err instanceof Error ? err.message : String(err);
        setProgressItems((prev) =>
          prev.map((item, i) =>
            i === currentUploadIndex
              ? { ...item, status: 'error', error: errorMessage }
              : item
          )
        );
      }
    }

    await processFileUpload(pendingUploadFiles, currentUploadIndex + 1, currentTargetFolderRef.current);
  }, [treeId, pendingUploadFiles, currentUploadIndex, uploadBinaryFile, selectedFilePath, onFileReload, processFileUpload, showToast, conflictFileName]);

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    if (!treeId) return;

    const files = Array.from(e.dataTransfer.files);

    if (files.length > 0) {
      setPendingUploadFiles(files);
      await processFileUpload(files, 0);
    }
  }, [treeId, processFileUpload, setIsDragging]);

  const handleFileInputChange = useCallback(async (e: React.ChangeEvent<HTMLInputElement>, targetFolder?: string) => {
    if (!treeId || !e.target.files) return;

    const files = Array.from(e.target.files);

    if (files.length > 0) {
      const warningFiles = checkWindowsWarning(files.map(f => f.name));

      if (warningFiles.length > 0) {
        pendingFilesRef.current = files;
        setPendingUploadTargetFolder(targetFolder || '');
        setWindowsConfirmFiles(warningFiles);
        setWindowsConfirmDialogOpen(true);
        e.target.value = '';
        return;
      }

      setPendingUploadFiles(files);
      await processFileUpload(files, 0, targetFolder);
    }

    e.target.value = '';
  }, [treeId, processFileUpload, checkWindowsWarning]);

  const executeFolderUpload = useCallback(
    async (
      entries: Array<{ path: string; type: 'blob' | 'tree'; content?: string; blob_id?: string }>,
      targetFolder: string,
      initialErrors: Array<{ path: string; error: string }> = []
    ) => {
      try {
        const response = await api.post<{
          id: string;
          entries: Array<{ path: string; blob_id: string | null; type: string }>;
          created_at: string;
        }>(`/trees/${treeId}/files/folder`, {
          base_path: targetFolder,
          entries,
        });

        const newEntriesCount = response.entries.length;
        if (newEntriesCount > 0) {
          showToast(`Successfully uploaded ${newEntriesCount} items`, 'success');
        }
        if (initialErrors.length > 0) {
          showToast(
            `${initialErrors.length} items failed to upload`,
            'error'
          );
        }

        await fetchTree();
      } catch (err) {
        logger.error('Failed to upload folder:', err);
        showToast('Failed to upload folder', 'error');
      } finally {
        setTimeout(() => {
          setProgressDialogOpen(false);
        }, 2000);
      }
    },
    [treeId, fetchTree, showToast]
  );

  const handleFolderInputChange = useCallback(async (e: React.ChangeEvent<HTMLInputElement>, targetFolder?: string) => {
    if (!treeId || !e.target.files) return;

    const files = Array.from(e.target.files);
    if (files.length === 0) {
      e.target.value = '';
      return;
    }

    const warningFiles = files
      .filter(f => f.webkitRelativePath && hasWindowsReservedChars(f.webkitRelativePath))
      .map(f => f.webkitRelativePath || f.name);

    if (warningFiles.length > 0) {
      pendingFilesRef.current = files;
      setPendingUploadTargetFolder(targetFolder || '');
      setWindowsConfirmFiles(warningFiles);
      setWindowsConfirmDialogOpen(true);
      e.target.value = '';
      return;
    }

    await processFolderUpload(files, targetFolder || '');
    e.target.value = '';
  }, [treeId]);

  const processFolderUpload = useCallback(async (files: File[], targetFolder: string) => {
    const entries: Array<{ path: string; type: 'blob' | 'tree'; content?: string; blob_id?: string }> =
      [];
    const directories = new Set<string>();
    const fileErrors: Array<{ path: string; error: string }> = [];

    setProgressDialogOpen(true);
    setProgressItems(files.map((f) => ({ name: f.webkitRelativePath || f.name, status: 'pending' })));
    setProgressTotal(files.length);
    setProgressCurrent(0);

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const relativePath = file.webkitRelativePath;

      setProgressCurrentFile(relativePath || file.name);
      setProgressItems((prev) =>
        prev.map((item, idx) => (idx === i ? { ...item, status: 'processing' } : item))
      );

      if (!relativePath) {
        fileErrors.push({ path: file.name, error: 'Invalid path' });
        setProgressItems((prev) =>
          prev.map((item, idx) => (idx === i ? { ...item, status: 'error', error: 'Invalid path' } : item))
        );
        continue;
      }

      if (file.name.startsWith('.')) {
        setProgressItems((prev) =>
          prev.map((item, idx) => (idx === i ? { ...item, status: 'success' } : item))
        );
        continue;
      }

      const parts = relativePath.split('/');
      for (let j = 1; j < parts.length; j++) {
        const dirPath = parts.slice(0, j).join('/');
        directories.add(dirPath);
      }

      try {
        const fileType = getFileType(file.name);
        if (fileType === 'text') {
          const content = await file.text();
          entries.push({
            path: relativePath,
            type: 'blob',
            content,
          });
        } else {
          const blobId = await uploadBinaryFile(file);
          entries.push({
            path: relativePath,
            type: 'blob',
            blob_id: blobId,
          });
        }
        setProgressItems((prev) =>
          prev.map((item, idx) => (idx === i ? { ...item, status: 'success' } : item))
        );
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : String(err);
        logger.error(`Failed to process file: ${relativePath}`, err);
        fileErrors.push({ path: relativePath, error: errorMessage });
        setProgressItems((prev) =>
          prev.map((item, idx) =>
            idx === i ? { ...item, status: 'error', error: errorMessage } : item
          )
        );
      }

      setProgressCurrent(i + 1);
    }

    const sortedDirs = Array.from(directories).sort((a, b) => {
      const depthA = a.split('/').length;
      const depthB = b.split('/').length;
      return depthA - depthB;
    });

    const dirEntries = sortedDirs.map((dir) => ({
      path: dir,
      type: 'tree' as const,
    }));

    const sortedFileEntries = entries.sort((a, b) => a.path.localeCompare(b.path));
    const allEntries = [...dirEntries, ...sortedFileEntries];

    const existingPaths = checkFilesExist(
      allEntries
        .filter((e) => e.type === 'blob')
        .map((e) => (targetFolder ? `${targetFolder}/${e.path}` : e.path))
    );

    if (existingPaths.length > 0) {
      setBatchConflictItems(
        existingPaths.map((path) => ({
          path: path.replace(targetFolder ? `${targetFolder}/` : '', ''),
        }))
      );
      setBatchConflictDialogOpen(true);
      pendingFolderUploadRef.current = { entries: allEntries, targetFolder: targetFolder || '' };
      return;
    }

    await executeFolderUpload(allEntries, targetFolder || '', fileErrors);
  }, [uploadBinaryFile, checkFilesExist, executeFolderUpload]);

  const handleBatchConflictResolve = useCallback(
    async (resolutions: Map<string, ConflictAction>) => {
      setBatchConflictDialogOpen(false);

      const pending = pendingFolderUploadRef.current;
      if (!pending) return;

      const { entries, targetFolder } = pending;
      const filteredEntries = entries.filter((entry) => {
        if (entry.type === 'tree') return true;
        const fullPath = targetFolder ? `${targetFolder}/${entry.path}` : entry.path;
        const action = resolutions.get(fullPath) || resolutions.get(entry.path);

        if (action === 'skip') {
          return false;
        }
        if (action === 'overwrite') {
          return true;
        }
        if (action === 'rename') {
          const parts = entry.path.split('.');
          if (parts.length > 1) {
            const ext = parts.pop();
            entry.path = `${parts.join('.')}_1.${ext}`;
          } else {
            entry.path = `${entry.path}_1`;
          }
          return true;
        }
        return false;
      });

      pendingFolderUploadRef.current = null;
      await executeFolderUpload(filteredEntries, targetFolder);
    },
    [executeFolderUpload]
  );

  const handleBatchConflictCancel = useCallback(() => {
    setBatchConflictDialogOpen(false);
    pendingFolderUploadRef.current = null;
    setProgressDialogOpen(false);
  }, []);

  const handleProgressCancel = useCallback(() => {
    abortControllerRef.current?.abort();
    setProgressDialogOpen(false);
  }, []);

  const handleProgressClose = useCallback(() => {
    setProgressDialogOpen(false);
  }, []);

  const handleWindowsConfirm = useCallback(async () => {
    setWindowsConfirmDialogOpen(false);
    const files = pendingFilesRef.current;
    const targetFolder = pendingUploadTargetFolder;

    if (files.length === 0) return;

    const isFolderUpload = files.some(f => f.webkitRelativePath);

    if (isFolderUpload) {
      await processFolderUpload(files, targetFolder);
    } else {
      setPendingUploadFiles(files);
      await processFileUpload(files, 0, targetFolder);
    }

    pendingFilesRef.current = [];
    setPendingUploadTargetFolder('');
    setWindowsConfirmFiles([]);
  }, [pendingUploadTargetFolder, processFileUpload]);

  const handleWindowsCancel = useCallback(() => {
    setWindowsConfirmDialogOpen(false);
    pendingFilesRef.current = [];
    setPendingUploadTargetFolder('');
    setWindowsConfirmFiles([]);
  }, []);

  return {
    isDragging,
    setIsDragging,
    pendingUploadFiles,
    currentUploadIndex,
    conflictDialogOpen,
    conflictFileName,

    progressDialogOpen,
    progressItems,
    progressCurrent,
    progressTotal,
    progressCurrentFile,

    batchConflictDialogOpen,
    batchConflictItems,

    uploadBinaryFile,
    processFileUpload,
    handleConflictResolution,
    handleFileInputChange,
    handleFolderInputChange,
    handleBatchConflictResolve,
    handleBatchConflictCancel,
    handleProgressCancel,
    handleProgressClose,
    checkFileExists,
    checkFilesExist,
    handleDrop,
    windowsWarningFiles,
    windowsConfirmDialogOpen,
    windowsConfirmFiles,
    pendingUploadTargetFolder,
    handleWindowsConfirm,
    handleWindowsCancel,
  };
}
