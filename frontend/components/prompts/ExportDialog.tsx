'use client';

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Copy, Check } from 'lucide-react';
import { Dialog } from '@/components/ui/Dialog';
import { Button } from '@/components/ui/Button';

export interface ExportDialogProps {
  isOpen: boolean;
  onClose: () => void;
  content: string;
}

export function ExportDialog({ isOpen, onClose, content }: ExportDialogProps) {
  const t = useTranslations('prompts');
  const tCommon = useTranslations('common');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    if (copied) {
      timeoutId = setTimeout(() => setCopied(false), 2000);
    }
    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [copied]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
    } catch (err) {
      console.error('Failed to copy to clipboard', err);
    }
  };

  return (
    <Dialog open={isOpen} onClose={onClose} title={t('exportPrompt')}>
      <div className="flex flex-col gap-4">
        <textarea
          readOnly
          value={content}
          className="min-h-[250px] w-full resize-y rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-900 font-mono focus:outline-none focus:ring-2 focus:ring-gray-900/20"
        />
        <div className="flex justify-end gap-2">
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
          >
            {tCommon('close')}
          </Button>
          <Button
            type="button"
            onClick={handleCopy}
            className="min-w-[100px]"
          >
            {copied ? (
              <>
                <Check className="mr-2 h-4 w-4" />
                Copied!
              </>
            ) : (
              <>
                <Copy className="mr-2 h-4 w-4" />
                Copy
              </>
            )}
          </Button>
        </div>
      </div>
    </Dialog>
  );
}
