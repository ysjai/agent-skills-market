import { useCallback } from 'react';
import { api } from '@/lib/api';
import { logger } from '@/lib/logger';
import { selectDirectory, writeFileToDirectory } from '@/lib/download';
import { sanitizeFileName, hasWindowsReservedChars } from '@/lib/windows-fs';
import type { FileTreeNode } from '@/types/file-tree';
import JSZip from 'jszip';

export interface UseFolderDownloadOptions {
  treeId?: string;
  nodes: FileTreeNode[];
  showToast: (message: string, type?: 'success' | 'error' | 'info') => void;
}

export interface FileWithPath {
  path: string;
  blobId: string;
}

export interface UseFolderDownloadReturn {
  downloadFolder: (folderPath: string, folderName: string, raw?: boolean) => Promise<void>;
  downloadFolderAsZip: (folderPath: string, folderName: string) => Promise<void>;
  collectFilesInFolder: (folderPath: string) => FileWithPath[];
  checkWindowsCompatibility: (folderPath: string) => { hasIllegalChars: boolean; affectedFiles: string[] };
}

export function useFolderDownload({
  treeId,
  nodes,
  showToast,
}: UseFolderDownloadOptions): UseFolderDownloadReturn {
  const collectFilesInFolder = useCallback((folderPath: string): FileWithPath[] => {
    const files: FileWithPath[] = [];

    const traverse = (nodeList: FileTreeNode[], parentPath: string = '') => {
      for (const node of nodeList) {
        const nodeName = node.name || '';
        const fullPath = parentPath ? `${parentPath}/${nodeName}` : nodeName;

        if (node.type === 'blob' && node.blob_id && fullPath.startsWith(folderPath)) {
          files.push({
            path: fullPath,
            blobId: node.blob_id,
          });
        }

        if (node.children && node.children.length > 0) {
          traverse(node.children as FileTreeNode[], fullPath);
        }
      }
    };

    traverse(nodes);
    return files;
  }, [nodes]);

  const checkWindowsCompatibility = useCallback((folderPath: string) => {
    const files = collectFilesInFolder(folderPath);
    const affectedFiles = files
      .filter(f => hasWindowsReservedChars(f.path))
      .map(f => f.path);
    
    return {
      hasIllegalChars: affectedFiles.length > 0,
      affectedFiles,
    };
  }, [collectFilesInFolder]);

  const downloadFolderAsZip = useCallback(async (folderPath: string, folderName: string) => {
    if (!treeId) {
      showToast('No tree selected', 'error');
      return;
    }

    const files = collectFilesInFolder(folderPath);

    if (files.length === 0) {
      showToast('Folder is empty', 'error');
      return;
    }

    showToast(`Creating ZIP with ${files.length} files...`, 'info');

    try {
      const zip = new JSZip();

      for (const file of files) {
        if (file.blobId) {
          const blob = await api.getBlob(`/blobs/${file.blobId}`);
          const relativePath = folderPath
            ? file.path.slice(folderPath.length).replace(/^\//, '')
            : file.path;
          zip.file(relativePath, blob);
        }
      }

      const zipBlob = await zip.generateAsync({ type: 'blob' });
      const url = window.URL.createObjectURL(zipBlob);
      const downloadLink = document.createElement('a');
      downloadLink.href = url;
      downloadLink.download = `${folderName}.zip`;
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);
      window.URL.revokeObjectURL(url);

      showToast(`Successfully downloaded ${files.length} files as ZIP`, 'success');
    } catch (err) {
      logger.error('Failed to create ZIP:', err);
      showToast('Failed to create ZIP archive', 'error');
    }
  }, [treeId, collectFilesInFolder, showToast]);

  const downloadFolder = useCallback(async (folderPath: string, folderName: string, raw?: boolean) => {
    if (!treeId) {
      showToast('No tree selected', 'error');
      return;
    }

    if (typeof window === 'undefined' || !('showDirectoryPicker' in window)) {
      showToast('Your browser does not support directory selection. Please use Chrome or Edge.', 'error');
      return;
    }

    const files = collectFilesInFolder(folderPath);

    if (files.length === 0) {
      showToast('Folder is empty', 'error');
      return;
    }

    const affectedFiles = files.filter(f => hasWindowsReservedChars(f.path));

    let dirHandle: FileSystemDirectoryHandle | null;
    try {
      dirHandle = await selectDirectory();
    } catch (err) {
      logger.error('Failed to select directory:', err);
      showToast(err instanceof Error ? err.message : 'Failed to select directory', 'error');
      return;
    }

    if (!dirHandle) {
      return;
    }

    showToast(`Downloading ${files.length} files...`, 'info');

    let successCount = 0;
    let failedCount = 0;

    let targetDirHandle: FileSystemDirectoryHandle;
    const finalFolderName = raw ? folderName : sanitizeFileName(folderName);
    try {
      targetDirHandle = await dirHandle.getDirectoryHandle(finalFolderName, { create: true });
    } catch (err) {
      logger.error(`Failed to create folder "${finalFolderName}":`, err);
      showToast(`Failed to create folder "${finalFolderName}"`, 'error');
      return;
    }

    for (const file of files) {
      try {
        const blob = await api.getBlob(`/blobs/${file.blobId}`);

        let relativePath: string;
        if (raw) {
          relativePath = folderPath
            ? file.path.slice(folderPath.length).replace(/^\//, '')
            : file.path;
        } else {
          const originalPath = folderPath
            ? file.path.slice(folderPath.length).replace(/^\//, '')
            : file.path;
          relativePath = originalPath.split('/').map(sanitizeFileName).join('/');
        }

        await writeFileToDirectory(targetDirHandle, relativePath, blob, raw);
        successCount++;
      } catch (err) {
        logger.error(`Failed to download file ${file.path}:`, err);
        failedCount++;
      }
    }

    if (successCount === 0) {
      showToast('Failed to download any files', 'error');
    } else if (failedCount > 0) {
      showToast(`Downloaded ${successCount} files, ${failedCount} failed`, 'error');
    } else if (!raw && affectedFiles.length > 0) {
      showToast(`Downloaded ${successCount} files. ${affectedFiles.length} file(s) renamed for Windows compatibility`, 'success');
    } else {
      showToast(`Successfully downloaded ${successCount} files`, 'success');
    }
  }, [treeId, collectFilesInFolder, showToast]);

  return {
    downloadFolder,
    downloadFolderAsZip,
    collectFilesInFolder,
    checkWindowsCompatibility,
  };
}
