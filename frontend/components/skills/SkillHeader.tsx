'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from '@/i18n/routing';
import { useTranslations } from 'next-intl';
import { ArrowLeft, Download, Trash2, Menu, User as UserIcon, ChevronDown, LogOut, Layers, BookOpen } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { LanguageSwitcher } from '@/components/misc/LanguageSwitcher';
import { getCurrentUser } from '@/app/api/auth';
import type { Skill } from '@/types/skill';
import type { User } from '@/types/user';

interface SkillHeaderProps {
  skill: Skill;
  isUserMenuOpen: boolean;
  onNavigate?: (path: string, options?: { locale?: string }) => void;
  onDownload: () => void;
  onDelete: () => void;
  onToggleSidebar: () => void;
  onUserMenuToggle: () => void;
}

export function SkillHeader({
  skill,
  isUserMenuOpen,
  onNavigate,
  onDownload,
  onDelete,
  onToggleSidebar,
  onUserMenuToggle,
}: SkillHeaderProps) {
  const t = useTranslations('skills');
  const tNav = useTranslations('nav');
  const tCommon = useTranslations('common');
  const tAuth = useTranslations('auth');
  const router = useRouter();

  const headerDescRef = useRef<HTMLParagraphElement>(null);
  const [isHeaderDescTruncated, setIsHeaderDescTruncated] = useState(false);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const checkTruncation = () => {
      if (headerDescRef.current) {
        setIsHeaderDescTruncated(
          headerDescRef.current.scrollWidth > headerDescRef.current.clientWidth
        );
      }
    };
    checkTruncation();
    window.addEventListener('resize', checkTruncation);
    return () => window.removeEventListener('resize', checkTruncation);
  }, [skill.description]);

  useEffect(() => {
    const loadUser = async () => {
      try {
        const userData = await getCurrentUser();
        setUser(userData);
      } catch {
        // Silently ignore user load errors
      }
    };
    loadUser();
  }, []);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (isUserMenuOpen && !target.closest('.user-menu-container')) {
        onUserMenuToggle();
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isUserMenuOpen, onUserMenuToggle]);

  return (
    <header className="border-b border-gray-200 bg-white/80 backdrop-blur-sm px-4 py-3 animate-fade-in-up relative z-[60]">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex min-w-0 flex-1 items-center gap-2 md:gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onNavigate ? onNavigate('/skills') : router.push('/skills')}
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg"
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-1.5 md:gap-2">
              <h1 className="truncate text-base font-semibold text-gray-900 md:text-lg">{skill.name}</h1>
              <span className="shrink-0 rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">
                v{skill.version}
              </span>
              {skill.is_public && (
                <span className="hidden shrink-0 rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 md:inline">
                  {t('public')}
                </span>
              )}
            </div>
            <div className="group relative hidden md:block">
              <p
                ref={headerDescRef}
                className="truncate text-sm text-gray-500 max-w-[600px]"
              >
                {skill.description || tCommon('description')}
              </p>
              {skill.description && isHeaderDescTruncated && (
                <div className="absolute top-full left-0 mt-2 z-[100] max-w-lg bg-gray-900 text-white text-sm rounded-lg px-3 py-2 shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                  {skill.description}
                  <div className="absolute -top-1 left-4 w-2 h-2 bg-gray-900 rotate-45"></div>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <LanguageSwitcher onNavigate={onNavigate} />

          <div className="hidden md:block h-5 w-px bg-gray-200 mx-1"></div>

          <div className="flex items-center gap-1.5">
            <Button
              variant="outline"
              size="sm"
              onClick={onDownload}
              className="btn-interactive h-9"
            >
              <Download className="h-4 w-4" />
              <span className="hidden md:inline ml-1.5">{tCommon('download')}</span>
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={onDelete}
              className="btn-interactive h-9 hover:text-red-600 hover:border-red-600 hover:bg-red-50"
            >
              <Trash2 className="h-4 w-4" />
              <span className="hidden md:inline ml-1.5">{tCommon('delete')}</span>
            </Button>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={onToggleSidebar}
            className="h-9 w-9 lg:hidden"
          >
            <Menu className="h-4 w-4" />
          </Button>

          <div className="hidden md:block h-5 w-px bg-gray-200 mx-1"></div>

          <div className="relative user-menu-container">
            <button
              onClick={onUserMenuToggle}
              className="flex items-center gap-2 h-9 rounded-md border border-input bg-background px-3 text-sm font-medium text-gray-700 hover:bg-accent hover:text-accent-foreground transition-colors"
            >
              <UserIcon className="h-4 w-4 text-gray-500" />
              <span className="hidden md:inline">{user?.username || 'User'}</span>
              <ChevronDown className="h-4 w-4 text-gray-400" />
            </button>

            {isUserMenuOpen && (
              <div className="absolute right-0 top-10 z-50 w-48 rounded-md border border-gray-200 bg-white py-1 shadow-lg">
                <button
                  onClick={() => {
                    onUserMenuToggle();
                    if (onNavigate) onNavigate('/skills'); else router.push('/skills');
                  }}
                  className="flex w-full min-h-[40px] items-center gap-2 px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50"
                >
                  <Layers className="h-4 w-4 text-gray-500" />
                  {tNav('skills')}
                </button>
                <button
                  onClick={() => {
                    onUserMenuToggle();
                    if (onNavigate) onNavigate('/prompts'); else router.push('/prompts');
                  }}
                  className="flex w-full min-h-[40px] items-center gap-2 px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50"
                >
                  <BookOpen className="h-4 w-4 text-gray-500" />
                  {tNav('prompts')}
                </button>
                <div className="my-1 border-t border-gray-100" />
                <button
                  onClick={() => {
                    onUserMenuToggle();
                    if (onNavigate) {
                      onNavigate('/login', {});
                    } else {
                      router.push('/login');
                    }
                  }}
                  className="flex w-full min-h-[40px] items-center gap-2 px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50"
                >
                  <LogOut className="h-4 w-4 text-gray-500" />
                  {tAuth('signOut')}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
