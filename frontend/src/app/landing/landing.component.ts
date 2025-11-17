import { Component, OnDestroy } from '@angular/core';
import { RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SearchService } from '../search.service';
import { Subscription } from 'rxjs';

interface Model {
  name: string;
  provider: string;
  description: string;
  category: string;
  downloads?: string;
  stars?: string;
}

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './landing.component.html',
  styleUrls: ['./landing.component.css'],
})
export class LandingComponent implements OnDestroy {
  searchTerm = '';
  private _sub?: Subscription;

  models: Model[] = [
    {
      name: 'GPT-Vision',
      provider: 'openai',
      description: 'State-of-the-art vision-language model for image understanding and generation.',
      category: 'Computer Vision',
      downloads: '125K',
      stars: '4.2K',
    },
    {
      name: 'LLaMA-3',
      provider: 'meta',
      description: 'Open-source large language model optimized for chat and instruction following.',
      category: 'Text Generation',
      downloads: '890K',
      stars: '12.5K',
    },
    {
      name: 'Whisper-v3',
      provider: 'openai',
      description: 'Robust speech recognition model with multilingual support and translation.',
      category: 'Audio',
      downloads: '560K',
      stars: '8.9K',
    },
  ];

  get filteredModels(): Model[] {
    const term = this.searchTerm.trim().toLowerCase();
    if (!term) return this.models;
    return this.models.filter((m) => {
      return (
        m.name.toLowerCase().includes(term) ||
        m.provider.toLowerCase().includes(term) ||
        m.description.toLowerCase().includes(term) ||
        m.category.toLowerCase().includes(term)
      );
    });
  }

  constructor(private search: SearchService) {
    this._sub = this.search.term$.subscribe((t) => {
      this.searchTerm = t;
    });
  }

  ngOnDestroy(): void {
    this._sub?.unsubscribe();
  }
}
