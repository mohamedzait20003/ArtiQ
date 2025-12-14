import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
  action?: {
    label: string;
    callback: () => void;
  };
}

@Injectable({
  providedIn: 'root'
})
export class ToastService {
  private toasts$ = new BehaviorSubject<Toast[]>([]);
  private toastCounter = 0;

  getToasts(): Observable<Toast[]> {
    return this.toasts$.asObservable();
  }

  success(message: string, duration: number = 3000): void {
    this.addToast({
      message,
      type: 'success',
      duration
    });
  }

  error(message: string, duration: number = 5000): void {
    this.addToast({
      message,
      type: 'error',
      duration
    });
  }

  warning(message: string, duration: number = 4000): void {
    this.addToast({
      message,
      type: 'warning',
      duration
    });
  }

  info(message: string, duration: number = 3000): void {
    this.addToast({
      message,
      type: 'info',
      duration
    });
  }

  private addToast(toast: Omit<Toast, 'id'>): void {
    const id = `toast-${this.toastCounter++}`;
    const newToast: Toast = { id, ...toast };
    
    const currentToasts = this.toasts$.value;
    this.toasts$.next([...currentToasts, newToast]);

    if (toast.duration) {
      setTimeout(() => {
        this.removeToast(id);
      }, toast.duration);
    }
  }

  removeToast(id: string): void {
    const currentToasts = this.toasts$.value;
    this.toasts$.next(currentToasts.filter(t => t.id !== id));
  }

  clearAll(): void {
    this.toasts$.next([]);
  }
}
