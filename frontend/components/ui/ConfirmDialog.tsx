'use client';

import { Trash2, X, Check } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface ConfirmDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  description: React.ReactNode;
  confirmText?: string;
  cancelText?: string;
  isLoading?: boolean;
  error?: string | null;
}

export function ConfirmDialog({
  open,
  onClose,
  onConfirm,
  title,
  description,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  isLoading = false,
  error = null,
}: ConfirmDialogProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in">
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={() => !isLoading && onClose()}
      />
      <div className="relative w-full max-w-sm rounded-xl bg-white p-5 shadow-2xl animate-scale-in sm:p-6">
        <div className="mb-4 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-100 sm:h-12 sm:w-12">
            <Trash2 className="h-5 w-5 text-red-600 sm:h-6 sm:w-6" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-gray-900 sm:text-lg">{title}</h3>
            <p className="text-xs text-gray-500 sm:text-sm">This action cannot be undone</p>
          </div>
        </div>
        <div className="mb-6 text-sm text-gray-600 sm:text-base">
          {description}
        </div>
        {error && (
          <div className="mb-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
            {error}
          </div>
        )}
        <div className="flex flex-col gap-2 sm:flex-row sm:gap-3">
          <Button
            variant="outline"
            className="btn-interactive min-h-[44px] flex-1 gap-2"
            onClick={onClose}
            disabled={isLoading}
          >
            <X className="h-4 w-4" />
            {cancelText}
          </Button>
          <Button
            variant="destructive"
            className="btn-interactive min-h-[44px] flex-1 gap-2"
            onClick={onConfirm}
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                {confirmText}
              </>
            ) : (
              <>
                <Check className="h-4 w-4" />
                {confirmText}
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
