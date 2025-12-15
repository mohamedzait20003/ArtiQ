export interface AuthState {
  token: string | null;
  role: string | null;
  user: {
    id: string;
    email: string;
    name: string;
  } | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

export const initialAuthState: AuthState = {
  token: null,
  role: null,
  user: null,
  isAuthenticated: false,
  loading: false,
  error: null
};
