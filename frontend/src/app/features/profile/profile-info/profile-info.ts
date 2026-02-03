import { Component, effect, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';

import { lastValueFrom } from 'rxjs';
import { UserService } from '@core/services/user-service';
import { IEditProfile } from '@core/models/user';
import { ProfileState } from '../profile.state';
import { ToastService } from '@core/services/toast-service';

@Component({
  selector: 'app-profile-info',
  imports: [ReactiveFormsModule],
  templateUrl: './profile-info.html',
  styleUrl: './profile-info.scss',
})
export class ProfileInfo {
  userService = inject(UserService);
  profileState = inject(ProfileState);
  toastService = inject(ToastService);

  profile = this.userService.currentUser;
  mainPhoto = this.userService.mainPhoto;
  editMode = this.profileState.editMode;

  loading = signal(false);
  constructor() {
    effect(() => {
      const user = this.profile();
      if (user) {
        this.profileEditor.patchValue({
          first_name: user.first_name,
          bio: user.bio,
          work: user.work,
          birth_date: user.birth_date,
          gender: user.gender,
          gender_preference: user.gender_preference,
          max_distance: user.max_distance,
          min_age: user.min_age,
          max_age: user.max_age,
        });
      }
    });
  }
  profileEditor = new FormGroup({
    first_name: new FormControl('', Validators.required),
    bio: new FormControl(''),
    work: new FormControl(''),
    birth_date: new FormControl(''),
    gender: new FormControl(this.profile()?.gender, [Validators.required]),
    gender_preference: new FormControl(this.profile()?.gender_preference, [Validators.required]),
    max_distance: new FormControl(0, [Validators.required]),
    min_age: new FormControl(18, [Validators.min(18), Validators.required]),
    max_age: new FormControl(99, [Validators.max(100), Validators.required]),
  });

  async onSubmit() {
    if (!this.profileEditor.valid) {
      console.log(this.profileEditor);
      return;
    }
    this.loading.set(true);
    try {
      await lastValueFrom(this.userService.updateProfile(this.profileEditor.value as IEditProfile));
      this.toastService.success('Perfil guardado!');
      this.editMode.set(false);
    } catch (err) {
      this.toastService.error(`Error guardando perfil`);
      console.log(err);
    } finally {
      this.loading.set(false);
    }
  }

  async updateLocation() {
    this.loading.set(true);
    try {
      await this.userService.updateLocation();
      this.toastService.success('Ubicación actualizada');
    } catch {
      this.toastService.error('Error al actualizar ubicación');
    } finally {
      this.loading.set(false);
    }
  }
}
