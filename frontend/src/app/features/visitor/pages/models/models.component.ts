import { Component, ChangeDetectionStrategy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { map, switchMap, debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { Store } from '@ngrx/store';
import { selectUser } from '../../../../store/auth.selectors';
import { VisitorService, Model } from '../../services/visitor.service';

export type SortOption = 'name' | 'size';

@Component({
  selector: 'app-visitor-models',
  standalone: true,
  imports: [CommonModule, FormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './models.component.html',
  styleUrls: ['./models.component.css']
})
export class VisitorModelsComponent implements OnInit {
  sortOptions: SortOption[] = ['name', 'size'];
  
  sortBy: SortOption = 'name';
  viewMode: 'grid' | 'list' = 'grid';

  user$: Observable<any>;

  searchQuery = '';
  private searchSubject = new Subject<string>();
  private modelsSubject = new BehaviorSubject<Model[]>([]);
  filteredModels$: Observable<Model[]>;

  constructor(
    private store: Store,
    private visitorService: VisitorService
  ) {
    this.user$ = this.store.select(selectUser);
    this.filteredModels$ = this.modelsSubject.asObservable().pipe(
      map(models => this.filterAndSort(models))
    );

    // Set up search with debounce
    this.searchSubject.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      switchMap(query => this.visitorService.searchModels(query))
    ).subscribe(models => {
      this.modelsSubject.next(models);
    });
  }

  ngOnInit(): void {
    // Load initial models
    this.visitorService.getModels().subscribe(models => {
      this.modelsSubject.next(models);
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

  viewModelDetails(modelId: string): void {
    console.log('View model details:', modelId);
    // Visitor users can only view, not interact
  }

  formatSize(sizeInBytes: number): string {
    const mb = sizeInBytes / (1024 * 1024);
    if (mb >= 1000) {
      return (mb / 1024).toFixed(1) + ' GB';
    }
    return mb.toFixed(1) + ' MB';
  }
}
