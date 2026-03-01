'use client';

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import Editor from '@monaco-editor/react';
import { Save, UploadCloud, LayoutTemplate, Loader2, History } from 'lucide-react';

import { usePromptsStore } from '@/stores/promptsStore';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { TagInput } from '@/components/prompts/TagInput';
import { VersionHistory } from '@/components/prompts/VersionHistory';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';
import type { Prompt, PromptVersion } from '@/types/prompt';


export function PromptEditor() {
  const t = useTranslations('prompts');
  const tCommon = useTranslations('common');
  
  const { selectedPrompt, updatePrompt, setSelectedPrompt } = usePromptsStore();
  
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [content, setContent] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);
  const [showVersionHistory, setShowVersionHistory] = useState(false);
  const [versions, setVersions] = useState<PromptVersion[]>([]);

  // Sync local state when selected prompt changes
  useEffect(() => {
    if (selectedPrompt) {
      setTitle(selectedPrompt.title || '');
      setDescription(selectedPrompt.description || '');
      setContent(selectedPrompt.content || '');
      setTags(selectedPrompt.tags || []);
      // Load versions when prompt changes
      loadVersions(selectedPrompt.id);
    } else {
      setTitle('');
      setDescription('');
      setContent('');
      setTags([]);
      setVersions([]);
      setShowVersionHistory(false);
    }
  }, [selectedPrompt]);

  const loadVersions = async (promptId: string) => {
    try {
      const data = await api.get<PromptVersion[]>(`/prompts/${promptId}/versions`);
      setVersions(data || []);
    } catch {
      setVersions([]);
    }
  };

  const handleSave = async () => {
    if (!selectedPrompt) return;
    setIsSaving(true);
    
    try {
      const updated = await api.put<Prompt>(`/prompts/${selectedPrompt.id}`, {
        title,
        description,
        content,
        tags,
      });
      updatePrompt(selectedPrompt.id, updated);
      setSelectedPrompt({ ...selectedPrompt, ...updated });
    } catch (err) {
      console.error('Failed to save prompt', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handlePublish = async () => {
    if (!selectedPrompt) return;
    setIsPublishing(true);
    
    try {
      // Save first if there are changes
      if (hasChanges) {
        const updated = await api.put<Prompt>(`/prompts/${selectedPrompt.id}`, {
          title,
          description,
          content,
          tags,
        });
        updatePrompt(selectedPrompt.id, updated);
        setSelectedPrompt({ ...selectedPrompt, ...updated });
      }
      
      // Publish version
      const version = await api.post<PromptVersion>(`/prompts/${selectedPrompt.id}/versions`);
      setVersions((prev) => [version, ...prev]);
      
      // Refresh the prompt to get updated version number
      const refreshed = await api.get<Prompt>(`/prompts/${selectedPrompt.id}`);
      updatePrompt(selectedPrompt.id, refreshed);
      setSelectedPrompt(refreshed);
    } catch (err) {
      console.error('Failed to publish version', err);
    } finally {
      setIsPublishing(false);
    }
  };

  const hasChanges = Boolean(selectedPrompt && (
    title !== selectedPrompt.title ||
    description !== (selectedPrompt.description || '') ||
    content !== selectedPrompt.content ||
    JSON.stringify(tags) !== JSON.stringify(selectedPrompt.tags)
  ));

  if (!selectedPrompt) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center bg-gray-50/50 text-center">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-white shadow-sm ring-1 ring-gray-100 mb-4">
          <LayoutTemplate className="h-8 w-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-1">{t('noPrompts')}</h3>
        <p className="text-sm text-gray-500 max-w-sm">
          {t('createFirst')}
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-1 h-full overflow-hidden">
      <div className="flex flex-1 flex-col h-full bg-white overflow-hidden">
        {/* Header Controls */}
        <div className="flex shrink-0 items-center justify-between border-b border-gray-100 px-6 py-4 bg-white/50 backdrop-blur-xl z-10">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold text-gray-900 tracking-tight">
              {tCommon('edit')} Prompt
            </h2>
            <span className="inline-flex items-center rounded-full bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10">
              {t('versionNumber', { number: selectedPrompt.version })}
            </span>
            {hasChanges && (
              <span className="text-xs font-medium text-amber-600 bg-amber-50 px-2 py-1 rounded-full">
                Unsaved changes
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              onClick={() => setShowVersionHistory(!showVersionHistory)}
              className="min-w-[100px]"
              title={t('versionHistory')}
            >
              <History className="h-4 w-4 mr-1.5" />
              {t('versionHistory')}
            </Button>
            <Button 
              variant="outline" 
              onClick={handleSave} 
              disabled={!hasChanges || isSaving || isPublishing}
              className="min-w-[100px]"
            >
              {isSaving ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Save className="h-4 w-4 mr-1.5" />
              )}
              {tCommon('save')}
            </Button>
            <Button 
              variant="default" 
              onClick={handlePublish}
              disabled={isSaving || isPublishing}
              className="bg-blue-600 hover:bg-blue-700 text-white min-w-[140px]"
            >
              {isPublishing ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <UploadCloud className="h-4 w-4 mr-1.5" />
              )}
              {t('publishVersion')}
            </Button>
          </div>
        </div>

        {/* Editor Content Scrollable */}
        <div className="flex-1 overflow-y-auto custom-scrollbar">
          <div className="mx-auto max-w-4xl p-6 space-y-8">
            
            {/* Metadata Section */}
            <div className="grid grid-cols-1 gap-6 md:grid-cols-[2fr_1fr]">
              <div className="space-y-4">
                <div className="space-y-1.5">
                  <label htmlFor="title" className="text-sm font-medium text-gray-700">
                    {tCommon('name')}
                  </label>
                  <Input
                    id="title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    maxLength={200}
                    placeholder={t('titlePlaceholder')}
                    className="text-lg font-medium h-12 shadow-sm"
                  />
                </div>

                <div className="space-y-1.5">
                  <label htmlFor="description" className="text-sm font-medium text-gray-700 flex justify-between">
                    <span>{tCommon('description')}</span>
                    <span className="text-xs text-gray-400 font-normal">{description.length}/1000</span>
                  </label>
                  <textarea
                    id="description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    maxLength={1000}
                    placeholder={t('descriptionPlaceholder')}
                    className={cn(
                      "flex w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-900 placeholder:text-gray-400 shadow-sm",
                      "focus:border-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-900/20 disabled:cursor-not-allowed disabled:opacity-50",
                      "min-h-[100px] resize-y"
                    )}
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-gray-700">
                  {t('tags')}
                </label>
                <div className="rounded-xl border border-gray-100 bg-gray-50/50 p-4">
                  <TagInput 
                    tags={tags} 
                    onChange={setTags} 
                  />
                </div>
              </div>
            </div>

            {/* Monaco Editor Section */}
            <div className="space-y-1.5 flex flex-col h-[500px] min-h-[400px]">
              <label className="text-sm font-medium text-gray-700 flex justify-between items-end">
                <span>{t('contentPlaceholder').split('\n')[0]}</span>
                <span className="text-xs text-gray-400 font-normal">Markdown supported</span>
              </label>
              <div className="flex-1 rounded-xl border border-gray-200 overflow-hidden shadow-sm ring-1 ring-black/5">
                <Editor
                  height="100%"
                  language="markdown"
                  value={content}
                  onChange={(val) => setContent(val || '')}
                  theme="light"
                  options={{
                    minimap: { enabled: false },
                    scrollBeyondLastLine: false,
                    wordWrap: 'on',
                    lineNumbers: 'on',
                    folding: true,
                    fontSize: 14,
                    fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
                    padding: { top: 16, bottom: 16 },
                    renderWhitespace: 'selection',
                  }}
                  loading={
                    <div className="flex h-full items-center justify-center bg-gray-50">
                      <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
                    </div>
                  }
                />
              </div>
            </div>
            
          </div>
        </div>
      </div>

      {/* Version History Panel */}
      {showVersionHistory && (
        <VersionHistory versions={versions} />
      )}
    </div>
  );
}
