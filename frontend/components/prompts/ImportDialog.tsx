'use client';

import React, { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Upload, AlertCircle, Loader2 } from 'lucide-react';
import { Dialog } from '@/components/ui/Dialog';
import { Button } from '@/components/ui/Button';

export interface ImportDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onImport: (content: string) => Promise<void>;
}

export function ImportDialog({ isOpen, onClose, onImport }: ImportDialogProps) {
  const t = useTranslations('prompts');
  const tCommon = useTranslations('common');
  const [content, setContent] = useState('');
  const [isImporting, setIsImporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!content.trim()) return;
    
    setIsImporting(true);
    setError(null);
    try {
      await onImport(content);
      setContent('');
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to import prompt');
    } finally {
      setIsImporting(false);
    }
  };

  const handleClose = () => {
    if (!isImporting) {
      setContent('');
      setError(null);
      onClose();
    }
  };

  const placeholderText = `---
title: My Prompt Title
description: Optional description
tags: [tag1, tag2]
---

Prompt content goes here...
Use {{variable}} for template variables.`;

  return (
    <Dialog open={isOpen} onClose={handleClose} title={t('importPrompt')}>
      <div className="flex flex-col gap-4">
        {error && (
          <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-600 border border-red-100">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <p>{error}</p>
          </div>
        )}
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder={placeholderText}
          className="min-h-[200px] w-full resize-y rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-900 font-mono placeholder:text-gray-400 focus:border-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-900/20 disabled:cursor-not-allowed disabled:opacity-50"
          disabled={isImporting}
        />
        <div className="flex justify-end gap-2">
          <Button
            type="button"
            variant="outline"
            onClick={handleClose}
            disabled={isImporting}
          >
            {tCommon('cancel')}
          </Button>
          <Button
            type="button"
            onClick={handleSubmit}
            disabled={!content.trim() || isImporting}
          >
            {isImporting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                {tCommon('loading')}
              </>
            ) : (
              <>
                <Upload className="mr-2 h-4 w-4" />
                {t('importPrompt')}
              </>
            )}
          </Button>
        </div>
      </div>
    </Dialog>
  );
}
