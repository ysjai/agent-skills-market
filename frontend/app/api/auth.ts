import { api, getLoginUrl } from '@/lib/api';
import type { LoginRequest, RegisterRequest, User } from '@/types/user';

export async function register(data: RegisterRequest): Promise<User> {
  const username = data.username || '';
  await api.register(data.email, username, data.password);
  return await api.get<User>('/auth/me');
}

export async function login(data: LoginRequest): Promise<User> {
  await api.login(data.email, data.password);
  return await api.get<User>('/auth/me');
}

export async function refreshToken(): Promise<void> {
  await api.post('/auth/refresh');
}

export async function getCurrentUser(): Promise<User> {
  const response = await api.get<User>('/auth/me');
  return response;
}

export async function logout(): Promise<void> {
  await api.post('/auth/logout');
  window.location.href = getLoginUrl();
}
