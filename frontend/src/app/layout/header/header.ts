import { Component, inject, input } from '@angular/core';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '@core/services/auth-service';

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
    // ¡Ya no necesitamos limpiar manualmente!
    // Los servicios reaccionan automáticamente al cambio de isAuthenticated
    this.router.navigate(['/login']);
  }
}
