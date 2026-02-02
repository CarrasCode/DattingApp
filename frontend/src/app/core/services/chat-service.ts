import { inject, Injectable, signal } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { environment } from '../../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { lastValueFrom, retry } from 'rxjs';

export interface ChatMessage {
  text: string;
  is_me: boolean;
  created_at: string;
}
// 2. Payloads de RED (Internos del servicio)
interface WSSendPayload {
  message: string;
}
interface WSReceivePayload {
  message: string;
  sender_id: string;
  timestamp: string;
}
@Injectable({
  providedIn: 'root',
})
export class ChatService {
  private http = inject(HttpClient);
  // La variable guarda la conexión activa, puede ser null al principio
  private socket$: WebSocketSubject<WSSendPayload | WSReceivePayload> | null = null;
  messages = signal<ChatMessage[]>([]);

  async connect(matchId: string, currentUserId: string) {
    // 1. Limpiar estado anterior (Evitar ghosts)
    this.messages.set([]);

    // 2. Desconectar websocket anterior si existía (Evitar doble conexión)
    this.disconnect();

    await this.getHistory(matchId);

    const token = localStorage.getItem('access_token');
    const url = `${environment.wsUrl}/${matchId}/?token=${token}`;
    // 3. Crear la conexión
    this.socket$ = webSocket(url);

    // 4. Escuchar (IMPORTANTE: Sin subscribe no conecta)
    this.socket$.subscribe((data) => {
      const payload = data as WSReceivePayload;
      const uiMessage: ChatMessage = {
        text: payload.message,
        is_me: payload.sender_id === currentUserId,
        created_at: payload.timestamp,
      };
      this.messages.update((prev) => [...prev, uiMessage]);
    });
  }
  sendMessage(text: string) {
    const payload: WSSendPayload = { message: text };
    this.socket$?.next(payload);
  }
  async getHistory(matchId: string) {
    try {
      const history = await lastValueFrom(
        this.http
          .get<ChatMessage[]>(`${environment.apiUrl}/chat/messages/?match_id=${matchId}`)
          .pipe(retry({ count: 3, delay: 2000 })),
      );
      this.messages.set(history.reverse());
    } catch (e) {
      console.log('Error cargando historial', e);
    }
  }
  disconnect() {
    this.socket$?.complete();
    this.socket$ = null;
  }
}
