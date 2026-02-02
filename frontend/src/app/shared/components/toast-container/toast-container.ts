import { Component, computed, inject } from '@angular/core';
import { ToastService } from '@core/services/toast-service';

@Component({
  selector: 'app-toast-container',
  imports: [],
  templateUrl: './toast-container.html',
  styleUrl: './toast-container.scss',
})
export class ToastContainer {
  private readonly toasService = inject(ToastService);
  protected readonly toasts = computed(() => this.toasService.toasts());

  dismiss(id: string) {
    this.toasService.removeToast(id);
  }
}
