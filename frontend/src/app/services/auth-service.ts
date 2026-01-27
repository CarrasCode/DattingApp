import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { tap } from 'rxjs/operators';

export interface loginCredentials {
  email: string;
  password: string;
}
interface loginResponse {
  access: string;
  refresh: string;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  httpClient = inject(HttpClient);

  login(credentials: loginCredentials) {
    return this.httpClient
      .post<loginResponse>(
        environment.apiUrl + '/users/auth/login/',

        credentials,
      )
      .pipe(tap((response) => localStorage.setItem('access_token', response.access)));
  }
}
