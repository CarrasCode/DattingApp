import { Routes } from '@angular/router';
import { Home } from './components/home/home';
import { Login } from './components/login/login';
import { ProfileEditor } from './components/profile/profile-editor/profile-editor';
import { Register } from './components/register/register';
import { Chat } from './components/chat/chat';
import { Matches } from './components/matches/matches';
import { authGuard } from './core/guards/auth-guard';

export const routes: Routes = [
  { path: '', canActivate: [authGuard], component: Home },
  { path: 'login', component: Login },
  { path: 'register', component: Register },
  { path: 'match', canActivate: [authGuard], component: Matches },
  { path: 'chat/:id', canActivate: [authGuard], component: Chat },
  { path: 'edit', canActivate: [authGuard], component: ProfileEditor },
];
