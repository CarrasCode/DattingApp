import { Component, computed, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { PhotoUpload } from '@core/models/user';
import { UserService } from '@core/services/user-service';
import { lastValueFrom } from 'rxjs';
import { ProfileState } from '../profile.state';
import { ToastService } from '@core/services/toast-service';

@Component({
  selector: 'app-profile-photos',
  imports: [ReactiveFormsModule],
  templateUrl: './profile-photos.html',
  styleUrl: './profile-photos.scss',
})
export class ProfilePhotos {
  private readonly userService = inject(UserService);
  private readonly profileState = inject(ProfileState);
  private readonly toasService = inject(ToastService);
  protected readonly editMode = this.profileState.editMode;
  protected readonly loading = signal(false);
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
    this.loading.set(true);
    try {
      await lastValueFrom(this.userService.uploadPhoto(this.photoForm.value as PhotoUpload));
      this.toasService.success('Foto subida!');
    } catch (err) {
      this.toasService.error('Error subiendo foto');
      console.error(err);
    } finally {
      this.loading.set(false);
      this.selectedFile.set(null);
    }
  }
  async onDeletePhoto(photoId: string) {
    this.loading.set(true);
    try {
      await lastValueFrom(this.userService.deletePhoto(photoId));

      this.toasService.success('Foto eliminada!');
    } catch (err) {
      this.toasService.error('Error eliminando foto');
      console.error(err);
    } finally {
      this.loading.set(false);
    }
  }
}
