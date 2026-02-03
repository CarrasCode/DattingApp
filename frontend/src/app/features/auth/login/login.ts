import { Component, inject } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService, LoginCredentials } from '@core/services/auth-service';
import { UserService } from '@core/services/user-service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {
  private readonly router = inject(Router);
  private readonly authService = inject(AuthService);
  private readonly userService = inject(UserService);

  loginForm = new FormGroup({
    email: new FormControl('usuario@demo.com', Validators.required),
    password: new FormControl('Test1234!', Validators.required),
  });

  async onSubmit() {
    if (!this.loginForm.valid) return;

    this.authService.login(this.loginForm.value as LoginCredentials).subscribe({
      next: async () => {
        // Refrescar datos del usuario después del login
        this.userService.refreshCurrentUser();
        this.userService.refreshUsers();

        // Actualizar ubicación (silencioso, no bloquea si deniega)
        await this.userService.updateLocation();

        this.router.navigate(['/']);
      },
      error: (e) => console.log('Error Login:', e),
    });
  }
}
