'use client';

import { Link, usePathname, useRouter } from '@/i18n/routing';
import { useTranslations } from 'next-intl';
import { User as UserIcon, ChevronDown, LogOut, Layers, BookOpen, Store, Star, Settings } from 'lucide-react';
import type { User } from '@/types/user';

interface AppHeaderProps {
  user: User | null;
  isUserMenuOpen: boolean;
  onUserMenuToggle: () => void;
  onLogoutClick: () => void;
}

export function AppHeader({ user, isUserMenuOpen, onUserMenuToggle, onLogoutClick }: AppHeaderProps) {
  const t = useTranslations('nav');
  const tAuth = useTranslations('auth');
  const pathname = usePathname();
  const router = useRouter();

  const parts = pathname.split('/').filter(Boolean);
  // usePathname from next-intl returns path WITHOUT locale prefix (e.g. /market, not /en/market)
  const currentPage = parts[0] || 'market';

  const navItems = [
    { key: 'market', href: '/market', icon: Store },
  ];

  const userMenuItems = [
    { key: 'my_skills', href: '/skills', icon: Layers },
    { key: 'my_prompts', href: '/prompts', icon: BookOpen },
    { key: 'my_favorites', href: '/favorites', icon: Star },
  ];

  const handleMenuItemClick = (href: string) => {
    onUserMenuToggle();
    router.push(href);
  };

  return (
    <header className="shrink-0 border-b border-gray-200 bg-white">
      <div className="px-4 sm:px-6">
        <div className="flex h-14 items-center justify-between gap-4">
          {/* Left: Logo + Navigation Tabs */}
          <div className="flex items-center gap-1 sm:gap-2">
            <Link href="/market" className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gray-900 text-white">
              <span className="text-base">🎯</span>
            </Link>

            <nav className="ml-2 flex items-center">
              {navItems.map((item) => {
                const isActive = currentPage === item.key;
                const Icon = item.icon;
                return (
                  <Link
                    key={item.key}
                    href={item.href}
                    className={`relative flex items-center gap-1.5 px-3 py-2 text-sm font-medium transition-colors rounded-md ${
                      isActive
                        ? 'text-gray-900'
                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className={`h-4 w-4 ${isActive ? 'text-gray-900' : 'text-gray-400'}`} />
                    <span>{t(item.key)}</span>
                    {isActive && (
                      <span className="absolute bottom-0 left-3 right-3 h-0.5 bg-gray-900 rounded-full translate-y-[9px]" />
                    )}
                  </Link>
                );
              })}
            </nav>
          </div>

          {/* Right: User Menu */}
          <div className="flex items-center gap-2">
            <div className="relative user-menu-container">
              <button
                onClick={onUserMenuToggle}
                className="flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2"
              >
                <div className="flex h-7 w-7 items-center justify-center rounded-full bg-gray-100">
                  <UserIcon className="h-3.5 w-3.5 text-gray-600" />
                </div>
                <span className="hidden sm:inline">{user?.username || 'User'}</span>
                <ChevronDown className="h-4 w-4 text-gray-400" />
              </button>

              {isUserMenuOpen && (
                <div className="absolute right-0 top-12 z-50 w-48 rounded-lg border border-gray-200 bg-white py-1 shadow-lg">
                  {/* My Skills / Prompts / Favorites */}
                  {userMenuItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = currentPage === item.key.replace('my_', '');
                    return (
                      <button
                        key={item.key}
                        onClick={() => handleMenuItemClick(item.href)}
                        className={`flex w-full min-h-[44px] items-center gap-2 px-3 py-2 text-left text-sm transition-colors ${
                          isActive
                            ? 'text-gray-900 bg-gray-50 font-medium'
                            : 'text-gray-700 hover:bg-gray-50'
                        }`}
                      >
                        <Icon className={`h-4 w-4 ${isActive ? 'text-gray-900' : 'text-gray-500'}`} />
                        {t(item.key)}
                      </button>
                    );
                  })}

                  {/* Divider */}
                  <div className="my-1 border-t border-gray-100" />

                  {/* Settings */}
                  <button
                    onClick={() => handleMenuItemClick('/settings')}
                    className={`flex w-full min-h-[44px] items-center gap-2 px-3 py-2 text-left text-sm transition-colors ${
                      currentPage === 'settings'
                        ? 'text-gray-900 bg-gray-50 font-medium'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <Settings className={`h-4 w-4 ${currentPage === 'settings' ? 'text-gray-900' : 'text-gray-500'}`} />
                    {t('settings')}
                  </button>

                  {/* Divider */}
                  <div className="my-1 border-t border-gray-100" />

                  {/* Sign Out */}
                  <button
                    onClick={onLogoutClick}
                    className="flex w-full min-h-[44px] items-center gap-2 px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50"
                  >
                    <LogOut className="h-4 w-4 text-gray-500" />
                    {tAuth('signOut')}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
