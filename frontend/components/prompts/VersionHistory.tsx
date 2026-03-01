'use client';

import React from 'react';
import { useTranslations } from 'next-intl';
import { History, Clock, LayoutTemplate, Eye } from 'lucide-react';

import { cn } from '@/lib/utils';
import { PromptVersion } from '@/types/prompt';

export interface VersionHistoryProps {
  versions: PromptVersion[];
  onPreview: (version: PromptVersion) => void;
}

export function VersionHistory({ versions, onPreview }: VersionHistoryProps) {
  const t = useTranslations('prompts');

  return (
    <div className="w-72 shrink-0 border-l border-gray-200 bg-white flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="flex shrink-0 items-center gap-2 p-4 pb-3 border-b border-gray-100">
        <History className="h-4 w-4 text-gray-500" />
        <h2 className="text-sm font-semibold tracking-tight text-gray-900">{t('versionHistory')}</h2>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto px-2 py-3 space-y-1 custom-scrollbar">
        {versions.length === 0 ? (
          <div className="flex h-32 flex-col items-center justify-center text-center px-4 mt-8">
            <LayoutTemplate className="h-8 w-8 text-gray-300 mb-2" />
            <p className="text-sm text-gray-500">{t('noVersions')}</p>
          </div>
        ) : (
          versions.map((version) => {
            const dateObj = new Date(version.created_at);
            const dateStr = `${dateObj.toLocaleDateString()} ${dateObj.toLocaleTimeString()}`;

            return (
              <div
                key={version.id}
                className="group flex items-center justify-between gap-2 rounded-xl border border-transparent px-3 py-2.5 hover:bg-gray-50 hover:border-gray-200 transition-all duration-150"
              >
                {/* Left: version info */}
                <div className="flex flex-col gap-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="inline-flex shrink-0 items-center justify-center rounded-full bg-gray-900 px-2 py-0.5 text-[10px] font-bold tracking-wide text-white shadow-sm">
                      {t('versionNumber', { number: version.version_number })}
                    </span>
                    <span className="truncate text-sm font-medium text-gray-800" title={version.title || t('untitled')}>
                      {version.title || t('untitled')}
                    </span>
                  </div>
                  <div className="flex items-center gap-1 text-gray-400">
                    <Clock className="h-3 w-3 shrink-0" />
                    <span className="text-[10px] font-medium tracking-wide">{dateStr}</span>
                  </div>
                </div>

                {/* Right: preview button */}
                <button
                  type="button"
                  onClick={() => onPreview(version)}
                  className={cn(
                    "shrink-0 flex items-center gap-1 rounded-lg border border-gray-200 bg-white px-2 py-1",
                    "text-xs font-medium text-gray-600 hover:bg-gray-900 hover:text-white hover:border-gray-900",
                    "transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-1"
                  )}
                >
                  <Eye className="h-3 w-3" />
                  {t('preview')}
                </button>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
