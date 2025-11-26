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
}

interface LoginRequest {
  user: {
    name: string;
    isAdmin: boolean;
  };
  secret: {
    password: string;
  };
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
      switchMap(({ email, password, isAdmin }) => {
        if (!isPlatformBrowser(this.platformId)) {
          return EMPTY;
        }

        const requestBody: LoginRequest = {
          user: {
            name: email,
            isAdmin: isAdmin
          },
          secret: {
            password: password
          }
        };

        return this.http.put<string>(`${this.API_URL}/authenticate`, requestBody).pipe(
          map((bearerToken: string) => {
            // Extract token from "bearer <token>" format
            const token = bearerToken.replace('bearer ', '');
            
            return AuthActions.loginSuccess({
              token: token,
              role: isAdmin ? 'admin' : 'user',
              user: {
                id: token,
                email: email,
                name: email
              }
            });
          }),
          catchError((error) => {
            let errorMessage = 'Login failed';
            if (error.status === 400) {
              errorMessage = 'Missing or invalid fields in request';
            } else if (error.status === 401) {
              errorMessage = 'Invalid username or password';
            } else if (error.status === 501) {
              errorMessage = 'Authentication not supported';
            }
            return of(AuthActions.loginFailure({ error: errorMessage }));
          })
        );
      })
    )
  );

  loginSuccess$ = createEffect(
    () =>
      this.actions$.pipe(
        ofType(AuthActions.loginSuccess),
        tap(() => {
          if (isPlatformBrowser(this.platformId)) {
            // Navigate to dashboard
            this.router.navigate(['/dashboard']);
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
