import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthRoutingModule } from './auth-routing.module';
import { LoginComponent } from './pages/login/login.component';
import { ResetComponent } from './pages/reset/reset.component';

@NgModule({
    imports: [
        CommonModule,
        RouterModule,
        AuthRoutingModule,
        LoginComponent,
        ResetComponent
    ],
})
export class AuthModule { }
