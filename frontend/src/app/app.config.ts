import { ApplicationConfig, provideBrowserGlobalErrorListeners, provideZoneChangeDetection, isDevMode, APP_INITIALIZER } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withFetch } from '@angular/common/http';
import { routes } from './app.routes';
import { provideClientHydration, withEventReplay } from '@angular/platform-browser';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { provideStore } from '@ngrx/store';
import { provideEffects } from '@ngrx/effects';
import { provideStoreDevtools } from '@ngrx/store-devtools';
import { localStorageSync } from 'ngrx-store-localstorage';
import { ActionReducer, MetaReducer } from '@ngrx/store';
import { authReducer } from './store/auth.reducer';
import { AuthEffects } from './store/auth.effects';
import { ApiService } from './core/services/api.service';

export function localStorageSyncReducer(reducer: ActionReducer<any>): ActionReducer<any> {
  // Only sync on browser, skip during SSR
  if (typeof window === 'undefined') {
    return reducer;
  }
  
  return localStorageSync({
    keys: ['auth'],
    rehydrate: true,
    storage: localStorage
  })(reducer);
}

const metaReducers: Array<MetaReducer<any, any>> = [localStorageSyncReducer];

/**
 * Initialize the app by authenticating with the backend
 */
function initializeApp(apiService: ApiService) {
  return () => {
    return apiService.authenticate().toPromise().catch((error: any) => {
      console.warn('Failed to authenticate during app initialization:', error);
      // Don't fail app startup if authentication fails
      return Promise.resolve();
    });
  };
}

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideClientHydration(withEventReplay()),
    provideAnimationsAsync(),
    provideHttpClient(withFetch()),
    provideStore({ auth: authReducer }, { metaReducers }),
    provideEffects([AuthEffects]),
    provideStoreDevtools({ maxAge: 25, logOnly: !isDevMode() }),
    ApiService,
    {
      provide: APP_INITIALIZER,
      useFactory: initializeApp,
      deps: [ApiService],
      multi: true
    }
  ]
};
