import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface LoaderState {
  isLoading: boolean;
  message?: string;
}

@Injectable({
  providedIn: 'root'
})
export class LoaderService {
  private loader$ = new BehaviorSubject<LoaderState>({ isLoading: false });
  private requestCount = 0;

  getLoader(): Observable<LoaderState> {
    return this.loader$.asObservable();
  }

  show(message?: string): void {
    this.requestCount++;
    this.updateLoader(true, message);
  }

  hide(): void {
    this.requestCount = Math.max(0, this.requestCount - 1);
    if (this.requestCount === 0) {
      this.updateLoader(false);
    }
  }

  hideAll(): void {
    this.requestCount = 0;
    this.updateLoader(false);
  }

  private updateLoader(isLoading: boolean, message?: string): void {
    this.loader$.next({ isLoading, message });
  }
}
