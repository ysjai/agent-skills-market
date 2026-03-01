'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { User as UserIcon, ChevronDown, LogOut, BookOpen, Layers } from 'lucide-react';
import { LanguageSwitcher } from '@/components/misc/LanguageSwitcher';
import type { User } from '@/types/user';

interface AppHeaderProps {
  user: User | null;
  isUserMenuOpen: boolean;
  onUserMenuToggle: () => void;
  onLogoutClick: () => void;
}

export function AppHeader({ user, isUserMenuOpen, onUserMenuToggle, onLogoutClick }: AppHeaderProps) {
  const t = useTranslations('nav');
  const tAuth = useTranslations('auth');
  const pathname = usePathname();

  // Detect locale and current page from pathname like /en/skills or /zh/prompts
  const parts = pathname.split('/').filter(Boolean);
  const locale = parts[0] || 'en';

  return (
    <header className="shrink-0 border-b border-gray-200 bg-white">
      <div className="px-4 sm:px-6">
        <div className="flex h-14 items-center justify-between gap-8">
          {/* Left: Logo */}
          <Link href={`/${locale}/skills`} className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gray-900 text-white">
            <span className="text-base">🎯</span>
          </Link>

          {/* Right: Language + User Menu */}
          <div className="flex items-center gap-2">
            <LanguageSwitcher />
            <div className="relative user-menu-container">
              <button
                onClick={onUserMenuToggle}
                className="flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2"
              >
                <div className="flex h-7 w-7 items-center justify-center rounded-full bg-gray-100">
                  <UserIcon className="h-3.5 w-3.5 text-gray-600" />
                </div>
                <span className="hidden sm:inline">{user?.username || 'User'}</span>
                <ChevronDown className="h-4 w-4 text-gray-400" />
              </button>

              {isUserMenuOpen && (
                <div className="absolute right-0 top-12 z-50 w-48 rounded-lg border border-gray-200 bg-white py-1 shadow-lg">
                  <Link
                    href={`/${locale}/skills`}
                    className="flex w-full min-h-[44px] items-center gap-2 px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50"
                  >
                    <Layers className="h-4 w-4 text-gray-500" />
                    {t('skills')}
                  </Link>
                  <Link
                    href={`/${locale}/prompts`}
                    className="flex w-full min-h-[44px] items-center gap-2 px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50"
                  >
                    <BookOpen className="h-4 w-4 text-gray-500" />
                    {t('prompts')}
                  </Link>
                  <div className="my-1 border-t border-gray-100" />
                  <button
                    onClick={onLogoutClick}
                    className="flex w-full min-h-[44px] items-center gap-2 px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50"
                  >
                    <LogOut className="h-4 w-4 text-gray-500" />
                    {tAuth('signOut')}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
