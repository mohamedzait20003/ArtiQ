import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { RegisterComponent } from './pages/register/register.component';
import { ResetComponent } from './pages/reset/reset.component';
import { LandingGuard } from '../../guards/landing.guard';

const routes: Routes = [
  { path: 'login', component: LoginComponent, canActivate: [LandingGuard] },
  { path: 'register', component: RegisterComponent, canActivate: [LandingGuard] },
  { path: 'reset', component: ResetComponent, canActivate: [LandingGuard] },
  { path: '', redirectTo: 'login', pathMatch: 'full' },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class AuthRoutingModule {}
