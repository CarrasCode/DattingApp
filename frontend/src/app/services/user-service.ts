import { Injectable } from '@angular/core';
import { signal, computed } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class UserService {
  users = signal([
    { name: 'Laura', age: 25 },
    { name: 'Pablo', age: 28 },
    { name: 'Lucía', age: 24 },
  ]);
  matchesCount = computed(() => this.users().length);

  removeUser(name: string) {
    this.users.update((prev) => prev.filter((u) => u.name !== name));
  }
}
