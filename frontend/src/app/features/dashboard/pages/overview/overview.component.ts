import { Component, ChangeDetectionStrategy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { selectUser } from '../../../../store/auth.selectors';
import { Observable, BehaviorSubject } from 'rxjs';

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

  constructor(private store: Store, private router: Router) {
    this.user$ = this.store.select(selectUser);
  }

  ngOnInit(): void {
    this.fetchArtifacts();
  }

  private fetchArtifacts(): void {
    // TODO: Implement NgRx store actions for fetching artifacts
    // For now, using placeholder data
    const mockModels = [
      { id: 1, name: 'GPT-4 Model', type: 'model', updated: 'recently', downloads: '1.2K' },
      { id: 2, name: 'BERT Classifier', type: 'model', updated: 'recently', downloads: '850' },
      { id: 3, name: 'ResNet-50', type: 'model', updated: 'recently', downloads: '2.3K' }
    ];

    const mockDatasets = [
      { id: 1, name: 'ImageNet', type: 'dataset', size: '150 GB', updated: 'recently' },
      { id: 2, name: 'COCO Dataset', type: 'dataset', size: '25 GB', updated: 'recently' },
      { id: 3, name: 'WikiText-103', type: 'dataset', size: '1.2 GB', updated: 'recently' }
    ];

    this.recentModels$.next(mockModels);
    this.recentDatasets$.next(mockDatasets);

    // Update stats with mock data
    this.quickStats = [
      { label: 'Total Models', value: '12', change: '+3', trend: 'up' },
      { label: 'Total Datasets', value: '8', change: '+2', trend: 'up' },
      { label: 'Total Code', value: '5', change: '+1', trend: 'up' },
      { label: 'Total Artifacts', value: '25', change: '+6', trend: 'up' }
    ];
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
