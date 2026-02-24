'use client';

import { useState, useCallback } from 'react';
import { useToast } from '@/components/ui/Toast';
import { useTranslations } from 'next-intl';

interface UseClipboardReturn {
  copy: (text: string) => Promise<boolean>;
  copied: boolean;
}

export function useClipboard(): UseClipboardReturn {
  const [copied, setCopied] = useState(false);
  const { showToast } = useToast();
  const t = useTranslations('fileViewer');

  const copy = useCallback(
    async (text: string): Promise<boolean> => {
      try {
        await navigator.clipboard.writeText(text);
        setCopied(true);
        showToast(t('copied'), 'success');

        setTimeout(() => {
          setCopied(false);
        }, 2000);

        return true;
      } catch {
        showToast(t('copyFailed'), 'error');
        return false;
      }
    },
    [showToast, t]
  );

  return { copy, copied };
}
