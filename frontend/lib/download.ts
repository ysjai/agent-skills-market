import { api } from './api';
import { sanitizeFileName } from './windows-fs';

declare global {
  interface Window {
    showDirectoryPicker(options?: {
      mode?: 'read' | 'readwrite';
    }): Promise<FileSystemDirectoryHandle>;
  }
}

export type Platform = 'opencode' | 'claude';

const PLATFORM_DIRS: Record<Platform, string> = {
  opencode: '.opencode/skills',
  claude: '.claude/skills',
};

export function checkFileSystemAccessSupport(): boolean {
  return typeof window !== 'undefined' && 'showDirectoryPicker' in window;
}

export type OperatingSystem = 'windows' | 'macos' | 'linux' | 'unknown';

export function detectOperatingSystem(): OperatingSystem {
  if (typeof window === 'undefined') {
    return 'unknown';
  }

  const platform = navigator.platform;
  const userAgent = navigator.userAgent;

  if (platform.startsWith('Win') || userAgent.includes('Windows')) {
    return 'windows';
  }

  if (platform.startsWith('Mac') || userAgent.includes('Mac')) {
    return 'macos';
  }

  if (platform.startsWith('Linux') || userAgent.includes('Linux')) {
    return 'linux';
  }

  return 'unknown';
}

export function isWindows(): boolean {
  return detectOperatingSystem() === 'windows';
}

export interface FileNameMapping {
  original: string;
  sanitized: string;
  hasChanged: boolean;
  path: string;
}

export function checkFileNamesForWindows(
  filePaths: string[]
): {
  hasIllegalChars: boolean;
  mappings: FileNameMapping[];
  affectedFiles: FileNameMapping[];
} {
  const mappings: FileNameMapping[] = [];
  const affectedFiles: FileNameMapping[] = [];
  let hasIllegalChars = false;

  for (const path of filePaths) {
    const parts = path.split('/');
    const fileName = parts.pop() || '';
    const sanitizedFileName = sanitizeFileName(fileName);
    const hasChanged = fileName !== sanitizedFileName;

    const mapping: FileNameMapping = {
      original: fileName,
      sanitized: sanitizedFileName,
      hasChanged,
      path,
    };

    mappings.push(mapping);

    if (hasChanged) {
      hasIllegalChars = true;
      affectedFiles.push(mapping);
    }
  }

  return { hasIllegalChars, mappings, affectedFiles };
}

export function getPlatformSubdirectory(platform: Platform): string {
  return PLATFORM_DIRS[platform];
}

export function getPlatformDisplayName(platform: Platform): string {
  return platform === 'opencode' ? 'OpenCode' : 'Claude Code';
}

export function formatDirectoryPath(dirHandle: FileSystemDirectoryHandle): string {
  return dirHandle.name;
}

export interface DownloadResult {
  success: boolean;
  filesExtracted: number;
  targetPath: string;
  error?: string;
}

export interface DownloadAndExtractOptions {
  skillId: string;
  skillName: string;
  platform: Platform;
  dirHandle: FileSystemDirectoryHandle;
  onProgress?: (progress: number, currentFile?: number, totalFiles?: number) => void;
  preserveNames?: boolean;
}

export async function downloadAndExtractSkill(
  options: DownloadAndExtractOptions
): Promise<DownloadResult> {
  const { skillId, skillName, platform, dirHandle, onProgress, preserveNames } = options;

  try {
    const response = await api.get<SkillFileResponse>(`/skills/${skillId}/files`);
    const files = response.files.filter((f) => f.type === 'blob');

    if (files.length === 0) {
      return {
        success: false,
        filesExtracted: 0,
        targetPath: '',
        error: 'No files found in this skill',
      };
    }

    const platformDir = PLATFORM_DIRS[platform];
    const dirParts = platformDir.split('/');
    let currentHandle = dirHandle;

    for (const part of dirParts) {
      if (part) {
        currentHandle = await currentHandle.getDirectoryHandle(part, { create: true });
      }
    }

    const finalSkillName = preserveNames ? skillName : sanitizeFileName(skillName);
    const skillHandle = await currentHandle.getDirectoryHandle(finalSkillName, { create: true });

    let filesExtracted = 0;
    const totalFiles = files.length;

    for (let i = 0; i < files.length; i++) {
      const file = files[i];

      if (!file.blob_id) {
        filesExtracted++;
        const progress = Math.round((filesExtracted / totalFiles) * 100);
        onProgress?.(progress, filesExtracted, totalFiles);
        continue;
      }

      const blob = await api.getBlob(`/blobs/${file.blob_id}`);
      await writeFileToDirectory(skillHandle, file.path, blob, preserveNames);

      filesExtracted++;
      const progress = Math.round((filesExtracted / totalFiles) * 100);
      onProgress?.(progress, filesExtracted, totalFiles);
    }

    return {
      success: true,
      filesExtracted,
      targetPath: `${platformDir}/${skillName}`,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Download failed';
    return {
      success: false,
      filesExtracted: 0,
      targetPath: '',
      error: errorMessage,
    };
  }
}

export async function selectDirectory(): Promise<FileSystemDirectoryHandle | null> {
  try {
    const dirHandle = await window.showDirectoryPicker({
      mode: 'readwrite',
    });
    return dirHandle;
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      return null;
    }
    if (error instanceof Error) {
      if (error.name === 'NotAllowedError') {
        throw new Error('Permission denied. Please allow access to the directory and try again.');
      }
      throw new Error(`Failed to select directory: ${error.message}`);
    }
    throw new Error('Failed to select directory: Unknown error');
  }
}

export async function writeFileToDirectory(
  dirHandle: FileSystemDirectoryHandle,
  path: string,
  content: Blob,
  preserveNames?: boolean
): Promise<void> {
  const parts = path.split('/');
  const rawFileName = parts.pop()!;
  const fileName = preserveNames ? rawFileName : sanitizeFileName(rawFileName);

  let currentDir = dirHandle;
  for (const part of parts) {
    if (part) {
      const dirName = preserveNames ? part : sanitizeFileName(part);
      try {
        currentDir = await currentDir.getDirectoryHandle(dirName, { create: true });
      } catch (error) {
        throw new Error(`Failed to create directory "${dirName}" in path "${path}": ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    }
  }

  try {
    const fileHandle = await currentDir.getFileHandle(fileName, { create: true });
    const writable = await fileHandle.createWritable();
    await writable.write(content);
    await writable.close();
  } catch (error) {
    throw new Error(`Failed to write file "${path}" (written as: "${fileName}"): ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

interface SkillFileResponse {
  files: Array<{
    path: string;
    type: string;
    blob_id?: string;
  }>;
}

// ===== Market download functions (using public API) =====

export interface MarketDownloadAndExtractOptions {
  sharedSkillId: string;
  skillName: string;
  platform: Platform;
  dirHandle: FileSystemDirectoryHandle;
  onProgress?: (progress: number, currentFile?: number, totalFiles?: number) => void;
  preserveNames?: boolean;
}

export async function downloadAndExtractMarketSkill(
  options: MarketDownloadAndExtractOptions
): Promise<DownloadResult> {
  const { sharedSkillId, skillName, platform, dirHandle, onProgress, preserveNames } = options;

  try {
    const tree = await api.getMarketSkillTree(sharedSkillId);
    const files = tree.entries.filter((e) => e.type === 'blob');

    if (files.length === 0) {
      return {
        success: false,
        filesExtracted: 0,
        targetPath: '',
        error: 'No files found in this skill',
      };
    }

    const platformDir = PLATFORM_DIRS[platform];
    const dirParts = platformDir.split('/');
    let currentHandle = dirHandle;

    for (const part of dirParts) {
      if (part) {
        currentHandle = await currentHandle.getDirectoryHandle(part, { create: true });
      }
    }

    const finalSkillName = preserveNames ? skillName : sanitizeFileName(skillName);
    const skillHandle = await currentHandle.getDirectoryHandle(finalSkillName, { create: true });

    let filesExtracted = 0;
    const totalFiles = files.length;

    for (let i = 0; i < files.length; i++) {
      const file = files[i];

      if (!file.blob_id) {
        filesExtracted++;
        const progress = Math.round((filesExtracted / totalFiles) * 100);
        onProgress?.(progress, filesExtracted, totalFiles);
        continue;
      }

      const blob = await api.getMarketSkillBlob(sharedSkillId, file.blob_id);
      await writeFileToDirectory(skillHandle, file.path, blob, preserveNames);

      filesExtracted++;
      const progress = Math.round((filesExtracted / totalFiles) * 100);
      onProgress?.(progress, filesExtracted, totalFiles);
    }

    return {
      success: true,
      filesExtracted,
      targetPath: `${platformDir}/${skillName}`,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Download failed';
    return {
      success: false,
      filesExtracted: 0,
      targetPath: '',
      error: errorMessage,
    };
  }
}

export async function downloadMarketSkillAsZip(
  sharedSkillId: string,
  skillName: string,
  onProgress?: (current: number, total: number) => void
): Promise<void> {
  const tree = await api.getMarketSkillTree(sharedSkillId);
  const files = tree.entries.filter((e) => e.type === 'blob' && e.blob_id);

  if (files.length === 0) {
    throw new Error('No files found in this skill');
  }

  const JSZip = (await import('jszip')).default;
  const zip = new JSZip();

  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    const blob = await api.getMarketSkillBlob(sharedSkillId, file.blob_id!);
    zip.file(file.path, blob);
    onProgress?.(i + 1, files.length);
  }

  const zipBlob = await zip.generateAsync({ type: 'blob' });
  const url = URL.createObjectURL(zipBlob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${skillName}.zip`;
  a.click();
  URL.revokeObjectURL(url);
}

export async function downloadSkill(
  skillId: string,
  skillName: string,
  platform: Platform,
  onProgress?: (current: number, total: number) => void
): Promise<void> {
  if (!checkFileSystemAccessSupport()) {
    throw new Error('File System Access API is not supported in this browser. Please use Chrome 86+ or Edge 86+.');
  }

  let files: SkillFileResponse['files'];
  try {
    const response = await api.get<SkillFileResponse>(`/skills/${skillId}/files`);
    files = response.files.filter((f) => f.type === 'blob');
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to get skill files: ${error.message}. Please check your network connection and try again.`);
    }
    throw new Error('Failed to get skill files: Unknown network error');
  }

  if (files.length === 0) {
    throw new Error('No files found in this skill');
  }

  const dirHandle = await selectDirectory();
  if (!dirHandle) {
    return;
  }

  const platformDir = PLATFORM_DIRS[platform];
  let skillHandle: FileSystemDirectoryHandle;
  
  try {
    const dirParts = platformDir.split('/');
    let currentHandle = dirHandle;
    
    for (const part of dirParts) {
      if (part) {
        currentHandle = await currentHandle.getDirectoryHandle(part, { create: true });
      }
    }
    
    const sanitizedSkillName = sanitizeFileName(skillName);
    skillHandle = await currentHandle.getDirectoryHandle(sanitizedSkillName, { create: true });
  } catch (error) {
    throw new Error(
      `Failed to create directory "${platformDir}/${skillName}": ${error instanceof Error ? error.message : 'Unknown error'}. ` +
      'Please ensure you have write permissions to the selected directory.'
    );
  }

  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    
    if (!file.blob_id) {
      console.warn(`File "${file.path}" has no blob_id, skipping`);
      onProgress?.(i + 1, files.length);
      continue;
    }

    try {
      const blob = await api.getBlob(`/blobs/${file.blob_id}`);
      await writeFileToDirectory(skillHandle, file.path, blob);
      onProgress?.(i + 1, files.length);
    } catch (error) {
      if (error instanceof Error) {
        if (error.message.includes('Network error') || error.message.includes('fetch')) {
          throw new Error(`Network error while downloading file "${file.path}". Please check your connection and try again.`);
        }
        throw new Error(`Failed to download file "${file.path}": ${error.message}`);
      }
      throw new Error(`Failed to download file "${file.path}": Unknown error`);
    }
  }
}
