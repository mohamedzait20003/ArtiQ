import { Routes } from '@angular/router';
import { DashboardComponent } from './dashboard/dashboard.component';

export const routes: Routes = [
	{
		path: '',
		loadChildren: () => import('./landing/landing.module').then((m) => m.LandingModule),
	},
	{
		path: 'auth',
		loadChildren: () => import('./auth/auth.module').then((m) => m.AuthModule),
	},
	{
		path: 'dashboard',
		component: DashboardComponent,
	},
	{ path: '**', redirectTo: '' },
];
