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

  private async handleError(response: Response, _url: string): Promise<Error> {
    if (response.status === 401) {
      const refreshed = await this.refreshToken();
      if (refreshed) {
        return new Error('Token refreshed, please retry');
      }

      this.clearTokens();
      window.location.href = getLoginUrl();
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
        errorMessage = errorData.detail || errorMessage;
      } catch {
        errorMessage = await response.text() || errorMessage;
      }
      throw new Error(errorMessage);
    }

    const refreshResponse: TokenResponse = await response.json();
    this.setTokens(refreshResponse.access_token, refreshResponse.refresh_token);
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
        errorMessage = errorData.detail || errorMessage;
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
}

export const api = new ApiClient();
export { getLoginUrl };
