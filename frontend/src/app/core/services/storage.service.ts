import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class StorageService {
  private readonly PREFIX = 'app_';

  setItem(key: string, value: any): void {
    try {
      const serialized = JSON.stringify(value);
      localStorage.setItem(this.PREFIX + key, serialized);
    } catch (error) {
      console.error(`Failed to save ${key}:`, error);
    }
  }

  getItem<T>(key: string, defaultValue?: T): T | null {
    try {
      const item = localStorage.getItem(this.PREFIX + key);
      return item ? JSON.parse(item) : (defaultValue || null);
    } catch (error) {
      console.error(`Failed to read ${key}:`, error);
      return defaultValue || null;
    }
  }

  removeItem(key: string): void {
    try {
      localStorage.removeItem(this.PREFIX + key);
    } catch (error) {
      console.error(`Failed to remove ${key}:`, error);
    }
  }

  clear(): void {
    try {
      Object.keys(localStorage).forEach(key => {
        if (key.startsWith(this.PREFIX)) {
          localStorage.removeItem(key);
        }
      });
    } catch (error) {
      console.error('Failed to clear storage:', error);
    }
  }

  getAll(): Record<string, any> {
    const result: Record<string, any> = {};
    try {
      Object.keys(localStorage).forEach(key => {
        if (key.startsWith(this.PREFIX)) {
          const cleanKey = key.replace(this.PREFIX, '');
          result[cleanKey] = this.getItem(cleanKey);
        }
      });
    } catch (error) {
      console.error('Failed to get all items:', error);
    }
    return result;
  }

  exists(key: string): boolean {
    return localStorage.getItem(this.PREFIX + key) !== null;
  }
}
