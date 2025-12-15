import { Component, ChangeDetectionStrategy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { selectUser } from '../../../../store/auth.selectors';
import { VisitorService } from '../../services/visitor.service';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-visitor-overview',
  standalone: true,
  imports: [CommonModule, RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './overview.component.html',
  styleUrls: ['./overview.component.css']
})
export class VisitorOverviewComponent implements OnInit {
  user$: Observable<any>;

  constructor(
    private store: Store,
    private router: Router,
    private visitorService: VisitorService
  ) {
    this.user$ = this.store.select(selectUser);
  }

  ngOnInit(): void {
    // Visitor dashboard initialization
    // Load visitor statistics if needed
    this.visitorService.getStats().subscribe(stats => {
      console.log('Visitor stats loaded:', stats);
    });
  }

  exploreModels(): void {
    // Navigate to models browsing page
    this.router.navigate(['/visitor/models']);
  }

  exploreDatasets(): void {
    // Navigate to datasets browsing page
    this.router.navigate(['/visitor/datasets']);
  }
}
