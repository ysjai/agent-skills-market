'use client';

import { useState, useEffect, use } from 'react';
import { useTranslations } from 'next-intl';
import { useRouter } from '@/i18n/routing';
import { ArrowLeft, Heart, Star, Clock, User as UserIcon, Tag, AlertTriangle } from 'lucide-react';
import { AppHeader } from '@/components/layout/AppHeader';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { useToast } from '@/components/ui/Toast';
import { api } from '@/lib/api';
import { getCurrentUser, logout } from '@/app/api/auth';
import type { SharedSkill } from '@/types/market';
import type { User } from '@/types/user';

export default function MarketSkillDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const { showToast } = useToast();
  const tMarket = useTranslations('market');

  const [skill, setSkill] = useState<SharedSkill | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);

  // For optimistic UI updates
  const [isLiked, setIsLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(0);
  const [isFavorited, setIsFavorited] = useState(false);
  const [favoriteCount, setFavoriteCount] = useState(0);
  const [actionLoading, setActionLoading] = useState(false);

  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  const handleLogout = async () => {
    try {
      await logout();
      setUser(null);
      router.push('/login');
    } catch {
      showToast('Logout failed', 'error');
    }
  };


  useEffect(() => {
    const fetchUserAndSkill = async () => {
      try {
        setLoading(true);

        if (api.isAuthenticated()) {
          try {
            const currentUser = await getCurrentUser();
            setUser(currentUser);
          } catch {
            setUser(null);
          }
        } else {
          setUser(null);
        }

        const data = await api.getMarketSkillDetail(id);
        setSkill(data);
        setIsLiked(!!data.is_liked);
        setLikeCount(data.like_count);
        setIsFavorited(!!data.is_favorited);
        setFavoriteCount(data.favorite_count);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : tMarket('failed_load'));
      } finally {
        setLoading(false);
      }
    };

    fetchUserAndSkill();
  }, [id]);

  const handleLike = async () => {
    if (!user) {
      showToast(tMarket('login_to_like'), 'warning');
      router.push('/login');
      return;
    }

    if (!skill || actionLoading) return;

    const previousLiked = isLiked;
    const previousCount = likeCount;

    try {
      setActionLoading(true);
      if (isLiked) {
        setIsLiked(false);
        setLikeCount(prev => Math.max(0, prev - 1));
        await api.unlikeSharedSkill(skill.id);
      } else {
        setIsLiked(true);
        setLikeCount(prev => prev + 1);
        await api.likeSharedSkill(skill.id);
      }
    } catch (err: unknown) {
      // Revert on error
      setIsLiked(previousLiked);
      setLikeCount(previousCount);
      showToast(err instanceof Error ? err.message : 'Action failed', 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const handleFavorite = async () => {
    if (!user) {
      showToast(tMarket('login_to_favorite'), 'warning');
      router.push('/login');
      return;
    }

    if (!skill || actionLoading) return;

    const previousFavorited = isFavorited;
    const previousCount = favoriteCount;

    try {
      setActionLoading(true);
      if (isFavorited) {
        setIsFavorited(false);
        setFavoriteCount(prev => Math.max(0, prev - 1));
        await api.unfavoriteSharedSkill(skill.id);
      } else {
        setIsFavorited(true);
        setFavoriteCount(prev => prev + 1);
        await api.favoriteSharedSkill(skill.id);
      }
    } catch (err: unknown) {
      // Revert on error
      setIsFavorited(previousFavorited);
      setFavoriteCount(previousCount);
      showToast(err instanceof Error ? err.message : 'Action failed', 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const isWithdrawn = skill?.status === 'withdrawn';

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <AppHeader
        user={user}
        isUserMenuOpen={isUserMenuOpen}
        onUserMenuToggle={() => setIsUserMenuOpen(!isUserMenuOpen)}
        onLogoutClick={handleLogout}
      />
      
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-8">
        <Button 
          variant="ghost" 
          onClick={() => router.push('/market')}
          className="mb-6 -ml-4 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          {tMarket('back_to_market')}
        </Button>

        {loading ? (
          <div className="space-y-4 animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/3"></div>
            <div className="h-64 bg-white rounded-lg border border-gray-100 p-6">
              <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-5/6 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-4/6 mb-6"></div>
              <div className="flex gap-4">
                <div className="h-10 bg-gray-200 rounded w-24"></div>
                <div className="h-10 bg-gray-200 rounded w-24"></div>
              </div>
            </div>
          </div>
        ) : error || !skill ? (
          <Card className="border-red-100 bg-red-50 text-center py-12">
            <CardContent className="flex flex-col items-center">
              <AlertTriangle className="w-12 h-12 text-red-500 mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                {error ? tMarket('skill_not_found') : tMarket('skill_unavailable')}
              </h2>
              <p className="text-gray-600 mb-6">
                {error || tMarket('skill_unavailable_desc')}
              </p>
              <Button onClick={() => router.push('/market')}>
                {tMarket('return_to_market')}
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {isWithdrawn && (
              <Card className="border-amber-200 bg-amber-50">
                <CardContent className="flex items-center gap-3 py-4">
                  <AlertTriangle className="w-5 h-5 text-amber-600" />
                  <p className="text-sm text-amber-800">{tMarket('skill_withdrawn_warning')}</p>
                </CardContent>
              </Card>
            )}
            <div className="flex justify-between items-start">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                  {skill.snapshot_name}
                </h1>
                <div className="flex items-center gap-4 text-sm text-gray-500 flex-wrap">
                  <span className="flex items-center gap-1">
                    <UserIcon className="w-4 h-4" />
                    {skill.snapshot_author_name}
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {new Date(skill.created_at).toLocaleDateString()}
                  </span>
                  {skill.category && (
                    <span className="flex items-center gap-1">
                      <Tag className="w-4 h-4" />
                      {skill.category.name}
                    </span>
                  )}
                </div>
              </div>
              <div className="flex gap-3">
                <Button 
                  variant={isLiked ? "default" : "outline"} 
                  onClick={handleLike}
                  disabled={actionLoading}
                  className={isLiked ? "bg-red-50 hover:bg-red-100 text-red-600 border-red-200" : ""}
                >
                  <Heart className={`w-4 h-4 mr-2 ${isLiked ? 'fill-current' : ''}`} />
                  {likeCount}
                </Button>
                <Button 
                  variant={isFavorited ? "default" : "outline"} 
                  onClick={handleFavorite}
                  disabled={actionLoading}
                  className={isFavorited ? "bg-amber-50 hover:bg-amber-100 text-amber-600 border-amber-200" : ""}
                >
                  <Star className={`w-4 h-4 mr-2 ${isFavorited ? 'fill-current' : ''}`} />
                  {favoriteCount}
                </Button>
              </div>
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">{tMarket('about_this_skill')}</CardTitle>
                {skill.share_message && (
                  <CardDescription className="italic mt-1 border-l-2 border-gray-200 pl-3 py-1">
                    &ldquo;{skill.share_message}&rdquo;
                  </CardDescription>
                )}
              </CardHeader>
              <CardContent className="prose max-w-none text-gray-700">
                {skill.snapshot_description ? (
                  <div className="whitespace-pre-wrap">{skill.snapshot_description}</div>
                ) : (
                  <p className="text-gray-400 italic">{tMarket('no_description')}</p>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
}
