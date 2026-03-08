'use client';

import { memo } from 'react';
import { useTranslations, useFormatter } from 'next-intl';
import { Heart, Star, User, Clock, MessageSquare } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import type { SharedSkill } from '@/types/market';

interface MarketSkillCardProps {
  skill: SharedSkill;
  onLike?: (id: string) => void;
  isLiked?: boolean;
  onFavorite?: (id: string) => void;
  isFavorited?: boolean;
  onNavigate?: (id: string) => void;
}

function MarketSkillCardComponent({
  skill,
  onLike,
  isLiked,
  onFavorite,
  isFavorited,
  onNavigate,
}: MarketSkillCardProps) {
  const t = useTranslations('market');
  const format = useFormatter();

  const handleLikeClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onLike) {
      onLike(skill.id);
    }
  };

  const handleFavoriteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onFavorite) {
      onFavorite(skill.id);
    }
  };

  const currentLiked = isLiked ?? skill.is_liked ?? false;
  const currentLikeCount = skill.like_count;
  const currentFavorited = isFavorited ?? skill.is_favorited ?? false;

  return (
    <Card
      className="group flex h-full cursor-pointer flex-col card-hover-lift overflow-hidden bg-white/50 backdrop-blur-sm border-white/20 shadow-sm hover:shadow-md transition-all duration-300"
      onClick={() => onNavigate && onNavigate(skill.id)}
    >
      <CardHeader className="pb-3 flex-none">
        <div className="flex items-start justify-between gap-3">
          <div className="flex min-w-0 flex-1 items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-indigo-50 text-indigo-500 transition-colors duration-300 ease-out group-hover:bg-indigo-500 group-hover:text-white">
              <span className="text-xl transition-transform duration-300 ease-out group-hover:scale-110">🚀</span>
            </div>
            <div className="min-w-0 flex-1">
              <CardTitle className="truncate text-base font-semibold leading-tight text-gray-900 sm:text-lg">
                {skill.name}
              </CardTitle>
              {skill.category && (
                <div className="mt-1 text-xs font-medium text-indigo-600">
                  {skill.category.name}
                </div>
              )}
            </div>
          </div>
          <div className="relative shrink-0 flex items-center gap-1.5">
            <button
              onClick={handleFavoriteClick}
              className={`flex items-center gap-1 rounded-full px-2 py-1 text-xs font-medium transition-colors ${
                currentFavorited
                  ? 'bg-amber-50 text-amber-600 hover:bg-amber-100'
                  : 'bg-gray-50 text-gray-500 hover:bg-gray-100 hover:text-gray-700'
              }`}
              title={currentFavorited ? t('unfavorite') : t('favorite')}
            >
              <Star
                className={`h-3.5 w-3.5 ${currentFavorited ? 'fill-amber-600' : ''}`}
              />
            </button>
            <button
              onClick={handleLikeClick}
              className={`flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium transition-colors ${
                currentLiked
                  ? 'bg-rose-50 text-rose-600 hover:bg-rose-100'
                  : 'bg-gray-50 text-gray-500 hover:bg-gray-100 hover:text-gray-700'
              }`}
              title={currentLiked ? t('unlike') : t('like')}
            >
              <Heart
                className={`h-4 w-4 ${currentLiked ? 'fill-rose-600' : ''}`}
              />
              <span>{currentLikeCount}</span>
            </button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="flex flex-1 flex-col pt-0">
        <CardDescription className="skill-description-truncate text-sm leading-relaxed flex-1 text-gray-600">
          {skill.description || <span className="italic opacity-70">No description provided</span>}
        </CardDescription>

        {skill.share_message && (
          <div className="mt-3 flex items-start gap-2 rounded-lg bg-indigo-50/50 p-2.5 text-xs text-indigo-700">
            <MessageSquare className="h-3.5 w-3.5 mt-0.5 shrink-0" />
            <span className="line-clamp-2 italic">&quot;{skill.share_message}&quot;</span>
          </div>
        )}

        <div className="mt-4 flex items-center justify-between text-xs text-gray-500 border-t border-gray-100 pt-3">
          <div className="flex items-center gap-1.5 truncate">
            <User className="h-3.5 w-3.5 shrink-0" />
            <span className="truncate">{skill.author_name}</span>
          </div>
          <div className="flex items-center gap-1.5 shrink-0">
            <Clock className="h-3.5 w-3.5" />
            <span>
              {format.dateTime(new Date(skill.created_at), {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
              })}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export const MarketSkillCard = memo(MarketSkillCardComponent);
