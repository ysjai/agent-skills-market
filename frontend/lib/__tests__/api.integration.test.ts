import { describe, it, expect, beforeEach, mock } from 'bun:test';
import '@testing-library/jest-dom';

// Mock localStorage
const createMockStorage = () => {
  const storage = new Map<string, string>();
  return {
    getItem: (key: string) => storage.get(key) || null,
    setItem: (key: string, value: string) => storage.set(key, value),
    removeItem: (key: string) => storage.delete(key),
    clear: () => storage.clear(),
  };
};

describe('API Integration', () => {
  let mockFetch: ReturnType<typeof mock>;
  let mockStorage: ReturnType<typeof createMockStorage>;

  // Import the API module fresh for each test
  const importApi = async () => {
    const mod = await import('../api');
    return mod;
  };

  beforeEach(() => {
    mockStorage = createMockStorage();
    mockFetch = mock(() => Promise.resolve(new Response()));

    // Setup global mocks
    Object.defineProperty(global, 'fetch', {
      value: mockFetch,
      writable: true,
      configurable: true,
    });

    Object.defineProperty(global, 'localStorage', {
      value: mockStorage,
      writable: true,
      configurable: true,
    });

    Object.defineProperty(global, 'window', {
      value: { location: { href: '', pathname: '/en/login' } },
      writable: true,
      configurable: true,
    });
  });

  it('GET returns data on success', async () => {
    const { api } = await importApi();
    const mockData = { id: 1, name: 'test' };
    mockFetch.mockResolvedValue({
      ok: true,
      headers: new Map([['content-type', 'application/json']]),
      json: () => Promise.resolve(mockData),
    });

    const result = await api.get('/users/1');
    expect(result).toEqual(mockData);
  });

  it('POST returns data on success', async () => {
    const { api } = await importApi();
    const mockData = { id: 2, name: 'created' };
    mockFetch.mockResolvedValue({
      ok: true,
      headers: new Map([['content-type', 'application/json']]),
      json: () => Promise.resolve(mockData),
    });

    const result = await api.post('/users', { name: 'created' });
    expect(result).toEqual(mockData);
  });

  it('throws on 401 unauthorized', async () => {
    const { api } = await importApi();
    mockFetch.mockResolvedValue({
      ok: false,
      status: 401,
      headers: new Map(),
      json: () => Promise.resolve({ detail: 'Unauthorized' }),
      text: () => Promise.resolve('Unauthorized'),
    });

    await expect(api.get('/protected')).rejects.toThrow('Unauthorized');
  });

  it('throws on network error', async () => {
    const { api } = await importApi();
    mockFetch.mockRejectedValue(new Error('Failed to fetch'));

    await expect(api.get('/users')).rejects.toThrow('Network error');
  });

  it('throws on 4xx error', async () => {
    const { api } = await importApi();
    mockFetch.mockResolvedValue({
      ok: false,
      status: 400,
      headers: new Map(),
      json: () => Promise.resolve({ detail: 'Bad request' }),
      text: () => Promise.resolve('Bad request'),
    });

    await expect(api.post('/users', {})).rejects.toThrow('Bad request');
  });

  it('throws on 5xx error', async () => {
    const { api } = await importApi();
    mockFetch.mockResolvedValue({
      ok: false,
      status: 500,
      headers: new Map(),
      json: () => Promise.resolve({ detail: 'Internal server error' }),
      text: () => Promise.resolve('Internal server error'),
    });

    await expect(api.get('/users')).rejects.toThrow('Internal server error');
  });

  it('isAuthenticated returns true when token exists', async () => {
    mockStorage.setItem('access_token', 'fake-token');
    const { api } = await importApi();
    
    const result = api.isAuthenticated();
    expect(result).toBe(true);
  });

  it('isAuthenticated returns false when token does not exist', async () => {
    const { api } = await importApi();
    
    const result = api.isAuthenticated();
    expect(result).toBe(false);
  });

  it('getBlob returns blob on success', async () => {
    const { api } = await importApi();
    const mockBlob = new Blob(['test content'], { type: 'text/plain' });
    mockFetch.mockResolvedValue({
      ok: true,
      headers: new Map([['content-type', 'text/plain']]),
      blob: () => Promise.resolve(mockBlob),
    });

    const result = await api.getBlob('/files/test.txt');
    expect(result).toBeInstanceOf(Blob);
  });
});
