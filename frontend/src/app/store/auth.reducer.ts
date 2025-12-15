import { createReducer, on } from '@ngrx/store';
import { AuthState, initialAuthState } from './auth.state';
import * as AuthActions from './auth.actions';

export const authReducer = createReducer(
  initialAuthState,

  // Login
  on(AuthActions.login, (state) => ({
    ...state,
    loading: true,
    error: null
  })),

  on(AuthActions.loginSuccess, (state, { token, role, user }) => ({
    ...state,
    token,
    role,
    user,
    isAuthenticated: true,
    loading: false,
    error: null
  })),

  on(AuthActions.loginFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error,
    isAuthenticated: false
  })),

  // Register
  on(AuthActions.register, (state) => ({
    ...state,
    loading: true,
    error: null
  })),

  on(AuthActions.registerSuccess, (state, { token, role, user }) => ({
    ...state,
    token,
    role,
    user,
    isAuthenticated: true,
    loading: false,
    error: null
  })),

  on(AuthActions.registerFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error,
    isAuthenticated: false
  })),

  // Logout
  on(AuthActions.logout, () => initialAuthState),

  // Load from storage
  on(AuthActions.loadAuthFromStorageSuccess, (state, { token, role, user }) => ({
    ...state,
    token,
    role,
    user,
    isAuthenticated: true
  }))
);
