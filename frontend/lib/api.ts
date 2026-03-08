const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

const SUPPORTED_LOCALES = ['en', 'zh'];
const DEFAULT_LOCALE = 'en';

function getLocaleFromPathname(pathname: string): string {
  const segments = pathname.split('/').filter(Boolean);
  const locale = segments[0];
  return SUPPORTED_LOCALES.includes(locale) ? locale : DEFAULT_LOCALE;
}

function getLoginUrl(): string {
  if (typeof window === 'undefined') return '/en/login';
  const locale = getLocaleFromPathname(window.location.pathname);
  return `/${locale}/login`;
}

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

interface BaseApiRequestOptions extends Omit<RequestInit, 'body'> {
  params?: Record<string, string>;
  data?: unknown;
}

interface ApiRequestOptions extends BaseApiRequestOptions {
  rawResponse?: boolean;
}

class ApiClient {
  private getAccessToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  }

  private getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  }

  private setTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  }

  private clearTokens(): void {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }

  private async request<T>(
    url: string,
    options: ApiRequestOptions = {},
  ): Promise<T> {
    const { params, rawResponse, data, ...fetchOptions } = options;

    const headers: Record<string, string> = {
      ...(fetchOptions.headers as Record<string, string> || {}),
    };

    if (!(data instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    const accessToken = this.getAccessToken();
    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
    }

    const queryParams = params ? new URLSearchParams(params).toString() : '';
    const fullUrl = `${API_BASE_URL}${url}${queryParams ? `?${queryParams}` : ''}`;

    let response: Response;

    try {
      response = await fetch(fullUrl, {
        ...fetchOptions,
        headers,
        body: data instanceof FormData ? data : (data ? JSON.stringify(data) : undefined),
      });
    } catch (error) {
      if (error instanceof Error && (error.name === 'AbortError' || error.message?.includes('aborted'))) {
        throw error;
      }
      throw new Error(`Network error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }

    if (!response.ok) {
      const error = await this.handleError(response, fullUrl);
      throw error;
    }

    if (rawResponse) {
      return response as unknown as T;
    }

    const contentType = response.headers.get('content-type');
    const contentLength = response.headers.get('content-length');
    if (response.status === 204 || contentLength === '0' || !contentType?.includes('application/json')) {
      return undefined as unknown as T;
    }

    const responseData = await response.json();
    return responseData;
  }

  private async handleError(response: Response, _url: string, skipAuthRedirect?: boolean): Promise<Error> {
    if (response.status === 401) {
      if (skipAuthRedirect) {
        return new Error('Unauthorized');
      }
      const refreshed = await this.refreshToken();
      if (refreshed) {
        return new Error('Token refreshed, please retry');
      }

      this.clearTokens();
      if (typeof window !== 'undefined') {
        window.location.href = getLoginUrl();
      }
      return new Error('Unauthorized');
    }

    let errorMessage = `Request failed with status ${response.status}`;

    try {
      const errorData = await response.json();
      if (errorData.detail) {
        errorMessage = errorData.detail;
      }
    } catch {
      const text = await response.text();
      if (text) {
        errorMessage = text;
      }
    }

    return new Error(errorMessage);
  }

  private async refreshToken(): Promise<boolean> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      return false;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${refreshToken}`,
        },
      });

      if (!response.ok) {
        return false;
      }

      const tokenResponse: TokenResponse = await response.json();
      this.setTokens(tokenResponse.access_token, tokenResponse.refresh_token);
      return true;
    } catch {
      return false;
    }
  }

  async login(email: string, password: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      let errorMessage = 'Login failed';
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch {
        errorMessage = await response.text() || errorMessage;
      }
      throw new Error(errorMessage);
    }

    const refreshResponse: TokenResponse = await response.json();
    this.setTokens(refreshResponse.access_token, refreshResponse.refresh_token);
  }

  async getCurrentUserDirect(): Promise<unknown> {
    const accessToken = this.getAccessToken();
    if (!accessToken) {
      throw new Error('Not authenticated');
    }
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
    });
    if (!response.ok) {
      throw new Error('Failed to get user info');
    }
    return response.json();
  }

  async register(email: string, username: string, password: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, username, password }),
    });

    if (!response.ok) {
      let errorMessage = 'Registration failed';
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch {
        errorMessage = await response.text() || errorMessage;
      }
      throw new Error(errorMessage);
    }

    const userData: TokenResponse = await response.json();
    this.setTokens(userData.access_token, userData.refresh_token);
  }

  async logout(): Promise<void> {
    try {
      await this.post('/auth/logout');
    } catch {
      // Silently ignore logout errors
    }
    this.clearTokens();
    window.location.href = getLoginUrl();
  }

  async get<T>(url: string, params?: Record<string, string>): Promise<T> {
    return this.request<T>(url, {
      method: 'GET',
      params,
    });
  }

  async getBlob(url: string, options?: ApiRequestOptions): Promise<Blob> {
    const response = await this.request<Response>(url, {
      method: 'GET',
      ...options,
      rawResponse: true,
    });
    return response.blob();
  }

  async post<T>(url: string, data?: unknown, options?: ApiRequestOptions): Promise<T> {
    return this.request<T>(url, {
      method: 'POST',
      data,
      ...options,
    });
  }

  async put<T>(url: string, data?: unknown, options?: ApiRequestOptions): Promise<T> {
    return this.request<T>(url, {
      method: 'PUT',
      data,
      ...options,
    });
  }

  async patch<T>(url: string, data?: unknown, options?: ApiRequestOptions): Promise<T> {
    return this.request<T>(url, {
      method: 'PATCH',
      data,
      ...options,
    });
  }

  async delete<T>(url: string, params?: Record<string, string>, options?: ApiRequestOptions): Promise<T> {
    return this.request<T>(url, {
      method: 'DELETE',
      params,
      ...options,
    });
  }

  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  }

  // --- Market & Skill Sharing API ---

  async getMarketSkills(params: import('@/types/market').MarketSearchParams): Promise<import('@/types/market').SharedSkillListResponse> {
    const queryParams: Record<string, string> = {};
    if (params.keyword) queryParams.keyword = params.keyword;
    if (params.category_id) queryParams.category_id = params.category_id;
    if (params.sort_by) queryParams.sort_by = params.sort_by;
    if (params.skip !== undefined) queryParams.skip = String(params.skip);
    if (params.limit !== undefined) queryParams.limit = String(params.limit);
    return this.get<import('@/types/market').SharedSkillListResponse>('/market/skills', queryParams);
  }

  async getMarketSkillDetail(id: string): Promise<import('@/types/market').SharedSkill> {
    return this.get<import('@/types/market').SharedSkill>(`/market/skills/${id}`);
  }

  async getMarketSkillTree(sharedSkillId: string): Promise<{
    id: string;
    entries: Array<{ path: string; blob_id: string | null; type: string }>;
    created_at: string;
  }> {
    return this.get(`/market/skills/${sharedSkillId}/tree`);
  }

  async getMarketSkillBlob(sharedSkillId: string, blobId: string): Promise<Blob> {
    return this.getBlob(`/market/skills/${sharedSkillId}/blobs/${blobId}`);
  }

  async likeSharedSkill(id: string): Promise<void> {
    return this.post<void>(`/market/skills/${id}/like`);
  }

  async unlikeSharedSkill(id: string): Promise<void> {
    return this.delete<void>(`/market/skills/${id}/like`);
  }

  async favoriteSharedSkill(id: string): Promise<void> {
    return this.post<void>(`/market/skills/${id}/favorite`);
  }

  async unfavoriteSharedSkill(id: string): Promise<void> {
    return this.delete<void>(`/market/skills/${id}/favorite`);
  }

  async getMyFavorites(skip: number = 0, limit: number = 20): Promise<import('@/types/market').FavoriteListResponse> {
    return this.get<import('@/types/market').FavoriteListResponse>('/favorites', { skip: String(skip), limit: String(limit) });
  }

  async getCategories(): Promise<import('@/types/market').CategoryListResponse> {
    return this.get<import('@/types/market').CategoryListResponse>('/categories');
  }

  async shareSkill(data: import('@/types/market').ShareSkillRequest & { skill_id: string }): Promise<import('@/types/market').SharedSkill> {
    return this.post<import('@/types/market').SharedSkill>(`/skills/${data.skill_id}/share`, { category_id: data.category_id, share_message: data.share_message });
  }

  async unshareSkill(id: string): Promise<void> {
    return this.delete<void>(`/skills/${id}/share`);
  }

  async getMySharedSkills(skip: number = 0, limit: number = 20): Promise<import('@/types/market').SharedSkillListResponse> {
    try {
      return await this.get<import('@/types/market').SharedSkillListResponse>('/market/skills', {
        skip: String(skip),
        limit: String(limit),
      });
    } catch {
      return { items: [], total: 0 };
    }
  }

  // --- Prompt Market API ---

  async getMarketPrompts(params: import('@/types/prompt-market').PromptMarketSearchParams = {}): Promise<import('@/types/prompt-market').SharedPromptListResponse> {
    const queryParams: Record<string, string> = {};
    if (params.keyword) queryParams.keyword = params.keyword;
    if (params.tags && params.tags.length > 0) {
      // Pass tags as comma-separated for now, or as multiple params
      queryParams.tags = params.tags.join(',');
    }
    if (params.sort_by) queryParams.sort_by = params.sort_by;
    if (params.skip !== undefined) queryParams.skip = String(params.skip);
    if (params.limit !== undefined) queryParams.limit = String(params.limit);
    return this.get<import('@/types/prompt-market').SharedPromptListResponse>('/market/prompts', queryParams);
  }

  async getMarketPromptDetail(id: string): Promise<import('@/types/prompt-market').SharedPrompt> {
    return this.get<import('@/types/prompt-market').SharedPrompt>(`/market/prompts/${id}`);
  }

  async likeSharedPrompt(id: string): Promise<void> {
    return this.post<void>(`/market/prompts/${id}/like`);
  }

  async unlikeSharedPrompt(id: string): Promise<void> {
    return this.delete<void>(`/market/prompts/${id}/like`);
  }

  async favoriteSharedPrompt(id: string): Promise<void> {
    return this.post<void>(`/market/prompts/${id}/favorite`);
  }

  async unfavoriteSharedPrompt(id: string): Promise<void> {
    return this.delete<void>(`/market/prompts/${id}/favorite`);
  }

  async getMyPromptFavorites(skip: number = 0, limit: number = 20): Promise<import('@/types/prompt-market').PromptFavoriteListResponse> {
    return this.get<import('@/types/prompt-market').PromptFavoriteListResponse>('/favorites/prompts', { skip: String(skip), limit: String(limit) });
  }

  async refreshPromptFavorite(favoriteId: string): Promise<import('@/types/prompt-market').PromptFavorite> {
    return this.post<import('@/types/prompt-market').PromptFavorite>(`/favorites/prompts/${favoriteId}/refresh`);
  }

  async exportMarketPrompt(id: string): Promise<string> {
    const response = await this.request<Response>(`/market/prompts/${id}/export`, {
      method: 'GET',
      rawResponse: true,
    });
    return response.text();
  }

  async sharePrompt(promptId: string, shareMessage?: string): Promise<import('@/types/prompt-market').SharedPrompt> {
    return this.post<import('@/types/prompt-market').SharedPrompt>(`/prompts/${promptId}/share`, shareMessage ? { share_message: shareMessage } : undefined);
  }

  async unsharePrompt(promptId: string): Promise<void> {
    return this.delete<void>(`/prompts/${promptId}/share`);
  }
}
export const api = new ApiClient();
export { getLoginUrl };
