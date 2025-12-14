import { Component, signal } from '@angular/core';
import { RouterOutlet, RouterLink } from '@angular/router';
import { Store } from '@ngrx/store';
import { selectIsAuthenticated } from './store/auth.selectors';
import { CommonModule } from '@angular/common';
import { Observable } from 'rxjs';
import * as AuthActions from './store/auth.actions';
import { MatIconModule } from '@angular/material/icon';
import { ToastContainerComponent } from './shared/components/toast-container/toast-container.component';
import { LoaderComponent } from './shared/components/loader/loader.component';
import { NavigationService } from './core/services/navigation.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, CommonModule, MatIconModule, ToastContainerComponent, LoaderComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})

export class App {
  protected readonly title = signal('frontend');
  isAuthenticated$: Observable<boolean>;

  constructor(
    private store: Store,
    private navigationService: NavigationService
  ) {
    this.isAuthenticated$ = this.store.select(selectIsAuthenticated);
  }

  logout(): void {
    this.store.dispatch(AuthActions.logout());
  }
}
