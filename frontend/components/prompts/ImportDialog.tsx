'use client';

import React, { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Upload, AlertCircle, Loader2, FolderUp } from 'lucide-react';
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
  const [fileName, setFileName] = useState('');
  const [isImporting, setIsImporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!content.trim()) return;
    
    setIsImporting(true);
    setError(null);
    try {
      await onImport(content);
      setContent('');
      setFileName('');
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
      setFileName('');
      setError(null);
      onClose();
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.md')) {
      setError('Please select a .md file');
      return;
    }

    try {
      const text = await file.text();
      setContent(text);
      setFileName(file.name);
      setError(null);
    } catch {
      setError('Failed to read file');
      setContent('');
      setFileName('');
    }
  };

  return (
    <Dialog open={isOpen} onClose={handleClose} title={t('importPrompt')}>
      <div className="flex flex-col gap-4">
        {error && (
          <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-600 border border-red-100">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <p>{error}</p>
          </div>
        )}
        <div className="relative flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 p-6 sm:p-8 hover:bg-gray-50 transition-colors">
          <FolderUp className="mb-2 h-8 w-8 text-gray-400 sm:h-10 sm:w-10" />
          <p className="mb-2 text-sm text-gray-500 font-medium">
            {fileName ? `Selected: ${fileName} ✓` : t('clickToSelect', { defaultValue: 'Click or drag file to this area to upload' })}
          </p>
          <input
            type="file"
            accept=".md"
            onChange={handleFileSelect}
            disabled={isImporting}
            className="absolute inset-0 cursor-pointer opacity-0 disabled:cursor-not-allowed"
          />
          <Button variant="outline" className="pointer-events-none relative z-10" disabled={isImporting}>
            {fileName ? t('changeFile', { defaultValue: 'Change File' }) : t('selectFile', { defaultValue: 'Select File' })}
          </Button>
        </div>
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
