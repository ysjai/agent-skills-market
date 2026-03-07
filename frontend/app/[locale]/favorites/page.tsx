'use client';

import { useState, useEffect } from 'react';
import { useRouter } from '@/i18n/routing';
import { useTranslations } from 'next-intl';
import { Bookmark, AlertTriangle, ExternalLink, BookmarkMinus } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/Card';
import { Dialog } from '@/components/ui/Dialog';
import { AppHeader } from '@/components/layout/AppHeader';
import { api } from '@/lib/api';
import { getCurrentUser, logout } from '@/app/api/auth';
import type { User } from '@/types/user';
import { useFavoritesStore } from '@/stores/favoritesStore';

export default function FavoritesPage() {
  const t = useTranslations('favorites');
  const tCommon = useTranslations('common');
  const tAuth = useTranslations('auth');
  const tMarket = useTranslations('market');
  const router = useRouter();

  const { favorites, total, isLoading, error, setFavorites, setTotal, setIsLoading, setError, removeFavorite } = useFavoritesStore();

  const [user, setUser] = useState<User | null>(null);
  const [isMounted, setIsMounted] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isLogoutDialogOpen, setIsLogoutDialogOpen] = useState(false);
  const [skip, setSkip] = useState(0);
  const limit = 20;

  useEffect(() => {
    const timer = setTimeout(() => setIsMounted(true), 50);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    loadUser();
  }, []);

  useEffect(() => {
    if (user) {
      loadFavorites(0, true);
    }
  }, [user]);

  const loadUser = async () => {
    try {
      const userData = await getCurrentUser();
      setUser(userData);
    } catch {
      router.push('/login');
    }
  };

  const loadFavorites = async (currentSkip: number, reset: boolean = false) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getMyFavorites(currentSkip, limit);
      if (reset) {
        setFavorites(data.items);
      } else {
        setFavorites([...favorites, ...data.items]);
      }
      setTotal(data.total);
      setSkip(currentSkip);
    } catch {
      setError(tCommon('failed') || 'Failed to load favorites');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoadMore = () => {
    loadFavorites(skip + limit, false);
  };

  const handleUnfavorite = async (sharedSkillId: string | null, favoriteId: string) => {
    if (!sharedSkillId) {
      // Skill was deleted, just remove from local state
      removeFavorite(favoriteId);
      return;
    }
    try {
      await api.unfavoriteSharedSkill(sharedSkillId);
      removeFavorite(favoriteId);
    } catch {
      // Silently ignore unfavorite errors
    }
  };

  const handleLogout = () => {
    logout();
  };

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

  return (
    <div className={`flex min-h-screen flex-col bg-gradient-subtle transition-opacity duration-500 ${isMounted ? 'opacity-100' : 'opacity-0'}`}>
      <AppHeader
        user={user}
        isUserMenuOpen={isUserMenuOpen}
        onUserMenuToggle={() => setIsUserMenuOpen(!isUserMenuOpen)}
        onLogoutClick={() => setIsLogoutDialogOpen(true)}
      />

      <div className="border-b bg-white dark:bg-gray-900">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                {t('title')}
              </h1>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {t('subtitle')}
              </p>
            </div>
              <Button
                variant="outline"
                onClick={() => router.push('/market')}
              >
              {t('browse_market')}
            </Button>
          </div>
        </div>
      </div>

      <main className="flex-1 p-4 sm:p-6">
        <div className="mx-auto max-w-7xl">
          {error && (
            <div className="mb-4 rounded-lg bg-red-50 dark:bg-red-900/30 px-4 py-3 text-sm text-red-800 dark:text-red-400">
              {error}
            </div>
          )}

          {isLoading && favorites.length === 0 ? (
            <div className="flex items-center justify-center py-20 animate-fade-in">
              <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
                <div className="h-5 w-5 animate-spin rounded-full border-2 border-gray-300 border-t-gray-900 dark:border-gray-600 dark:border-t-white" />
                <span>{tCommon('loading')}</span>
              </div>
            </div>
          ) : favorites.length === 0 ? (
            <Card className="border-dashed animate-scale-in dark:border-gray-800 dark:bg-gray-900/50">
              <CardContent className="flex flex-col items-center justify-center px-4 py-12 text-center sm:py-20">
                <div className="flex h-14 w-14 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800 sm:h-16 sm:w-16">
                  <Bookmark className="h-7 w-7 text-gray-400 dark:text-gray-500 sm:h-8 sm:w-8" />
                </div>
                <h3 className="mt-4 text-base font-medium text-gray-900 dark:text-white sm:text-lg">
                  {t('no_favorites')}
                </h3>
                <p className="mt-1 max-w-xs text-sm text-gray-500 dark:text-gray-400 sm:max-w-sm">
                  {t('no_favorites_desc')}
                </p>
                <Button
                  onClick={() => router.push('/market')}
                  className="mt-6 min-h-[44px]"
                >
                  {t('browse_market')}
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-6">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 animate-fade-in-scale items-stretch">
                {favorites.map((fav) => (
                  <Card key={fav.id} className="flex flex-col dark:border-gray-800 dark:bg-gray-900">
                    <CardHeader className="flex-1 pb-3">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 overflow-hidden">
                          <CardTitle className="truncate text-lg font-semibold text-gray-900 dark:text-white">
                            {fav.snapshot_name}
                          </CardTitle>
                          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                            By {fav.snapshot_author_name}
                          </p>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-gray-400 hover:text-red-500 dark:hover:text-red-400 shrink-0"
                          onClick={() => handleUnfavorite(fav.shared_skill_id, fav.id)}
                          title={t('remove_favorite')}
                        >
                          <BookmarkMinus className="h-5 w-5" />
                        </Button>
                      </div>
                      
                      {fav.snapshot_status !== 'active' && (
                        <div className="mt-3 flex items-center gap-1.5 rounded-md bg-amber-50 dark:bg-amber-900/30 px-2.5 py-1.5 text-xs font-medium text-amber-800 dark:text-amber-400 border border-amber-200 dark:border-amber-800/50">
                          <AlertTriangle className="h-3.5 w-3.5" />
                          {fav.snapshot_status === 'skill_withdrawn' 
                            ? t('snapshot_warning_withdrawn') 
                            : t('snapshot_warning_deleted')}
                        </div>
                      )}
                    </CardHeader>
                    
                    <CardContent className="pb-4">
                      <p className="line-clamp-3 text-sm text-gray-600 dark:text-gray-300">
                        {fav.snapshot_description || tCommon('description')}
                      </p>
                    </CardContent>
                    
                    <CardFooter className="pt-0 border-t dark:border-gray-800 mt-auto flex justify-between items-center bg-gray-50/50 dark:bg-gray-800/50 p-4 rounded-b-xl">
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        {new Date(fav.created_at).toLocaleDateString()}
                      </div>
                      <Button
                        variant="secondary"
                        size="sm"
                        disabled={fav.snapshot_status !== 'active'}
                        onClick={() => fav.snapshot_status === 'active' && router.push(`/market/${fav.shared_skill_id}`)}
                        className="gap-1.5 bg-white hover:bg-gray-50 dark:bg-gray-800 dark:hover:bg-gray-700 dark:text-white"
                      >
                        <ExternalLink className="h-3.5 w-3.5" />
                        {tCommon('choose')}
                      </Button>
                    </CardFooter>
                  </Card>
                ))}
              </div>
              
              {favorites.length < total && (
                <div className="flex justify-center pt-4">
                  <Button
                    variant="outline"
                    onClick={handleLoadMore}
                    disabled={isLoading}
                    className="min-w-[120px]"
                  >
                    {isLoading ? (
                      <div className="flex items-center gap-2">
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-gray-900 dark:border-gray-600 dark:border-t-white" />
                        <span>{tCommon('loading')}</span>
                      </div>
                    ) : (
                      tMarket('load_more')
                    )}
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      <Dialog
        open={isLogoutDialogOpen}
        onClose={() => setIsLogoutDialogOpen(false)}
        title={tAuth('signOut')}
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600 dark:text-gray-400 sm:text-base">
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
              className="min-h-[44px] flex-1 bg-gray-900 hover:bg-gray-800 text-white dark:bg-white dark:text-gray-900 dark:hover:bg-gray-200"
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
