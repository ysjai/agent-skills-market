'use client';

import { useState, useCallback } from 'react';
import { X, AlertTriangle, FileText, Check } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useTranslations } from 'next-intl';

export type ConflictAction = 'skip' | 'overwrite' | 'rename';

export interface ConflictItem {
  path: string;
  existingSize?: number;
  existingModified?: string;
  newSize?: number;
}

export interface BatchConflictDialogProps {
  open: boolean;
  items: ConflictItem[];
  onResolve: (resolutions: Map<string, ConflictAction>) => void;
  onCancel: () => void;
}

export function BatchConflictDialog({
  open,
  items,
  onResolve,
  onCancel,
}: BatchConflictDialogProps) {
  const t = useTranslations('conflict');
  const tCommon = useTranslations('common');
  const [resolutions, setResolutions] = useState<Map<string, ConflictAction>>(new Map());
  const [applyToAll, setApplyToAll] = useState<ConflictAction | null>(null);

  const handleAction = useCallback((path: string, action: ConflictAction) => {
    setResolutions((prev) => {
      const next = new Map(prev);
      next.set(path, action);
      return next;
    });
  }, []);

  const handleApplyToAll = useCallback((action: ConflictAction) => {
    setApplyToAll(action);
    const newResolutions = new Map<string, ConflictAction>();
    items.forEach((item) => {
      newResolutions.set(item.path, action);
    });
    setResolutions(newResolutions);
  }, [items]);

  const handleConfirm = useCallback(() => {
    const finalResolutions = new Map<string, ConflictAction>();
    items.forEach((item) => {
      finalResolutions.set(item.path, resolutions.get(item.path) || 'skip');
    });
    onResolve(finalResolutions);
    setResolutions(new Map());
    setApplyToAll(null);
  }, [items, resolutions, onResolve]);

  const handleCancel = useCallback(() => {
    setResolutions(new Map());
    setApplyToAll(null);
    onCancel();
  }, [onCancel]);

  const resolvedCount = items.filter((item) => resolutions.has(item.path)).length;
  const allResolved = resolvedCount === items.length;

  if (!open || items.length === 0) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={handleCancel} />
      <div className="relative max-h-[90vh] w-full max-w-2xl overflow-hidden rounded-xl bg-white shadow-2xl">
        <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-yellow-100">
              <AlertTriangle className="h-5 w-5 text-yellow-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{t('title')}</h3>
              <p className="text-sm text-gray-500">
                {t('description', { count: items.length })}
              </p>
            </div>
          </div>
          <button
            onClick={handleCancel}
            className="flex h-8 w-8 items-center justify-center rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-600"
            aria-label={tCommon('close')}
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="px-6 py-4">
          <div className="mb-4 rounded-lg bg-gray-50 px-4 py-3">
            <p className="mb-2 text-sm font-medium text-gray-700">{t('applyToAll')}</p>
            <div className="flex flex-wrap gap-2">
              <Button
                variant={applyToAll === 'skip' ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleApplyToAll('skip')}
                className="min-h-[36px]"
              >
                {applyToAll === 'skip' && <Check className="mr-1 h-3.5 w-3.5" />}
                {tCommon('skip')}
              </Button>
              <Button
                variant={applyToAll === 'overwrite' ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleApplyToAll('overwrite')}
                className="min-h-[36px]"
              >
                {applyToAll === 'overwrite' && <Check className="mr-1 h-3.5 w-3.5" />}
                {tCommon('overwrite')}
              </Button>
              <Button
                variant={applyToAll === 'rename' ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleApplyToAll('rename')}
                className="min-h-[36px]"
              >
                {applyToAll === 'rename' && <Check className="mr-1 h-3.5 w-3.5" />}
                {t('rename')}
              </Button>
            </div>
          </div>

          <div className="max-h-80 overflow-y-auto rounded-lg border border-gray-100">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-gray-50">
                <tr>
                  <th className="px-3 py-2 text-left font-medium text-gray-700">{t('fileName')}</th>
                  <th className="hidden px-3 py-2 text-right font-medium text-gray-700 sm:table-cell">{t('existingSize')}</th>
                  <th className="px-3 py-2 text-right font-medium text-gray-700">{t('action')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {items.map((item, index) => {
                  const action = resolutions.get(item.path);
                  return (
                    <tr key={index} className={action ? 'bg-blue-50/50' : 'hover:bg-gray-50'}>
                      <td className="px-3 py-2">
                        <div className="flex items-center gap-2">
                          <FileText className="h-4 w-4 shrink-0 text-gray-400" />
                          <span className="truncate font-mono text-xs text-gray-900" title={item.path}>
                            {item.path}
                          </span>
                        </div>
                      </td>
                      <td className="hidden px-3 py-2 text-right text-xs text-gray-500 sm:table-cell">
                        {item.existingSize ? formatFileSize(item.existingSize) : '-'}
                      </td>
                      <td className="px-3 py-2 text-right">
                        <div className="flex items-center justify-end gap-1">
                          <button
                            onClick={() => handleAction(item.path, 'skip')}
                            className={`rounded px-2 py-1 text-xs transition-colors ${
                              action === 'skip'
                                ? 'bg-gray-900 text-white'
                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                            }`}
                          >
                            {tCommon('skip')}
                          </button>
                          <button
                            onClick={() => handleAction(item.path, 'overwrite')}
                            className={`rounded px-2 py-1 text-xs transition-colors ${
                              action === 'overwrite'
                                ? 'bg-gray-900 text-white'
                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                            }`}
                          >
                            {tCommon('overwrite')}
                          </button>
                          <button
                            onClick={() => handleAction(item.path, 'rename')}
                            className={`rounded px-2 py-1 text-xs transition-colors ${
                              action === 'rename'
                                ? 'bg-gray-900 text-white'
                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                            }`}
                          >
                            {t('rename')}
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <div className="mt-4 text-sm text-gray-500">
            {t('resolvedCount', { resolved: resolvedCount, total: items.length })}
          </div>
        </div>

        <div className="flex items-center justify-end gap-2 border-t border-gray-100 px-6 py-4">
          <Button variant="outline" onClick={handleCancel} className="min-h-[44px]">
            {tCommon('cancel')}
          </Button>
          <Button onClick={handleConfirm} disabled={!allResolved} className="min-h-[44px]">
            {t('confirm')}
          </Button>
        </div>
      </div>
    </div>
  );
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const BYTES_PER_KB = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const index = Math.floor(Math.log(bytes) / Math.log(BYTES_PER_KB));
  return parseFloat((bytes / Math.pow(BYTES_PER_KB, index)).toFixed(1)) + ' ' + sizes[index];
}
