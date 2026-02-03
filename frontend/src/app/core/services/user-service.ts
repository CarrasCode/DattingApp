import { inject, Injectable } from '@angular/core';
import { signal, computed } from '@angular/core';
import { ICurrentProfile, IEditProfile, IPhoto, PhotoUpload, PublicProfile } from '../models/user';
import { environment } from '../../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { tap } from 'rxjs';
@Injectable({
  providedIn: 'root',
})
export class UserService {
  private readonly httpClient = inject(HttpClient);
  users = signal<PublicProfile[]>([]);
  matchesCount = computed(() => this.users().length);
  currentUser = signal<ICurrentProfile | null>(null);
  mainPhoto = computed(() => this.currentUser()?.photos.find((photo) => photo.is_main));

  constructor() {
    this.refreshUsers();
    this.refreshCurrentUser();
  }

  private removeUser(id: string) {
    this.users.update((users) => users.filter((u) => u.id !== id));
  }

  // Limpiar datos al cerrar sesión
  clearUserData() {
    this.currentUser.set(null);
    this.users.set([]);
  }

  // Métodos públicos para refrescar datos
  refreshUsers() {
    this.httpClient
      .get<PublicProfile[]>(environment.apiUrl + '/users/profiles/')
      .subscribe({ next: (data) => this.users.set(data), error: (err) => console.log(err) });
  }

  refreshCurrentUser() {
    this.httpClient
      .get<ICurrentProfile>(environment.apiUrl + '/users/profiles/me/')
      .subscribe({ next: (data) => this.currentUser.set(data), error: (err) => console.log(err) });
  }

  // Captura ubicación del navegador y la guarda en el perfil
  updateLocation(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation no soportado'));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const coords = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          };
          this.updateProfile(coords).subscribe({
            next: () => resolve(),
            error: (err) => reject(err),
          });
        },
        (err) => {
          console.warn('Ubicación denegada:', err.message);
          // No rechazamos, solo resolvemos sin ubicación (es opcional)
          resolve();
        },
      );
    });
  }

  sendSwipe(targetId: string, action: 'LIKE' | 'DISLIKE') {
    // 1. Eliminamos visualmente al usuario YA (falsa sensación de velocidad)
    this.removeUser(targetId);

    // 2. Enviamos la petición real
    return this.httpClient.post<{ match: boolean }>(environment.apiUrl + '/social/swipes/', {
      target: targetId,
      value: action,
    });
  }
  updateProfile(datosNuevos: IEditProfile) {
    return this.httpClient
      .patch<IEditProfile>(environment.apiUrl + '/users/profiles/me/', {
        ...datosNuevos,
      })
      .pipe(
        tap((updateData) => {
          this.currentUser.update((prev) => {
            if (!prev) return null;
            return { ...prev, ...updateData };
          });
          // Refrescar usuarios ya que las preferencias pueden haber cambiado
          this.refreshUsers();
        }),
      );
  }

  undoRemove(user: PublicProfile) {
    this.users.update((prev) => [user, ...prev]);
  }

  uploadPhoto(imagen: PhotoUpload) {
    const fd = new FormData();
    fd.append('image', imagen.image);
    fd.append('is_main', imagen.is_main ? 'true' : 'false');
    if (imagen.caption) fd.append('caption', imagen.caption);

    return this.httpClient.post<IPhoto>(environment.apiUrl + '/users/photos/', fd).pipe(
      tap((updated) =>
        this.currentUser.update((prev) => {
          if (!prev) return null;
          const photos = [...prev.photos, updated];
          return { ...prev, photos };
        }),
      ),
    );
  }
  deletePhoto(photoId: string) {
    return this.httpClient.delete<void>(environment.apiUrl + `/users/photos/${photoId}/`).pipe(
      tap(() => {
        this.currentUser.update((prev) => {
          if (!prev) return null;
          const photos = prev.photos.filter((p) => p.id !== photoId);
          return { ...prev, photos: photos };
        });
      }),
    );
  }
}
