import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { tap } from 'rxjs/operators';

export interface LoginCredentials {
  email: string;
  password: string;
}
interface LoginResponse {
  access: string;
  refresh: string;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  httpClient = inject(HttpClient);

  login(credentials: LoginCredentials) {
    return this.httpClient
      .post<LoginResponse>(
        environment.apiUrl + '/users/auth/login/',

        credentials,
      )
      .pipe(
        tap((response) => {
          localStorage.setItem('access_token', response.access);
          localStorage.setItem('refresh_token', response.refresh);
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
          localStorage.setItem('access_token', response.access);
          localStorage.setItem('refresh_token', response.refresh);
        }),
      );
  }
}
