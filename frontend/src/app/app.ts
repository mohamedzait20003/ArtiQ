import { Component, signal } from '@angular/core';
import { RouterOutlet, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { SearchService } from './search.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})

export class App {
  protected readonly title = signal('frontend');
  headerSearch = '';

  constructor(private search: SearchService) {}

  onSearch(value: string) {
    this.search.set(value);
  }

  onEnter() {
    // ensure latest value is set and scroll to models section
    this.search.set(this.headerSearch);
    const el = document.getElementById('models');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }
}
