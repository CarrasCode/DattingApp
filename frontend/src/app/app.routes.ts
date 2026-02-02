import { Routes } from '@angular/router';
import { Login } from './features/auth/login/login';
import { ProfileEditor } from './features/profile/profile-editor/profile-editor';
import { Register } from './features/auth/register/register';
import { Chat } from './features/social/chat/chat';
import { authGuard } from './core/guards/auth-guard';
import { Home } from './features/home/home';
import { Matches } from '@features/social/matches/matches';

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
  { path: 'edit', canActivate: [authGuard], component: ProfileEditor },
];
