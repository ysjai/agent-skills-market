'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';

import { Link } from '@/i18n/routing';

export default function Home() {
  const t = useTranslations('home');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setMounted(true), 100);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className={`flex min-h-screen flex-col items-center justify-center bg-gradient-hero px-4 py-8 transition-opacity duration-700 ${mounted ? 'opacity-100' : 'opacity-0'}`}>
      <div className="max-w-2xl text-center">
        <div className="mb-6 flex justify-center">
          <div className={`flex h-14 w-14 items-center justify-center rounded-2xl bg-gray-900 text-white sm:h-16 sm:w-16 animate-float transition-all duration-700 ${mounted ? 'scale-100 opacity-100' : 'scale-95 opacity-0'}`}>
            <span className="text-2xl sm:text-3xl">🎯</span>
          </div>
        </div>
        <h1 className={`mb-4 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl md:text-5xl animate-fade-in-up transition-all duration-700 delay-100 ${mounted ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'}`}>
          {t('title')}
        </h1>
        <p className={`mb-8 text-lg text-gray-600 sm:text-xl animate-fade-in-up transition-all duration-700 delay-200 ${mounted ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'}`}>
          {t('subtitle')}
        </p>
        <div className={`flex flex-col items-center gap-3 px-4 sm:flex-row sm:justify-center sm:gap-4 sm:px-0 animate-fade-in-up transition-all duration-700 delay-300 ${mounted ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'}`}>
          <Link
            href="/login"
            className="btn-interactive inline-flex min-h-[44px] items-center justify-center rounded-lg bg-gray-900 px-6 py-3 font-semibold text-white transition-all hover:bg-gray-800 hover:shadow-lg hover:shadow-gray-900/20 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2 sm:px-8"
          >
            {t('getStarted')}
          </Link>
          <Link
            href="/register"
            className="btn-interactive inline-flex min-h-[44px] items-center justify-center rounded-lg border border-gray-200 bg-white px-6 py-3 font-semibold text-gray-900 transition-all hover:bg-gray-50 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2 sm:px-8"
          >
            {t('createAccount')}
          </Link>
        </div>
      </div>
    </div>
  );
}
