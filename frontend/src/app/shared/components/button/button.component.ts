import { Component, Input, Output, EventEmitter, HostBinding } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

export type ButtonVariant = 'primary' | 'secondary' | 'tertiary' | 'danger';
export type ButtonSize = 'sm' | 'md' | 'lg';

@Component({
  selector: 'app-button',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <button 
      *ngIf="!routerLink; else routerLinkButton"
      [type]="type"
      [disabled]="disabled || loading"
      [class]="buttonClasses"
      (click)="handleClick()">
      <span *ngIf="!loading">{{ label }}</span>
      <span *ngIf="loading" class="flex items-center space-x-2">
        <span class="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
        <span>{{ loadingText }}</span>
      </span>
    </button>
    <ng-template #routerLinkButton>
      <a 
        [routerLink]="routerLink"
        [class]="buttonClasses"
        (click)="handleClick()">
        <span *ngIf="!loading">{{ label }}</span>
        <span *ngIf="loading" class="flex items-center space-x-2">
          <span class="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
          <span>{{ loadingText }}</span>
        </span>
      </a>
    </ng-template>
  `
})
export class ButtonComponent {
  @Input() label: string = '';
  @Input() variant: ButtonVariant = 'primary';
  @Input() size: ButtonSize = 'md';
  @Input() disabled: boolean = false;
  @Input() loading: boolean = false;
  @Input() loadingText: string = 'Loading...';
  @Input() routerLink: string | string[] | null = null;
  @Input() type: 'button' | 'submit' | 'reset' = 'button';
  @Input() fullWidth: boolean = false;
  @Output() click = new EventEmitter<void>();

  get buttonClasses(): string {
    const baseClasses = 'inline-flex items-center justify-center font-semibold rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
    
    const sizeClasses = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-6 py-3 text-lg'
    };

    const variantClasses = {
      primary: 'bg-gradient-to-r from-yellow-400 to-orange-500 hover:from-yellow-500 hover:to-orange-600 text-gray-900 focus:ring-yellow-500 shadow-md hover:shadow-lg',
      secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-900 focus:ring-gray-400',
      tertiary: 'bg-transparent border-2 border-gray-300 hover:border-gray-400 text-gray-900 focus:ring-gray-400',
      danger: 'bg-red-500 hover:bg-red-600 text-white focus:ring-red-500'
    };

    const widthClass = this.fullWidth ? 'w-full' : '';

    return `${baseClasses} ${sizeClasses[this.size]} ${variantClasses[this.variant]} ${widthClass}`;
  }

  handleClick(): void {
    this.click.emit();
  }
}
