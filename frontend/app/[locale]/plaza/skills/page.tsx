'use client';

import { useState, useEffect, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { ChevronLeft, ChevronRight, Rocket } from 'lucide-react';

import { useRouter } from '@/i18n/routing';
import { Button } from '@/components/ui/Button';
import { Dialog } from '@/components/ui/Dialog';
import { AppHeader } from '@/components/layout/AppHeader';
import { MarketSkillCard } from '@/components/market/MarketSkillCard';
import { MarketFilters } from '@/components/market/MarketFilters';
import { MarketPageStates } from '@/components/market/MarketPageStates';
import { api } from '@/lib/api';
import { useMarketStore } from '@/stores/marketStore';
import { useToast } from '@/components/ui/Toast';
import { logout, getCurrentUser } from '@/app/api/auth';
import type { User } from '@/types/user';

export default function SkillPlazaPage() {
  const t = useTranslations('market');
  const tCommon = useTranslations('common');
  const tAuth = useTranslations('auth');
  const tNav = useTranslations('nav');
  const router = useRouter();
  const { showToast } = useToast();

  const {
    skills,
    total,
    categories,
    isLoading,
    error,
    filters,
    setSkills,
    setFilters,
    loadMarketSkills,
    loadCategories,
    toggleLikeOptimistic,
    toggleFavoriteOptimistic,
  } = useMarketStore();

  const [user, setUser] = useState<User | null>(null);
  const [localSearch, setLocalSearch] = useState(filters.keyword || '');
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
    void loadCategories();
    const timer = setTimeout(() => setIsMounted(true), 50);
    return () => clearTimeout(timer);
  }, [loadCategories]);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (localSearch !== filters.keyword) {
        setFilters({ keyword: localSearch, skip: 0 });
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [localSearch, filters.keyword, setFilters]);

  // Fetch skills when filters change
  useEffect(() => {
    void loadMarketSkills();
  }, [filters, loadMarketSkills]);

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

  const handleNavigate = useCallback((skillId: string) => {
    router.push(`/plaza/skills/${skillId}`);
  }, [router]);

  const handleLike = async (skillId: string) => {
    if (!user) {
      showToast(t('login_to_like'), 'warning');
      router.push('/login');
      return;
    }

    const skillIndex = skills.findIndex(s => s.id === skillId);
    if (skillIndex === -1) return;

    const skill = skills[skillIndex];
    const wasLiked = skill.is_liked;
    const previousSkills = skills;
    toggleLikeOptimistic(skillId);

    try {
      if (wasLiked) {
        await api.unlikeSharedSkill(skillId);
      } else {
        await api.likeSharedSkill(skillId);
      }
    } catch {
      setSkills(previousSkills);
      showToast(tCommon('failed'), 'error');
    }
  };

  const handlePageChange = (newSkip: number) => {
    setFilters({ skip: newSkip });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleFavorite = async (skillId: string) => {
    if (!user) {
      showToast(t('login_to_like'), 'warning');
      router.push('/login');
      return;
    }

    const skillIndex = skills.findIndex(s => s.id === skillId);
    if (skillIndex === -1) return;

    const skill = skills[skillIndex];
    const wasFavorited = skill.is_favorited;
    const previousSkills = skills;
    toggleFavoriteOptimistic(skillId);

    try {
      if (wasFavorited) {
        await api.unfavoriteSharedSkill(skillId);
      } else {
        await api.favoriteSharedSkill(skillId);
      }
    } catch {
      setSkills(previousSkills);
      showToast(tCommon('failed'), 'error');
    }
  };

  const currentLimit = filters.limit || 20;
  const currentSkip = filters.skip || 0;
  const currentPage = Math.floor(currentSkip / currentLimit) + 1;
  const totalPages = Math.max(1, Math.ceil(total / currentLimit));

  return (
    <div className={`flex min-h-screen flex-col bg-slate-50 transition-opacity duration-500 ${isMounted ? 'opacity-100' : 'opacity-0'}`}>
      <AppHeader
        user={user}
        isUserMenuOpen={isUserMenuOpen}
        onUserMenuToggle={() => setIsUserMenuOpen(!isUserMenuOpen)}
        onLogoutClick={() => setIsLogoutDialogOpen(true)}
      />

      <div className="bg-white border-b border-gray-200 py-4 px-4 sm:px-6">
        <div className="mx-auto max-w-7xl">
          <div className="flex items-center gap-3">
            <div className="bg-indigo-100 p-2 rounded-lg">
              <Rocket className="h-6 w-6 text-indigo-600" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">{tNav('skill_plaza')}</h1>
            <span className="text-gray-400 hidden sm:inline">·</span>
            <p className="text-gray-500 hidden sm:inline">{t('subtitle')}</p>
          </div>
        </div>
      </div>

      <main className="flex-1 p-4 sm:p-6">
        <div className="mx-auto max-w-7xl">
          <MarketFilters
            filters={{
              keyword: localSearch,
              category_id: filters.category_id || '',
              sort_by: filters.sort_by || 'newest',
            }}
            categories={categories}
            onFilterChange={(next) => {
              if (next.keyword !== undefined) {
                setLocalSearch(next.keyword);
              }
              if (next.category_id !== undefined || next.sort_by !== undefined) {
                setFilters({
                  ...(next.category_id !== undefined ? { category_id: next.category_id } : {}),
                  ...(next.sort_by !== undefined
                    ? { sort_by: next.sort_by as 'newest' | 'popular' }
                    : {}),
                  skip: 0,
                });
              }
            }}
          />

          <MarketPageStates
            isLoading={isLoading}
            error={error}
            isEmpty={!isLoading && !error && skills.length === 0}
            onRetry={() => void loadMarketSkills()}
          />

          {!isLoading && !error && skills.length > 0 && (
            <>
              <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 animate-fade-in-scale items-stretch">
                {skills.map((skill) => (
                  <MarketSkillCard
                    key={skill.id}
                    skill={skill}
                    onLike={handleLike}
                    isLiked={skill.is_liked}
                    onFavorite={handleFavorite}
                    isFavorited={skill.is_favorited}
                    onNavigate={handleNavigate}
                  />
                ))}
              </div>

              {/* Pagination */}
              {total > 0 && (
                <div className="mt-10 flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-gray-200 pt-6">
                  <div className="text-sm text-gray-500">
                    <span className="font-medium text-gray-900">{Math.min(currentSkip + 1, total)}</span>
                    {' - '}
                    <span className="font-medium text-gray-900">{Math.min(currentSkip + currentLimit, total)}</span>
                    {' / '}
                    <span className="font-medium text-gray-900">{total}</span>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      onClick={() => handlePageChange(Math.max(0, currentSkip - currentLimit))}
                      disabled={currentPage <= 1}
                      className="h-9 px-3"
                    >
                      <ChevronLeft className="h-4 w-4 sm:mr-1" />
                      <span className="hidden sm:inline">{t('prev')}</span>
                    </Button>
                    <div className="text-sm font-medium px-4 text-gray-700 bg-white border border-gray-200 h-9 flex items-center rounded-md shadow-sm">
                      {currentPage} / {totalPages}
                    </div>
                    <Button
                      variant="outline"
                      onClick={() => handlePageChange(currentSkip + currentLimit)}
                      disabled={currentPage >= totalPages}
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
