'use client';

import * as React from 'react';
import { useTranslations } from 'next-intl';
import { AlertTriangle } from 'lucide-react';

import { InputDialog } from '@/components/ui/InputDialog';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { ConflictDialog } from '@/components/ui/ConflictDialog';
import { ProgressDialog } from '@/components/ui/ProgressDialog';
import { BatchConflictDialog } from '@/components/ui/BatchConflictDialog';
import { DialogPortal } from '@/components/ui/DialogPortal';
import type { ProgressItem } from '@/components/ui/ProgressDialog';
import type { ConflictItem, ConflictAction } from '@/components/ui/BatchConflictDialog';
import type { ConflictAction as SingleConflictAction } from '@/components/ui/ConflictDialog';
import { isWindows } from '@/lib/download';

export interface FileTreeDialogsProps {
  // Input Dialog
  dialogOpen: boolean;
  dialogType: 'file' | 'folder';
  dialogError: string | undefined;
  onDialogConfirm: (name: string) => void;
  onDialogCancel: () => void;

  // Delete Confirm Dialog
  deleteConfirmOpen: boolean;
  deleteTargetName: string;
  deleteTargetPath: string;
  isDeleting: boolean;
  deleteError: string | null;
  onDeleteConfirm: () => void;
  onDeleteCancel: () => void;

  // Conflict Dialog
  conflictDialogOpen: boolean;
  conflictFileName: string;
  onConflictResolve: (action: SingleConflictAction, newName?: string) => void;

  // Progress Dialog
  progressDialogOpen: boolean;
  progressItems: ProgressItem[];
  progressCurrent: number;
  progressTotal: number;
  progressCurrentFile: string;
  onProgressCancel: () => void;
  onProgressClose: () => void;

  // Batch Conflict Dialog
  batchConflictDialogOpen: boolean;
  batchConflictItems: ConflictItem[];
  onBatchConflictResolve: (resolutions: Map<string, ConflictAction>) => void;
  onBatchConflictCancel: () => void;

  // Download Warning Dialog
  downloadWarningOpen: boolean;
  downloadWarningFiles: string[];
  pendingDownloadFolder: { path: string; name: string } | null;
  onDownloadWarningClose: () => void;
  onDownloadWithAutoRename: () => void;
  onDownloadAsZip: () => void;

  // Windows Upload Confirm Dialog
  windowsConfirmDialogOpen: boolean;
  windowsConfirmFiles: string[];
  onWindowsConfirm: () => void;
  onWindowsCancel: () => void;
}

export function FileTreeDialogs({
  // Input Dialog
  dialogOpen,
  dialogType,
  dialogError,
  onDialogConfirm,
  onDialogCancel,

  // Delete Confirm Dialog
  deleteConfirmOpen,
  deleteTargetName,
  deleteTargetPath,
  isDeleting,
  deleteError,
  onDeleteConfirm,
  onDeleteCancel,

  // Conflict Dialog
  conflictDialogOpen,
  conflictFileName,
  onConflictResolve,

  // Progress Dialog
  progressDialogOpen,
  progressItems,
  progressCurrent,
  progressTotal,
  progressCurrentFile,
  onProgressCancel,
  onProgressClose,

  // Batch Conflict Dialog
  batchConflictDialogOpen,
  batchConflictItems,
  onBatchConflictResolve,
  onBatchConflictCancel,

  // Download Warning Dialog
  downloadWarningOpen,
  downloadWarningFiles,
  pendingDownloadFolder,
  onDownloadWarningClose,
  onDownloadWithAutoRename,
  onDownloadAsZip,

  // Windows Upload Confirm Dialog
  windowsConfirmDialogOpen,
  windowsConfirmFiles,
  onWindowsConfirm,
  onWindowsCancel,
}: FileTreeDialogsProps) {
  const t = useTranslations('files');
  const tCommon = useTranslations('common');

  return (
    <DialogPortal>
      <InputDialog
        open={dialogOpen}
        title={dialogType === 'file' ? t('newFile') : t('newFolder')}
        label={tCommon('name')}
        placeholder={dialogType === 'file' ? t('fileName') : t('folderName')}
        error={dialogError}
        onConfirm={onDialogConfirm}
        onCancel={onDialogCancel}
      />

      <ConfirmDialog
        open={deleteConfirmOpen}
        onClose={onDeleteCancel}
        onConfirm={onDeleteConfirm}
        title={tCommon('delete')}
        description={
          <>
            {t('deleteConfirm', {
              name: deleteTargetName,
              type: deleteTargetPath.includes('/') ? t('folderType') : t('fileType')
            })}
          </>
        }
        confirmText={tCommon('delete')}
        cancelText={tCommon('cancel')}
        isLoading={isDeleting}
        error={deleteError}
      />

      <ConflictDialog
        open={conflictDialogOpen}
        fileName={conflictFileName}
        title={t('fileExists')}
        description={t('overwriteConfirm', { name: conflictFileName })}
        skipText={tCommon('skip')}
        overwriteText={tCommon('overwrite')}
        renameText={tCommon('rename')}
        renamePlaceholder={t('newFileNamePlaceholder')}
        confirmRenameText={t('confirmRename')}
        cancelText={tCommon('cancel')}
        onResolve={onConflictResolve}
      />

      <ProgressDialog
        open={progressDialogOpen}
        type="upload"
        current={progressCurrent}
        total={progressTotal}
        currentFile={progressCurrentFile}
        items={progressItems}
        onCancel={onProgressCancel}
        onClose={onProgressClose}
      />

      <BatchConflictDialog
        open={batchConflictDialogOpen}
        items={batchConflictItems}
        onResolve={onBatchConflictResolve}
        onCancel={onBatchConflictCancel}
      />

      {downloadWarningOpen && pendingDownloadFolder && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={onDownloadWarningClose}
          />
          <div className="relative w-full max-w-md rounded-xl bg-white p-6 shadow-2xl">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {t('downloadWindowsWarning.title', { count: downloadWarningFiles.length })}
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              {t('downloadWindowsWarning.description', { count: downloadWarningFiles.length })}
            </p>
            <div className="rounded-lg bg-yellow-50 p-3 mb-4">
              <p className="text-sm font-medium text-yellow-800 mb-2">
                {t('downloadWindowsWarning.affectedFiles')}
              </p>
              <ul className="max-h-32 overflow-y-auto space-y-1">
                {downloadWarningFiles.map((path, index) => (
                  <li key={index} className="font-mono text-xs text-yellow-700 break-all">
                    {path}
                  </li>
                ))}
              </ul>
            </div>
            <div className="space-y-2">
              {isWindows() ? (
                <>
                  <button
                    onClick={onDownloadWithAutoRename}
                    className="w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 flex items-center justify-center gap-2"
                  >
                    {t('downloadWindowsWarning.autoRenameOption')}
                    <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                      {t('downloadWindowsWarning.recommended')}
                    </span>
                  </button>
                  <p className="text-xs text-gray-500 px-1">
                    {t('downloadWindowsWarning.autoRenameHelp')}
                  </p>
                  <button
                    onClick={onDownloadAsZip}
                    className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    {t('downloadWindowsWarning.zipOption')}
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={onDownloadAsZip}
                    className="w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 flex items-center justify-center gap-2"
                  >
                    {t('downloadWindowsWarning.zipOption')}
                    <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                      {t('downloadWindowsWarning.recommended')}
                    </span>
                  </button>
                  <button
                    onClick={onDownloadWithAutoRename}
                    className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 flex items-center justify-center gap-2"
                  >
                    {t('downloadWindowsWarning.autoRenameOption')}
                    <span className="text-xs bg-orange-100 text-orange-700 px-2 py-0.5 rounded-full">
                      {t('downloadWindowsWarning.autoRenameBadge')}
                    </span>
                  </button>
                  <p className="text-xs text-gray-500 px-1">
                    {t('downloadWindowsWarning.autoRenameHelp')}
                  </p>
                </>
              )}
              <button
                onClick={onDownloadWarningClose}
                className="w-full rounded-lg px-4 py-2 text-sm font-medium text-gray-500 hover:text-gray-700"
              >
                {tCommon('cancel')}
              </button>
            </div>
          </div>
        </div>
      )}

      {windowsConfirmDialogOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={onWindowsCancel}
          />
          <div className="relative w-full max-w-md rounded-xl bg-white p-6 shadow-2xl">
            <div className="flex items-start gap-3 mb-4">
              <AlertTriangle className="h-6 w-6 text-yellow-500 shrink-0 mt-0.5" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {t('uploadWindowsConfirm.title', { count: windowsConfirmFiles.length })}
                </h3>
              </div>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              {t('uploadWindowsConfirm.description', { count: windowsConfirmFiles.length })}
            </p>
            <div className="rounded-lg bg-yellow-50 p-3 mb-4">
              <p className="text-sm font-medium text-yellow-800 mb-2">
                {t('uploadWindowsConfirm.affectedFiles')}
              </p>
              <ul className="max-h-32 overflow-y-auto space-y-1">
                {windowsConfirmFiles.map((path, index) => (
                  <li key={index} className="font-mono text-xs text-yellow-700 break-all">
                    {path}
                  </li>
                ))}
              </ul>
            </div>
            <div className="space-y-2">
              <button
                onClick={() => void onWindowsConfirm()}
                className="w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
              >
                {t('uploadWindowsConfirm.continueUpload')}
              </button>
              <button
                onClick={onWindowsCancel}
                className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                {tCommon('cancel')}
              </button>
            </div>
          </div>
        </div>
      )}
    </DialogPortal>
  );
}
