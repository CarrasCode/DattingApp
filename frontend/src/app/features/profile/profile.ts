import { Component, inject } from '@angular/core';
import { RouterOutlet, RouterLink } from '@angular/router';
import { ProfileState } from './profile.state';

@Component({
  selector: 'app-profile',
  imports: [RouterOutlet, RouterLink],
  templateUrl: './profile.html',
  styleUrl: './profile.scss',
  providers: [ProfileState],
})
export class Profile {
  protected profileStateService = inject(ProfileState);
}
