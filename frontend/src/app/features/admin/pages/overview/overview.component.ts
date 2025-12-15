import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AdminService } from '../../services/admin.service';

@Component({
  selector: 'app-admin-overview',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './overview.component.html',
  styleUrls: ['./overview.component.css'],
})
export class OverviewComponent implements OnInit {
  totalUsers = 0;
  totalModels = 0;
  totalDatasets = 0;

  constructor(
    private adminService: AdminService,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Load stats
    this.loadStats();
  }

  private loadStats(): void {
    this.adminService.getUsers().subscribe({
      next: (users) => {
        this.totalUsers = users.length;
      },
      error: (error) => {
        console.error('Error loading users:', error);
      }
    });

    this.adminService.getModels().subscribe({
      next: (models) => {
        this.totalModels = models.length;
      },
      error: (error) => {
        console.error('Error loading models:', error);
      }
    });

    this.adminService.getDatasets().subscribe({
      next: (datasets) => {
        this.totalDatasets = datasets.length;
      },
      error: (error) => {
        console.error('Error loading datasets:', error);
      }
    });
  }

  manageUsers(): void {
    this.router.navigate(['/admin/users']);
  }
}
