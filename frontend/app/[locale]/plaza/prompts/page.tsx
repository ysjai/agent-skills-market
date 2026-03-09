'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from '@/i18n/routing';
import { Link } from '@/i18n/routing';
import { useTranslations } from 'next-intl';
import { ChevronLeft, ChevronRight, BookOpen } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Dialog } from '@/components/ui/Dialog';
import { AppHeader } from '@/components/layout/AppHeader';
import { MarketPromptCard } from '@/components/market/MarketPromptCard';
import { MarketPageStates } from '@/components/market/MarketPageStates';
import { api } from '@/lib/api';
import { useMarketPromptStore } from '@/stores/marketPromptStore';
import { useToast } from '@/components/ui/Toast';
import { logout, getCurrentUser } from '@/app/api/auth';
import type { User } from '@/types/user';

export default function PromptPlazaPage() {
  const t = useTranslations('market');
  const tCommon = useTranslations('common');
  const tAuth = useTranslations('auth');
  const tNav = useTranslations('nav');
  const router = useRouter();
  const { showToast } = useToast();

  const {
    prompts: marketPrompts,
    total: promptTotal,
    isLoading: promptsLoading,
    error: promptsError,
    filters: promptFilters,
    setPrompts: setMarketPrompts,
    setFilters: setPromptFilters,
    loadMarketPrompts,
    toggleLikeOptimistic: togglePromptLikeOptimistic,
    toggleFavoriteOptimistic: togglePromptFavoriteOptimistic,
  } = useMarketPromptStore();

  const [user, setUser] = useState<User | null>(null);
  const [localPromptSearch, setLocalPromptSearch] = useState(promptFilters.keyword || '');
  const [isLogoutDialogOpen, setIsLogoutDialogOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    const bootstrap = async () => {
      if (!api.isAuthenticated()) {
        setUser(null);
        return;
      }
      try {
        const userData = await getCurrentUser();
        setUser(userData);
      } catch {
        setUser(null);
      }
    };
    void bootstrap();
    const timer = setTimeout(() => setIsMounted(true), 50);
    return () => clearTimeout(timer);
  }, []);

  // Debounce prompt search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (localPromptSearch !== promptFilters.keyword) {
        setPromptFilters({ keyword: localPromptSearch, skip: 0 });
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [localPromptSearch, promptFilters.keyword, setPromptFilters]);

  // Fetch prompts when filters change
  useEffect(() => {
    void loadMarketPrompts();
  }, [promptFilters]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest('.user-menu-container')) {
        setIsUserMenuOpen(false);
      }
    };
    if (isUserMenuOpen) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [isUserMenuOpen]);

  const handleLogout = () => {
    logout();
  };

  const handlePromptNavigate = useCallback((promptId: string) => {
    router.push(`/plaza/prompts/${promptId}`);
  }, [router]);

  const handlePromptLike = async (promptId: string) => {
    if (!user) {
      showToast(t('login_to_like'), 'warning');
      router.push('/login');
      return;
    }

    const promptIndex = marketPrompts.findIndex(p => p.id === promptId);
    if (promptIndex === -1) return;

    const prompt = marketPrompts[promptIndex];
    const wasLiked = prompt.is_liked;
    const previousPrompts = marketPrompts;
    togglePromptLikeOptimistic(promptId);

    try {
      if (wasLiked) {
        await api.unlikeSharedPrompt(promptId);
      } else {
        await api.likeSharedPrompt(promptId);
      }
    } catch {
      setMarketPrompts(previousPrompts);
      showToast(tCommon('failed'), 'error');
    }
  };

  const handlePromptPageChange = (newSkip: number) => {
    setPromptFilters({ skip: newSkip });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handlePromptFavorite = async (promptId: string) => {
    if (!user) {
      showToast(t('login_to_like'), 'warning');
      router.push('/login');
      return;
    }

    const promptIndex = marketPrompts.findIndex(p => p.id === promptId);
    if (promptIndex === -1) return;

    const prompt = marketPrompts[promptIndex];
    const wasFavorited = prompt.is_favorited;
    const previousPrompts = marketPrompts;
    togglePromptFavoriteOptimistic(promptId);

    try {
      if (wasFavorited) {
        await api.unfavoriteSharedPrompt(promptId);
      } else {
        await api.favoriteSharedPrompt(promptId);
      }
    } catch {
      setMarketPrompts(previousPrompts);
      showToast(tCommon('failed'), 'error');
    }
  };

  const promptLimit = promptFilters.limit || 20;
  const promptSkip = promptFilters.skip || 0;
  const promptPage = Math.floor(promptSkip / promptLimit) + 1;
  const promptTotalPages = Math.max(1, Math.ceil(promptTotal / promptLimit));

  return (
    <div className={`flex min-h-screen flex-col bg-slate-50 transition-opacity duration-500 ${isMounted ? 'opacity-100' : 'opacity-0'}`}>
      <AppHeader
        user={user}
        isUserMenuOpen={isUserMenuOpen}
        onUserMenuToggle={() => setIsUserMenuOpen(!isUserMenuOpen)}
        onLogoutClick={() => setIsLogoutDialogOpen(true)}
      />

      <div className="bg-white border-b border-gray-200 py-8 px-4 sm:px-6">
        <div className="mx-auto max-w-7xl">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3">
              <div className="bg-purple-100 p-2 rounded-lg">
                <BookOpen className="h-6 w-6 text-purple-600" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">{tNav('prompt_plaza')}</h1>
            </div>
            <Link
              href="/prompts"
              className="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <BookOpen className="h-4 w-4 text-gray-500" />
              {tNav('my_prompts')}
            </Link>
          </div>
          <p className="text-gray-500 mt-1">{t('prompt_plaza_subtitle')}</p>
        </div>
      </div>

      <main className="flex-1 p-4 sm:p-6">
        <div className="mx-auto max-w-7xl">
          {/* Search for prompts */}
          <div className="mb-6">
            <div className="flex gap-3">
              <div className="relative flex-1">
                <input
                  type="text"
                  placeholder={t('search_prompts_placeholder')}
                  value={localPromptSearch}
                  onChange={(e) => setLocalPromptSearch(e.target.value)}
                  className="w-full rounded-lg border border-gray-200 bg-white px-4 py-2.5 pl-10 text-sm text-gray-900 placeholder-gray-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
                <svg className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
              </div>
              <select
                value={promptFilters.sort_by || 'newest'}
                onChange={(e) => setPromptFilters({ sort_by: e.target.value as 'newest' | 'popular', skip: 0 })}
                className="rounded-lg border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-700 focus:border-indigo-500 focus:outline-none"
              >
                <option value="newest">{t('sort_newest')}</option>
                <option value="popular">{t('sort_popular')}</option>
              </select>
            </div>
          </div>

          <MarketPageStates
            isLoading={promptsLoading}
            error={promptsError}
            isEmpty={!promptsLoading && !promptsError && marketPrompts.length === 0}
            onRetry={() => void loadMarketPrompts()}
          />

          {!promptsLoading && !promptsError && marketPrompts.length > 0 && (
            <>
              <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 animate-fade-in-scale items-stretch">
                {marketPrompts.map((prompt) => (
                  <MarketPromptCard
                    key={prompt.id}
                    prompt={prompt}
                    onLike={handlePromptLike}
                    isLiked={prompt.is_liked}
                    onFavorite={handlePromptFavorite}
                    isFavorited={prompt.is_favorited}
                    onNavigate={handlePromptNavigate}
                  />
                ))}
              </div>

              {/* Pagination */}
              {promptTotal > 0 && (
                <div className="mt-10 flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-gray-200 pt-6">
                  <div className="text-sm text-gray-500">
                    <span className="font-medium text-gray-900">{Math.min(promptSkip + 1, promptTotal)}</span>
                    {' - '}
                    <span className="font-medium text-gray-900">{Math.min(promptSkip + promptLimit, promptTotal)}</span>
                    {' / '}
                    <span className="font-medium text-gray-900">{promptTotal}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      onClick={() => handlePromptPageChange(Math.max(0, promptSkip - promptLimit))}
                      disabled={promptPage <= 1}
                      className="h-9 px-3"
                    >
                      <ChevronLeft className="h-4 w-4 sm:mr-1" />
                      <span className="hidden sm:inline">{t('prev')}</span>
                    </Button>
                    <div className="text-sm font-medium px-4 text-gray-700 bg-white border border-gray-200 h-9 flex items-center rounded-md shadow-sm">
                      {promptPage} / {promptTotalPages}
                    </div>
                    <Button
                      variant="outline"
                      onClick={() => handlePromptPageChange(promptSkip + promptLimit)}
                      disabled={promptPage >= promptTotalPages}
                      className="h-9 px-3"
                    >
                      <span className="hidden sm:inline">{t('next')}</span>
                      <ChevronRight className="h-4 w-4 sm:ml-1" />
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </main>

      <Dialog
        open={isLogoutDialogOpen}
        onClose={() => setIsLogoutDialogOpen(false)}
        title={tAuth('signOut')}
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600 sm:text-base">
            {tAuth('logoutConfirm')}
          </p>
          <div className="flex flex-col gap-2 sm:flex-row sm:gap-3">
            <Button
              variant="outline"
              className="min-h-[44px] flex-1"
              onClick={() => setIsLogoutDialogOpen(false)}
            >
              {tCommon('cancel')}
            </Button>
            <Button
              variant="default"
              className="min-h-[44px] flex-1 bg-gray-900 hover:bg-gray-800 text-white"
              onClick={handleLogout}
            >
              {tAuth('signOut')}
            </Button>
          </div>
        </div>
      </Dialog>
    </div>
  );
}
