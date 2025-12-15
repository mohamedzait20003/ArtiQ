import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Store } from '@ngrx/store';
import { Observable, map, take } from 'rxjs';
import { selectIsAuthenticated, selectRole } from '../store/auth.selectors';
import { combineLatest } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class LandingGuard implements CanActivate {
  
  constructor(
    private router: Router,
    private store: Store
  ) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean> {
    return combineLatest([
      this.store.select(selectIsAuthenticated),
      this.store.select(selectRole)
    ]).pipe(
      take(1),
      map(([isAuthenticated, role]) => {
        if (isAuthenticated) {
          // Redirect authenticated users to their role-based dashboard
          this.redirectToRoleDashboard(role);
          return false;
        }
        return true;
      })
    );
  }

  private redirectToRoleDashboard(role: string | null): void {
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
}
