import { Routes } from "@angular/router";
import { DashboardHtbComponent } from "./pages/dashboard-htb/dashboard-htb";
import { DashboardHtaComponent } from "./pages/dashboard-hta/dashboard-hta";
import { ProductionComponent } from "./pages/production/production";
import { VentesComponent } from "./pages/ventes/ventes";
import { authGuard } from "./guards/auth.guard";
import { LoginComponent } from "./pages/login/login";

export const routes: Routes = [
  {
    path: "login",
    component: LoginComponent,
  },
  {
    path: "htb",
    component: DashboardHtbComponent,
    canActivate: [authGuard],
  },
  {
    path: "hta",
    component: DashboardHtaComponent,
    canActivate: [authGuard],
  },
  {
    path: "production",
    component: ProductionComponent,
    canActivate: [authGuard],
  },
  {
    path: "ventes",
    component: VentesComponent,
    canActivate: [authGuard],
  },
  { path: "", redirectTo: "/htb", pathMatch: "full" },
  { path: "**", redirectTo: "/login" }, // Redirect unknown paths to login
];
