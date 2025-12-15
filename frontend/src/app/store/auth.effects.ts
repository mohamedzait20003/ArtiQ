import { Injectable, PLATFORM_ID, Inject, inject } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { of, EMPTY } from 'rxjs';
import { map, catchError, tap, switchMap } from 'rxjs/operators';
import * as AuthActions from './auth.actions';

interface LoginResponse {
  token: string;
  role: string;
  userData: {
    name: string;
  };
}

interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterResponse {
  token: string;
  role: string;
  userData: {
    name: string;
  };
}

interface RegisterRequest {
  name: string;
  email: string;
  password: string;
  confirm_password: string;
}

@Injectable()
export class AuthEffects {
  private readonly API_URL = 'http://localhost:8000';
  private actions$ = inject(Actions);
  private http = inject(HttpClient);
  private router = inject(Router);
  private store = inject(Store);
  private platformId = inject(PLATFORM_ID);

  login$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AuthActions.login),
      switchMap(({ email, password }) => {
        if (!isPlatformBrowser(this.platformId)) {
          return EMPTY;
        }

        const requestBody: LoginRequest = {
          email: email,
          password: password
        };

        return this.http.post<LoginResponse>(`${this.API_URL}/login`, requestBody).pipe(
          map((response: LoginResponse) => {
            return AuthActions.loginSuccess({
              token: response.token,
              role: response.role,
              user: {
                id: response.token,
                email: email,
                name: response.userData.name
              }
            });
          }),
          catchError((error) => {
            let errorMessage = 'Login failed';
            if (error.error?.detail) {
              errorMessage = error.error.detail;
            } else if (error.status === 400) {
              errorMessage = 'Missing field(s) in the login request';
            } else if (error.status === 401) {
              errorMessage = 'Invalid email or password';
            }
            return of(AuthActions.loginFailure({ error: errorMessage }));
          })
        );
      })
    )
  );

  register$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AuthActions.register),
      switchMap(({ name, email, password, confirm_password }) => {
        if (!isPlatformBrowser(this.platformId)) {
          return EMPTY;
        }

        const requestBody: RegisterRequest = {
          name: name,
          email: email,
          password: password,
          confirm_password: confirm_password
        };

        return this.http.post<RegisterResponse>(`${this.API_URL}/register`, requestBody).pipe(
          map((response: RegisterResponse) => {
            return AuthActions.registerSuccess({
              token: response.token,
              role: response.role,
              user: {
                id: response.token,
                email: email,
                name: response.userData.name
              }
            });
          }),
          catchError((error) => {
            let errorMessage = 'Registration failed';
            if (error.error?.detail) {
              errorMessage = error.error.detail;
            } else if (error.status === 400) {
              errorMessage = 'Missing field(s) or passwords do not match';
            }
            return of(AuthActions.registerFailure({ error: errorMessage }));
          })
        );
      })
    )
  );

  loginSuccess$ = createEffect(
    () =>
      this.actions$.pipe(
        ofType(AuthActions.loginSuccess),
        tap(({ role }) => {
          if (isPlatformBrowser(this.platformId)) {
            // Navigate based on role
            switch (role) {
              case 'Admin':
                this.router.navigate(['/admin']);
                break;
              case 'Manager':
                this.router.navigate(['/dashboard']);
                break;
              case 'Visitor':
                this.router.navigate(['/visitor']);
                break;
              default:
                this.router.navigate(['/']);
            }
          }
        })
      ),
    { dispatch: false }
  );

  registerSuccess$ = createEffect(
    () =>
      this.actions$.pipe(
        ofType(AuthActions.registerSuccess),
        tap(({ role }) => {
          if (isPlatformBrowser(this.platformId)) {
            // Navigate based on role (registration creates Visitor by default)
            switch (role) {
              case 'Admin':
                this.router.navigate(['/admin']);
                break;
              case 'Manager':
                this.router.navigate(['/dashboard']);
                break;
              case 'Visitor':
                this.router.navigate(['/visitor']);
                break;
              default:
                this.router.navigate(['/']);
            }
          }
        })
      ),
    { dispatch: false }
  );

  logout$ = createEffect(
    () =>
      this.actions$.pipe(
        ofType(AuthActions.logout),
        tap(() => {
          if (isPlatformBrowser(this.platformId)) {
            // Navigate to home
            this.router.navigate(['/']);
          }
        })
      ),
    { dispatch: false }
  );
}
