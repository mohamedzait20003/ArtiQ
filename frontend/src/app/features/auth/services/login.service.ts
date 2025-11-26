import { Injectable } from '@angular/core';
import { Store } from '@ngrx/store';
import * as AuthActions from '../../../store/auth.actions';

@Injectable({
  providedIn: 'root'
})
export class LoginService {
  
  constructor(private store: Store) {}

  login(email: string, password: string, isAdmin: boolean = false): void {
    this.store.dispatch(AuthActions.login({ email, password, isAdmin }));
  }
}
