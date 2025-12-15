export class ValidationUtils {
  static isEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  static isPassword(password: string, minLength: number = 8): boolean {
    // At least one uppercase, one lowercase, one number, one special char
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return passwordRegex.test(password) && password.length >= minLength;
  }

  static isUsername(username: string): boolean {
    const usernameRegex = /^[a-zA-Z0-9_-]{3,20}$/;
    return usernameRegex.test(username);
  }

  static isUrl(url: string): boolean {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }

  static isPhoneNumber(phone: string): boolean {
    const phoneRegex = /^[+]?[(]?[0-9]{3}[)]?[-\s.]?[0-9]{3}[-\s.]?[0-9]{4,6}$/;
    return phoneRegex.test(phone);
  }

  static isEmpty(value: any): boolean {
    return !value || (typeof value === 'string' && value.trim() === '') || 
           (Array.isArray(value) && value.length === 0) ||
           (typeof value === 'object' && Object.keys(value).length === 0);
  }

  static isStrongPassword(password: string): { isStrong: boolean; feedback: string[] } {
    const feedback: string[] = [];

    if (password.length < 8) {
      feedback.push('Password must be at least 8 characters long');
    }

    if (!/[A-Z]/.test(password)) {
      feedback.push('Must contain an uppercase letter');
    }

    if (!/[a-z]/.test(password)) {
      feedback.push('Must contain a lowercase letter');
    }

    if (!/[0-9]/.test(password)) {
      feedback.push('Must contain a number');
    }

    if (!/[@$!%*?&]/.test(password)) {
      feedback.push('Must contain a special character (@$!%*?&)');
    }

    return {
      isStrong: feedback.length === 0,
      feedback
    };
  }
}

export class StringUtils {
  static capitalize(str: string): string {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  static camelToKebab(str: string): string {
    return str.replace(/([a-z0-9]|(?=[A-Z]))([A-Z])/g, '$1-$2').toLowerCase();
  }

  static kebabToCamel(str: string): string {
    return str.replace(/-([a-z])/g, (g) => g[1].toUpperCase());
  }

  static slugify(str: string): string {
    return str
      .toLowerCase()
      .trim()
      .replace(/[^\w\s-]/g, '')
      .replace(/[\s_-]+/g, '-')
      .replace(/^-+|-+$/g, '');
  }

  static truncate(str: string, length: number, suffix: string = '...'): string {
    if (str.length <= length) return str;
    return str.substring(0, length - suffix.length) + suffix;
  }

  static removeSpecialChars(str: string): string {
    return str.replace(/[^a-zA-Z0-9\s]/g, '');
  }
}

export class DateUtils {
  static getDaysDifference(date1: Date, date2: Date = new Date()): number {
    const oneDay = 24 * 60 * 60 * 1000;
    return Math.round(Math.abs((date1.getTime() - date2.getTime()) / oneDay));
  }

  static isToday(date: Date): boolean {
    const today = new Date();
    return date.getDate() === today.getDate() &&
           date.getMonth() === today.getMonth() &&
           date.getFullYear() === today.getFullYear();
  }

  static isYesterday(date: Date): boolean {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    return date.getDate() === yesterday.getDate() &&
           date.getMonth() === yesterday.getMonth() &&
           date.getFullYear() === yesterday.getFullYear();
  }

  static formatDate(date: Date, format: string = 'MM/DD/YYYY'): string {
    const d = new Date(date);
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const year = d.getFullYear();
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    const seconds = String(d.getSeconds()).padStart(2, '0');

    return format
      .replace('MM', month)
      .replace('DD', day)
      .replace('YYYY', String(year))
      .replace('HH', hours)
      .replace('mm', minutes)
      .replace('SS', seconds);
  }
}
