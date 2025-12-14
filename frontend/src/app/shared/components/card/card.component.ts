import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div [class]="cardClasses">
      <ng-content></ng-content>
    </div>
  `
})
export class CardComponent {
  @Input() hoverable: boolean = false;
  @Input() padding: 'none' | 'sm' | 'md' | 'lg' = 'md';
  @Input() border: boolean = true;
  @Input() shadow: 'none' | 'sm' | 'md' | 'lg' = 'md';
  @Input() rounded: 'none' | 'sm' | 'md' | 'lg' = 'lg';

  get cardClasses(): string {
    const baseClass = 'bg-white transition-all duration-300';

    const paddingClasses = {
      none: '',
      sm: 'p-3',
      md: 'p-6',
      lg: 'p-8'
    };

    const borderClass = this.border ? 'border border-gray-200' : '';

    const shadowClasses = {
      none: '',
      sm: 'shadow-sm',
      md: 'shadow-md',
      lg: 'shadow-lg'
    };

    const roundedClasses = {
      none: '',
      sm: 'rounded-md',
      md: 'rounded-lg',
      lg: 'rounded-xl'
    };

    const hoverClass = this.hoverable ? 'hover:shadow-lg hover:-translate-y-1 cursor-pointer' : '';

    return `${baseClass} ${paddingClasses[this.padding]} ${borderClass} ${shadowClasses[this.shadow]} ${roundedClasses[this.rounded]} ${hoverClass}`;
  }
}
