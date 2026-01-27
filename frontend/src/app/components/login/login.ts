import { Component, inject } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService } from '../../services/auth-service';

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
    if (this.loginForm.valid) {
      console.log(this.loginForm.value);

      this.authService
        .login({
          email: this.loginForm.value.email!,
          password: this.loginForm.value.password!,
        })
        .subscribe((token) => console.log(token));
    }
  }
}
