import createMiddleware from 'next-intl/middleware';
import {routing} from './i18n/routing';
import {NextRequest} from 'next/server';

const intlMiddleware = createMiddleware(routing);

export default function middleware(request: NextRequest) {
  const response = intlMiddleware(request);

  // Extract locale from the URL for root layout to set <html lang>
  const pathname = request.nextUrl.pathname;
  const localeMatch = pathname.match(/^\/(\w{2})(\/|$)/);
  const locale = localeMatch && routing.locales.includes(localeMatch[1] as 'en' | 'zh')
    ? localeMatch[1]
    : routing.defaultLocale;

  response.headers.set('x-locale', locale);
  return response;
}

export const config = {
  matcher: ['/((?!api|_next|_vercel|.*\\..*).*)']
};
