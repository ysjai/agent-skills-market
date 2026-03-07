'use client';

import { AlertTriangle, Loader2, Rocket } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { Button } from '@/components/ui/Button';

interface MarketPageStatesProps {
  isLoading: boolean;
  error: string | null;
  isEmpty: boolean;
  onRetry?: () => void;
}

export function MarketPageStates({ isLoading, error, isEmpty, onRetry }: MarketPageStatesProps) {
  const t = useTranslations('market');
  const tCommon = useTranslations('common');

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20 animate-fade-in">
        <div className="flex flex-col items-center gap-3 text-gray-500">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="text-sm font-medium">{tCommon('loading')}</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mb-6 rounded-lg bg-red-50 px-4 py-6 text-center border border-red-100 animate-fade-in-up">
        <div className="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-red-100">
          <AlertTriangle className="h-5 w-5 text-red-500" />
        </div>
        <p className="text-sm text-red-800 mb-4">{error}</p>
        {onRetry && (
          <Button variant="outline" onClick={onRetry} className="min-h-[40px]">
            {tCommon('retry')}
          </Button>
        )}
      </div>
    );
  }

  if (isEmpty) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center bg-white rounded-xl border border-dashed border-gray-300 animate-scale-in">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-indigo-50 mb-4">
          <Rocket className="h-8 w-8 text-indigo-400" />
        </div>
        <h3 className="text-lg font-medium text-gray-900">{t('no_skills')}</h3>
        <p className="mt-1 text-sm text-gray-500 max-w-sm">{t('no_skills_desc')}</p>
      </div>
    );
  }

  return null;
}
