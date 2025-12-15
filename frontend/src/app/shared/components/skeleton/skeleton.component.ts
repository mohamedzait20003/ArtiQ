import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type SkeletonType = 'text' | 'card' | 'avatar' | 'line';

@Component({
  selector: 'app-skeleton',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div [class]="skeletonClasses">
      <div class="animate-pulse bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 bg-[length:200%_100%] animate-shimmer"></div>
    </div>
  `,
  styles: [`
    @keyframes shimmer {
      0% { background-position: 200% 0; }
      100% { background-position: -200% 0; }
    }
    .animate-shimmer {
      animation: shimmer 1.5s infinite;
    }
  `]
})
export class SkeletonComponent {
  @Input() type: SkeletonType = 'text';
  @Input() width: string = '100%';
  @Input() height: string = '1rem';
  @Input() count: number = 1;

  get skeletonClasses(): string {
    let baseClass = 'rounded-md overflow-hidden';
    let dimensions = `width: ${this.width}; height: ${this.height};`;
    
    const typeClasses = {
      text: 'h-4 w-full mb-3',
      card: 'h-32 w-full rounded-lg mb-4',
      avatar: 'h-12 w-12 rounded-full',
      line: 'h-2 w-full mb-2'
    };

    return `${baseClass} ${typeClasses[this.type]}`;
  }
}
