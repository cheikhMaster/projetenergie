import { Routes } from '@angular/router';
import { DashboardHtbComponent } from './pages/dashboard-htb/dashboard-htb';
import { DashboardHtaComponent } from './pages/dashboard-hta/dashboard-hta';
import { DashboardGlobalComponent } from './pages/dashboard-global/dashboard-global';
import { ProductionComponent } from './pages/production/production';
import { VentesComponent } from './pages/ventes/ventes';
import { authGuard } from './guards/auth.guard';
import { rootRedirectGuard } from './guards/root-redirect.guard';
import { LoginComponent } from './pages/login/login';

export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    canActivate: [rootRedirectGuard],
    children: []
  },
  {
    path: 'login',
    component: LoginComponent
  },
  {
    path: 'dashboard',
    component: DashboardGlobalComponent,
    canActivate: [authGuard]
  },
  {
    path: 'htb',
    component: DashboardHtbComponent,
    canActivate: [authGuard]
  },
  {
    path: 'hta',
    component: DashboardHtaComponent,
    canActivate: [authGuard]
  },
  {
    path: 'production',
    component: ProductionComponent,
    canActivate: [authGuard]
  },
  {
    path: 'ventes',
    component: VentesComponent,
    canActivate: [authGuard]
  },
  { path: '**', redirectTo: '/login' }
];
