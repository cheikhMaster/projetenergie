import { Component, signal, OnInit } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { KeycloakService } from 'keycloak-angular';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements OnInit {
  protected readonly title = signal('frontend');
  username: string = '';

  constructor(private keycloak: KeycloakService) {}

  async ngOnInit() {
    if (await this.keycloak.isLoggedIn()) {
      const profile = await this.keycloak.loadUserProfile();
      this.username = profile.username || '';
    }
  }

  logout() {
    this.keycloak.logout();
  }
}
