'use client';

import { useState, useEffect } from 'react';
import { useRouter } from '@/i18n/routing';
import { useTranslations } from 'next-intl';
import { Bookmark, AlertTriangle, ExternalLink, BookmarkMinus, FileText, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/Card';
import { Dialog } from '@/components/ui/Dialog';
import { AppHeader } from '@/components/layout/AppHeader';
import { api } from '@/lib/api';
import { getCurrentUser, logout } from '@/app/api/auth';
import type { User } from '@/types/user';
import { useFavoritesStore } from '@/stores/favoritesStore';
import { usePromptFavoritesStore } from '@/stores/promptFavoritesStore';

export default function FavoritesPage() {
  const t = useTranslations('favorites');
  const tCommon = useTranslations('common');
  const tAuth = useTranslations('auth');
  const tMarket = useTranslations('market');
  const router = useRouter();

  const { favorites, total, isLoading, error, setFavorites, setTotal, setIsLoading, setError, removeFavorite } = useFavoritesStore();

  const [activeTab, setActiveTab] = useState<'skills' | 'prompts'>('skills');

  const {
    favorites: promptFavorites,
    total: promptTotal,
    isLoading: promptsLoading,
    error: promptsError,
    setFavorites: setPromptFavorites,
    setTotal: setPromptTotal,
    setIsLoading: setPromptIsLoading,
    setError: setPromptError,
    removeFavorite: removePromptFavorite,
    updateFavorite: updatePromptFavorite,
  } = usePromptFavoritesStore();

  const [user, setUser] = useState<User | null>(null);
  const [isMounted, setIsMounted] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isLogoutDialogOpen, setIsLogoutDialogOpen] = useState(false);
  const [skip, setSkip] = useState(0);
  const [promptSkip, setPromptSkip] = useState(0);
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

  useEffect(() => {
    if (user && activeTab === 'prompts') {
      loadPromptFavorites(0, true);
    }
  }, [user, activeTab]);

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

  const loadPromptFavorites = async (currentSkip: number, reset: boolean = false) => {
    setPromptIsLoading(true);
    setPromptError(null);
    try {
      const data = await api.getMyPromptFavorites(currentSkip, limit);
      if (reset) {
        setPromptFavorites(data.items);
      } else {
        setPromptFavorites([...promptFavorites, ...data.items]);
      }
      setPromptTotal(data.total);
      setPromptSkip(currentSkip);
    } catch {
      setPromptError(tCommon('failed') || 'Failed to load favorites');
    } finally {
      setPromptIsLoading(false);
    }
  };

  const handleUnfavoritePrompt = async (sharedPromptId: string | null, favoriteId: string) => {
    if (!sharedPromptId) {
      removePromptFavorite(favoriteId);
      return;
    }
    try {
      await api.unfavoriteSharedPrompt(sharedPromptId);
      removePromptFavorite(favoriteId);
    } catch {
      // Silently ignore
    }
  };

  const handleRefreshPromptFavorite = async (favoriteId: string) => {
    try {
      const updated = await api.refreshPromptFavorite(favoriteId);
      // The response has { message, favorite } - extract the favorite
      updatePromptFavorite(favoriteId, (updated as any).favorite || updated);
    } catch {
      // Silently ignore
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
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
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
          {/* Tab Switch */}
          <div className="mt-4 flex gap-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1 w-fit">
            <button
              onClick={() => setActiveTab('skills')}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                activeTab === 'skills'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              {t('tabs_skills') || 'Skills'}
            </button>
            <button
              onClick={() => setActiveTab('prompts')}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                activeTab === 'prompts'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              {t('tabs_prompts') || 'Prompts'}
            </button>
          </div>
        </div>
      </div>

      <main className="flex-1 p-4 sm:p-6">
        <div className="mx-auto max-w-7xl">
          {activeTab === 'skills' && (
            <>
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
                        
                        <CardFooter className="pt-0 border-t dark:border-gray-800 mt-auto flex justify-between items-center bg-gray-50/50 dark:bg-gray-800/50 px-6 py-4 rounded-b-xl">
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            {new Date(fav.created_at).toLocaleDateString()}
                          </div>
                          <Button
                            variant="secondary"
                            size="sm"
                            disabled={fav.snapshot_status !== 'active'}
                            onClick={() => fav.snapshot_status === 'active' && router.push(`/favorites/${fav.shared_skill_id}`)}
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
            </>
          )}

          {activeTab === 'prompts' && (
            <>
              {promptsError && (
                <div className="mb-4 rounded-lg bg-red-50 dark:bg-red-900/30 px-4 py-3 text-sm text-red-800 dark:text-red-400">
                  {promptsError}
                </div>
              )}

              {promptsLoading && promptFavorites.length === 0 ? (
                <div className="flex items-center justify-center py-20 animate-fade-in">
                  <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
                    <div className="h-5 w-5 animate-spin rounded-full border-2 border-gray-300 border-t-gray-900 dark:border-gray-600 dark:border-t-white" />
                    <span>{tCommon('loading')}</span>
                  </div>
                </div>
              ) : promptFavorites.length === 0 ? (
                <Card className="border-dashed animate-scale-in dark:border-gray-800 dark:bg-gray-900/50">
                  <CardContent className="flex flex-col items-center justify-center px-4 py-12 text-center sm:py-20">
                    <div className="flex h-14 w-14 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800 sm:h-16 sm:w-16">
                      <FileText className="h-7 w-7 text-gray-400 dark:text-gray-500 sm:h-8 sm:w-8" />
                    </div>
                    <h3 className="mt-4 text-base font-medium text-gray-900 dark:text-white sm:text-lg">
                      {t('no_prompt_favorites') || 'No prompt favorites yet'}
                    </h3>
                    <p className="mt-1 max-w-xs text-sm text-gray-500 dark:text-gray-400 sm:max-w-sm">
                      {t('no_prompt_favorites_desc') || 'Browse the market and favorite prompts to save them here'}
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
                    {promptFavorites.map((fav) => (
                      <Card key={fav.id} className="flex flex-col dark:border-gray-800 dark:bg-gray-900">
                        <CardHeader className="flex-1 pb-3">
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex-1 overflow-hidden">
                              <CardTitle className="truncate text-lg font-semibold text-gray-900 dark:text-white">
                                {fav.snapshot_title}
                              </CardTitle>
                              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                                By {fav.snapshot_author_name}
                              </p>
                            </div>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8 text-gray-400 hover:text-red-500 dark:hover:text-red-400 shrink-0"
                              onClick={() => handleUnfavoritePrompt(fav.shared_prompt_id, fav.id)}
                              title={t('remove_favorite')}
                            >
                              <BookmarkMinus className="h-5 w-5" />
                            </Button>
                          </div>
                          
                          {fav.is_stale && fav.snapshot_status === 'active' && (
                            <div className="mt-3 flex items-center justify-between gap-2 rounded-md bg-blue-50 dark:bg-blue-900/30 px-2.5 py-1.5 text-xs font-medium text-blue-800 dark:text-blue-400 border border-blue-200 dark:border-blue-800/50">
                              <div className="flex items-center gap-1.5">
                                <AlertTriangle className="h-3.5 w-3.5" />
                                {t('prompt_changed') || 'Content has been updated'}
                              </div>
                              <button
                                onClick={() => handleRefreshPromptFavorite(fav.id)}
                                className="flex items-center gap-1 text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                              >
                                <RefreshCw className="h-3.5 w-3.5" />
                                {t('refresh_prompt') || 'Refresh'}
                              </button>
                            </div>
                          )}

                          {fav.snapshot_status !== 'active' && (
                            <div className="mt-3 flex items-center gap-1.5 rounded-md bg-amber-50 dark:bg-amber-900/30 px-2.5 py-1.5 text-xs font-medium text-amber-800 dark:text-amber-400 border border-amber-200 dark:border-amber-800/50">
                              <AlertTriangle className="h-3.5 w-3.5" />
                              {fav.snapshot_status === 'prompt_withdrawn' 
                                ? (t('snapshot_warning_prompt_withdrawn') || 'This prompt has been withdrawn')
                                : (t('snapshot_warning_prompt_deleted') || 'This prompt has been deleted')}
                            </div>
                          )}

                          {fav.snapshot_tags && fav.snapshot_tags.length > 0 && (
                            <div className="mt-2 flex gap-1 flex-wrap">
                              {fav.snapshot_tags.slice(0, 3).map((tag) => (
                                <span key={tag} className="rounded-full bg-purple-50 dark:bg-purple-900/30 px-2 py-0.5 text-xs text-purple-700 dark:text-purple-400 border border-purple-200 dark:border-purple-800/50">
                                  {tag}
                                </span>
                              ))}
                            </div>
                          )}
                        </CardHeader>
                        
                        <CardContent className="pb-4">
                          <p className="line-clamp-3 text-sm text-gray-600 dark:text-gray-300">
                            {fav.snapshot_description || fav.snapshot_content.substring(0, 150)}
                          </p>
                        </CardContent>
                        
                        <CardFooter className="pt-0 border-t dark:border-gray-800 mt-auto flex justify-between items-center bg-gray-50/50 dark:bg-gray-800/50 px-6 py-4 rounded-b-xl">
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            v{fav.snapshot_version} · {new Date(fav.created_at).toLocaleDateString()}
                          </div>
                          <Button
                            variant="secondary"
                            size="sm"
                            disabled={fav.snapshot_status !== 'active'}
                            onClick={() => fav.snapshot_status === 'active' && fav.shared_prompt_id && router.push(`/favorites/prompts/${fav.shared_prompt_id}`)}
                            className="gap-1.5 bg-white hover:bg-gray-50 dark:bg-gray-800 dark:hover:bg-gray-700 dark:text-white"
                          >
                            <ExternalLink className="h-3.5 w-3.5" />
                            {tCommon('choose')}
                          </Button>
                        </CardFooter>
                      </Card>
                    ))}
                  </div>
                  
                  {promptFavorites.length < promptTotal && (
                    <div className="flex justify-center pt-4">
                      <Button
                        variant="outline"
                        onClick={() => loadPromptFavorites(promptSkip + limit, false)}
                        disabled={promptsLoading}
                        className="min-h-[44px] min-w-[200px]"
                      >
                        {promptsLoading ? tCommon('loading') : (t('load_more') || 'Load More')}
                      </Button>
                    </div>
                  )}
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
