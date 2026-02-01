import { Component, inject, OnInit, signal } from '@angular/core';
import { ChatService } from '../../services/chat-service';
import { FormsModule } from '@angular/forms';
import { UserService } from '../../services/user-service';

@Component({
  selector: 'app-chat',
  imports: [FormsModule],
  templateUrl: './chat.html',
  styleUrl: './chat.scss',
})
export class Chat implements OnInit {
  private readonly chatService = inject(ChatService);
  private readonly userService = inject(UserService);
  messages = this.chatService.messages;
  currentUser = this.userService.currentUser;

  newMessage = signal('');
  ngOnInit(): void {
    this.chatService.connect('9f3944ee-5c31-4500-b71c-b8d15b070fb8');
  }

  sendMessage() {
    if (!this.newMessage().trim()) return;

    this.chatService.sendMessage(this.newMessage());
    this.newMessage.set('');
  }
}
