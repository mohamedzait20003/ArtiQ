import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class SearchService {
  private _term$ = new BehaviorSubject<string>('');
  readonly term$ = this._term$.asObservable();

  set(term: string) {
    this._term$.next(term ?? '');
  }

  clear() {
    this._term$.next('');
  }
}
