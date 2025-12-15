import { Injectable } from '@angular/core';
import { Store } from '@ngrx/store';
import * as AuthActions from '../../../store/auth.actions';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  
  constructor(private store: Store) {}

  login(email: string, password: string): void {
    this.store.dispatch(AuthActions.login({ email, password }));
  }

  register(name: string, email: string, password: string, confirmPassword: string): void {
    this.store.dispatch(AuthActions.register({ 
      name, 
      email, 
      password, 
      confirm_password: confirmPassword 
    }));
  }
}
