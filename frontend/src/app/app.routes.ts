import { Routes } from '@angular/router';
import { RoleGuard } from './guards/role.guard';
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
		canActivate: [RoleGuard],
		data: { roles: ['Manager'] },
		loadChildren: () => import('./features/dashboard/dashboard.module').then((m) => m.DashboardModule),
	},
	{
		path: 'admin',
		canActivate: [RoleGuard],
		data: { roles: ['Admin'] },
		loadChildren: () => import('./features/admin/admin.module').then((m) => m.AdminModule),
	},
	{
		path: 'visitor',
		canActivate: [RoleGuard],
		data: { roles: ['Visitor'] },
		loadChildren: () => import('./features/visitor/visitor.module').then((m) => m.VisitorModule),
	},
	
	{ path: '**', redirectTo: '' },
];
