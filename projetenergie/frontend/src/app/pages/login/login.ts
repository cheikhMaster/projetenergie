import { Component, inject } from '@angular/core';
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

  loginForm = this.fb.group({
    username: ['admin', Validators.required],
    password: ['admin123', Validators.required]
  });

  errorMessage: string | null = null;

  login() {
    if (this.loginForm.valid) {
      const { username, password } = this.loginForm.value;
      this.authService.login({ username: username!, password: password! }).subscribe({
        next: () => {
          this.router.navigate(['/htb']);
        },
        error: (err) => {
          this.errorMessage = 'Identifiants incorrects';
        }
      });
    }
  }
}
