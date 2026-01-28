import { inject, Injectable } from '@angular/core';
import { signal, computed } from '@angular/core';
import { User } from '../models/user';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
@Injectable({
  providedIn: 'root',
})
export class UserService {
  private httpClient = inject(HttpClient);
  users = signal<User[]>([]);
  matchesCount = computed(() => this.users().length);

  constructor() {
    this.getUsers();
  }
  private removeUser(id: number) {
    this.users.update((users) => users.filter((u) => u.id !== id));
  }

  getUsers() {
    this.httpClient
      .get<User[]>(environment.apiUrl + '/users/profiles/')
      .subscribe({ next: (data) => this.users.set(data), error: (err) => console.log(err) });
  }

  sendSwipe(targetId: number, action: 'LIKE' | 'DISLIKE') {
    // 1. Eliminamos visualmente al usuario YA (falsa sensación de velocidad)
    this.removeUser(targetId);

    // 2. Enviamos la petición real
    return this.httpClient.post<{ match: boolean }>(environment.apiUrl + '/social/swipes/', {
      target: targetId,
      value: action,
    });
  }

  undoRemove(user: User) {
    this.users.update((prev) => [user, ...prev]);
  }
}
