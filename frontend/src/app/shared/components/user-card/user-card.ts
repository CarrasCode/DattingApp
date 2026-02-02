import { Component, input, output } from '@angular/core';
import { PublicProfile } from '@core/models/user';

@Component({
  selector: 'app-user-card',
  imports: [],
  templateUrl: './user-card.html',
  styleUrl: './user-card.scss',
})
export class UserCard {
  user = input.required<PublicProfile>();

  swipe = output<'LIKE' | 'DISLIKE'>();

  onSwipe(value: 'LIKE' | 'DISLIKE') {
    this.swipe.emit(value);
  }
}
