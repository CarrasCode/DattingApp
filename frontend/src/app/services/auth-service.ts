import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { environment } from '../../environments/environment';

export interface loginCredentials {
  email: string;
  password: string;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  httpClient = inject(HttpClient);

  login(credentials: loginCredentials) {
    return this.httpClient.post(environment.apiUrl + '/users/auth/login', { credentials });
  }
}
