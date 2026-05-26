'use client';

import { useTranslations } from 'next-intl';
import { Plus, Search, FolderUp } from 'lucide-react';

import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

interface SkillsPageHeaderProps {
  searchQuery: string;
  onSearchChange: (value: string) => void;
  onCreateClick: () => void;
  onImportClick: () => void;
}

export function SkillsPageHeader({
  searchQuery,
  onSearchChange,
  onCreateClick,
  onImportClick,
}: SkillsPageHeaderProps) {
  const t = useTranslations('skills');

  return (
    <div className="border-b border-gray-200 bg-white/80 backdrop-blur-sm px-4 py-4 sm:px-6 animate-fade-in-up">
      <div className="mx-auto max-w-7xl">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <Input
              placeholder={t('searchPlaceholder')}
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              className="w-full pl-9"
            />
          </div>
          <div className="flex items-center gap-2">
            <Button
              onClick={onImportClick}
              className="btn-interactive flex items-center justify-center gap-2"
            >
              <FolderUp className="h-4 w-4" />
              {t('importSkill')}
            </Button>
            <Button
              variant="outline"
              onClick={onCreateClick}
              className="btn-interactive flex items-center justify-center gap-2"
            >
              <Plus className="h-4 w-4" />
              <span className="hidden sm:inline">{t('newSkill')}</span>
              <span className="sm:hidden">New</span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
