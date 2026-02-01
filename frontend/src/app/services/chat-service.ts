import { Injectable, signal } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { environment } from '../../environments/environment';

interface ChatMessage {
  message: string;
  sender_id?: string;
  timestamp?: string;
}

@Injectable({
  providedIn: 'root',
})
export class ChatService {
  // 1. La variable guarda la conexión activa, puede ser null al principio
  private socket$: WebSocketSubject<ChatMessage> | null = null;

  // 2. El State local
  messages = signal<ChatMessage[]>([]);

  connect(matchId: string) {
    const token = localStorage.getItem('access_token');
    const url = `${environment.wsUrl}/${matchId}/?token=${token}`;

    // 3. Crear la conexión
    this.socket$ = webSocket(url);

    // 4. Escuchar (IMPORTANTE: Sin subscribe no conecta)
    this.socket$.subscribe({
      next: (msg) => {
        console.log('Mensaje recibido:', msg);
        // Actualizar signal inmutablemente
        this.messages.update((prev) => [...prev, msg]);
      },
      error: (err) => console.error('Error WS:', err),
      complete: () => console.log('Conexión cerrada'),
    });
  }
  sendMessage(text: string) {
    if (this.socket$) {
      // 5. Enviar mensaje al backend
      this.socket$.next({ message: text });
    }
  }
  disconnect() {
    this.socket$?.complete();
    this.socket$ = null;
  }
}
