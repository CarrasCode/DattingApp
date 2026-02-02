import { HttpClient } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';
import { environment } from '../../../environments/environment';
import { tap } from 'rxjs/operators';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
  password_confirm: string;
}
interface LoginResponse {
  access: string;
  refresh: string;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly httpClient = inject(HttpClient);
  isAuthenticated = signal<boolean>(!!localStorage.getItem('access_token'));

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.isAuthenticated.set(false);
  }
  login(credentials: LoginCredentials) {
    return this.httpClient
      .post<LoginResponse>(
        environment.apiUrl + '/users/auth/login/',

        credentials,
      )
      .pipe(
        tap((response) => {
          this.saveToken(response);
          this.isAuthenticated.set(true);
        }),
      );
  }

  register(newUser: RegisterCredentials) {
    return this.httpClient
      .post<LoginResponse>(
        environment.apiUrl + '/users/auth/register/',

        newUser,
      )
      .pipe(
        tap((response) => {
          this.saveToken(response);
        }),
      );
  }

  refreshToken(refresh: string) {
    return this.httpClient
      .post<LoginResponse>(environment.apiUrl + '/users/auth/refresh/', {
        refresh,
      })
      .pipe(
        tap((response) => {
          this.saveToken(response);
        }),
      );
  }

  private saveToken(token: LoginResponse) {
    localStorage.setItem('access_token', token.access);
    localStorage.setItem('refresh_token', token.refresh);
  }
}
