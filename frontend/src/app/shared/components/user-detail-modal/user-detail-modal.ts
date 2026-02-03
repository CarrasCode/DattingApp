import { Component, input, output } from '@angular/core';
import { PublicProfile } from '@core/models/user';

@Component({
  selector: 'app-user-detail-modal',
  imports: [],
  templateUrl: './user-detail-modal.html',
  styleUrl: './user-detail-modal.scss',
})
export class UserDetailModal {
  user = input.required<PublicProfile>();

  closeModal = output<void>();
  swipe = output<'LIKE' | 'DISLIKE'>();

  protected currentPhotoIndex = 0;

  onClose() {
    this.closeModal.emit();
  }

  onSwipe(value: 'LIKE' | 'DISLIKE') {
    this.swipe.emit(value);
    this.closeModal.emit();
  }

  nextPhoto() {
    const photos = this.user().photos;
    if (this.currentPhotoIndex < photos.length - 1) {
      this.currentPhotoIndex++;
    }
  }

  prevPhoto() {
    if (this.currentPhotoIndex > 0) {
      this.currentPhotoIndex--;
    }
  }
}
