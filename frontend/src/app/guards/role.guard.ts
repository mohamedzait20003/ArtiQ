import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Store } from '@ngrx/store';
import { Observable, map, take } from 'rxjs';
import { selectIsAuthenticated, selectRole } from '../store/auth.selectors';
import { combineLatest } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class RoleGuard implements CanActivate {
  
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
      map(([isAuthenticated, userRole]) => {
        if (!isAuthenticated) {
          this.router.navigate(['/auth/login']);
          return false;
        }

        // Get required roles from route data
        const requiredRoles: string[] = route.data['roles'] || [];
        
        // If no roles specified, just check authentication
        if (requiredRoles.length === 0) {
          return true;
        }

        // Check if user has the required role
        if (userRole && requiredRoles.includes(userRole)) {
          return true;
        }

        // User doesn't have required role, redirect to their dashboard
        this.redirectToRoleDashboard(userRole);
        return false;
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
