'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';

import { useRouter, Link } from '@/i18n/routing';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { login } from '@/app/api/auth';

export default function LoginPage() {
  const router = useRouter();
  const t = useTranslations('auth');
  const tHome = useTranslations('home');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login({ email, password });
      router.push('/skills');
    } catch {
      setError(t('signIn') === '登录' ? '邮箱或密码错误' : 'Invalid email or password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-8">
      <div className="w-full max-w-md">
        <div className="mb-6 text-center">
          <div className="mb-4 flex justify-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gray-900 text-white">
              <span className="text-2xl">🎯</span>
            </div>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">{tHome('brandName')}</h1>
          <p className="text-gray-600">{tHome('brandTagline')}</p>
        </div>

        <div className="rounded-xl bg-white p-5 shadow-sm sm:p-6">
          <h2 className="mb-6 text-xl font-semibold text-gray-900">{t('signIn')}</h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-gray-700 sm:mb-2">
                {t('email')}
              </label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={isLoading}
                className="min-h-[44px]"
              />
            </div>

            <div>
              <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-gray-700 sm:mb-2">
                {t('password')}
              </label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={isLoading}
                className="min-h-[44px]"
              />
            </div>

            {error && (
              <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-800">
                {error}
              </div>
            )}

            <Button type="submit" className="min-h-[44px] w-full" disabled={isLoading}>
              {isLoading ? `${t('signIn')}...` : t('signIn')}
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-600">
            {t('signUp')}{' '}
            <Link href="/register" className="text-gray-900 hover:text-gray-700">
              {t('signUp')}
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
