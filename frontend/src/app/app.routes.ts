import { Routes } from '@angular/router';
import { Home } from './components/home/home';
import { Login } from './components/login/login';
import { ProfileEditor } from './components/profile/profile-editor/profile-editor';
import { Register } from './components/register/register';

export const routes: Routes = [
  { path: '', component: Home },
  { path: 'login', component: Login },
  { path: 'register', component: Register },

  { path: 'edit', component: ProfileEditor },
];
