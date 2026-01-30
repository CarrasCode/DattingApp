import { Component, inject } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService, RegisterCredentials } from '../../services/auth-service';

@Component({
  selector: 'app-register',
  imports: [ReactiveFormsModule],
  templateUrl: './register.html',
  styleUrl: './register.scss',
})
export class Register {
  authService = inject(AuthService);
  registerForm = new FormGroup({
    email: new FormControl('usuario@demo.com', [Validators.required]),
    password: new FormControl('Test1234!', [Validators.required]),
    password_confirm: new FormControl('Test1234!', [Validators.required]),
  });

  onSubmit() {
    if (!this.registerForm.valid) return;
    console.log(this.registerForm.value);

    this.authService
      .register(this.registerForm.value as RegisterCredentials)
      .subscribe((token) => console.log(token));
  }
}
