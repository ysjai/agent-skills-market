'use client';

import { Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useTranslations } from 'next-intl';

interface DeletePromptDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  isLoading?: boolean;
}

export function DeletePromptDialog({
  open,
  onClose,
  onConfirm,
  isLoading = false,
}: DeletePromptDialogProps) {
  const t = useTranslations('prompts');
  const tCommon = useTranslations('common');

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in">
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={() => !isLoading && onClose()}
      />
      <div className="relative w-full max-w-sm rounded-xl bg-white p-5 shadow-2xl animate-scale-in sm:p-6">
        <div className="mb-4 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-100 sm:h-12 sm:w-12">
            <Trash2 className="h-5 w-5 text-gray-900 sm:h-6 sm:w-6" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-gray-900 sm:text-lg">{t('deletePrompt')}</h3>
          </div>
        </div>
        <p className="mb-6 text-sm text-gray-600 sm:text-base">
          {t('deleteConfirm')}
        </p>
        <div className="flex flex-col gap-2 sm:flex-row sm:gap-3">
          <Button
            variant="outline"
            className="btn-interactive min-h-[44px] flex-1"
            onClick={onClose}
            disabled={isLoading}
          >
            {tCommon('cancel')}
          </Button>
          <Button
            variant="default"
            className="btn-interactive min-h-[44px] flex-1 bg-gray-900 hover:bg-gray-800 text-white"
            onClick={onConfirm}
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                {tCommon('delete')}...
              </>
            ) : (
              tCommon('delete')
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
