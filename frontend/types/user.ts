export interface User {
  id: string;
  email: string;
  username: string;
  phone: string | null;
  is_active: boolean;
  email_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserWithTokens extends User {
  access_token: string;
  refresh_token: string;
}

export interface LoginRequest {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}
