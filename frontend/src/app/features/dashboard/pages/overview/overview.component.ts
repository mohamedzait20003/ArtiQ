import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Store } from '@ngrx/store';
import { selectUser } from '../../../../store/auth.selectors';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-overview',
  standalone: true,
  imports: [CommonModule, RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './overview.component.html',
  styleUrls: ['./overview.component.css']
})

export class OverviewComponent {
  user$: Observable<any>;

  recentModels = [
    { id: 1, name: 'GPT-4-Turbo', type: 'Language Model', updated: '2 days ago', downloads: '1.2M' },
    { id: 2, name: 'DALL-E-3', type: 'Image Generation', updated: '5 days ago', downloads: '856K' },
    { id: 3, name: 'Whisper-Large', type: 'Speech Recognition', updated: '1 week ago', downloads: '634K' }
  ];

  recentDatasets = [
    { id: 1, name: 'ImageNet-2024', type: 'Computer Vision', size: '150GB', updated: '1 day ago' },
    { id: 2, name: 'CommonCrawl-Q4', type: 'Text Corpus', size: '2.3TB', updated: '3 days ago' },
    { id: 3, name: 'AudioSet-Extended', type: 'Audio Classification', size: '89GB', updated: '1 week ago' }
  ];

  quickStats = [
    { label: 'Total Models', value: '1,247', change: '+12%', trend: 'up' },
    { label: 'Total Datasets', value: '3,891', change: '+8%', trend: 'up' },
    { label: 'Active Users', value: '45.2K', change: '+23%', trend: 'up' },
    { label: 'Downloads', value: '2.1M', change: '+15%', trend: 'up' }
  ];

  trackByStat(_index: number, item: any) {
    return item?.label ?? _index;
  }

  trackByRecentId(_index: number, item: any) {
    return item?.id ?? _index;
  }

  constructor(private store: Store) {
    this.user$ = this.store.select(selectUser);
  }
}
