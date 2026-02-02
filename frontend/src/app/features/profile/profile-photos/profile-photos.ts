import { Component, computed, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { PhotoUpload } from '@core/models/user';
import { UserService } from '@core/services/user-service';
import { lastValueFrom } from 'rxjs';
import { ProfileState } from '../profile.state';

@Component({
  selector: 'app-profile-photos',
  imports: [ReactiveFormsModule],
  templateUrl: './profile-photos.html',
  styleUrl: './profile-photos.scss',
})
export class ProfilePhotos {
  private readonly userService = inject(UserService);
  private readonly profileState = inject(ProfileState);
  protected readonly editMode = this.profileState.editMode;
  protected readonly state = signal({
    loading: false,
    error: null as string | null,
    success: false,
  });
  protected readonly selectedFile = signal<File | null>(null);
  protected readonly photos = computed(() => this.userService.currentUser()?.photos ?? []);

  protected photoForm = new FormGroup({
    image: new FormControl(),
    caption: new FormControl(''),
    is_main: new FormControl(false),
  });

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files?.length) {
      this.selectedFile.set(input.files[0]);
      this.photoForm.patchValue({ image: input.files[0] });
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
    } finally {
      this.selectedFile.set(null);
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
