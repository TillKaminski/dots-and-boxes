import { Component, output } from '@angular/core';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [],
  templateUrl: './header.component.html',
  styleUrl: './header.component.css',
})
export class HeaderComponent {
  settingsRequest = output<void>();
  helpRequest = output<void>();

  openSettings() {
    this.settingsRequest.emit();
  }

  openHelp() {
    this.helpRequest.emit();
  }
}
