import { Injectable } from '@angular/core';
import {
  HttpInterceptor,
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpResponse
} from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

@Injectable()
export class LoggingInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const startTime = performance.now();

    return next.handle(req).pipe(
      tap(
        (event: HttpEvent<any>) => {
          if (event instanceof HttpResponse) {
            const endTime = performance.now();
            const duration = endTime - startTime;

            this.logResponse(req, event, duration);
          }
        },
        (error) => {
          const endTime = performance.now();
          const duration = endTime - startTime;

          this.logError(req, error, duration);
        }
      )
    );
  }

  private logResponse(req: HttpRequest<any>, res: HttpResponse<any>, duration: number): void {
    const message = `${req.method} ${req.url} [${res.status}] - ${duration.toFixed(2)}ms`;

    if (res.status >= 200 && res.status < 300) {
      console.log('%c' + message, 'color: green;');
    } else if (res.status >= 400) {
      console.log('%c' + message, 'color: orange;');
    } else {
      console.log('%c' + message, 'color: blue;');
    }

    if (res.body) {
      console.log('Response Body:', res.body);
    }
  }

  private logError(req: HttpRequest<any>, error: any, duration: number): void {
    const status = error.status || 'Unknown';
    const message = `${req.method} ${req.url} [${status}] - ${duration.toFixed(2)}ms`;

    console.log('%c' + message, 'color: red;');
    console.log('Error Details:', error);
  }
}
