import { Component, ChangeDetectionStrategy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { AdminService, User } from '../../services/admin.service';
import { ToastService } from '../../../../core/services/toast.service';

export type SortOption = 'name' | 'email' | 'role';

@Component({
  selector: 'app-admin-users',
  standalone: true,
  imports: [CommonModule, FormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './users.component.html',
  styleUrls: ['./users.component.css']
})
export class UsersComponent implements OnInit {
  sortOptions: SortOption[] = ['name', 'email', 'role'];
  
  sortBy: SortOption = 'name';
  viewMode: 'grid' | 'list' = 'grid';

  searchQuery = '';
  private usersSubject = new BehaviorSubject<User[]>([]);
  filteredUsers$: Observable<User[]>;

  editingUser: User | null = null;
  showEditModal = false;
  showDeleteModal = false;
  userToDelete: User | null = null;

  constructor(
    private adminService: AdminService,
    private toastService: ToastService
  ) {
    this.filteredUsers$ = this.usersSubject.asObservable().pipe(
      map(users => this.filterAndSort(users))
    );
  }

  ngOnInit(): void {
    // Load initial users
    this.loadUsers();
  }

  private loadUsers(): void {
    this.adminService.getUsers().subscribe({
      next: (users) => {
        this.usersSubject.next(users);
      },
      error: (error) => {
        this.toastService.error('Failed to load users');
        console.error('Error loading users:', error);
      }
    });
  }

  private filterAndSort(users: User[]): User[] {
    let filtered = users;
    
    // Client-side search filtering
    if (this.searchQuery && this.searchQuery.trim() !== '') {
      const query = this.searchQuery.toLowerCase();
      filtered = users.filter(user => 
        user.name.toLowerCase().includes(query) ||
        user.email.toLowerCase().includes(query) ||
        user.role.toLowerCase().includes(query)
      );
    }
    
    return this.sortUsers(filtered);
  }

  private sortUsers(users: User[]): User[] {
    return [...users].sort((a, b) => {
      switch (this.sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'email':
          return a.email.localeCompare(b.email);
        case 'role':
          return a.role.localeCompare(b.role);
        default:
          return 0;
      }
    });
  }

  onSortChange(sort: SortOption): void {
    this.sortBy = sort;
    this.updateFilters();
  }

  onSearchChange(): void {
    this.updateFilters();
  }

  toggleViewMode(): void {
    this.viewMode = this.viewMode === 'grid' ? 'list' : 'grid';
  }

  private updateFilters(): void {
    // Trigger re-filtering of current users
    const currentUsers = this.usersSubject.getValue();
    this.usersSubject.next([...currentUsers]);
  }

  openEditModal(user: User): void {
    this.editingUser = { ...user };
    this.showEditModal = true;
  }

  closeEditModal(): void {
    this.showEditModal = false;
    this.editingUser = null;
  }

  saveUser(): void {
    if (!this.editingUser) return;

    this.adminService.updateUser(this.editingUser.id, {
      name: this.editingUser.name,
      email: this.editingUser.email,
      role: this.editingUser.role
    }).subscribe({
      next: () => {
        this.toastService.success('User updated successfully');
        this.closeEditModal();
        this.loadUsers();
      },
      error: (error) => {
        this.toastService.error('Failed to update user');
        console.error('Error updating user:', error);
      }
    });
  }

  openDeleteModal(user: User): void {
    this.userToDelete = user;
    this.showDeleteModal = true;
  }

  closeDeleteModal(): void {
    this.showDeleteModal = false;
    this.userToDelete = null;
  }

  confirmDelete(): void {
    if (!this.userToDelete) return;

    this.adminService.deleteUser(this.userToDelete.id).subscribe({
      next: () => {
        this.toastService.success('User deleted successfully');
        this.closeDeleteModal();
        this.loadUsers();
      },
      error: (error) => {
        this.toastService.error('Failed to delete user');
        console.error('Error deleting user:', error);
      }
    });
  }

  getRoleBadgeClass(role: string): string {
    switch (role.toLowerCase()) {
      case 'admin':
        return 'bg-gradient-to-r from-red-500/20 to-pink-500/20 border-red-400/30 text-red-300';
      case 'manager':
        return 'bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border-yellow-400/30 text-yellow-300';
      case 'visitor':
        return 'bg-gradient-to-r from-indigo-500/20 to-purple-500/20 border-indigo-400/30 text-indigo-300';
      default:
        return 'bg-gradient-to-r from-slate-500/20 to-slate-600/20 border-slate-400/30 text-slate-300';
    }
  }
}
