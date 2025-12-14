import { Component, Input, Output, EventEmitter, forwardRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

@Component({
  selector: 'app-input',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="w-full">
      <label *ngIf="label" [for]="id" class="block text-sm font-medium text-gray-700 mb-2">
        {{ label }}
        <span *ngIf="required" class="text-red-500">*</span>
      </label>
      <div class="relative">
        <input
          [id]="id"
          [type]="type"
          [placeholder]="placeholder"
          [value]="value"
          [disabled]="disabled"
          [required]="required"
          [class]="inputClasses"
          (input)="onInput($event)"
          (blur)="onBlur()"
          (focus)="onFocus()"
        />
        <span *ngIf="icon" class="absolute right-3 top-3 text-gray-400">
          {{ icon }}
        </span>
      </div>
      <p *ngIf="error" class="text-red-500 text-sm mt-1">{{ error }}</p>
      <p *ngIf="hint" class="text-gray-500 text-sm mt-1">{{ hint }}</p>
    </div>
  `
})
export class InputComponent implements ControlValueAccessor {
  @Input() id: string = 'input-' + Math.random().toString(36).substr(2, 9);
  @Input() type: string = 'text';
  @Input() placeholder: string = '';
  @Input() label: string = '';
  @Input() error: string = '';
  @Input() hint: string = '';
  @Input() icon: string = '';
  @Input() disabled: boolean = false;
  @Input() required: boolean = false;
  @Input() value: string = '';
  @Output() valueChange = new EventEmitter<string>();
  @Output() focus = new EventEmitter<void>();
  @Output() blur = new EventEmitter<void>();

  get inputClasses(): string {
    const baseClass = 'w-full px-4 py-2 border rounded-lg transition-colors focus:outline-none focus:ring-2 disabled:bg-gray-100 disabled:cursor-not-allowed';
    const borderClass = this.error 
      ? 'border-red-500 focus:ring-red-500' 
      : 'border-gray-300 focus:ring-yellow-500 focus:border-yellow-500';
    
    return `${baseClass} ${borderClass}`;
  }

  onInput(event: any): void {
    this.value = event.target.value;
    this.valueChange.emit(this.value);
    this.onChange(this.value);
  }

  onFocus(): void {
    this.focus.emit();
  }

  onBlur(): void {
    this.blur.emit();
    this.onTouched();
  }

  writeValue(value: any): void {
    this.value = value || '';
  }

  onChange: (value: any) => void = () => {};
  onTouched: () => void = () => {};

  registerOnChange(fn: (value: any) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    this.disabled = isDisabled;
  }
}
