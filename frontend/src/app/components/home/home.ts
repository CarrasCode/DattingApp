import { Component, inject, signal } from '@angular/core';
import { UserService } from '../../services/user-service';
import { UserCard } from '../user-card/user-card';
import { MatchModal } from '../match-modal/match-modal';

@Component({
  selector: 'app-home',
  imports: [UserCard, MatchModal],
  templateUrl: './home.html',
  styleUrl: './home.scss',
})
export class Home {
  userService = inject(UserService);
  showMatchModal = signal<boolean>(true);
  users = this.userService.users;
  matchesCount = this.userService.matchesCount;

  onSwipe(id: string, value: 'LIKE' | 'DISLIKE') {
    const userBackup = this.users().find((u) => u.id === id);

    this.userService.sendSwipe(id, value).subscribe({
      next: (data) => {
        console.log(data);
        this.showMatchModal.set(true);
      },
      error: (err) => {
        console.log(err);
        if (userBackup) this.userService.undoRemove(userBackup);
      },
    });
  }

  cerrarModal() {
    this.showMatchModal.set(false);
  }
}
