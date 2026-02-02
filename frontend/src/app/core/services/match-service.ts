import { HttpClient } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';
import { environment } from '../../../environments/environment';
import { PublicProfile } from '../models/user';

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
  private http = inject(HttpClient);
  matches = signal<Match[]>([]);

  constructor() {
    this.getMatches();
  }
  getMatches() {
    this.http.get<Match[]>(environment.apiUrl + '/social/matches/').subscribe({
      next: (data) => {
        this.matches.set(data);
      },
      error: (err) => console.log(err),
    });
  }
}
