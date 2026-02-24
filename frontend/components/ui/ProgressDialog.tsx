'use client';

import { X, Loader2, AlertCircle, CheckCircle, FileUp, FileDown } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useTranslations } from 'next-intl';

export interface ProgressItem {
  name: string;
  status: 'pending' | 'processing' | 'success' | 'error';
  error?: string;
}

export interface ProgressDialogProps {
  open: boolean;
  type: 'upload' | 'download';
  title?: string;
  current: number;
  total: number;
  currentFile?: string;
  speed?: string;
  eta?: string;
  items?: ProgressItem[];
  error?: string;
  onCancel: () => void;
  onClose?: () => void;
  showErrors?: boolean;
}

export function ProgressDialog({
  open,
  type,
  title,
  current,
  total,
  currentFile,
  speed,
  eta,
  items,
  error,
  onCancel,
  onClose,
  showErrors = true,
}: ProgressDialogProps) {
  const t = useTranslations('progress');
  const tCommon = useTranslations('common');

  if (!open) return null;

  const progress = total > 0 ? Math.round((current / total) * 100) : 0;
  const isComplete = current >= total && total > 0;
  const hasErrors = items?.some((item) => item.status === 'error') ?? false;
  const errorItems = items?.filter((item) => item.status === 'error') ?? [];

  const Icon = type === 'upload' ? FileUp : FileDown;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={isComplete ? onClose : undefined} />
      <div className="relative max-h-[90vh] w-full max-w-lg overflow-hidden rounded-xl bg-white shadow-2xl">
        <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100">
              <Icon className="h-5 w-5 text-gray-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                {title || (type === 'upload' ? t('uploading') : t('downloading'))}
              </h3>
              <p className="text-sm text-gray-500">
                {isComplete
                  ? t('completed', { count: current, total })
                  : t('progress', { current, total })}
              </p>
            </div>
          </div>
          {!isComplete && (
            <button
              onClick={onCancel}
              className="flex h-8 w-8 items-center justify-center rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-600"
              aria-label={tCommon('close')}
            >
              <X className="h-5 w-5" />
            </button>
          )}
        </div>

        <div className="px-6 py-4">
          <div className="mb-4">
            <div className="mb-2 flex items-center justify-between text-sm">
              <span className="text-gray-600">
                {currentFile || (isComplete ? t('complete') : t('processing'))}
              </span>
              <span className="font-medium text-gray-900">{progress}%</span>
            </div>
            <div className="h-2.5 w-full rounded-full bg-gray-100">
              <div
                className="h-full rounded-full bg-gray-900 transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          {(speed || eta) && !isComplete && (
            <div className="mb-4 flex gap-4 text-sm text-gray-500">
              {speed && (
                <div className="flex items-center gap-1.5">
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  <span>{speed}</span>
                </div>
              )}
              {eta && (
                <div className="flex items-center gap-1.5">
                  <span>{t('eta', { time: eta })}</span>
                </div>
              )}
            </div>
          )}

          {hasErrors && showErrors && (
            <div className="mb-4 rounded-lg bg-red-50 px-4 py-3">
              <div className="flex items-start gap-2">
                <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-500" />
                <div className="flex-1">
                  <p className="font-medium text-red-800">
                    {t('errorsFound', { count: errorItems.length })}
                  </p>
                  <div className="mt-2 max-h-32 space-y-1 overflow-y-auto text-sm">
                    {errorItems.slice(0, 5).map((item, index) => (
                      <div key={index} className="flex items-start gap-2 text-red-700">
                        <span className="truncate font-mono text-xs">{item.name}</span>
                        <span className="shrink-0 text-red-500">:</span>
                        <span className="text-xs">{item.error || t('unknownError')}</span>
                      </div>
                    ))}
                    {errorItems.length > 5 && (
                      <p className="text-xs text-red-500">
                        {t('andMore', { count: errorItems.length - 5 })}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {isComplete && !hasErrors && (
            <div className="mb-4 rounded-lg bg-green-50 px-4 py-3">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <span className="font-medium text-green-800">
                  {type === 'upload' ? t('uploadSuccess') : t('downloadSuccess')}
                </span>
              </div>
            </div>
          )}

          {error && (
            <div className="mb-4 rounded-lg bg-red-50 px-4 py-3">
              <div className="flex items-start gap-2">
                <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-500" />
                <span className="text-red-800">{error}</span>
              </div>
            </div>
          )}

          {items && items.length > 0 && showErrors && (
            <div className="max-h-48 overflow-y-auto rounded-lg border border-gray-100">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-gray-50">
                  <tr>
                    <th className="px-3 py-2 text-left font-medium text-gray-700">{t('fileName')}</th>
                    <th className="px-3 py-2 text-right font-medium text-gray-700">{t('status')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {items.map((item, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-3 py-2 text-gray-900">
                        <span className="truncate font-mono text-xs">{item.name}</span>
                      </td>
                      <td className="px-3 py-2 text-right">
                        {item.status === 'pending' && (
                          <span className="text-xs text-gray-400">{t('pending')}</span>
                        )}
                        {item.status === 'processing' && (
                          <Loader2 className="ml-auto h-4 w-4 animate-spin text-gray-600" />
                        )}
                        {item.status === 'success' && (
                          <CheckCircle className="ml-auto h-4 w-4 text-green-500" />
                        )}
                        {item.status === 'error' && (
                          <span className="text-xs text-red-500" title={item.error}>
                            {t('error')}
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="flex items-center justify-end gap-2 border-t border-gray-100 px-6 py-4">
          {isComplete ? (
            <Button onClick={onClose} className="min-h-[44px]">
              {tCommon('close')}
            </Button>
          ) : (
            <Button variant="outline" onClick={onCancel} className="min-h-[44px]">
              {tCommon('cancel')}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
