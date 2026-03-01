'use client';

import { useEffect, useState, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { TopNav } from '@/components/layout/TopNav';
import { PromptList } from '@/components/prompts/PromptList';
import { PromptEditor } from '@/components/prompts/PromptEditor';
import { ImportDialog } from '@/components/prompts/ImportDialog';
import { ExportDialog } from '@/components/prompts/ExportDialog';
import { usePromptsStore } from '@/stores/promptsStore';
import { api } from '@/lib/api';
import type { Prompt, PromptListResponse } from '@/types/prompt';

export default function PromptsPage() {
  const t = useTranslations('prompts');
  const tCommon = useTranslations('common');
  const [isMounted, setIsMounted] = useState(false);
  const [showImport, setShowImport] = useState(false);
  const [exportContent, setExportContent] = useState('');
  const [showExport, setShowExport] = useState(false);

  const {
    isLoading,
    setIsLoading,
    setErrorMessage,
    setPrompts,
    addPrompt,
    removePrompt,
    selectedPrompt,
    setSelectedPrompt,
    errorMessage
  } = usePromptsStore();

  useEffect(() => {
    loadPrompts();
    const timer = setTimeout(() => setIsMounted(true), 50);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadPrompts = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const data = await api.get<PromptListResponse>('/prompts');
      setPrompts(data.items);
    } catch (error: unknown) {
      if (error instanceof Error && error.message.includes('404')) {
        setPrompts([]);
      } else {
        setErrorMessage(t('loadFailed'));
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleImport = useCallback(async (content: string) => {
    const imported = await api.post<Prompt>('/prompts/import', { content });
    addPrompt(imported);
    setSelectedPrompt(imported);
  }, [addPrompt, setSelectedPrompt]);

  const handleExport = useCallback(async (promptId: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
      const resp = await fetch(`${apiUrl}/prompts/${promptId}/export`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      const text = await resp.text();
      setExportContent(text);
      setShowExport(true);
    } catch (err) {
      console.error('Failed to export prompt', err);
    }
  }, []);

  const handleDelete = useCallback(async (promptId: string) => {
    if (!confirm(t('deleteConfirm'))) return;
    try {
      await api.delete(`/prompts/${promptId}`);
      removePrompt(promptId);
      if (selectedPrompt?.id === promptId) {
        setSelectedPrompt(null);
      }
    } catch (err) {
      console.error('Failed to delete prompt', err);
    }
  }, [removePrompt, selectedPrompt, setSelectedPrompt, t]);

  return (
    <div className={`flex h-screen flex-col bg-gray-50 transition-opacity duration-500 ${isMounted ? 'opacity-100' : 'opacity-0'}`}>
      <TopNav />

      {errorMessage && (
        <div className="mx-auto mt-4 w-full max-w-7xl px-4 sm:px-6 shrink-0">
          <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-800 shadow-sm">
            {errorMessage}
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="flex flex-1 items-center justify-center animate-fade-in">
          <div className="flex items-center gap-2 text-gray-500 bg-white px-6 py-4 rounded-full shadow-sm">
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-gray-300 border-t-gray-900" />
            <span className="font-medium">{tCommon('loading')}</span>
          </div>
        </div>
      ) : (
        <div className="flex flex-1 overflow-hidden">
          <PromptList
            onImportClick={() => setShowImport(true)}
            onExportClick={handleExport}
            onDeleteClick={handleDelete}
          />
          <PromptEditor />
        </div>
      )}

      <ImportDialog
        isOpen={showImport}
        onClose={() => setShowImport(false)}
        onImport={handleImport}
      />

      <ExportDialog
        isOpen={showExport}
        onClose={() => setShowExport(false)}
        content={exportContent}
        promptTitle={selectedPrompt?.title}
      />
    </div>
  );
}
