import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { routing } from '@/i18n/routing';

export function NextIntlProvider({
  children,
  locale,
}: {
  children: React.ReactNode;
  locale: string;
}) {
  if (!routing.locales.includes(locale as any)) {
    notFound();
  }

  return (
    <NextIntlClientProvider messages={getMessages()}>
      {children}
    </NextIntlClientProvider>
  );
}