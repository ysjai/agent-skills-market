'use client';

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Copy, Check, Download } from 'lucide-react';
import { Dialog } from '@/components/ui/Dialog';
import { Button } from '@/components/ui/Button';

export interface ExportDialogProps {
  isOpen: boolean;
  onClose: () => void;
  content: string;
  promptTitle?: string;
}

export function ExportDialog({ isOpen, onClose, content, promptTitle }: ExportDialogProps) {
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

  const handleDownload = () => {
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${(promptTitle || 'prompt').toLowerCase().replace(/\s+/g, '-')}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
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
            variant="outline"
            onClick={handleDownload}
          >
            <Download className="mr-2 h-4 w-4" />
            {tCommon('download', { defaultValue: 'Download' })}
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
