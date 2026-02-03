import { HttpClient } from '@angular/common/http';
import { effect, inject, Injectable, signal } from '@angular/core';
import { environment } from '../../../environments/environment';
import { PublicProfile } from '../models/user';
import { AuthService } from './auth-service';

export interface Match {
  id: string;
  created_at: string;
  other_user: PublicProfile;
  distance: string;
}

@Injectable({
  providedIn: 'root',
})
export class MatchService {
  private readonly http = inject(HttpClient);
  private readonly authService = inject(AuthService);

  matches = signal<Match[]>([]);

  constructor() {
    // Reacciona automáticamente a cambios en el estado de autenticación
    effect(() => {
      if (this.authService.isAuthenticated()) {
        this.refreshMatches();
      } else {
        this.clearMatches();
      }
    });
  }

  // Método público para refrescar matches
  refreshMatches() {
    this.http.get<Match[]>(environment.apiUrl + '/social/matches/').subscribe({
      next: (data) => {
        this.matches.set(data);
      },
      error: (err) => console.log(err),
    });
  }

  // Limpiar datos al cerrar sesión
  private clearMatches() {
    this.matches.set([]);
  }
}
