import { Component, input } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { Match } from '@core/services/match-service';

@Component({
  selector: 'app-matches-list',
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './matches-list.html',
  styleUrl: './matches-list.scss',
})
export class MatchesList {
  matches = input.required<Match[]>();
}
