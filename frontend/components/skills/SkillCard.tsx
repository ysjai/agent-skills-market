'use client';

import { memo } from 'react';
import { useTranslations, useFormatter } from 'next-intl';
import { Clock, MoreVertical, Trash2, Download, Globe } from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import type { Skill } from '@/types/skill';

interface SkillCardProps {
  skill: Skill;
  openMenuId: string | null;
  onMenuToggle: (skillId: string | null) => void;
  onDownload: (skillId: string, skillName: string) => void;
  onDelete: (skillId: string) => void;
  onNavigate: (skillId: string) => void;
  isShared?: boolean;
  onShare?: (skillId: string) => void;
  onUnshare?: (skillId: string) => void;
}

function SkillCardComponent({
  skill,
  openMenuId,
  onMenuToggle,
  onDownload,
  onDelete,
  onNavigate,
  isShared,
  onShare,
  onUnshare,
}: SkillCardProps) {
  const t = useTranslations('skills');
  const tMarket = useTranslations('market');
  const tCommon = useTranslations('common');
  const format = useFormatter();

  return (
    <Card
      className="group flex h-full cursor-pointer flex-col card-hover-lift"
      onClick={() => onNavigate(skill.id)}
    >
      <CardHeader className="pb-3 flex-none">
        <div className="flex items-start justify-between gap-3">
          <div className="flex min-w-0 flex-1 items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-gray-100 transition-colors duration-300 ease-out group-hover:bg-black">
              <span className="text-xl transition-transform duration-300 ease-out group-hover:scale-110">📄</span>
            </div>
            <CardTitle className="text-base font-semibold leading-tight text-gray-900 sm:text-lg">{skill.name}</CardTitle>
          </div>
          <div className="relative menu-container shrink-0">
            <button
              onClick={(e) => {
                e.stopPropagation();
                e.nativeEvent.stopImmediatePropagation();
                onMenuToggle(openMenuId === skill.id ? null : skill.id);
              }}
              className="flex h-9 w-9 items-center justify-center rounded-lg text-gray-400 opacity-100 transition-opacity hover:bg-gray-100 hover:text-gray-600 sm:opacity-0 sm:group-hover:opacity-100"
              aria-label="More options"
            >
              <MoreVertical className="h-4 w-4" />
            </button>
            {openMenuId === skill.id && (
              <div className="absolute right-0 top-10 z-10 w-36 rounded-lg border border-gray-200 bg-white py-1 shadow-lg">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    e.nativeEvent.stopImmediatePropagation();
                    onDownload(skill.id, skill.name);
                    onMenuToggle(null);
                  }}
                  className="flex w-full min-h-[44px] items-center gap-2 px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50"
                >
                  <Download className="h-4 w-4" />
                  {t('downloadSkill')}
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete(skill.id);
                    onMenuToggle(null);
                  }}
                  className="flex w-full min-h-[44px] items-center gap-2 px-3 py-2 text-left text-sm text-red-600 hover:bg-red-50"
                >
                  <Trash2 className="h-4 w-4" />
                  {t('deleteSkill')}
                </button>
                {isShared ? (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onUnshare?.(skill.id);
                      onMenuToggle(null);
                    }}
                    className="flex w-full min-h-[44px] items-center gap-2 px-3 py-2 text-left text-sm text-amber-700 hover:bg-amber-50"
                  >
                    <Globe className="h-4 w-4" />
                    {tMarket('unshare')}
                  </button>
                ) : (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onShare?.(skill.id);
                      onMenuToggle(null);
                    }}
                    className="flex w-full min-h-[44px] items-center gap-2 px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50"
                  >
                    <Globe className="h-4 w-4" />
                    {tMarket('share_to_market')}
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex flex-1 flex-col pt-0">
        <CardDescription className="skill-description-truncate text-sm leading-relaxed flex-1">
          {skill.description || tCommon('description')}
        </CardDescription>
        <div className="mt-auto flex items-center justify-between pt-4">
          <div className="flex items-center gap-1 text-xs text-gray-500 sm:text-sm">
            <Clock className="h-3.5 w-3.5" />
            <span>
              {format.dateTime(new Date(skill.updated_at), {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
              })}
            </span>
          </div>
          {isShared ? (
            <div className="flex items-center gap-2">
              <span className="text-xs text-green-600 font-medium flex items-center gap-1">
                <Globe className="w-3 h-3" /> {tMarket('already_shared')}
              </span>
              <Button variant="ghost" size="sm" onClick={(e) => {
                e.stopPropagation();
                onUnshare?.(skill.id);
              }}>
                {tMarket('unshare')}
              </Button>
            </div>
          ) : (
            <Button variant="ghost" size="sm" onClick={(e) => {
              e.stopPropagation();
              onShare?.(skill.id);
            }}>
              <Globe className="w-3 h-3 mr-1" /> {tMarket('share_to_market')}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export const SkillCard = memo(SkillCardComponent);
