'use client';

import { useTranslations } from 'next-intl';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { cn } from '@/lib/utils';

export function TopNav() {
  const t = useTranslations('nav');
  const pathname = usePathname();

  // Extract locale and current path from pathname
  // pathname format: /en/skills or /en/prompts, etc.
  const parts = pathname.split('/').filter(Boolean);
  const locale = parts[0] || 'en';
  const currentPage = parts[1] || '';

  const isSkillsActive = currentPage === 'skills';
  const isPromptsActive = currentPage === 'prompts';

  return (
    <nav
      className="border-b border-gray-200 bg-white"
      data-testid="top-nav"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-14 items-center justify-between gap-8">
          {/* Navigation Links */}
          <div className="flex gap-1">
            <Link
              href={`/${locale}/skills`}
              className={cn(
                'flex h-14 items-center px-4 text-sm font-medium transition-colors border-b-2',
                isSkillsActive
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              )}
            >
              {t('skills')}
            </Link>
            <Link
              href={`/${locale}/prompts`}
              className={cn(
                'flex h-14 items-center px-4 text-sm font-medium transition-colors border-b-2',
                isPromptsActive
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              )}
            >
              {t('prompts')}
            </Link>
          </div>

          {/* Right side spacer - reserved for user menu/auth */}
          <div className="flex-1" />
        </div>
      </div>
    </nav>
  );
}
