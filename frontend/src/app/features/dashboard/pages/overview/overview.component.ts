import { Component, ChangeDetectionStrategy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { selectUser } from '../../../../store/auth.selectors';
import { Observable, BehaviorSubject } from 'rxjs';
import { ApiService } from '../../../../core/services/api.service';
import { ArtifactMetadata } from '../../../../core/services/api.types';

@Component({
  selector: 'app-overview',
  standalone: true,
  imports: [CommonModule, RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './overview.component.html',
  styleUrls: ['./overview.component.css']
})

export class OverviewComponent implements OnInit {
  user$: Observable<any>;

  recentModels$ = new BehaviorSubject<any[]>([]);
  recentDatasets$ = new BehaviorSubject<any[]>([]);

  quickStats = [
    { label: 'Total Models', value: '0', change: '--', trend: 'up' },
    { label: 'Total Datasets', value: '0', change: '--', trend: 'up' },
    { label: 'Total Code', value: '0', change: '--', trend: 'up' },
    { label: 'Total Artifacts', value: '0', change: '--', trend: 'up' }
  ];

  trackByStat(_index: number, item: any) {
    return item?.label ?? _index;
  }

  trackByRecentId(_index: number, item: any) {
    return item?.id ?? _index;
  }

  constructor(private store: Store, private apiService: ApiService, private router: Router) {
    this.user$ = this.store.select(selectUser);
  }

  ngOnInit(): void {
    this.fetchArtifacts();
  }

  private fetchArtifacts(): void {
    // Fetch all artifacts
    this.apiService.getAllArtifacts().subscribe({
      next: (artifacts: ArtifactMetadata[]) => {
        // Separate by type
        const models = artifacts.filter(a => a.type === 'model').slice(0, 3);
        const datasets = artifacts.filter(a => a.type === 'dataset').slice(0, 3);

        // Transform to display format
        const displayModels = models.map((m, idx) => ({
          id: idx + 1,
          name: m.name,
          type: m.type,
          updated: 'recently',
          downloads: '--'
        }));

        const displayDatasets = datasets.map((d, idx) => ({
          id: idx + 1,
          name: d.name,
          type: d.type,
          size: '--',
          updated: 'recently'
        }));

        this.recentModels$.next(displayModels);
        this.recentDatasets$.next(displayDatasets);

        // Update stats
        const modelCount = artifacts.filter(a => a.type === 'model').length;
        const datasetCount = artifacts.filter(a => a.type === 'dataset').length;
        const codeCount = artifacts.filter(a => a.type === 'code').length;

        this.quickStats = [
          { label: 'Total Models', value: modelCount.toString(), change: '--', trend: 'up' },
          { label: 'Total Datasets', value: datasetCount.toString(), change: '--', trend: 'up' },
          { label: 'Total Code', value: codeCount.toString(), change: '--', trend: 'up' },
          { label: 'Total Artifacts', value: artifacts.length.toString(), change: '--', trend: 'up' }
        ];
      },
      error: (err: any) => {
        console.error('Error fetching artifacts:', err);
        // Keep default empty data on error
      }
    });
  }

  browseModels(): void {
    this.router.navigate(['/dashboard/models']);
  }

  goToDocumentation(): void {
    this.router.navigate(['/']);
  }

  joinCommunity(): void {
    this.router.navigate(['/']);
  }
}
