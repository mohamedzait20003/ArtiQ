import { Directive, ElementRef, HostListener, Input } from '@angular/core';

@Directive({
  selector: '[appHoverEffect]',
  standalone: true
})
export class HoverEffectDirective {
  @Input() appHoverEffect: 'lift' | 'glow' | 'scale' = 'lift';

  constructor(private el: ElementRef) {}

  @HostListener('mouseenter')
  onMouseEnter(): void {
    this.applyEffect(true);
  }

  @HostListener('mouseleave')
  onMouseLeave(): void {
    this.applyEffect(false);
  }

  private applyEffect(isHovering: boolean): void {
    const element = this.el.nativeElement;
    
    if (isHovering) {
      switch (this.appHoverEffect) {
        case 'lift':
          element.style.transform = 'translateY(-4px)';
          element.style.boxShadow = '0 10px 25px rgba(0,0,0,0.1)';
          break;
        case 'glow':
          element.style.boxShadow = '0 0 20px rgba(255, 193, 7, 0.5)';
          break;
        case 'scale':
          element.style.transform = 'scale(1.05)';
          break;
      }
    } else {
      element.style.transform = '';
      element.style.boxShadow = '';
    }
  }
}
