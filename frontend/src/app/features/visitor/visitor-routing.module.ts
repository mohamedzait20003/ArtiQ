import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { VisitorModelsComponent } from './pages/models/models.component';
import { VisitorOverviewComponent } from './pages/overview/overview.component';
import { VisitorDatasetsComponent } from './pages/datasets/datasets.component';

const routes: Routes = [
  { path: '', redirectTo: 'overview', pathMatch: 'full' },
  { path: 'overview', component: VisitorOverviewComponent },
  { path: 'models', component: VisitorModelsComponent },
  { path: 'datasets', component: VisitorDatasetsComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class VisitorRoutingModule {}
