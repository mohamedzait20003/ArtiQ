import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';

export interface AdminUser {
  id: string;
  email: string;
  role: string;
}

@Injectable({ providedIn: 'root' })
export class AdminService {
  // This service is UI-facing only; it returns sample data for now.
  constructor() {}

  getUsers(): Observable<AdminUser[]> {
    const sample: AdminUser[] = [
      { id: '1', email: 'alice@example.com', role: 'admin' },
      { id: '2', email: 'bob@example.com', role: 'member' },
    ];
    return of(sample);
  }
}
