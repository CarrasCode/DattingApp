import { Component, output } from '@angular/core';

@Component({
  selector: 'app-match-modal',
  imports: [],
  templateUrl: './match-modal.html',
  styleUrl: './match-modal.scss',
})
export class MatchModal {
  modalEmit = output<void>();

  hideModal() {
    this.modalEmit.emit();
  }
  onContentClick(event: Event) {
    event.stopPropagation();
  }
}
