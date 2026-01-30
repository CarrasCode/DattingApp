import { Component, effect, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { UserService } from '../../../services/user-service';
import { IEditProfile, PhotoUpload } from '../../../models/user';
import { lastValueFrom } from 'rxjs';

@Component({
  selector: 'app-profile-editor',
  imports: [ReactiveFormsModule],
  templateUrl: './profile-editor.html',
  styleUrl: './profile-editor.scss',
})
export class ProfileEditor {
  userService = inject(UserService);
  profile = this.userService.currentUser;
  selectedFile: File | null = null;

  state = signal({
    loading: false,
    error: null as string | null,
    success: false,
  });

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

  photoForm = new FormGroup({
    image: new FormControl(),
    caption: new FormControl(''),
    is_main: new FormControl(false),
  });

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files?.length) {
      this.selectedFile = input.files[0];
      this.photoForm.patchValue({ image: input.files[0] });
    }
  }
  async onSubmit() {
    if (!this.profileEditor.valid) {
      console.log(this.profileEditor);
      return;
    }
    this.state.set({
      error: null,
      loading: true,
      success: false,
    });
    try {
      const response = await lastValueFrom(
        this.userService.updateProfile(this.profileEditor.value as IEditProfile),
      );

      this.state.set({
        loading: false,
        success: true,
        error: null,
      });
      console.log(response);
      setTimeout(() => {
        this.state.set({
          loading: false,
          success: false,
          error: null,
        });
      }, 3000);
    } catch (err) {
      console.error(err);
      this.state.set({
        error: 'Ocurrio un error, prueba otra vez',
        loading: false,
        success: false,
      });
    }
  }

  async onSubmitPhoto() {
    if (!this.photoForm.valid) {
      console.log(this.photoForm);
      return;
    }
    this.state.set({
      error: null,
      loading: true,
      success: false,
    });
    try {
      const response = await lastValueFrom(
        this.userService.uploadPhoto(this.photoForm.value as PhotoUpload),
      );

      this.state.set({
        loading: false,
        success: true,
        error: null,
      });
      console.log(response);
      setTimeout(() => {
        this.state.set({
          loading: false,
          success: false,
          error: null,
        });
      }, 3000);
    } catch (err) {
      console.error(err);
      this.state.set({
        error: 'Ocurrio un error, prueba otra vez',
        loading: false,
        success: false,
      });
    }
  }
  async onDeletePhoto(photoId: string) {
    this.state.set({
      error: null,
      loading: true,
      success: false,
    });
    try {
      await lastValueFrom(this.userService.deletePhoto(photoId));

      this.state.set({
        loading: false,
        success: true,
        error: null,
      });

      setTimeout(() => {
        this.state.set({
          loading: false,
          success: false,
          error: null,
        });
      }, 3000);
    } catch (err) {
      console.error(err);
      this.state.set({
        error: 'Ocurrio un error, prueba otra vez',
        loading: false,
        success: false,
      });
    }
  }
}
