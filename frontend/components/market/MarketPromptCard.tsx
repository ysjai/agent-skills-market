'use client';

import { memo } from 'react';
import { useTranslations, useFormatter } from 'next-intl';
import { Heart, User, Clock, MessageSquare, FileText, Tag } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import type { SharedPrompt } from '@/types/prompt-market';

interface MarketPromptCardProps {
  prompt: SharedPrompt;
  onLike?: (id: string) => void;
  isLiked?: boolean;
  onNavigate?: (id: string) => void;
}

function MarketPromptCardComponent({
  prompt,
  onLike,
  isLiked,
  onNavigate,
}: MarketPromptCardProps) {
  const t = useTranslations('market');
  const format = useFormatter();

  const handleLikeClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onLike) {
      onLike(prompt.id);
    }
  };

  const currentLiked = isLiked ?? prompt.is_liked ?? false;
  const currentLikeCount = prompt.like_count;

  return (
    <Card
      className="group flex h-full cursor-pointer flex-col card-hover-lift overflow-hidden bg-white/50 backdrop-blur-sm border-white/20 shadow-sm hover:shadow-md transition-all duration-300"
      onClick={() => onNavigate && onNavigate(prompt.id)}
    >
      <CardHeader className="pb-3 flex-none">
        <div className="flex items-start justify-between gap-3">
          <div className="flex min-w-0 flex-1 items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-purple-50 text-purple-500 transition-colors duration-300 ease-out group-hover:bg-purple-500 group-hover:text-white">
              <FileText className="h-5 w-5 transition-transform duration-300 ease-out group-hover:scale-110" />
            </div>
            <div className="min-w-0 flex-1">
              <CardTitle className="truncate text-base font-semibold leading-tight text-gray-900 sm:text-lg">
                {prompt.title}
              </CardTitle>
              {prompt.tags && prompt.tags.length > 0 && (
                <div className="mt-1 flex items-center gap-1 overflow-hidden">
                  <Tag className="h-3 w-3 text-purple-500 shrink-0" />
                  <span className="text-xs font-medium text-purple-600 truncate">
                    {prompt.tags.slice(0, 3).join(', ')}
                    {prompt.tags.length > 3 && ` +${prompt.tags.length - 3}`}
                  </span>
                </div>
              )}
            </div>
          </div>
          <div className="relative shrink-0 flex items-center">
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
          {prompt.description || <span className="italic opacity-70">No description provided</span>}
        </CardDescription>

        {prompt.share_message && (
          <div className="mt-3 flex items-start gap-2 rounded-lg bg-purple-50/50 p-2.5 text-xs text-purple-700">
            <MessageSquare className="h-3.5 w-3.5 mt-0.5 shrink-0" />
            <span className="line-clamp-2 italic">&quot;{prompt.share_message}&quot;</span>
          </div>
        )}

        <div className="mt-4 flex items-center justify-between text-xs text-gray-500 border-t border-gray-100 pt-3">
          <div className="flex items-center gap-1.5 truncate">
            <User className="h-3.5 w-3.5 shrink-0" />
            <span className="truncate">{prompt.author_name}</span>
          </div>
          <div className="flex items-center gap-1.5 shrink-0">
            <Clock className="h-3.5 w-3.5" />
            <span>
              {format.dateTime(new Date(prompt.created_at), {
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

export const MarketPromptCard = memo(MarketPromptCardComponent);
