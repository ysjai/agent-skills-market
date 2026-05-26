'use client';

import { useTranslations } from 'next-intl';

import { Dialog } from '@/components/ui/Dialog';
import { Button } from '@/components/ui/Button';

interface DeleteSkillDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  deleting: boolean;
  error: string;
  title: string;
  message: string;
}

export function DeleteSkillDialog({
  open,
  onClose,
  onConfirm,
  deleting,
  error,
  title,
  message,
}: DeleteSkillDialogProps) {
  const tCommon = useTranslations('common');

  return (
    <Dialog open={open} onClose={onClose} title={title}>
      <div className="space-y-4">
        <p className="text-sm text-gray-600 sm:text-base">
          {message}
        </p>
        {error && (
          <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
            {error}
          </div>
        )}
        <div className="flex flex-col gap-2 sm:flex-row sm:gap-3">
          <Button
            variant="outline"
            className="min-h-[44px] flex-1"
            onClick={onClose}
            disabled={deleting}
          >
            {tCommon('cancel')}
          </Button>
          <Button
            variant="destructive"
            className="min-h-[44px] flex-1"
            onClick={onConfirm}
            disabled={deleting}
          >
            {deleting ? (
              <>
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                {tCommon('delete')}...
              </>
            ) : (
              tCommon('confirm')
            )}
          </Button>
        </div>
      </div>
    </Dialog>
  );
}
