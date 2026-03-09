'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useRouter } from '@/i18n/routing';
import { Heart, Star, Clock, User as UserIcon, Tag, AlertTriangle, Download, FileText } from 'lucide-react';
import { AppHeader } from '@/components/layout/AppHeader';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { useToast } from '@/components/ui/Toast';
import { api } from '@/lib/api';
import { getCurrentUser, logout } from '@/app/api/auth';
import type { SharedPrompt } from '@/types/prompt-market';
import type { User } from '@/types/user';

interface SharedPromptDetailProps {
  id: string;
  backPath: string;
  backLabelKey?: string;
}

export function SharedPromptDetail({ id, backPath }: SharedPromptDetailProps) {
  const router = useRouter();
  const { showToast } = useToast();
  const tMarket = useTranslations('market');

  const [prompt, setPrompt] = useState<SharedPrompt | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);

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
    const fetchData = async () => {
      try {
        setLoading(true);

        if (api.isAuthenticated()) {
          try {
            const currentUser = await getCurrentUser();
            setUser(currentUser);
          } catch {
            setUser(null);
          }
        }

        const data = await api.getMarketPromptDetail(id);
        setPrompt(data);
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

    fetchData();
  }, [id]);

  const handleLike = async () => {
    if (!user) {
      showToast(tMarket('login_to_like'), 'warning');
      router.push('/login');
      return;
    }

    if (!prompt || actionLoading) return;

    const previousLiked = isLiked;
    const previousCount = likeCount;

    try {
      setActionLoading(true);
      if (isLiked) {
        setIsLiked(false);
        setLikeCount(prev => Math.max(0, prev - 1));
        await api.unlikeSharedPrompt(prompt.id);
      } else {
        setIsLiked(true);
        setLikeCount(prev => prev + 1);
        await api.likeSharedPrompt(prompt.id);
      }
    } catch (err: unknown) {
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

    if (!prompt || actionLoading) return;

    const previousFavorited = isFavorited;
    const previousCount = favoriteCount;

    try {
      setActionLoading(true);
      if (isFavorited) {
        setIsFavorited(false);
        setFavoriteCount(prev => Math.max(0, prev - 1));
        await api.unfavoriteSharedPrompt(prompt.id);
      } else {
        setIsFavorited(true);
        setFavoriteCount(prev => prev + 1);
        await api.favoriteSharedPrompt(prompt.id);
      }
    } catch (err: unknown) {
      setIsFavorited(previousFavorited);
      setFavoriteCount(previousCount);
      showToast(err instanceof Error ? err.message : 'Action failed', 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const handleExport = async () => {
    if (!prompt) return;
    try {
      const markdown = await api.exportMarketPrompt(prompt.id);
      const blob = new Blob([markdown], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${prompt.title.replace(/[^a-zA-Z0-9-_]/g, '_')}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch {
      showToast('Export failed', 'error');
    }
  };

  const isWithdrawn = prompt?.status === 'withdrawn';

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <AppHeader
        user={user}
        isUserMenuOpen={isUserMenuOpen}
        onUserMenuToggle={() => setIsUserMenuOpen(!isUserMenuOpen)}
        onLogoutClick={handleLogout}
      />
      
      <main className="flex-1 max-w-7xl w-full mx-auto py-8">

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
        ) : error || !prompt ? (
          <Card className="border-red-100 bg-red-50 text-center py-12">
            <CardContent className="flex flex-col items-center">
              <AlertTriangle className="w-12 h-12 text-red-500 mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                {tMarket('prompt_not_found') || 'Prompt Not Found'}
              </h2>
              <p className="text-gray-600 mb-6">
                {error || (tMarket('prompt_unavailable_desc') || 'This prompt is no longer available.')}
              </p>
              <Button onClick={() => router.push(backPath)}>
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
                  <p className="text-sm text-amber-800">{tMarket('prompt_withdrawn_warning') || 'This prompt has been withdrawn from the market'}</p>
                </CardContent>
              </Card>
            )}
            
            <div className="flex justify-between items-start">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                  {prompt.title}
                </h1>
                <div className="flex items-center gap-4 text-sm text-gray-500 flex-wrap">
                  <span className="flex items-center gap-1">
                    <UserIcon className="w-4 h-4" />
                    {prompt.author_name}
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {new Date(prompt.created_at).toLocaleDateString()}
                  </span>
                </div>
                {prompt.tags && prompt.tags.length > 0 && (
                  <div className="flex items-center gap-2 mt-2 flex-wrap">
                    <Tag className="w-4 h-4 text-purple-500" />
                    {prompt.tags.map((tag) => (
                      <span
                        key={tag}
                        className="inline-flex items-center rounded-full bg-purple-50 px-2.5 py-0.5 text-xs font-medium text-purple-700 border border-purple-200"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
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
                <Button
                  variant="outline"
                  onClick={handleExport}
                >
                  <Download className="w-4 h-4 mr-2" />
                  {tMarket('export_prompt') || 'Export'}
                </Button>
              </div>
            </div>

            {prompt.description && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">{tMarket('about_this_prompt') || 'About this prompt'}</CardTitle>
                  {prompt.share_message && (
                    <CardDescription className="italic mt-1 border-l-2 border-gray-200 pl-3 py-1">
                      &ldquo;{prompt.share_message}&rdquo;
                    </CardDescription>
                  )}
                </CardHeader>
                <CardContent className="prose max-w-none text-gray-700">
                  <div className="whitespace-pre-wrap">{prompt.description}</div>
                </CardContent>
              </Card>
            )}

            {!isWithdrawn && (
              <Card>
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <FileText className="w-5 h-5 text-purple-500" />
                    <CardTitle className="text-lg">{tMarket('prompt_content') || 'Prompt Content'}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="bg-gray-50 rounded-lg p-4 overflow-auto max-h-[600px]">
                    <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono leading-relaxed">
                      {prompt.content}
                    </pre>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
