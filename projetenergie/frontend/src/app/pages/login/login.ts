import { Component, inject } from "@angular/core";
import { FormBuilder, ReactiveFormsModule, Validators } from "@angular/forms";
import { Router } from "@angular/router";
import { AuthService } from "../../services/auth.service";
import { CommonModule } from "@angular/common";

@Component({
  selector: "app-login",
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: "./login.html",
  styleUrls: ["./login.scss"],
})
export class LoginComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);

  // Champs vides par défaut : l'utilisateur doit saisir ses propres identifiants.
  loginForm = this.fb.group({
    email: ["", [Validators.required, Validators.email]],
    password: ["", Validators.required],
  });

  errorMessage: string | null = null;

  login() {
    if (this.loginForm.valid) {
      const { email, password } = this.loginForm.value;
      this.authService
        .login({ username: email!, password: password! })
        .subscribe({
          next: () => {
            this.router.navigate(["/dashboard"]);
          },
          error: (err) => {
            this.errorMessage = "Identifiants incorrects";
          },
        });
    }
  }
}

/*import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './login.html',
  styleUrls: ['./login.scss']
})
export class LoginComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);

  // Le champ s'appelle "email" côté formulaire Angular (plus clair pour
  // l'utilisateur), mais sera envoyé sous la clé "username" au backend
  // dans login() ci-dessous - c'est le nom de champ imposé par le
  // standard OAuth2 (OAuth2PasswordRequestForm côté FastAPI), peu importe
  // que la valeur soit un email ou un simple identifiant.
  loginForm = this.fb.group({
    email: ['admin@senelec.sn', [Validators.required, Validators.email]],
    password: ['admin123', Validators.required]
  });

  errorMessage: string | null = null;

  login() {
    if (this.loginForm.valid) {
      const { email, password } = this.loginForm.value;
      this.authService.login({ username: email!, password: password! }).subscribe({
        next: () => {
          this.router.navigate(['/dashboard']);
        },
        error: (err) => {
          this.errorMessage = 'Identifiants incorrects';
        }
      });
    }
  }
}*/
