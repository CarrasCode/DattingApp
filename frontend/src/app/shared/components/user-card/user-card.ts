import { Component, input, output, signal } from '@angular/core';
import { PublicProfile } from '@core/models/user';
import { UserDetailModal } from '../user-detail-modal/user-detail-modal';

@Component({
  selector: 'app-user-card',
  imports: [UserDetailModal],
  templateUrl: './user-card.html',
  styleUrl: './user-card.scss',
})
export class UserCard {
  user = input.required<PublicProfile>();

  swipe = output<'LIKE' | 'DISLIKE'>();

  protected showDetail = signal(false);

  openDetail() {
    this.showDetail.set(true);
  }

  closeDetail() {
    this.showDetail.set(false);
  }

  onSwipe(value: 'LIKE' | 'DISLIKE') {
    this.swipe.emit(value);
    this.showDetail.set(false);
  }
}
