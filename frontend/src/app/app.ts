import { Component, signal } from '@angular/core';
import { RouterOutlet, RouterLink } from '@angular/router';
import { Store } from '@ngrx/store';
import { selectIsAuthenticated } from './store/auth.selectors';
import { CommonModule } from '@angular/common';
import { Observable } from 'rxjs';
import * as AuthActions from './store/auth.actions';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, CommonModule, MatIconModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})

export class App {
  protected readonly title = signal('frontend');
  isAuthenticated$: Observable<boolean>;

  constructor(private store: Store) {
    this.isAuthenticated$ = this.store.select(selectIsAuthenticated);
  }

  logout(): void {
    this.store.dispatch(AuthActions.logout());
  }
}
