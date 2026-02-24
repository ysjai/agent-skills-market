'use client';

import { useState, useEffect } from 'react';
import { Globe } from 'lucide-react';
import { usePathname, useRouter } from '@/i18n/routing';
import { useLocale } from 'next-intl';
import { routing } from '@/i18n/routing';

interface LanguageSwitcherProps {
  onNavigate?: (path: string, options?: { locale?: string }) => void;
}

export function LanguageSwitcher({ onNavigate }: LanguageSwitcherProps) {
  const router = useRouter();
  const pathname = usePathname();
  const currentLocale = useLocale();
  const [locale, setLocale] = useState<string>(routing.defaultLocale);
  const [mounted, setMounted] = useState(false);

  // Use layout effect to sync state after initial render to avoid hydration mismatch
  useEffect(() => {
    // Schedule state updates in a microtask to avoid synchronous setState in effect
    queueMicrotask(() => {
      setMounted(true);
      if (routing.locales.includes(currentLocale as typeof routing.locales[number])) {
        setLocale(currentLocale);
      }
    });
  }, [currentLocale]);

  const handleChange = (newLocale: string) => {
    if (onNavigate) {
      onNavigate(pathname, { locale: newLocale });
    } else {
      router.push(pathname, { locale: newLocale });
    }
  };

  if (!mounted) {
    return (
      <div className="flex items-center gap-1 h-9 px-3 text-sm text-gray-500">
        <Globe className="w-4 h-4" />
      </div>
    );
  }

  return (
    <div className="flex items-center">
      <select
        value={locale}
        onChange={(e) => handleChange(e.target.value)}
        className="h-9 rounded-md border border-input bg-background px-2 py-1 text-sm text-gray-700 hover:bg-accent hover:text-accent-foreground transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2"
      >
        <option value="en">English</option>
        <option value="zh">中文</option>
      </select>
    </div>
  );
}
