import { Injectable } from '@angular/core';
import {
  HttpInterceptor,
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, finalize } from 'rxjs/operators';
import { LoaderService } from '../../core/services/loader.service';
import { ToastService } from '../../core/services/toast.service';

export interface ErrorResponse {
  status: number;
  message: string;
  errors?: any;
}

@Injectable()
export class ErrorInterceptor implements HttpInterceptor {
  constructor(
    private loaderService: LoaderService,
    private toastService: ToastService
  ) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(req).pipe(
      catchError((error: HttpErrorResponse) => {
        this.handleError(error);
        return throwError(() => error);
      }),
      finalize(() => {
        this.loaderService.hide();
      })
    );
  }

  private handleError(error: HttpErrorResponse): void {
    const errorResponse: ErrorResponse = {
      status: error.status,
      message: this.getErrorMessage(error),
      errors: error.error?.errors || null
    };

    switch (error.status) {
      case 0:
        this.toastService.error('Network error. Please check your connection.');
        break;
      case 400:
        this.toastService.error(errorResponse.message || 'Bad request. Please check your input.');
        break;
      case 401:
        this.toastService.error('Unauthorized. Please log in again.');
        // Could trigger logout here
        break;
      case 403:
        this.toastService.error('Forbidden. You do not have access to this resource.');
        break;
      case 404:
        this.toastService.error('Resource not found.');
        break;
      case 409:
        this.toastService.error('Conflict. The resource may have been modified.');
        break;
      case 500:
        this.toastService.error('Server error. Please try again later.');
        break;
      case 502:
      case 503:
      case 504:
        this.toastService.error('Service unavailable. Please try again later.');
        break;
      default:
        this.toastService.error(errorResponse.message || 'An unexpected error occurred.');
    }

    console.error('HTTP Error:', errorResponse);
  }

  private getErrorMessage(error: HttpErrorResponse): string {
    // Try to get message from response body
    if (error.error?.message) {
      return error.error.message;
    }

    if (error.error?.error?.message) {
      return error.error.error.message;
    }

    // Fallback to status text
    return error.statusText || 'An error occurred';
  }
}
