import { describe, it, expect, beforeEach, mock } from 'bun:test';

import { logout } from '../../app/api/auth';
import '@testing-library/jest-dom';

const createMockStorage = () => {
  const storage = new Map<string, string>();
  return {
    getItem: (key: string) => storage.get(key) || null,
    setItem: (key: string, value: string) => storage.set(key, value),
    removeItem: (key: string) => storage.delete(key),
    clear: () => storage.clear(),
  };
};

describe('auth', () => {
  let mockFetch: ReturnType<typeof mock>;

  beforeEach(() => {
    mockFetch = mock(() => Promise.resolve(new Response(null, { status: 204 })));

    Object.defineProperty(global, 'fetch', {
      value: mockFetch,
      writable: true,
      configurable: true,
    });

    Object.defineProperty(global, 'localStorage', {
      value: createMockStorage(),
      writable: true,
      configurable: true,
    });

    Object.defineProperty(global, 'window', {
      value: { location: { href: '', pathname: '/en/settings' } },
      writable: true,
      configurable: true,
    });
  });

  describe('logout', () => {
    it('should call logout endpoint', async () => {
      await logout();

      expect(mockFetch).toHaveBeenCalledWith('/api/auth/logout', expect.objectContaining({
        method: 'POST',
      }));
    });

    it('should redirect to localized login after logout', async () => {
      await logout();

      expect(window.location.href).toBe('/en/login');
    });
  });
});
