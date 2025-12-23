import {
  Component,
  computed,
  effect,
  inject,
  signal,
  untracked,
} from '@angular/core';
import { GameState, MoveRequest } from '../../../../core/models/game-data';
import { BoardComponent } from '../../components/board/board.component';
import { GameService } from '../../../../core/services/game.service';
import { catchError } from 'rxjs';
import { FormsModule } from '@angular/forms';

/**
 * Main page component for the game.
 * Connects the BoardComponent with the GameService to handle moves.
 */
@Component({
  selector: 'app-game-page',
  standalone: true,
  imports: [BoardComponent, FormsModule],
  templateUrl: './game-page.component.html',
  styleUrl: './game-page.component.css',
})
export class GamePageComponent {
  private gameId = 'mock-game';
  private gameService = inject(GameService);

  gameState = this.gameService.state;

  autoBot = signal(true); // Checkbox state
  isBotThinking = signal(false);
  localPlayerId = this.gameService.localPlayerId;
  isFinished = this.gameService.isFinished;

  isLocalPlayerTurn = computed(() => {
    const state = this.gameState();
    return state?.currentPlayer === this.localPlayerId();
  });

  constructor() {
    this.gameService
      .createNewGame(this.gameId, {
        startingPlayer: 1,
        botModel: 'rule',
      })
      .pipe(
        catchError((error) => {
          console.warn('Error occurred, attempting restart...' + error);
          return this.gameService.restartGame(this.gameId);
        }),
      )
      .subscribe({
        next: (state) => console.log('Game initialized:', state),
        error: (err) => console.error('Could not initialize game:', err),
      });

    /**
     * Trigger bot moves automatically.
     */
    effect(() => {
      const state = this.gameState();
      const isAuto = this.autoBot();
      if (state && state.currentPlayer === 2 && !state.finished && isAuto) {
        untracked(() => {
          this.triggerBotMove();
        });
      }
    });
  }

  private triggerBotMove() {
    if (this.isBotThinking()) return;
    this.isBotThinking.set(true);

    // Delay Bot Move
    setTimeout(() => {
      this.gameService.getBotMove(this.gameId).subscribe({
        next: () => this.isBotThinking.set(false),
        error: () => this.isBotThinking.set(false),
      });
    }, 800);
  }

  /**
   * Receives move requests from the board.
   * The board will update automatically (service uses a signal).
   */
  handleMove(move: MoveRequest) {
    this.gameService.makeMove(this.gameId, move).subscribe({
      next: (newState) => {
        console.log('Move successful:', newState);
      },
      error: (err) => {
        console.error('Move failed:', err);
      },
    });
  }

  /** Mock state used for testing and CSS styling */
  _gameState = signal<GameState>({
    size: 4,
    edges: {
      horizontal: [
        [1, 2, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
      ],
      vertical: [
        [1, 0, 0, 2],
        [1, 2, 0, 2],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
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
}
