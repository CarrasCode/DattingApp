import { Component, effect, inject, input, OnDestroy, signal } from '@angular/core';
import { ChatService } from '@core/services/chat-service';
import { FormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';
import { UserService } from '@core/services/user-service';

@Component({
  selector: 'app-chat',
  imports: [FormsModule, DatePipe],
  templateUrl: './chat.html',
  styleUrl: './chat.scss',
})
export class Chat implements OnDestroy {
  private readonly chatService = inject(ChatService);
  private readonly userService = inject(UserService);
  messages = this.chatService.messages;
  id = input<string>();

  newMessage = signal('');
  constructor() {
    effect(() => {
      const userId = this.userService.currentUser()?.id;
      const matchId = this.id();

      if (userId && matchId) this.chatService.connect(matchId, userId);
    });
  }

  sendMessage() {
    if (!this.newMessage().trim()) return;

    this.chatService.sendMessage(this.newMessage());
    this.newMessage.set('');
  }
  ngOnDestroy(): void {
    this.chatService.disconnect();
  }
}
