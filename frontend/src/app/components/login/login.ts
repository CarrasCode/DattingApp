import { Component, inject } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService, LoginCredentials } from '../../services/auth-service';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {
  authService = inject(AuthService);
  loginForm = new FormGroup({
    email: new FormControl('usuario@demo.com', Validators.required),
    password: new FormControl('Test1234!', Validators.required),
  });

  onSubmit() {
    if (!this.loginForm.valid) return;
    console.log(this.loginForm.value);

    this.authService
      .login(this.loginForm.value as LoginCredentials)
      .subscribe((token) => console.log(token));
  }
}
