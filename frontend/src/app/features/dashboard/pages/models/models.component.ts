import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { ToastService } from '../../../../core/services/toast.service';

export type SortOption = 'name' | 'downloads' | 'likes' | 'recent';

@Component({
  selector: 'app-models',
  standalone: true,
  imports: [CommonModule, FormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './models.component.html',
  styleUrls: ['./models.component.css']
})
export class ModelsComponent {
  categories = ['All', 'Language Models', 'Image Generation', 'Speech Recognition', 'Computer Vision', 'Audio'];
  sortOptions: SortOption[] = ['name', 'downloads', 'likes', 'recent'];
  
  selectedCategory = 'All';
  sortBy: SortOption = 'recent';
  viewMode: 'grid' | 'list' = 'grid';

  models = [
    {
      id: 1,
      name: 'GPT-4-Turbo',
      author: 'OpenAI',
      category: 'Language Models',
      description: 'Most advanced language model with improved reasoning and extended context',
      downloads: 1200000,
      likes: 45000,
      updated: '2 days ago',
      tags: ['NLP', 'Chat', 'Generation']
    },
    {
      id: 2,
      name: 'DALL-E-3',
      author: 'OpenAI',
      category: 'Image Generation',
      description: 'Generate high-quality images from text descriptions',
      downloads: 856000,
      likes: 38000,
      updated: '5 days ago',
      tags: ['Image', 'Generation', 'Creative']
    },
    {
      id: 3,
      name: 'Whisper-Large',
      author: 'OpenAI',
      category: 'Speech Recognition',
      description: 'Robust speech recognition with multilingual support',
      downloads: 634000,
      likes: 29000,
      updated: '1 week ago',
      tags: ['Audio', 'Speech', 'Transcription']
    },
    {
      id: 4,
      name: 'CLIP-ViT',
      author: 'OpenAI',
      category: 'Computer Vision',
      description: 'Connect text and images for zero-shot classification',
      downloads: 512000,
      likes: 24000,
      updated: '3 days ago',
      tags: ['Vision', 'Classification', 'Embedding']
    },
    {
      id: 5,
      name: 'Stable Diffusion XL',
      author: 'Stability AI',
      category: 'Image Generation',
      description: 'Advanced text-to-image model with superior quality',
      downloads: 923000,
      likes: 41000,
      updated: '1 week ago',
      tags: ['Image', 'Generation', 'Diffusion']
    },
    {
      id: 6,
      name: 'LLaMA-2-70B',
      author: 'Meta',
      category: 'Language Models',
      description: 'Open-source large language model for various NLP tasks',
      downloads: 789000,
      likes: 35000,
      updated: '4 days ago',
      tags: ['NLP', 'Open Source', 'Chat']
    }
  ];

  searchQuery = '';
  private modelsSubject = new BehaviorSubject(this.models);
  filteredModels$: Observable<any[]>;

  constructor(private toastService: ToastService) {
    this.filteredModels$ = this.modelsSubject.asObservable().pipe(
      map(models => this.getFilteredAndSortedModels(models))
    );
  }

  trackByModel(_index: number, item: any) {
    return item?.id ?? _index;
  }

  selectCategory(category: string): void {
    this.selectedCategory = category;
    this.modelsSubject.next(this.models);
  }

  setSortBy(sort: SortOption): void {
    this.sortBy = sort;
    this.modelsSubject.next(this.models);
  }

  toggleViewMode(): void {
    this.viewMode = this.viewMode === 'grid' ? 'list' : 'grid';
  }

  onSearchChange(): void {
    this.modelsSubject.next(this.models);
  }

  likeModel(model: any): void {
    model.likes += 1;
    this.toastService.success(`Liked ${model.name}!`, 2000);
  }

  downloadModel(model: any): void {
    this.toastService.info(`Downloading ${model.name}...`, 2000);
  }

  private getFilteredAndSortedModels(models: any[]): any[] {
    let filtered = this.filterModels(models);
    return this.sortModels(filtered);
  }

  private filterModels(models: any[]): any[] {
    let filtered = models;
    
    if (this.selectedCategory !== 'All') {
      filtered = filtered.filter(m => m.category === this.selectedCategory);
    }
    
    if (this.searchQuery) {
      const query = this.searchQuery.toLowerCase();
      filtered = filtered.filter(m => 
        m.name.toLowerCase().includes(query) ||
        m.author.toLowerCase().includes(query) ||
        m.description.toLowerCase().includes(query) ||
        m.tags.some((tag: string) => tag.toLowerCase().includes(query))
      );
    }
    
    return filtered;
  }

  private sortModels(models: any[]): any[] {
    const sorted = [...models];
    
    switch (this.sortBy) {
      case 'name':
        sorted.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'downloads':
        sorted.sort((a, b) => b.downloads - a.downloads);
        break;
      case 'likes':
        sorted.sort((a, b) => b.likes - a.likes);
        break;
      case 'recent':
      default:
        // Keep original order (most recent)
        break;
    }
    
    return sorted;
  }

  get filteredModels() {
    return this.getFilteredAndSortedModels(this.models);
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
