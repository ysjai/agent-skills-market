'use client';

import React, { useState } from 'react';
import { useTranslations } from 'next-intl';
import { History, ChevronDown, ChevronUp, Clock, FileText, LayoutTemplate } from 'lucide-react';

import { cn } from '@/lib/utils';
import { PromptVersion } from '@/types/prompt';

export interface VersionHistoryProps {
  versions: PromptVersion[];
}

export function VersionHistory({ versions }: VersionHistoryProps) {
  const t = useTranslations('prompts');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const toggleExpand = (id: string) => {
    setExpandedId((prev) => (prev === id ? null : id));
  };

  return (
    <div className="w-72 shrink-0 border-l border-gray-200 bg-white flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="flex shrink-0 items-center gap-2 p-4 pb-3 border-b border-gray-100">
        <History className="h-4 w-4 text-gray-500" />
        <h2 className="text-sm font-semibold tracking-tight text-gray-900">{t('versionHistory')}</h2>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto px-2 py-3 space-y-2 custom-scrollbar">
        {versions.length === 0 ? (
          <div className="flex h-32 flex-col items-center justify-center text-center px-4 mt-8">
            <LayoutTemplate className="h-8 w-8 text-gray-300 mb-2" />
            <p className="text-sm text-gray-500">{t('noVersions')}</p>
          </div>
        ) : (
          versions.map((version) => {
            const isExpanded = expandedId === version.id;
            const dateObj = new Date(version.created_at);
            const dateStr = `${dateObj.toLocaleDateString()} ${dateObj.toLocaleTimeString()}`;

            return (
              <div
                key={version.id}
                className={cn(
                  "group flex flex-col rounded-xl transition-all duration-200 overflow-hidden",
                  isExpanded 
                    ? "bg-gray-50 border border-gray-200 shadow-sm" 
                    : "bg-transparent border border-transparent hover:bg-gray-50 hover:border-gray-200"
                )}
              >
                {/* Row Header */}
                <button
                  type="button"
                  onClick={() => toggleExpand(version.id)}
                  className="flex w-full items-start justify-between gap-2 p-3 text-left focus:outline-none"
                >
                  <div className="flex flex-col gap-1.5 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="inline-flex shrink-0 items-center justify-center rounded-full bg-gray-900 px-2 py-0.5 text-[10px] font-bold tracking-wide text-white shadow-sm">
                        {t('versionNumber', { number: version.version_number })}
                      </span>
                      <span className="truncate text-sm font-semibold text-gray-900" title={version.title || t('untitled')}>
                        {version.title || t('untitled')}
                      </span>
                    </div>
                    <div className="flex items-center gap-1 text-gray-500">
                      <Clock className="h-3 w-3 shrink-0" />
                      <span className="text-[10px] font-medium tracking-wide">{dateStr}</span>
                    </div>
                  </div>
                  <div className="shrink-0 pt-0.5 text-gray-400 group-hover:text-gray-600">
                    {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                  </div>
                </button>

                {/* Expanded Content */}
                {isExpanded && (
                  <div className="px-3 pb-3">
                    <div className="flex flex-col gap-3 rounded-lg border border-gray-200/50 bg-white p-3 shadow-sm ring-1 ring-black/5">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5">
                          <FileText className="h-3.5 w-3.5 text-gray-400" />
                          <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">
                            Content
                          </span>
                        </div>
                        <span className="inline-flex rounded bg-blue-50 px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wider text-blue-600 ring-1 ring-inset ring-blue-700/10">
                          Read Only
                        </span>
                      </div>
                      
                      <div className="max-h-48 overflow-y-auto rounded-md bg-gray-50 p-2.5 custom-scrollbar border border-gray-100">
                        <pre className="whitespace-pre-wrap text-[11px] font-mono leading-relaxed text-gray-700">
                          {version.content || <span className="text-gray-400 italic">Empty content</span>}
                        </pre>
                      </div>

                      {version.tags && version.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 pt-1 border-t border-gray-100">
                          {version.tags.map((tag) => (
                            <span
                              key={tag}
                              className="inline-flex items-center rounded text-[10px] font-medium bg-gray-100 text-gray-600 px-1.5 py-0.5"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
