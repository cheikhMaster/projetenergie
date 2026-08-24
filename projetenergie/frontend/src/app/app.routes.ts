import { Routes } from '@angular/router';
import { DashboardHtbComponent } from './pages/dashboard-htb/dashboard-htb';
import { DashboardHtaComponent } from './pages/dashboard-hta/dashboard-hta';
import { ProductionComponent } from './pages/production/production';
import { VentesComponent } from './pages/ventes/ventes';
import { AuthGuard } from './guards/auth.guard';

export const routes: Routes = [
  {
    path: 'htb',
    component: DashboardHtbComponent,
    canActivate: [AuthGuard],
    data: { roles: ['admin', 'analyste', 'manager'] }
  },
  {
    path: 'hta',
    component: DashboardHtaComponent,
    canActivate: [AuthGuard],
    data: { roles: ['admin', 'analyste', 'manager'] }
  },
  {
    path: 'production',
    component: ProductionComponent,
    canActivate: [AuthGuard],
    data: { roles: ['admin', 'operateur', 'manager'] }
  },
  {
    path: 'ventes',
    component: VentesComponent,
    canActivate: [AuthGuard],
    data: { roles: ['admin', 'manager'] }
  },
  { path: '', redirectTo: '/htb', pathMatch: 'full' }
];
