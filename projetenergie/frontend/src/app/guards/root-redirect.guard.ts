import { inject } from "@angular/core";
import { CanActivateFn, Router } from "@angular/router";
import { AuthService } from "../services/auth.service";

/**
 * Guard appliqué sur la route racine ('').
 * Redirige directement vers /htb si connecté, /login sinon —
 * évite de passer par /htb pour un utilisateur non authentifié.
 */
export const rootRedirectGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  return authService.isAuthenticated()
    ? router.parseUrl("/htb")
    : router.parseUrl("/login");
};
