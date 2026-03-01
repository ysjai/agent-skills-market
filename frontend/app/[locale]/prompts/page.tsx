'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { TopNav } from '@/components/layout/TopNav';
import { PromptList } from '@/components/prompts/PromptList';
import { PromptEditor } from '@/components/prompts/PromptEditor';
import { usePromptsStore } from '@/stores/promptsStore';
import { api } from '@/lib/api';
import type { PromptListResponse } from '@/types/prompt';

export default function PromptsPage() {
  const t = useTranslations('prompts');
  const tCommon = useTranslations('common');
  const [isMounted, setIsMounted] = useState(false);

  const {
    isLoading,
    setIsLoading,
    setErrorMessage,
    setPrompts,
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
      // Mock API call for now if real backend doesn't exist
      // Will try real API, fallback to empty array if it fails with 404
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
          <PromptList />
          <PromptEditor />
        </div>
      )}
    </div>
  );
}
