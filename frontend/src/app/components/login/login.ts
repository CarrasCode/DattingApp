import { Component, inject } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService, LoginCredentials } from '../../services/auth-service';
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
  loginForm = new FormGroup({
    email: new FormControl('usuario@demo.com', Validators.required),
    password: new FormControl('Test1234!', Validators.required),
  });

  onSubmit() {
    if (!this.loginForm.valid) return;
    console.log(this.loginForm.value);

    this.authService.login(this.loginForm.value as LoginCredentials).subscribe({
      next: (data) => {
        this.router.navigate(['/']);
      },
      error: (e) => console.log(' Error Login:', e),
    });
  }
}
