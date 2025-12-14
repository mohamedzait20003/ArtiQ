import { Component, ChangeDetectionStrategy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BehaviorSubject } from 'rxjs';
import { ApiService } from '../../../../core/services/api.service';
import { ArtifactMetadata } from '../../../../core/services/api.types';

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
  selectedCategory = 'All';

  datasets$ = new BehaviorSubject<any[]>([]);
  filteredDatasets$ = new BehaviorSubject<any[]>([]);

  searchQuery = '';
  isLoading = true;

  trackByDataset(_index: number, item: any) {
    return item?.id ?? _index;
  }

  constructor(private apiService: ApiService) {}

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
          size: '--',
          downloads: '--',
          likes: '--',
          updated: 'recently',
          tags: [artifact.type],
          artifactId: artifact.id,
          artifactType: artifact.type
        }));

        this.datasets$.next(displayDatasets);
        this.filteredDatasets$.next(displayDatasets);
        this.isLoading = false;
      },
      error: (err: any) => {
        console.error('Error fetching datasets:', err);
        this.isLoading = false;
        this.datasets$.next([]);
        this.filteredDatasets$.next([]);
      }
    });
  }

  selectCategory(category: string) {
    this.selectedCategory = category;
    this.applyFilters();
  }

  onSearchChange(): void {
    this.applyFilters();
  }

  private applyFilters(): void {
    const datasets = this.datasets$.value;
    let filtered = datasets;

    if (this.selectedCategory !== 'All') {
      filtered = filtered.filter(d => d.category === this.selectedCategory);
    }

    if (this.searchQuery) {
      filtered = filtered.filter(d => 
        d.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        d.description.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        d.tags.some((tag: string) => tag.toLowerCase().includes(this.searchQuery.toLowerCase()))
      );
    }

    this.filteredDatasets$.next(filtered);
  }
}
