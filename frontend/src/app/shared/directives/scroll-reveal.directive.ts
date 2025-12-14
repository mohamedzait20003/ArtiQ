import { Directive, ElementRef, HostListener, Input } from '@angular/core';

@Directive({
  selector: '[appScrollReveal]',
  standalone: true
})
export class ScrollRevealDirective {
  @Input() appScrollReveal: 'fadeIn' | 'slideUp' | 'slideDown' | 'slideLeft' | 'slideRight' = 'fadeIn';
  @Input() appScrollRevealDelay: number = 0;

  private hasBeenInView = false;

  constructor(private el: ElementRef) {
    this.el.nativeElement.style.opacity = '0';
  }

  @HostListener('window:scroll')
  onWindowScroll(): void {
    if (this.hasBeenInView) return;

    if (this.isElementInViewport()) {
      this.hasBeenInView = true;
      this.animateElement();
    }
  }

  ngOnInit(): void {
    // Check if already in viewport on init
    setTimeout(() => {
      if (this.isElementInViewport()) {
        this.hasBeenInView = true;
        this.animateElement();
      }
    }, 0);
  }

  private isElementInViewport(): boolean {
    const rect = this.el.nativeElement.getBoundingClientRect();
    return rect.top < window.innerHeight && rect.bottom > 0;
  }

  private animateElement(): void {
    const element = this.el.nativeElement;
    
    setTimeout(() => {
      element.style.animation = `${this.appScrollReveal} 0.6s ease-out forwards`;
      element.style.opacity = '1';
    }, this.appScrollRevealDelay);
  }
}
