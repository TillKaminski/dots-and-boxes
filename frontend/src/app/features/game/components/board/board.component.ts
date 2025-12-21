import { CommonModule } from '@angular/common';
import { Component, computed, input, output } from '@angular/core';
import { GameState, MoveRequest } from '../../../../core/models/game-data';

@Component({
  selector: 'app-board',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './board.component.html',
  styleUrl: './board.component.css',
})
export class BoardComponent {
  state = input.required<GameState | null>();
  makeMove = output<MoveRequest>();

  gridIndexes = computed(() => {
    const boxCount = this.state()?.size ?? 0;
    return Array.from({ length: boxCount + 1 }, (_, i) => i);
  });

  // Define CSS Grid
  gridStyle = computed(() => {
    const boxCount = this.state()?.size ?? 0;
    const template = `repeat(${boxCount}, auto 60px) auto`;

    return {
      display: 'grid',
      'grid-template-columns': template,
      'grid-template-rows': template,
      'justify-content': 'start',
      gap: '0',
      width: 'fit-content',
    };
  });

  getPlayerClass(playerId: number | undefined): string {
    if (!playerId || playerId === 0) return '';
    return `player-${playerId}`;
  }
}
