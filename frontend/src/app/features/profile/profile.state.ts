import { Injectable, signal } from '@angular/core';

@Injectable()
export class ProfileState {
  editMode = signal(false);
  toggleEditMode() {
    this.editMode.update((prev) => !prev);
  }
}
