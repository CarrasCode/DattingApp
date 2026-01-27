import { Component, input } from '@angular/core';

@Component({
  selector: 'app-header',
  imports: [],
  templateUrl: './header.html',
  styleUrl: './header.scss',
})
export class Header {
  // protected readonly appName = signal('LoveConnect');
  appName = input.required<string>();
  matchesCount = input.required<number>();

  changeTitle() {
    //   this.appName.update((prev) => {
    //     if (prev == 'LoveConnect') return '💘 Match Found';
    //     return '💘' + prev;
    //   });
  }
}
