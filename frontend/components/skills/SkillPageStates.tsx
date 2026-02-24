'use client';

import { useRouter } from '@/i18n/routing';
import { useTranslations } from 'next-intl';
import { ArrowLeft, Loader2, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface LoadingStateProps {
  tCommon: ReturnType<typeof useTranslations>;
}

export function LoadingState({ tCommon }: LoadingStateProps) {
  return (
    <div className="flex h-screen items-center justify-center bg-gradient-subtle px-4 animate-fade-in">
      <div className="flex items-center gap-2 text-gray-500">
        <Loader2 className="h-5 w-5 animate-spin" />
        <span>{tCommon('loading')}</span>
      </div>
    </div>
  );
}

interface ErrorStateProps {
  error: string;
  t: ReturnType<typeof useTranslations>;
  tCommon: ReturnType<typeof useTranslations>;
}

export function ErrorState({ error, t, tCommon }: ErrorStateProps) {
  const router = useRouter();
  return (
    <div className="flex h-screen flex-col items-center justify-center bg-gradient-subtle px-4 py-8 animate-fade-in-up">
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-red-100 sm:h-16 sm:w-16">
        <AlertCircle className="h-7 w-7 text-red-500 sm:h-8 sm:w-8" />
      </div>
      <h1 className="mt-4 text-lg font-semibold text-gray-900 sm:text-xl">
        {error || t('notFound') || 'Skill not found'}
      </h1>
      <Button onClick={() => router.push('/skills')} className="btn-interactive mt-4 min-h-[44px]">
        <ArrowLeft className="mr-2 h-4 w-4" />
        {tCommon('back')}
      </Button>
    </div>
  );
}
