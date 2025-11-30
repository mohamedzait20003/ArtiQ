import { Routes } from '@angular/router';
import { AuthGuard } from './guards/auth.guard';
import { LandingGuard } from './guards/landing.guard';

export const routes: Routes = [
	{
		path: '',
		canActivate: [LandingGuard],
		loadChildren: () => import('./features/landing/landing.module').then((m) => m.LandingModule),
	},
	{
		path: 'auth',
		loadChildren: () => import('./features/auth/auth.module').then((m) => m.AuthModule),
	},
	{
		path: 'dashboard',
		canActivate: [AuthGuard],
		loadChildren: () => import('./features/dashboard/dashboard.module').then((m) => m.DashboardModule),
	},
	{
		path: 'admin',
		// canActivate: [AuthGuard],
		loadChildren: () => import('./features/admin/admin.module').then((m) => m.AdminModule),
	},
	
	{ path: '**', redirectTo: '' },
];
