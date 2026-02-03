import { Component, inject, input } from '@angular/core';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '@core/services/auth-service';
import { UserService } from '@core/services/user-service';

@Component({
  selector: 'app-header',
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './header.html',
  styleUrl: './header.scss',
})
export class Header {
  private readonly authService = inject(AuthService);
  private readonly userService = inject(UserService);
  private readonly router = inject(Router);
  protected isAuthenticated = this.authService.isAuthenticated;

  appName = input.required<string>();
  matchesCount = input.required<number>();

  protected logout() {
    this.authService.logout();
    this.userService.clearUserData();
    this.router.navigate(['/login']);
  }
}
