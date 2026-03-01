'use client';

import React, { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Search, Plus, LayoutTemplate, Trash2, Download, Upload } from 'lucide-react';
import { usePromptsStore } from '@/stores/promptsStore';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';
import type { Prompt } from '@/types/prompt';

interface PromptListProps {
  onImportClick?: () => void;
  onExportClick?: (promptId: string) => void;
  onDeleteClick?: (promptId: string) => void;
}

export function PromptList({ onImportClick, onExportClick, onDeleteClick }: PromptListProps) {
  const t = useTranslations('prompts');
  const [isCreating, setIsCreating] = useState(false);

  const {
    selectedPrompt,
    searchQuery,
    setSearchQuery,
    setSelectedPrompt,
    addPrompt,
    getFilteredPrompts
  } = usePromptsStore();

  const filteredPrompts = getFilteredPrompts();

  const handleNewPrompt = async () => {
    if (isCreating) return;
    setIsCreating(true);
    try {
      const newPrompt = await api.post<Prompt>('/prompts', {
        title: 'Untitled Prompt',
        content: '',
        description: '',
        tags: [],
      });
      addPrompt(newPrompt);
      setSelectedPrompt(newPrompt);
    } catch (err) {
      console.error('Failed to create prompt', err);
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="flex h-full w-[320px] flex-col border-r border-gray-100 bg-white shadow-sm shrink-0">
      {/* Header */}
      <div className="flex items-center justify-between p-4 pb-2">
        <h2 className="text-lg font-bold tracking-tight text-gray-900">{t('title')}</h2>
        <div className="flex items-center gap-1">
          {onImportClick && (
            <Button size="icon" variant="ghost" className="h-8 w-8 rounded-full bg-gray-50 text-gray-600 hover:bg-gray-100 hover:text-gray-900" title={t('importPrompt')} onClick={onImportClick}>
              <Upload className="h-4 w-4" />
            </Button>
          )}
          <Button size="icon" variant="ghost" className="h-8 w-8 rounded-full bg-gray-50 text-gray-600 hover:bg-gray-100 hover:text-gray-900" title={t('newPrompt')} onClick={handleNewPrompt} disabled={isCreating}>
            <Plus className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="px-4 pb-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            className="h-9 w-full bg-gray-50 pl-9 border-none shadow-none ring-1 ring-inset ring-gray-200 focus:ring-2 focus:ring-inset focus:ring-gray-900 text-sm rounded-full transition-all"
            placeholder={t('searchPlaceholder')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto px-2 pb-4 space-y-1">
        {filteredPrompts.length === 0 ? (
          <div className="flex h-32 flex-col items-center justify-center text-center px-4">
            <LayoutTemplate className="h-8 w-8 text-gray-300 mb-2" />
            <p className="text-sm text-gray-500">{searchQuery ? t('noPromptsFound') : t('noPrompts')}</p>
          </div>
        ) : (
          filteredPrompts.map((prompt) => (
            <button
              key={prompt.id}
              onClick={() => setSelectedPrompt(prompt)}
              className={cn(
                "w-full group flex flex-col items-start gap-1.5 rounded-xl p-3 text-left transition-all duration-200 border border-transparent",
                selectedPrompt?.id === prompt.id
                  ? "bg-gray-900 shadow-sm text-white border-gray-800"
                  : "bg-transparent text-gray-700 hover:bg-gray-50 hover:border-gray-200"
              )}
            >
              <div className="flex w-full items-start justify-between gap-2">
                <span className={cn("font-semibold truncate text-sm",
                  selectedPrompt?.id === prompt.id ? "text-white" : "text-gray-900"
                )}>
                  {prompt.title || 'Untitled Prompt'}
                </span>
                <div className="flex items-center gap-1 shrink-0">
                  {selectedPrompt?.id === prompt.id && (
                    <>
                      {onExportClick && (
                        <span
                          role="button"
                          tabIndex={0}
                          onClick={(e) => { e.stopPropagation(); onExportClick(prompt.id); }}
                          onKeyDown={(e) => { if (e.key === 'Enter') { e.stopPropagation(); onExportClick(prompt.id); } }}
                          className="p-0.5 rounded hover:bg-white/20 text-white/70 hover:text-white cursor-pointer"
                          title="Export"
                        >
                          <Download className="h-3.5 w-3.5" />
                        </span>
                      )}
                      {onDeleteClick && (
                        <span
                          role="button"
                          tabIndex={0}
                          onClick={(e) => { e.stopPropagation(); onDeleteClick(prompt.id); }}
                          onKeyDown={(e) => { if (e.key === 'Enter') { e.stopPropagation(); onDeleteClick(prompt.id); } }}
                          className="p-0.5 rounded hover:bg-red-500/20 text-white/70 hover:text-red-300 cursor-pointer"
                          title="Delete"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </span>
                      )}
                    </>
                  )}
                  <span className={cn(
                    "shrink-0 rounded-full px-2 py-0.5 text-[10px] font-medium tracking-wide shadow-sm",
                    selectedPrompt?.id === prompt.id
                      ? "bg-white/20 text-white"
                      : "bg-gray-100 text-gray-600 border border-gray-200/50"
                  )}>
                    v{prompt.version}
                  </span>
                </div>
              </div>

              {/* Tags inline */}
              {prompt.tags && prompt.tags.length > 0 && (
                <div className="flex w-full flex-wrap gap-1 mt-1">
                  {prompt.tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className={cn(
                        "inline-flex items-center rounded text-[10px] font-medium px-1.5 py-0.5",
                        selectedPrompt?.id === prompt.id
                          ? "bg-white/10 text-white/90"
                          : "bg-gray-100 text-gray-500"
                      )}
                    >
                      {tag}
                    </span>
                  ))}
                  {prompt.tags.length > 3 && (
                    <span className={cn(
                      "inline-flex items-center rounded text-[10px] font-medium px-1.5 py-0.5",
                      selectedPrompt?.id === prompt.id
                        ? "text-white/70"
                        : "text-gray-400"
                    )}>
                      +{prompt.tags.length - 3}
                    </span>
                  )}
                </div>
              )}
            </button>
          ))
        )}
      </div>
    </div>
  );
}
