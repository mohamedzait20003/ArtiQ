import { Component, ChangeDetectionStrategy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { map, switchMap, debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { Store } from '@ngrx/store';
import { selectUser } from '../../../../store/auth.selectors';
import { VisitorService, Dataset } from '../../services/visitor.service';

export type SortOption = 'name' | 'size';

@Component({
  selector: 'app-visitor-datasets',
  standalone: true,
  imports: [CommonModule, FormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './datasets.component.html',
  styleUrls: ['./datasets.component.css']
})
export class VisitorDatasetsComponent implements OnInit {
  sortOptions: SortOption[] = ['name', 'size'];
  
  sortBy: SortOption = 'name';
  viewMode: 'grid' | 'list' = 'grid';

  user$: Observable<any>;

  searchQuery = '';
  private searchSubject = new Subject<string>();
  private datasetsSubject = new BehaviorSubject<Dataset[]>([]);
  filteredDatasets$: Observable<Dataset[]>;

  constructor(
    private store: Store,
    private visitorService: VisitorService
  ) {
    this.user$ = this.store.select(selectUser);
    this.filteredDatasets$ = this.datasetsSubject.asObservable().pipe(
      map(datasets => this.filterAndSort(datasets))
    );

    // Set up search with debounce
    this.searchSubject.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      switchMap(query => this.visitorService.searchDatasets(query))
    ).subscribe(datasets => {
      this.datasetsSubject.next(datasets);
    });
  }

  ngOnInit(): void {
    // Load initial datasets
    this.visitorService.getDatasets().subscribe(datasets => {
      this.datasetsSubject.next(datasets);
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

  viewDatasetDetails(datasetId: string): void {
    console.log('View dataset details:', datasetId);
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
