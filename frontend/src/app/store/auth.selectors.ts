import { createFeatureSelector, createSelector } from '@ngrx/store';
import { AuthState } from './auth.state';

export const selectAuthState = createFeatureSelector<AuthState>('auth');

export const selectToken = createSelector(
  selectAuthState,
  (state: AuthState) => state.token
);

export const selectRole = createSelector(
  selectAuthState,
  (state: AuthState) => state.role
);

export const selectUser = createSelector(
  selectAuthState,
  (state: AuthState) => state.user
);

export const selectIsAuthenticated = createSelector(
  selectAuthState,
  (state: AuthState) => state.isAuthenticated
);

export const selectAuthLoading = createSelector(
  selectAuthState,
  (state: AuthState) => state.loading
);

export const selectAuthError = createSelector(
  selectAuthState,
  (state: AuthState) => state.error
);

// Get start URL based on role
export const selectStartUrl = createSelector(
  selectRole,
  selectIsAuthenticated,
  (role, isAuthenticated) => {
    if (!isAuthenticated) return '/';
    
    switch (role) {
      case 'admin':
        return '/dashboard/admin';
      case 'user':
        return '/dashboard/user';
      default:
        return '/';
    }
  }
);
