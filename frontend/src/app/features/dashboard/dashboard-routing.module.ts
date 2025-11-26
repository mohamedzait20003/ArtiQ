import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { OverviewComponent } from './pages/overview/overview.component';
import { ModelsComponent } from './pages/models/models.component';
import { DatasetsComponent } from './pages/datasets/datasets.component';

const routes: Routes = [
  { path: '', component: OverviewComponent },
  { path: 'models', component: ModelsComponent },
  { path: 'datasets', component: DatasetsComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class DashboardRoutingModule { }
