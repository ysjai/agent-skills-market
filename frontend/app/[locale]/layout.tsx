import {NextIntlClientProvider} from 'next-intl';
import {notFound} from 'next/navigation';

import {routing} from '@/i18n/routing';
import '../globals.css';
import {ToastProvider} from '@/components/ui/Toast';
import SetHtmlLang from '@/components/SetHtmlLang';

export default async function LocaleLayout({
  children,
  params
}: {
  children: React.ReactNode;
  params: Promise<{locale: string}>;
}) {
  const {locale} = await params;

  // Ensure that the incoming `locale` is valid
  if (!routing.locales.includes(locale as typeof routing.locales[number])) {
    notFound();
  }

  // Load messages for the current locale
  const messages = (await import(`../../i18n/locales/${locale}.json`)).default;

  return (
    <ToastProvider>
      <NextIntlClientProvider locale={locale} messages={messages}>
        <SetHtmlLang locale={locale} />
        {children}
      </NextIntlClientProvider>
    </ToastProvider>
  );
}
