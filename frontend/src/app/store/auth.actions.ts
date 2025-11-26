import { createAction, props } from '@ngrx/store';

export interface LoginPayload {
  email: string;
  password: string;
  isAdmin: boolean;
}

export interface LoginSuccessPayload {
  token: string;
  role: 'admin' | 'user';
  user: {
    id: string;
    email: string;
    name: string;
  };
}

// Login Actions
export const login = createAction(
  '[Auth] Login',
  props<LoginPayload>()
);

export const loginSuccess = createAction(
  '[Auth] Login Success',
  props<LoginSuccessPayload>()
);

export const loginFailure = createAction(
  '[Auth] Login Failure',
  props<{ error: string }>()
);

// Logout Action
export const logout = createAction('[Auth] Logout');

// Load Auth from Storage (for app initialization)
export const loadAuthFromStorage = createAction('[Auth] Load From Storage');

export const loadAuthFromStorageSuccess = createAction(
  '[Auth] Load From Storage Success',
  props<LoginSuccessPayload>()
);
