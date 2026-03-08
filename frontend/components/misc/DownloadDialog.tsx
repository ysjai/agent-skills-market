'use client';

import { useState, useEffect, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { X, Folder, AlertCircle, CheckCircle, Loader2, Package, FileText, ChevronDown, ChevronUp, Copy, Check } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import {
  checkFileSystemAccessSupport,
  selectDirectory,
  downloadAndExtractSkill,
  downloadAndExtractMarketSkill,
  downloadMarketSkillAsZip,
  formatDirectoryPath,
  checkFileNamesForWindows,
  isWindows,
  type Platform,
  type DownloadResult,
  type FileNameMapping,
} from '@/lib/download';
import { api } from '@/lib/api';
import JSZip from 'jszip';

interface DownloadDialogProps {
  open: boolean;
  skillId: string;
  skillName: string;
  onClose: () => void;
  onSuccess?: () => void;
  /** 'private' uses auth-protected endpoints; 'market' uses public market endpoints */
  mode?: 'private' | 'market';
  /** Required when mode is 'market' */
  sharedSkillId?: string;
}

type DialogState = 'checking' | 'initial' | 'selecting' | 'downloading' | 'success' | 'error' | 'mapping';
type DownloadMethod = 'zip' | 'replace';

export function DownloadDialog({
  open,
  skillId,
  skillName,
  onClose,
  onSuccess,
  mode = 'private',
  sharedSkillId,
}: DownloadDialogProps) {
  const t = useTranslations('download');
  const tCommon = useTranslations('common');
  
  const [platform, setPlatform] = useState<Platform>('opencode');
  const [dirHandle, setDirHandle] = useState<FileSystemDirectoryHandle | null>(null);
  const [dialogState, setDialogState] = useState<DialogState>('checking');
  const [downloadMethod, setDownloadMethod] = useState<DownloadMethod>('zip');
  const [progress, setProgress] = useState(0);
  const [currentFile, setCurrentFile] = useState(0);
  const [totalFiles, setTotalFiles] = useState(0);
  const [error, setError] = useState('');
  const [isSupported, setIsSupported] = useState(true);
  const [downloadResult, setDownloadResult] = useState<DownloadResult | null>(null);
  const [fileMappings, setFileMappings] = useState<FileNameMapping[]>([]);
  const [hasIllegalChars, setHasIllegalChars] = useState(false);
  const [showMappingDetails, setShowMappingDetails] = useState(false);
  const [copied, setCopied] = useState(false);

  const resetState = useCallback(() => {
    setPlatform('opencode');
    setDirHandle(null);
    setDialogState('checking');
    setDownloadMethod('zip');
    setProgress(0);
    setCurrentFile(0);
    setTotalFiles(0);
    setError('');
    setDownloadResult(null);
    setFileMappings([]);
    setHasIllegalChars(false);
    setShowMappingDetails(false);
    setCopied(false);
  }, []);

  useEffect(() => {
    if (!open) return;
    
    const supported = checkFileSystemAccessSupport();
    setIsSupported(supported);
    
    checkFileNames();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, skillId]);

  const checkFileNames = async () => {
    try {
      let filePaths: string[];

      if (mode === 'market' && sharedSkillId) {
        const tree = await api.getMarketSkillTree(sharedSkillId);
        filePaths = tree.entries.filter(e => e.type === 'blob').map(e => e.path);
      } else {
        const response = await api.get<{ files: Array<{ path: string; type: string }> }>(`/skills/${skillId}/files`);
        filePaths = response.files.filter(f => f.type === 'blob').map(f => f.path);
      }

      const check = checkFileNamesForWindows(filePaths);
      setHasIllegalChars(check.hasIllegalChars);
      setFileMappings(check.mappings);

      setDialogState('initial');
    } catch {
      setDialogState('initial');
    }
  };

  const handleDownloadZip = async () => {
    setDialogState('downloading');
    setError('');
    setProgress(0);

    try {
      if (mode === 'market' && sharedSkillId) {
        // Market mode: use public API via downloadMarketSkillAsZip
        await downloadMarketSkillAsZip(sharedSkillId, skillName, (current, total) => {
          setProgress(Math.round((current / total) * 100));
          setCurrentFile(current);
          setTotalFiles(total);
        });

        setDownloadResult({
          success: true,
          filesExtracted: totalFiles,
          targetPath: `${skillName}.zip`,
        });
      } else {
        // Private mode: use auth-protected API
        const response = await api.get<{ files: Array<{ path: string; type: string; blob_id?: string }> }>(`/skills/${skillId}/files`);
        const files = response.files.filter(f => f.type === 'blob');
        
        const zip = new JSZip();
        const total = files.length;
        let current = 0;

        for (const file of files) {
          if (file.blob_id) {
            const blob = await api.getBlob(`/blobs/${file.blob_id}`);
            zip.file(file.path, blob);
          }
          current++;
          setProgress(Math.round((current / total) * 100));
          setCurrentFile(current);
          setTotalFiles(total);
        }

        const zipBlob = await zip.generateAsync({ type: 'blob' });
        const url = window.URL.createObjectURL(zipBlob);
        const downloadLink = document.createElement('a');
        downloadLink.href = url;
        downloadLink.download = `${skillName}.zip`;
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
        window.URL.revokeObjectURL(url);

        setDownloadResult({
          success: true,
          filesExtracted: files.length,
          targetPath: `${skillName}.zip`,
        });
      }

      setDialogState('success');
      onSuccess?.();
    } catch {
      setError(t('errors.createZipFailed'));
      setDialogState('error');
    }
  };

  const handleSelectDirectory = async () => {
    setDialogState('selecting');
    setError('');
    try {
      const handle = await selectDirectory();
      if (handle) {
        setDirHandle(handle);
        await handleDownloadReplace(handle);
      } else {
        setDialogState('initial');
      }
    } catch {
      setError(t('errors.selectDirectoryFailed'));
      setDialogState('error');
    }
  };

  const handleDownloadReplace = async (handle?: FileSystemDirectoryHandle) => {
    const targetHandle = handle || dirHandle;
    if (!targetHandle) return;

    setDialogState('downloading');
    setError('');
    setProgress(0);
    setCurrentFile(0);

    let result: DownloadResult;

    if (mode === 'market' && sharedSkillId) {
      result = await downloadAndExtractMarketSkill({
        sharedSkillId,
        skillName,
        platform,
        dirHandle: targetHandle,
        preserveNames: false,
        onProgress: (progressPercent, current, total) => {
          setProgress(progressPercent);
          if (current !== undefined) setCurrentFile(current);
          if (total !== undefined) setTotalFiles(total);
        },
      });
    } else {
      result = await downloadAndExtractSkill({
        skillId,
        platform,
        dirHandle: targetHandle,
        skillName,
        preserveNames: false,
        onProgress: (progressPercent, current, total) => {
          setProgress(progressPercent);
          if (current !== undefined) setCurrentFile(current);
          if (total !== undefined) setTotalFiles(total);
        },
      });
    }

    if (result.success) {
      setDownloadResult(result);
      if (hasIllegalChars) {
        setDialogState('mapping');
      } else {
        setDialogState('success');
      }
      onSuccess?.();
    } else {
      setError(result.error || 'Download failed');
      setDialogState('error');
    }
  };

  const handleRetry = () => {
    resetState();
    checkFileNames();
  };

  const handleClose = () => {
    if (dialogState !== 'downloading') {
      onClose();
    }
  };

  const getTargetPath = () => {
    if (!dirHandle) return '';
    const platformDir = platform === 'opencode' ? '.opencode' : '.claude';
    return `${formatDirectoryPath(dirHandle)}/${platformDir}/skills/${skillName}/`;
  };

  const affectedFiles = fileMappings.filter(m => m.hasChanged);

  const getRelativeDir = (filePath: string): string => {
    const lastSlashIndex = filePath.lastIndexOf('/');
    if (lastSlashIndex === -1) {
      return '.';
    }
    return filePath.substring(0, lastSlashIndex + 1);
  };

  const generateMarkdownTable = () => {
    const header = `| Original | Renamed | Directory |`;
    const separator = `|---|---|---|`;
    const rows = affectedFiles.map(m => {
      const dir = getRelativeDir(m.path);
      return `| ${m.original} | ${m.sanitized} | ${dir} |`;
    }).join('\n');
    return `${header}\n${separator}\n${rows}`;
  };

  const handleCopyMappings = async () => {
    const markdown = generateMarkdownTable();
    try {
      await navigator.clipboard.writeText(markdown);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Silently ignore clipboard copy errors
    }
  };

  if (!open) return null;

  const illegalChars = '< > : " | ? *';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={handleClose}
      />
      <div className="relative max-h-[90vh] w-full max-w-md overflow-y-auto rounded-xl bg-white p-4 shadow-2xl animate-in fade-in zoom-in duration-200 sm:max-w-lg sm:p-6">
        
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 sm:text-xl">
            {t('title')}
          </h2>
          <button
            onClick={handleClose}
            disabled={dialogState === 'downloading'}
            className="flex h-10 w-10 items-center justify-center rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-600 disabled:opacity-50"
            aria-label="Close dialog"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {dialogState === 'checking' && (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          </div>
        )}

        {dialogState === 'success' && (
          <div className="space-y-4">
            <div className="rounded-lg bg-green-50 px-4 py-4">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <span className="font-medium text-green-800">{t('success')}</span>
              </div>
              {downloadResult && (
                <div className="mt-3 text-sm text-green-700">
                  <p className="font-medium mb-1">{t('savedTo')}</p>
                  <p className="font-mono text-xs bg-green-100 px-2 py-1 rounded break-all">
                    {getTargetPath()}
                  </p>
                  <p className="mt-2 text-xs">
                    {t('filesExtracted', { count: downloadResult.filesExtracted })}
                  </p>
                </div>
              )}
            </div>
            <Button
              onClick={handleClose}
              className="w-full min-h-[44px]"
            >
              {tCommon('close')}
            </Button>
          </div>
        )}

        {dialogState === 'mapping' && (
          <div className="space-y-4">
            <div className="rounded-lg bg-blue-50 px-4 py-4">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="h-5 w-5 text-blue-600" />
                <span className="font-medium text-blue-800">{t('complete')}</span>
              </div>
              <p className="text-sm text-blue-700">
                {t('windowsCompatibility.renamed')}
              </p>
            </div>

            <div className="border rounded-lg overflow-hidden">
              <div
                onClick={() => setShowMappingDetails(!showMappingDetails)}
                className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 cursor-pointer"
              >
                <span className="font-medium text-sm">{t('windowsCompatibility.filenameChanges', { count: affectedFiles.length })}</span>
                <div className="flex items-center gap-2">
                  {showMappingDetails && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        void handleCopyMappings();
                      }}
                      className="flex items-center justify-center w-7 h-7 text-gray-600 hover:text-gray-900 rounded hover:bg-gray-200 transition-colors"
                      title="Copy as Markdown"
                    >
                      {copied ? (
                        <Check className="h-4 w-4 text-green-600" />
                      ) : (
                        <Copy className="h-4 w-4" />
                      )}
                    </button>
                  )}
                  {showMappingDetails ? (
                    <ChevronUp className="h-4 w-4 text-gray-500" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-gray-500" />
                  )}
                </div>
              </div>

              {showMappingDetails && (
                <div className="max-h-48 overflow-y-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">{t('windowsCompatibility.original')}</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">{t('windowsCompatibility.renamed')}</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {affectedFiles.map((mapping, index) => (
                        <tr key={index}>
                          <td className="px-3 py-2 text-gray-600 font-mono text-xs truncate max-w-[150px]" title={mapping.original}>
                            {mapping.original}
                          </td>
                          <td className="px-3 py-2 text-gray-900 font-mono text-xs truncate max-w-[150px]" title={mapping.sanitized}>
                            {mapping.sanitized}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            <div className="rounded-lg bg-yellow-50 px-4 py-3">
              <p className="text-sm text-yellow-800">
                {t('windowsCompatibility.referenceWarning')}
              </p>
            </div>

            <Button
              onClick={handleClose}
              className="w-full min-h-[44px]"
            >
              {tCommon('close')}
            </Button>
          </div>
        )}

        {dialogState === 'error' && (
          <div className="space-y-4">
            <div className="rounded-lg bg-red-50 px-4 py-4">
              <div className="flex items-start gap-2">
                <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-600" />
                <div>
                  <p className="font-medium text-red-800">{tCommon('download')} {tCommon('failed')}</p>
                  <p className="mt-1 text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
            <div className="flex flex-col gap-2 sm:flex-row sm:gap-3">
              <Button
                variant="outline"
                className="min-h-[44px] flex-1"
                onClick={onClose}
              >
                {tCommon('cancel')}
              </Button>
              <Button
                className="min-h-[44px] flex-1"
                onClick={handleRetry}
              >
                {tCommon('retry')}
              </Button>
            </div>
          </div>
        )}

        {dialogState === 'downloading' && (
          <div className="space-y-6 py-4">
            <div className="flex items-center justify-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gray-100">
                <Loader2 className="h-8 w-8 animate-spin text-gray-900" />
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">
                  {downloadMethod === 'zip' 
                    ? `${t('creatingZip')} ${totalFiles > 0 ? `(${currentFile}/${totalFiles})` : ''}`
                    : totalFiles > 0 ? t('downloadingFile', { current: currentFile, total: totalFiles }) : tCommon('downloading')
                  }
                </span>
                <span className="font-medium text-gray-900">{progress}%</span>
              </div>
              <div className="h-2 w-full rounded-full bg-gray-100">
                <div
                  className="h-full rounded-full bg-gray-900 transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          </div>
        )}

        {dialogState === 'initial' && (
          <div className="space-y-4">
            {hasIllegalChars ? (
              <div className="space-y-4">
                <div className="rounded-lg bg-yellow-50 px-4 py-4">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-yellow-600" />
                    <div>
                      <p className="font-medium text-yellow-800">{t('windowsCompatibility.title')}</p>
                      <p className="mt-1 text-sm text-yellow-700">
                        {t('windowsCompatibility.description', { 
                          count: affectedFiles.length, 
                          chars: illegalChars 
                        })}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  <p className="text-sm font-medium text-gray-700">{tCommon('choose')} {tCommon('download')} {tCommon('method')}:</p>
                  
                  {isWindows() ? (
                    <>
                      <button
                        onClick={() => setDownloadMethod('replace')}
                        className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                          downloadMethod === 'replace'
                            ? 'border-gray-900 bg-gray-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-orange-100 shrink-0">
                            <FileText className="h-5 w-5 text-orange-600" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-gray-900">{t('options.replace.title')}</span>
                              <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">{t('recommended')}</span>
                            </div>
                            <p className="mt-1 text-xs text-gray-500">
                              {t('options.replace.description')}
                            </p>
                          </div>
                        </div>
                      </button>

                      <button
                        onClick={() => setDownloadMethod('zip')}
                        className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                          downloadMethod === 'zip'
                            ? 'border-gray-900 bg-gray-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100 shrink-0">
                            <Package className="h-5 w-5 text-blue-600" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-gray-900">{t('options.zip.title')}</span>
                            </div>
                            <p className="mt-1 text-xs text-gray-500">
                              {t('options.zip.description')}
                            </p>
                          </div>
                        </div>
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        onClick={() => setDownloadMethod('zip')}
                        className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                          downloadMethod === 'zip'
                            ? 'border-gray-900 bg-gray-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100 shrink-0">
                            <Package className="h-5 w-5 text-blue-600" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-gray-900">{t('options.zip.title')}</span>
                              <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">{t('recommended')}</span>
                            </div>
                            <p className="mt-1 text-xs text-gray-500">
                              {t('options.zip.description')}
                            </p>
                          </div>
                        </div>
                      </button>

                      <button
                        onClick={() => setDownloadMethod('replace')}
                        className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                          downloadMethod === 'replace'
                            ? 'border-gray-900 bg-gray-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-orange-100 shrink-0">
                            <FileText className="h-5 w-5 text-orange-600" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-gray-900">{t('options.replace.title')}</span>
                              <span className="text-xs bg-orange-100 text-orange-700 px-2 py-0.5 rounded-full">{t('options.replace.badge')}</span>
                            </div>
                            <p className="mt-1 text-xs text-gray-500">
                              {t('options.replace.description')}
                            </p>
                          </div>
                        </div>
                      </button>
                    </>
                  )}
                </div>

                {downloadMethod === 'zip' && (
                  <Button
                    onClick={handleDownloadZip}
                    className="w-full min-h-[44px]"
                  >
                    <Package className="mr-2 h-4 w-4" />
                    {t('downloadZip')}
                  </Button>
                )}

                {downloadMethod === 'replace' && (
                  <div className="space-y-3">
                    <div>
                      <label className="mb-2 block text-sm font-medium text-gray-700">
                        {t('selectPlatform')}
                      </label>
                      <div className="flex gap-2">
                        <button
                          onClick={() => setPlatform('opencode')}
                          className={`flex-1 rounded-lg border px-4 py-3 text-sm font-medium transition-colors ${
                            platform === 'opencode'
                              ? 'border-gray-900 bg-gray-900 text-white'
                              : 'border-gray-200 bg-white text-gray-700 hover:bg-gray-50'
                          }`}
                        >
                          OpenCode
                        </button>
                        <button
                          onClick={() => setPlatform('claude')}
                          className={`flex-1 rounded-lg border px-4 py-3 text-sm font-medium transition-colors ${
                            platform === 'claude'
                              ? 'border-gray-900 bg-gray-900 text-white'
                              : 'border-gray-200 bg-white text-gray-700 hover:bg-gray-50'
                          }`}
                        >
                          Claude Code
                        </button>
                      </div>
                    </div>

                    <Button
                      onClick={() => handleSelectDirectory()}
                      disabled={!isSupported}
                      variant="outline"
                      className="w-full justify-start gap-2 min-h-[44px]"
                    >
                      <Folder className="h-4 w-4" />
                      <span>{t('selectProjectFolder')}</span>
                    </Button>

                    {!isSupported && (
                      <p className="text-sm text-red-600">
                        {t('errors.browserNotSupported')}
                      </p>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">
                    {t('selectPlatform')}
                  </label>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setPlatform('opencode')}
                      className={`flex-1 rounded-lg border px-4 py-3 text-sm font-medium transition-colors ${
                        platform === 'opencode'
                          ? 'border-gray-900 bg-gray-900 text-white'
                          : 'border-gray-200 bg-white text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      OpenCode
                    </button>
                    <button
                      onClick={() => setPlatform('claude')}
                      className={`flex-1 rounded-lg border px-4 py-3 text-sm font-medium transition-colors ${
                        platform === 'claude'
                          ? 'border-gray-900 bg-gray-900 text-white'
                          : 'border-gray-200 bg-white text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      Claude Code
                    </button>
                  </div>
                </div>

                <Button
                  onClick={handleSelectDirectory}
                  disabled={!isSupported}
                  variant="outline"
                  className="w-full justify-start gap-2"
                >
                  <Folder className="h-4 w-4" />
                  <span>{dirHandle ? formatDirectoryPath(dirHandle) : t('selectProjectFolder')}</span>
                </Button>

                {dirHandle && (
                  <p className="text-xs text-gray-500">
                    {t('savedTo')}{' '}
                    <span className="font-medium text-gray-700">
                      {getTargetPath()}
                    </span>
                  </p>
                )}
              </div>
            )}

            <div className="pt-2">
              <Button
                type="button"
                variant="outline"
                className="w-full min-h-[44px]"
                onClick={handleClose}
              >
                {tCommon('cancel')}
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
