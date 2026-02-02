import { Component, inject, input } from '@angular/core';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../services/auth-service';

@Component({
  selector: 'app-header',
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './header.html',
  styleUrl: './header.scss',
})
export class Header {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  protected isAuthenticated = this.authService.isAuthenticated;

  appName = input.required<string>();
  matchesCount = input.required<number>();

  protected logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
