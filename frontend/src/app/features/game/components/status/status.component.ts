import { Component, computed, input, model } from '@angular/core';
import { GameState } from '../../../../core/models/game-data';

@Component({
  selector: 'app-status',
  standalone: true,
  imports: [],
  templateUrl: './status.component.html',
  styleUrl: './status.component.css',
})
export class StatusComponent {
  gameState = input<GameState | null>(null);
  isFinished = input<boolean>(false);
  isBotThinking = input<boolean>(false);
  autoBot = model<boolean>(false);
  winner = computed(() => {
    const scores = this.gameState()?.scores;
    if (!this.isFinished() || !scores) return null;

    if (scores['1'] > scores['2']) return 'Player 1';
    if (scores['2'] > scores['1']) return 'Player 2';
    return 'Draw';
  });

  isCurrentPlayer(playerId: number): string {
    return this.gameState()?.currentPlayer === playerId ? 'active' : '';
  }
}
