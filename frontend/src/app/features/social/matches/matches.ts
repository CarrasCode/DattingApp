import { Component, inject } from '@angular/core';
import { MatchService } from '@core/services/match-service';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-matches',
  imports: [RouterLink],
  templateUrl: './matches.html',
  styleUrl: './matches.scss',
})
export class Matches {
  private matchService = inject(MatchService);

  protected matches = this.matchService.matches;
}
