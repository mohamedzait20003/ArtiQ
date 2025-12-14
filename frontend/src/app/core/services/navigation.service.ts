import { Injectable } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { BehaviorSubject, Observable } from 'rxjs';
import { filter } from 'rxjs/operators';

export interface NavigationEvent {
  path: string;
  timestamp: Date;
  source: 'link' | 'button' | 'redirect';
}

@Injectable({
  providedIn: 'root'
})
export class NavigationService {
  private navigationHistory$ = new BehaviorSubject<NavigationEvent[]>([]);
  private currentPath$ = new BehaviorSubject<string>('');

  constructor(private router: Router) {
    this.initializeNavigation();
  }

  private initializeNavigation(): void {
    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe((event: NavigationEnd) => {
        const navEvent: NavigationEvent = {
          path: event.url,
          timestamp: new Date(),
          source: 'redirect'
        };
        this.addToHistory(navEvent);
        this.currentPath$.next(event.url);
      });
  }

  navigateTo(path: string, source: 'link' | 'button' | 'redirect' = 'button'): void {
    const navEvent: NavigationEvent = {
      path,
      timestamp: new Date(),
      source
    };
    this.addToHistory(navEvent);
    this.router.navigate([path]);
  }

  private addToHistory(event: NavigationEvent): void {
    const currentHistory = this.navigationHistory$.value;
    const newHistory = [...currentHistory, event].slice(-50); // Keep last 50
    this.navigationHistory$.next(newHistory);
  }

  getHistory(): Observable<NavigationEvent[]> {
    return this.navigationHistory$.asObservable();
  }

  getCurrentPath(): Observable<string> {
    return this.currentPath$.asObservable();
  }

  getLastPath(): string {
    const history = this.navigationHistory$.value;
    return history.length > 1 ? history[history.length - 2]?.path : '/';
  }

  goBack(): void {
    this.router.navigate([this.getLastPath()]);
  }
}
