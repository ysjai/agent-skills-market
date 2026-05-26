'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';

import { useRouter, Link } from '@/i18n/routing';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { register } from '@/app/api/auth';

export default function RegisterPage() {
  const router = useRouter();
  const t = useTranslations('auth');
  const tHome = useTranslations('home');
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError(t('passwordMismatch'));
      return;
    }

    if (password.length < 8) {
      setError(t('passwordTooShort'));
      return;
    }

    setLoading(true);

    try {
      await register({ email, username, password });
      router.push('/skills');
    } catch {
      setError(t('emailAlreadyRegistered'));
    } finally {
      setLoading(false);
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
          <h1 className="text-2xl font-bold text-gray-900">{tHome('createAccount')}</h1>
          <p className="text-gray-600">{tHome('startManaging')}</p>
        </div>

        <div className="rounded-xl bg-white p-5 shadow-sm sm:p-6">
          <h2 className="mb-6 text-xl font-semibold text-gray-900">{t('signUp')}</h2>

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
                disabled={loading}
                className="min-h-[44px]"
              />
            </div>

            <div>
              <label htmlFor="username" className="mb-1.5 block text-sm font-medium text-gray-700 sm:mb-2">
                {t('username')}
              </label>
              <Input
                id="username"
                type="text"
                placeholder="johndoe"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                disabled={loading}
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
                disabled={loading}
                minLength={8}
                className="min-h-[44px]"
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="mb-1.5 block text-sm font-medium text-gray-700 sm:mb-2">
                {t('confirmPassword')}
              </label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                disabled={loading}
                minLength={8}
                className="min-h-[44px]"
              />
            </div>

            {error && (
              <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-800">
                {error}
              </div>
            )}

            <Button type="submit" className="min-h-[44px] w-full" disabled={loading}>
              {loading ? t('creatingAccount') : t('createAccount')}
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-600">
            {t('alreadyHaveAccount')}{' '}
            <Link href="/login" className="text-gray-900 hover:text-gray-700">
              {t('signIn')}
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
