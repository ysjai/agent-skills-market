'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Dialog } from '@/components/ui/Dialog';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { api } from '@/lib/api';
import { parseApiError } from '@/lib/errors';

interface SharePromptDialogProps {
  open: boolean;
  onClose: () => void;
  promptId: string;
  onSuccess?: () => void;
}

export function SharePromptDialog({ open, onClose, promptId, onSuccess }: SharePromptDialogProps) {
  const tCommon = useTranslations('common');
  const tPrompts = useTranslations('prompts');

  const [shareMessage, setShareMessage] = useState('');
  const [sharing, setSharing] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setSharing(true);
    setError('');
    try {
      await api.sharePrompt(promptId, shareMessage.trim() || undefined);

      if (onSuccess) onSuccess();

      handleClose();
    } catch (err: unknown) {
      setError(parseApiError(err) || 'Failed to share prompt');
    } finally {
      setSharing(false);
    }
  };

  const handleClose = () => {
    if (!sharing) {
      onClose();
      setShareMessage('');
      setError('');
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} title={tPrompts('share')}>
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
            {error}
          </div>
        )}

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 sm:mb-2">
            {tPrompts('share_message_label')}
          </label>
          <Input
            placeholder={tPrompts('share_message_placeholder')}
            value={shareMessage}
            onChange={(e) => setShareMessage(e.target.value)}
            disabled={sharing}
            className="min-h-[44px]"
          />
        </div>

        <div className="flex flex-col gap-2 pt-2 sm:flex-row sm:gap-3">
          <Button
            type="button"
            variant="outline"
            className="min-h-[44px] flex-1"
            onClick={handleClose}
            disabled={sharing}
          >
            {tCommon('cancel')}
          </Button>
          <Button
            type="submit"
            className="min-h-[44px] flex-1"
            disabled={sharing}
          >
            {sharing ? (
              <>
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                {tPrompts('sharing')}
              </>
            ) : (
              tPrompts('share')
            )}
          </Button>
        </div>
      </form>
    </Dialog>
  );
}
