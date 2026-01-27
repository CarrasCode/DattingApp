import { Component, inject } from '@angular/core';
import { UserService } from '../../services/user-service';
import { UserCard } from '../user-card/user-card';

@Component({
  selector: 'app-home',
  imports: [UserCard],
  templateUrl: './home.html',
  styleUrl: './home.scss',
})
export class Home {
  userService = inject(UserService);

  users = this.userService.users;
  matchesCount = this.userService.matchesCount;

  removeUser(name: string) {
    this.userService.removeUser(name);
  }
}
