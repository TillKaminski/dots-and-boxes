import { Component, inject, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { GameService } from './core/services/game.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit {
  title = 'dots-and-boxes-frontend';
  backendStatus = 'Connecting...';

  private gameService = inject(GameService);

  constructor() {
    //
  }

  ngOnInit(): void { 
    this.gameService.checkStatus().subscribe({
      next: (data) => {
        this.backendStatus = `Backend running: ${data['api-version']} - ${data['root-message']}`;
        console.log('Backend Status:', data);
      },
      error: (err) => {
        this.backendStatus = `ERROR: Failed to connect to backend.`;
        console.error('Connection Error:', err);
      }
    });
  }
}
