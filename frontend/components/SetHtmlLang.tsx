'use client';

import { useEffect } from 'react';

/**
 * Sets the `lang` attribute on <html> from within the locale layout.
 * Since <html> lives in the root layout (required by Next.js 15),
 * this client component bridges the gap by updating it dynamically.
 */
export default function SetHtmlLang({ locale }: { locale: string }) {
  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);

  return null;
}
