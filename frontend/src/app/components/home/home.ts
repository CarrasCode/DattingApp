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

  onSwipe(id: number, value: 'LIKE' | 'DISLIKE') {
    const userBackup = this.users().find((u) => u.id === id);

    this.userService.sendSwipe(id, value).subscribe({
      next: (data) => console.log(data),
      error: (err) => {
        console.log(err);
        if (userBackup) this.userService.undoRemove(userBackup);
      },
    });
  }
}
