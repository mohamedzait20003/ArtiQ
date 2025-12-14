import { Injectable } from '@angular/core';
import {
  HttpInterceptor,
  HttpRequest,
  HttpHandler,
  HttpEvent
} from '@angular/common/http';
import { Observable } from 'rxjs';
import { StorageService } from '../../core/services/storage.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(private storageService: StorageService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Get token from storage
    const token = this.storageService.getItem('auth_token');

    // Clone request and add authorization header if token exists
    if (token) {
      req = req.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });
    }

    // Add common headers
    req = req.clone({
      setHeaders: {
        'Content-Type': 'application/json'
      }
    });

    return next.handle(req);
  }
}
