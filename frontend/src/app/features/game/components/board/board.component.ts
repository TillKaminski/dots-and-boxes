import { CommonModule } from '@angular/common';
import { Component, computed, input, output } from '@angular/core';
import { GameState, MoveRequest } from '../../../../core/models/game-data';

/**
 * Visualizes the Dots and Boxes game board using CSS Grid.
 * * Note: While the game uses (x, y) coordinates for moves, the internal
 * GameState arrays are indexed as [y][x] to ensure that elements are
 * rendered row-by-row correctly. (x=2, y=0) -> array[0][x]
 */
@Component({
  selector: 'app-board',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './board.component.html',
  styleUrl: './board.component.css',
})
export class BoardComponent {
  /** Required input: The current state of the game from the backend */
  state = input.required<GameState | null>();
  /** Output: Sends a move request when a user clicks an edge */
  makeMove = output<MoveRequest>();

  /** Generates an array of indexes based on board size (size + 1 for dots) */
  gridIndexes = computed(() => {
    const boxCount = this.state()?.size ?? 0;
    return Array.from({ length: boxCount + 1 }, (_, i) => i);
  });

  /** CSS Grid template for columns and rows */
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

  /** Returns the CSS class name for a player ('player-1' or 'player-2') */
  getPlayerClass(playerId: number | undefined): string {
    if (!playerId || playerId === 0) return '';
    return `player-${playerId}`;
  }

  /**
   * Handles edge clicks. Checks if edge is already taken.
   */
  onEdgeClick(
    x: number,
    y: number,
    orientation: 'horizontal' | 'vertical',
  ): void {
    const currentState = this.state();
    if (!currentState) return;

    const isTaken =
      orientation === 'horizontal'
        ? currentState.edges.horizontal[y][x] !== 0
        : currentState.edges.vertical[y][x] !== 0;

    if (!isTaken) {
      this.makeMove.emit({
        playerId: currentState.currentPlayer,
        x,
        y,
        orientation,
      });
    }
  }
}
