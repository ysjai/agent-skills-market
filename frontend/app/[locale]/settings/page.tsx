'use client';

import { useState, useEffect } from 'react';
import { useRouter, usePathname } from '@/i18n/routing';
import { useTranslations, useLocale } from 'next-intl';
import { Globe, Check } from 'lucide-react';
import { AppHeader } from '@/components/layout/AppHeader';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Dialog } from '@/components/ui/Dialog';
import { Button } from '@/components/ui/Button';
import { api } from '@/lib/api';
import { getCurrentUser, logout } from '@/app/api/auth';
import { routing } from '@/i18n/routing';
import type { User } from '@/types/user';

const languageNames: Record<string, { native: string; english: string }> = {
  en: { native: 'English', english: 'English' },
  zh: { native: '中文', english: 'Chinese' },
};

export default function SettingsPage() {
  const t = useTranslations('settings');
  const tAuth = useTranslations('auth');
  const tCommon = useTranslations('common');
  const router = useRouter();
  const pathname = usePathname();
  const currentLocale = useLocale();

  const [user, setUser] = useState<User | null>(null);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isLogoutDialogOpen, setIsLogoutDialogOpen] = useState(false);

  useEffect(() => {
    const loadUser = async () => {
      if (api.isAuthenticated()) {
        try {
          const currentUser = await getCurrentUser();
          setUser(currentUser);
        } catch {
          router.push('/login');
        }
      } else {
        router.push('/login');
      }
    };
    loadUser();
  }, [router]);

  // Close user menu on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest('.user-menu-container')) {
        setIsUserMenuOpen(false);
      }
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    await logout();
    setIsLogoutDialogOpen(false);
    router.push('/login');
  };

  const handleLanguageChange = (newLocale: string) => {
    router.push(pathname, { locale: newLocale });
  };

  return (
    <div className="flex h-screen flex-col bg-gray-50">
      <AppHeader
        user={user}
        isUserMenuOpen={isUserMenuOpen}
        onUserMenuToggle={() => setIsUserMenuOpen(!isUserMenuOpen)}
        onLogoutClick={() => {
          setIsUserMenuOpen(false);
          setIsLogoutDialogOpen(true);
        }}
      />

      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6">
          {/* Page Header */}
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">
              {t('title')}
            </h1>
            <p className="mt-1 text-gray-500">
              {t('subtitle')}
            </p>
          </div>

          {/* Language Setting */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Globe className="h-5 w-5 text-gray-500" />
                {t('language_title')}
              </CardTitle>
              <p className="text-sm text-gray-500 mt-1">
                {t('language_description')}
              </p>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                {routing.locales.map((locale) => {
                  const isSelected = locale === currentLocale;
                  const lang = languageNames[locale];
                  return (
                    <button
                      key={locale}
                      onClick={() => handleLanguageChange(locale)}
                      className={`relative flex items-center gap-3 rounded-lg border-2 px-4 py-3 text-left transition-all ${
                        isSelected
                          ? 'border-gray-900 bg-gray-50'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex-1">
                        <div className={`text-sm font-medium ${isSelected ? 'text-gray-900' : 'text-gray-700'}`}>
                          {lang.native}
                        </div>
                        <div className="text-xs text-gray-500">
                          {lang.english}
                        </div>
                      </div>
                      {isSelected && (
                        <Check className="h-4 w-4 text-gray-900 shrink-0" />
                      )}
                    </button>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Logout Dialog */}
      <Dialog
        open={isLogoutDialogOpen}
        onClose={() => setIsLogoutDialogOpen(false)}
        title={tAuth('signOut')}
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600 sm:text-base">
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
              className="min-h-[44px] flex-1 bg-gray-900 hover:bg-gray-800 text-white"
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
