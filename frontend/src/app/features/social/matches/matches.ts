import { Component, inject } from '@angular/core';
import { MatchService } from '@core/services/match-service';
import { RouterOutlet } from '@angular/router';
import { MatchesList } from '../components/matches-list/matches-list';

@Component({
  selector: 'app-matches',
  imports: [RouterOutlet, MatchesList],
  templateUrl: './matches.html',
  styleUrl: './matches.scss',
})
export class Matches {
  private matchService = inject(MatchService);

  protected matches = this.matchService.matches;
}
