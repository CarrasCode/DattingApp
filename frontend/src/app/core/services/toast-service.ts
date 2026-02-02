import { Injectable, signal } from '@angular/core';

interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info';
}
@Injectable({
  providedIn: 'root',
})
export class ToastService {
  readonly toasts = signal<Toast[]>([]);

  removeToast(id: string) {
    this.toasts.update((list) => list.filter((toast) => toast.id !== id));
  }

  private showToast(message: string, type: Toast['type'] = 'info', duration = 3000) {
    const id = crypto.randomUUID();
    const newToast: Toast = {
      id,
      message,
      type,
    };
    this.toasts.update((prev) => [...prev, newToast]);

    setTimeout(() => this.removeToast(id), duration);
  }

  success(msg: string) {
    this.showToast(msg, 'success');
  }
  error(msg: string) {
    this.showToast(msg, 'success');
  }
  warning(msg: string) {
    this.showToast(msg, 'success');
  }
}
