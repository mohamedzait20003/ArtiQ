import { Component, ChangeDetectionStrategy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { map, switchMap, debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { DashboardService, Model } from '../../services/dashboard.service';
import { ToastService } from '../../../../core/services/toast.service';

export type SortOption = 'name' | 'size';

@Component({
  selector: 'app-dashboard-models',
  standalone: true,
  imports: [CommonModule, FormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './models.component.html',
  styleUrls: ['./models.component.css']
})
export class ModelsComponent implements OnInit {
  sortOptions: SortOption[] = ['name', 'size'];
  
  sortBy: SortOption = 'name';
  viewMode: 'grid' | 'list' = 'grid';

  searchQuery = '';
  private searchSubject = new Subject<string>();
  private modelsSubject = new BehaviorSubject<Model[]>([]);
  filteredModels$: Observable<Model[]>;

  editingModel: Model | null = null;
  showEditModal = false;
  showDeleteModal = false;
  modelToDelete: Model | null = null;

  constructor(
    private dashboardService: DashboardService,
    private toastService: ToastService
  ) {
    this.filteredModels$ = this.modelsSubject.asObservable().pipe(
      map(models => this.filterAndSort(models))
    );

    // Set up search with debounce
    this.searchSubject.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      switchMap(query => this.dashboardService.searchModels(query))
    ).subscribe(models => {
      this.modelsSubject.next(models);
    });
  }

  ngOnInit(): void {
    // Load initial models
    this.loadModels();
  }

  private loadModels(): void {
    this.dashboardService.getModels().subscribe({
      next: (models) => {
        this.modelsSubject.next(models);
      },
      error: (error) => {
        this.toastService.error('Failed to load models');
        console.error('Error loading models:', error);
      }
    });
  }

  private filterAndSort(models: Model[]): Model[] {
    return this.sortModels(models);
  }

  private sortModels(models: Model[]): Model[] {
    return [...models].sort((a, b) => {
      switch (this.sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'size':
          return b.size - a.size;
        default:
          return 0;
      }
    });
  }

  onSortChange(sort: SortOption): void {
    this.sortBy = sort;
    this.updateFilters();
  }

  onSearchChange(): void {
    this.searchSubject.next(this.searchQuery);
  }

  toggleViewMode(): void {
    this.viewMode = this.viewMode === 'grid' ? 'list' : 'grid';
  }

  private updateFilters(): void {
    // Trigger re-filtering of current models
    const currentModels = this.modelsSubject.getValue();
    this.modelsSubject.next([...currentModels]);
  }

  openEditModal(model: Model): void {
    this.editingModel = { ...model };
    this.showEditModal = true;
  }

  closeEditModal(): void {
    this.showEditModal = false;
    this.editingModel = null;
  }

  saveModel(): void {
    if (!this.editingModel) return;

    this.dashboardService.updateModel(this.editingModel.id, {
      name: this.editingModel.name,
      description: this.editingModel.description
    }).subscribe({
      next: () => {
        this.toastService.success('Model updated successfully');
        this.closeEditModal();
        this.loadModels();
      },
      error: (error) => {
        this.toastService.error('Failed to update model');
        console.error('Error updating model:', error);
      }
    });
  }

  openDeleteModal(model: Model): void {
    this.modelToDelete = model;
    this.showDeleteModal = true;
  }

  closeDeleteModal(): void {
    this.showDeleteModal = false;
    this.modelToDelete = null;
  }

  confirmDelete(): void {
    if (!this.modelToDelete) return;

    this.dashboardService.deleteModel(this.modelToDelete.id).subscribe({
      next: () => {
        this.toastService.success('Model deleted successfully');
        this.closeDeleteModal();
        this.loadModels();
      },
      error: (error) => {
        this.toastService.error('Failed to delete model');
        console.error('Error deleting model:', error);
      }
    });
  }

  formatSize(sizeInBytes: number): string {
    const mb = sizeInBytes / (1024 * 1024);
    if (mb >= 1000) {
      return (mb / 1024).toFixed(1) + ' GB';
    }
    return mb.toFixed(1) + ' MB';
  }
}
