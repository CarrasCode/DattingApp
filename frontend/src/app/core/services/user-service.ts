import { inject, Injectable } from '@angular/core';
import { signal, computed } from '@angular/core';
import { ICurrentProfile, IEditProfile, IPhoto, PhotoUpload, User } from '../models/user';
import { environment } from '../../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { tap } from 'rxjs';
@Injectable({
  providedIn: 'root',
})
export class UserService {
  private readonly httpClient = inject(HttpClient);
  users = signal<User[]>([]);
  matchesCount = computed(() => this.users().length);
  currentUser = signal<ICurrentProfile | null>(null);

  constructor() {
    this.getUsers();
    this.getCurrentUser();
  }
  private removeUser(id: string) {
    this.users.update((users) => users.filter((u) => u.id !== id));
  }

  private getUsers() {
    this.httpClient
      .get<User[]>(environment.apiUrl + '/users/profiles/')
      .subscribe({ next: (data) => this.users.set(data), error: (err) => console.log(err) });
  }
  private getCurrentUser() {
    this.httpClient
      .get<ICurrentProfile>(environment.apiUrl + '/users/profiles/me/')
      .subscribe({ next: (data) => this.currentUser.set(data), error: (err) => console.log(err) });
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
        }),
      );
  }
  undoRemove(user: User) {
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
