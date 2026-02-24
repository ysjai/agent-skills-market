'use client';

import { Link } from '@/i18n/routing';
import { useTranslations } from 'next-intl';
import { Plus, Search, FolderUp, User as UserIcon, ChevronDown, LogOut } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { LanguageSwitcher } from '@/components/misc/LanguageSwitcher';
import type { User } from '@/types/user';

interface SkillsPageHeaderProps {
  user: User | null;
  skillsCount: number;
  searchQuery: string;
  onSearchChange: (value: string) => void;
  onCreateClick: () => void;
  onImportClick: () => void;
  isUserMenuOpen: boolean;
  onUserMenuToggle: () => void;
  onLogoutClick: () => void;
}

export function SkillsPageHeader({
  user,
  skillsCount,
  searchQuery,
  onSearchChange,
  onCreateClick,
  onImportClick,
  isUserMenuOpen,
  onUserMenuToggle,
  onLogoutClick,
}: SkillsPageHeaderProps) {
  const t = useTranslations('skills');
  const tAuth = useTranslations('auth');

  return (
    <header className="border-b border-gray-200 bg-white/80 backdrop-blur-sm px-4 py-4 sm:px-6 animate-fade-in-up">
      <div className="mx-auto flex max-w-7xl flex-col gap-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/" className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gray-900 text-white">
              <span className="text-xl">🎯</span>
            </Link>
            <div>
              <h1 className="text-lg font-bold text-gray-900 sm:text-xl">{t('title')}</h1>
              <p className="text-xs text-gray-500 sm:text-sm">{t('skillsCount', { count: skillsCount })}</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <LanguageSwitcher />
            <div className="relative user-menu-container">
              <button
                onClick={onUserMenuToggle}
                className="flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2"
              >
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100">
                  <UserIcon className="h-4 w-4 text-gray-600" />
                </div>
                <span className="hidden sm:inline">{user?.username || 'User'}</span>
                <ChevronDown className="h-4 w-4 text-gray-400" />
              </button>

              {isUserMenuOpen && (
                <div className="absolute right-0 top-12 z-10 w-48 rounded-lg border border-gray-200 bg-white py-1 shadow-lg">
                  <button
                    onClick={onLogoutClick}
                    className="flex w-full min-h-[44px] items-center gap-2 px-3 py-2 text-left text-sm text-red-600 hover:bg-red-50"
                  >
                    <LogOut className="h-4 w-4" />
                    {tAuth('signOut')}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

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
    </header>
  );
}
