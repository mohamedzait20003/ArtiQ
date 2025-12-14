import { Component, ChangeDetectionStrategy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BehaviorSubject } from 'rxjs';
import { ApiService } from '../../../../core/services/api.service';
import { ArtifactMetadata } from '../../../../core/services/api.types';
import { ToastService } from '../../../../core/services/toast.service';

export type SortOption = 'name' | 'size' | 'downloads' | 'recent';

@Component({
  selector: 'app-datasets',
  standalone: true,
  imports: [CommonModule, FormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './datasets.component.html',
  styleUrls: ['./datasets.component.css']
})
export class DatasetsComponent implements OnInit {
  categories = ['All'];
  sortOptions: SortOption[] = ['name', 'size', 'downloads', 'recent'];
  
  selectedCategory = 'All';
  sortBy: SortOption = 'recent';
  viewMode: 'grid' | 'list' = 'grid';

  datasets$ = new BehaviorSubject<any[]>([]);
  filteredDatasets$ = new BehaviorSubject<any[]>([]);

  searchQuery = '';
  isLoading = true;

  trackByDataset(_index: number, item: any) {
    return item?.id ?? _index;
  }

  constructor(
    private apiService: ApiService,
    private toastService: ToastService
  ) {}

  ngOnInit(): void {
    this.fetchDatasets();
  }

  private fetchDatasets(): void {
    this.isLoading = true;
    this.apiService.getArtifactsByType('dataset').subscribe({
      next: (artifacts: ArtifactMetadata[]) => {
        // Transform artifact metadata to display format
        const displayDatasets = artifacts.map((artifact, idx) => ({
          id: idx + 1,
          name: artifact.name,
          author: 'Unknown',
          category: 'Dataset',
          description: `Artifact ID: ${artifact.id}`,
          size: Math.floor(Math.random() * 5000) + 100, // MB
          downloads: Math.floor(Math.random() * 50000),
          likes: Math.floor(Math.random() * 5000),
          updated: 'recently',
          tags: [artifact.type],
          artifactId: artifact.id,
          artifactType: artifact.type
        }));

        this.datasets$.next(displayDatasets);
        this.applyFilters();
        this.isLoading = false;
      },
      error: (err: any) => {
        console.error('Error fetching datasets:', err);
        this.toastService.error('Failed to load datasets');
        this.isLoading = false;
        this.datasets$.next([]);
        this.filteredDatasets$.next([]);
      }
    });
  }

  selectCategory(category: string): void {
    this.selectedCategory = category;
    this.applyFilters();
  }

  setSortBy(sort: SortOption): void {
    this.sortBy = sort;
    this.applyFilters();
  }

  toggleViewMode(): void {
    this.viewMode = this.viewMode === 'grid' ? 'list' : 'grid';
  }

  onSearchChange(): void {
    this.applyFilters();
  }

  likeDataset(dataset: any): void {
    dataset.likes += 1;
    this.toastService.success(`Liked ${dataset.name}!`, 2000);
  }

  downloadDataset(dataset: any): void {
    this.toastService.info(`Downloading ${dataset.name}...`, 2000);
  }

  private applyFilters(): void {
    const datasets = this.datasets$.value;
    let filtered = this.filterDatasets(datasets);
    filtered = this.sortDatasets(filtered);
    this.filteredDatasets$.next(filtered);
  }

  private filterDatasets(datasets: any[]): any[] {
    let filtered = datasets;

    if (this.selectedCategory !== 'All') {
      filtered = filtered.filter(d => d.category === this.selectedCategory);
    }

    if (this.searchQuery) {
      const query = this.searchQuery.toLowerCase();
      filtered = filtered.filter(d => 
        d.name.toLowerCase().includes(query) ||
        d.author.toLowerCase().includes(query) ||
        d.description.toLowerCase().includes(query) ||
        d.tags.some((tag: string) => tag.toLowerCase().includes(query))
      );
    }

    return filtered;
  }

  private sortDatasets(datasets: any[]): any[] {
    const sorted = [...datasets];
    
    switch (this.sortBy) {
      case 'name':
        sorted.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'size':
        sorted.sort((a, b) => b.size - a.size);
        break;
      case 'downloads':
        sorted.sort((a, b) => b.downloads - a.downloads);
        break;
      case 'recent':
      default:
        // Keep original order
        break;
    }
    
    return sorted;
  }

  formatSize(mb: number): string {
    if (mb >= 1024) {
      return (mb / 1024).toFixed(2) + ' GB';
    }
    return mb.toFixed(0) + ' MB';
  }

  formatNumber(num: number): string {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  }
}
