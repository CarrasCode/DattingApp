import { Component, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService, LoginCredentials } from '@core/services/auth-service';
import { UserService } from '@core/services/user-service';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {
  private readonly router = inject(Router);
  private readonly authService = inject(AuthService);
  private readonly userService = inject(UserService);

  protected loading = signal(false);
  protected error = signal<string | null>(null);

  loginForm = new FormGroup({
    email: new FormControl('usuario@demo.com', Validators.required),
    password: new FormControl('Test1234!', Validators.required),
  });

  async onSubmit() {
    if (!this.loginForm.valid) return;

    this.loading.set(true);
    this.error.set(null);

    this.authService.login(this.loginForm.value as LoginCredentials).subscribe({
      next: async () => {
        // Los servicios (UserService, MatchService) reaccionan automáticamente
        // al cambio de isAuthenticated gracias a effect()

        // Solo la ubicación necesita llamada manual (es async/opcional)
        await this.userService.updateLocation();

        this.router.navigate(['/']);
      },
      error: (e) => {
        this.error.set('Email o contraseña incorrectos');
        this.loading.set(false);
      },
    });
  }
}
