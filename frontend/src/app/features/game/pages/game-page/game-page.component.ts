import { Component, signal } from '@angular/core';
import { GameState, MoveRequest } from '../../../../core/models/game-data';
import { BoardComponent } from '../../components/board/board.component';

@Component({
  selector: 'app-game-page',
  standalone: true,
  imports: [BoardComponent],
  templateUrl: './game-page.component.html',
  styleUrl: './game-page.component.css',
})
export class GamePageComponent {
  /** Mock state used for testing and CSS styling */
  gameState = signal<GameState>({
    size: 4,
    edges: {
      horizontal: [
        [1, 2, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [1, 1, 1, 1],
      ],
      vertical: [
        [1, 0, 0, 0, 2],
        [1, 2, 0, 0, 2],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
      ],
    },
    boxes: [
      [1, 0, 0, 0],
      [0, 2, 0, 0],
      [0, 0, 0, 0],
      [0, 0, 0, 0],
    ],
    scores: { '1': 2, '2': 1 },
    currentPlayer: 1,
    finished: false,
  });

  /** Receives move requests from the board */
  handleMove(event: MoveRequest) {
    console.log('Move requested:', event);
  }
}
