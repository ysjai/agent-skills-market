import {NextIntlClientProvider} from 'next-intl';
import {notFound} from 'next/navigation';
import {routing} from '@/i18n/routing';
import '../globals.css';
import {ToastProvider} from '@/components/ui/Toast';

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
    <html lang={locale}>
      <body>
        <ToastProvider>
          <NextIntlClientProvider locale={locale} messages={messages}>
            {children}
          </NextIntlClientProvider>
        </ToastProvider>
      </body>
    </html>
  );
}
