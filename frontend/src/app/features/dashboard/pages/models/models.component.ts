import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-models',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './models.component.html',
  styleUrls: ['./models.component.css']
})
export class ModelsComponent {
  categories = ['All', 'Language Models', 'Image Generation', 'Speech Recognition', 'Computer Vision', 'Audio'];
  selectedCategory = 'All';

  models = [
    {
      id: 1,
      name: 'GPT-4-Turbo',
      author: 'OpenAI',
      category: 'Language Models',
      description: 'Most advanced language model with improved reasoning and extended context',
      downloads: '1.2M',
      likes: '45K',
      updated: '2 days ago',
      tags: ['NLP', 'Chat', 'Generation']
    },
    {
      id: 2,
      name: 'DALL-E-3',
      author: 'OpenAI',
      category: 'Image Generation',
      description: 'Generate high-quality images from text descriptions',
      downloads: '856K',
      likes: '38K',
      updated: '5 days ago',
      tags: ['Image', 'Generation', 'Creative']
    },
    {
      id: 3,
      name: 'Whisper-Large',
      author: 'OpenAI',
      category: 'Speech Recognition',
      description: 'Robust speech recognition with multilingual support',
      downloads: '634K',
      likes: '29K',
      updated: '1 week ago',
      tags: ['Audio', 'Speech', 'Transcription']
    },
    {
      id: 4,
      name: 'CLIP-ViT',
      author: 'OpenAI',
      category: 'Computer Vision',
      description: 'Connect text and images for zero-shot classification',
      downloads: '512K',
      likes: '24K',
      updated: '3 days ago',
      tags: ['Vision', 'Classification', 'Embedding']
    },
    {
      id: 5,
      name: 'Stable Diffusion XL',
      author: 'Stability AI',
      category: 'Image Generation',
      description: 'Advanced text-to-image model with superior quality',
      downloads: '923K',
      likes: '41K',
      updated: '1 week ago',
      tags: ['Image', 'Generation', 'Diffusion']
    },
    {
      id: 6,
      name: 'LLaMA-2-70B',
      author: 'Meta',
      category: 'Language Models',
      description: 'Open-source large language model for various NLP tasks',
      downloads: '789K',
      likes: '35K',
      updated: '4 days ago',
      tags: ['NLP', 'Open Source', 'Chat']
    }
  ];

  searchQuery = '';

  selectCategory(category: string) {
    this.selectedCategory = category;
  }

  get filteredModels() {
    let filtered = this.models;
    
    if (this.selectedCategory !== 'All') {
      filtered = filtered.filter(m => m.category === this.selectedCategory);
    }
    
    if (this.searchQuery) {
      filtered = filtered.filter(m => 
        m.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        m.description.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        m.tags.some(tag => tag.toLowerCase().includes(this.searchQuery.toLowerCase()))
      );
    }
    
    return filtered;
  }
}
