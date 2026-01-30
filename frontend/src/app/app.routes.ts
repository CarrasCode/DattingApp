import { Routes } from '@angular/router';
import { Home } from './components/home/home';
import { Login } from './components/login/login';
import { ProfileEditor } from './components/profile/profile-editor/profile-editor';

export const routes: Routes = [
  { path: '', component: Home },
  { path: 'login', component: Login },
  { path: 'edit', component: ProfileEditor },
];
