import { Component, input, output } from '@angular/core';
import { User } from '../../models/user';

@Component({
  selector: 'app-user-card',
  imports: [],
  templateUrl: './user-card.html',
  styleUrl: './user-card.scss',
})
export class UserCard {
  user = input.required<User>();

  remove = output<void>();

  onRemove() {
    this.remove.emit();
  }
}
