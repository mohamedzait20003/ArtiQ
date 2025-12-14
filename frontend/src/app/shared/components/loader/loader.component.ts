import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoaderService, LoaderState } from '../../../core/services/loader.service';

@Component({
  selector: 'app-loader',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div *ngIf="loader.isLoading" class="fixed inset-0 z-40 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-8 flex flex-col items-center space-y-4">
        <!-- Spinner -->
        <div class="relative w-12 h-12">
          <div class="absolute inset-0 border-4 border-gray-200 rounded-full"></div>
          <div class="absolute inset-0 border-4 border-transparent border-t-yellow-500 rounded-full animate-spin"></div>
        </div>
        <!-- Loading text -->
        <p *ngIf="loader.message" class="text-gray-700 font-medium">{{ loader.message }}</p>
        <p *ngIf="!loader.message" class="text-gray-700 font-medium">Loading...</p>
      </div>
    </div>
  `
})
export class LoaderComponent implements OnInit {
  loader: LoaderState = { isLoading: false };

  constructor(private loaderService: LoaderService) {}

  ngOnInit(): void {
    this.loaderService.getLoader().subscribe(state => {
      this.loader = state;
    });
  }
}
