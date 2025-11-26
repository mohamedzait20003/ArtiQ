import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-datasets',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './datasets.component.html',
  styleUrls: ['./datasets.component.css']
})
export class DatasetsComponent {
  categories = ['All', 'Text Corpus', 'Computer Vision', 'Audio Classification', 'Speech', 'Multimodal'];
  selectedCategory = 'All';

  datasets = [
    {
      id: 1,
      name: 'ImageNet-2024',
      author: 'Stanford Vision Lab',
      category: 'Computer Vision',
      description: 'Large-scale visual recognition dataset with 14M+ images across 20K+ categories',
      size: '150GB',
      downloads: '2.3M',
      likes: '56K',
      updated: '1 day ago',
      tags: ['Vision', 'Classification', 'Benchmark']
    },
    {
      id: 2,
      name: 'CommonCrawl-Q4',
      author: 'CommonCrawl Foundation',
      category: 'Text Corpus',
      description: 'Massive web crawl dataset for training large language models',
      size: '2.3TB',
      downloads: '1.8M',
      likes: '42K',
      updated: '3 days ago',
      tags: ['NLP', 'Web', 'Pretraining']
    },
    {
      id: 3,
      name: 'AudioSet-Extended',
      author: 'Google Research',
      category: 'Audio Classification',
      description: 'Large-scale dataset of audio events with 2M+ YouTube videos',
      size: '89GB',
      downloads: '987K',
      likes: '31K',
      updated: '1 week ago',
      tags: ['Audio', 'Classification', 'Events']
    },
    {
      id: 4,
      name: 'LibriSpeech-HD',
      author: 'OpenSLR',
      category: 'Speech',
      description: 'High-quality speech recognition corpus with 1000 hours of read English',
      size: '45GB',
      downloads: '1.2M',
      likes: '38K',
      updated: '5 days ago',
      tags: ['Speech', 'ASR', 'English']
    },
    {
      id: 5,
      name: 'COCO-2024',
      author: 'Microsoft',
      category: 'Computer Vision',
      description: 'Object detection, segmentation, and captioning dataset',
      size: '67GB',
      downloads: '1.9M',
      likes: '49K',
      updated: '2 days ago',
      tags: ['Vision', 'Detection', 'Segmentation']
    },
    {
      id: 6,
      name: 'LAION-5B',
      author: 'LAION',
      category: 'Multimodal',
      description: 'Largest openly available image-text dataset with 5B+ pairs',
      size: '1.8TB',
      downloads: '856K',
      likes: '35K',
      updated: '1 week ago',
      tags: ['Multimodal', 'Image-Text', 'Large-Scale']
    }
  ];

  searchQuery = '';

  selectCategory(category: string) {
    this.selectedCategory = category;
  }

  get filteredDatasets() {
    let filtered = this.datasets;
    
    if (this.selectedCategory !== 'All') {
      filtered = filtered.filter(d => d.category === this.selectedCategory);
    }
    
    if (this.searchQuery) {
      filtered = filtered.filter(d => 
        d.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        d.description.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        d.tags.some(tag => tag.toLowerCase().includes(this.searchQuery.toLowerCase()))
      );
    }
    
    return filtered;
  }
}
