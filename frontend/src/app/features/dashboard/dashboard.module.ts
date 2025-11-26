import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DashboardRoutingModule } from './dashboard-routing.module';
import { OverviewComponent } from './pages/overview/overview.component';
import { ModelsComponent } from './pages/models/models.component';
import { DatasetsComponent } from './pages/datasets/datasets.component';

@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    DashboardRoutingModule,
    OverviewComponent,
    ModelsComponent,
    DatasetsComponent
  ]
})
export class DashboardModule { }
