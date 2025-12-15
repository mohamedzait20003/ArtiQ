import { Component, ChangeDetectionStrategy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { map, switchMap, debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { DashboardService, Dataset } from '../../services/dashboard.service';
import { ToastService } from '../../../../core/services/toast.service';

export type SortOption = 'name' | 'size';

@Component({
  selector: 'app-dashboard-datasets',
  standalone: true,
  imports: [CommonModule, FormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './datasets.component.html',
  styleUrls: ['./datasets.component.css']
})
export class DatasetsComponent implements OnInit {
  sortOptions: SortOption[] = ['name', 'size'];
  
  sortBy: SortOption = 'name';
  viewMode: 'grid' | 'list' = 'grid';

  searchQuery = '';
  private searchSubject = new Subject<string>();
  private datasetsSubject = new BehaviorSubject<Dataset[]>([]);
  filteredDatasets$: Observable<Dataset[]>;

  editingDataset: Dataset | null = null;
  showEditModal = false;
  showDeleteModal = false;
  datasetToDelete: Dataset | null = null;

  constructor(
    private dashboardService: DashboardService,
    private toastService: ToastService
  ) {
    this.filteredDatasets$ = this.datasetsSubject.asObservable().pipe(
      map(datasets => this.filterAndSort(datasets))
    );

    // Set up search with debounce
    this.searchSubject.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      switchMap(query => this.dashboardService.searchDatasets(query))
    ).subscribe(datasets => {
      this.datasetsSubject.next(datasets);
    });
  }

  ngOnInit(): void {
    // Load initial datasets
    this.loadDatasets();
  }

  private loadDatasets(): void {
    this.dashboardService.getDatasets().subscribe({
      next: (datasets) => {
        this.datasetsSubject.next(datasets);
      },
      error: (error) => {
        this.toastService.error('Failed to load datasets');
        console.error('Error loading datasets:', error);
      }
    });
  }

  private filterAndSort(datasets: Dataset[]): Dataset[] {
    return this.sortDatasets(datasets);
  }

  private sortDatasets(datasets: Dataset[]): Dataset[] {
    return [...datasets].sort((a, b) => {
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
    // Trigger re-filtering of current datasets
    const currentDatasets = this.datasetsSubject.getValue();
    this.datasetsSubject.next([...currentDatasets]);
  }

  openEditModal(dataset: Dataset): void {
    this.editingDataset = { ...dataset };
    this.showEditModal = true;
  }

  closeEditModal(): void {
    this.showEditModal = false;
    this.editingDataset = null;
  }

  saveDataset(): void {
    if (!this.editingDataset) return;

    this.dashboardService.updateDataset(this.editingDataset.id, {
      name: this.editingDataset.name,
      description: this.editingDataset.description
    }).subscribe({
      next: () => {
        this.toastService.success('Dataset updated successfully');
        this.closeEditModal();
        this.loadDatasets();
      },
      error: (error) => {
        this.toastService.error('Failed to update dataset');
        console.error('Error updating dataset:', error);
      }
    });
  }

  openDeleteModal(dataset: Dataset): void {
    this.datasetToDelete = dataset;
    this.showDeleteModal = true;
  }

  closeDeleteModal(): void {
    this.showDeleteModal = false;
    this.datasetToDelete = null;
  }

  confirmDelete(): void {
    if (!this.datasetToDelete) return;

    this.dashboardService.deleteDataset(this.datasetToDelete.id).subscribe({
      next: () => {
        this.toastService.success('Dataset deleted successfully');
        this.closeDeleteModal();
        this.loadDatasets();
      },
      error: (error) => {
        this.toastService.error('Failed to delete dataset');
        console.error('Error deleting dataset:', error);
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
