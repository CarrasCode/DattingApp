import { Component, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService, RegisterCredentials } from '@core/services/auth-service';
import { UserService } from '@core/services/user-service';
import { IEditProfile, PhotoUpload } from '@core/models/user';
import { lastValueFrom } from 'rxjs';

interface Step {
  title: string;
  icon: string;
}

@Component({
  selector: 'app-register',
  imports: [ReactiveFormsModule],
  templateUrl: './register.html',
  styleUrl: './register.scss',
})
export class Register {
  private readonly authService = inject(AuthService);
  private readonly userService = inject(UserService);
  private readonly router = inject(Router);

  protected currentStep = signal(0);
  protected loading = signal(false);
  protected error = signal<string | null>(null);

  protected steps: Step[] = [
    { title: 'Cuenta', icon: '📧' },
    { title: 'Sobre ti', icon: '👤' },
    { title: 'Preferencias', icon: '💘' },
    { title: 'Foto', icon: '📷' },
  ];

  // --- FORMULARIOS POR PASO ---

  // Paso 1: Cuenta
  accountForm = new FormGroup({
    email: new FormControl('', [Validators.required, Validators.email]),
    password: new FormControl('', [Validators.required, Validators.minLength(8)]),
    password_confirm: new FormControl('', [Validators.required]),
  });

  // Paso 2: Sobre ti
  profileForm = new FormGroup({
    first_name: new FormControl('', [Validators.required, Validators.minLength(2)]),
    birth_date: new FormControl('', [Validators.required]),
    gender: new FormControl('', [Validators.required]),
    work: new FormControl(''),
    bio: new FormControl(''),
  });

  // Paso 3: Preferencias
  preferencesForm = new FormGroup({
    gender_preference: new FormControl('A', [Validators.required]),
    min_age: new FormControl(18, [Validators.required, Validators.min(18)]),
    max_age: new FormControl(99, [Validators.required, Validators.max(99)]),
    max_distance: new FormControl(50, [Validators.required]),
  });

  // Paso 4: Foto
  protected selectedPhoto = signal<File | null>(null);
  protected photoPreview = signal<string | null>(null);

  // --- NAVEGACIÓN ---

  nextStep() {
    if (this.currentStep() < this.steps.length - 1) {
      this.currentStep.update((s) => s + 1);
    }
  }

  prevStep() {
    if (this.currentStep() > 0) {
      this.currentStep.update((s) => s - 1);
    }
  }

  isStepValid(): boolean {
    switch (this.currentStep()) {
      case 0:
        return this.accountForm.valid && this.passwordsMatch();
      case 1:
        return this.profileForm.valid;
      case 2:
        return this.preferencesForm.valid;
      case 3:
        return this.selectedPhoto() !== null;
      default:
        return false;
    }
  }

  passwordsMatch(): boolean {
    return (
      this.accountForm.get('password')?.value === this.accountForm.get('password_confirm')?.value
    );
  }

  // --- FOTO ---

  onPhotoSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      const file = input.files[0];
      this.selectedPhoto.set(file);

      // Preview
      const reader = new FileReader();
      reader.onload = (e) => {
        this.photoPreview.set(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  }

  // --- ENVÍO FINAL ---

  async onSubmit() {
    if (!this.isStepValid()) return;

    this.loading.set(true);
    this.error.set(null);

    try {
      // 1. Crear cuenta
      await lastValueFrom(this.authService.register(this.accountForm.value as RegisterCredentials));

      // 2. Crear perfil
      const profileData: IEditProfile = {
        ...this.profileForm.value,
        ...this.preferencesForm.value,
      } as IEditProfile;

      await lastValueFrom(this.userService.updateProfile(profileData));

      // 3. Subir foto
      const photoData: PhotoUpload = {
        image: this.selectedPhoto()!,
        is_main: true,
        caption: '',
      };
      await lastValueFrom(this.userService.uploadPhoto(photoData));

      // 4. Capturar ubicación (opcional, no bloquea si el usuario deniega)
      await this.userService.updateLocation();

      // 5. Refrescar datos y navegar
      this.userService.refreshCurrentUser();
      this.userService.refreshUsers();
      this.authService.isAuthenticated.set(true);
      this.router.navigate(['/']);
    } catch (err: unknown) {
      console.error(err);
      this.error.set(this.extractErrorMessage(err));
    } finally {
      this.loading.set(false);
    }
  }

  // Extrae mensaje de error legible del backend
  private extractErrorMessage(err: unknown): string {
    const httpError = err as { error?: Record<string, string[]> };

    if (httpError?.error) {
      // Recorre los campos con error y construye mensaje
      const messages: string[] = [];
      for (const [field, errors] of Object.entries(httpError.error)) {
        if (Array.isArray(errors)) {
          messages.push(`${field}: ${errors.join(', ')}`);
        }
      }
      if (messages.length > 0) {
        return messages.join(' | ');
      }
    }

    return 'Error al registrarse. Inténtalo de nuevo.';
  }
}
