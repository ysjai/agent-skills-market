// @ts-nocheck
import { vi } from 'vitest';

class MockApiClient {
  logout = vi.fn().mockResolvedValue(undefined);
  get = vi.fn();
  post = vi.fn();
  put = vi.fn();
  patch = vi.fn();
  delete = vi.fn();
}

export const api = new MockApiClient();

export default api;
