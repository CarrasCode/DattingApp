import { Routes } from '@angular/router';
import { Login } from './features/auth/login/login';
import { Register } from './features/auth/register/register';
import { Chat } from './features/social/chat/chat';
import { authGuard } from './core/guards/auth-guard';
import { Home } from './features/home/home';
import { Matches } from '@features/social/matches/matches';
import { Profile } from '@features/profile/profile';
import { ProfileInfo } from '@features/profile/profile-info/profile-info';
import { ProfilePhotos } from '@features/profile/profile-photos/profile-photos';

export const routes: Routes = [
  { path: '', canActivate: [authGuard], component: Home },
  { path: 'login', component: Login },
  { path: 'register', component: Register },
  {
    path: 'matches',
    canActivate: [authGuard],
    component: Matches,
    children: [{ path: ':id', component: Chat }],
  },
  {
    path: 'profile',
    canActivate: [authGuard],
    component: Profile,
    children: [
      { path: '', redirectTo: 'info', pathMatch: 'full' },
      { path: 'info', component: ProfileInfo },
      { path: 'photos', component: ProfilePhotos },
    ],
  },
];
