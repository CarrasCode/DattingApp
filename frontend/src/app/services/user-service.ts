import { inject, Injectable } from '@angular/core';
import { signal, computed } from '@angular/core';
import { User } from '../models/user';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class UserService {
  httpClient = inject(HttpClient);
  users = signal<User[]>([]);
  matchesCount = computed(() => this.users().length);

  removeUser(id: number) {
    this.users.update((prev) => prev.filter((u) => u.id !== id));
  }

  getUsers() {
    return this.httpClient
      .get<User[]>(environment.apiUrl + 'users/profiles/')
      .subscribe((usuarios) => this.users.set(usuarios));
  }
}
