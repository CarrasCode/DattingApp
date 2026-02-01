import { Component, inject, OnInit, signal } from '@angular/core';
import { ChatService } from '../../services/chat-service';
import { FormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-chat',
  imports: [FormsModule, DatePipe],
  templateUrl: './chat.html',
  styleUrl: './chat.scss',
})
export class Chat implements OnInit {
  private readonly chatService = inject(ChatService);
  messages = this.chatService.messages;

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
