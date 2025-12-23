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
import { StatusComponent } from '../../components/status/status.component';
import { HeaderComponent } from '../../components/header/header.component';
import { FormsModule } from '@angular/forms';

/**
 * Main page component for the game.
 * Connects the BoardComponent with the GameService to handle moves.
 */
@Component({
  selector: 'app-game-page',
  standalone: true,
  imports: [BoardComponent, StatusComponent, HeaderComponent, FormsModule],
  templateUrl: './game-page.component.html',
  styleUrl: './game-page.component.css',
})
export class GamePageComponent {
  private gameId = 'initial-game';
  private gameService = inject(GameService);

  gameState = this.gameService.state;

  botSpeed = signal<number>(1000);

  autoBot = signal(true); // Checkbox state
  isBotThinking = signal(false);
  localPlayerId = this.gameService.localPlayerId;
  isFinished = this.gameService.isFinished;

  errorMessage = signal<string | null>(null);

  winner = computed(() => {
    const scores = this.gameState()?.scores;
    if (!this.isFinished() || !scores) return null;

    if (scores['1'] > scores['2']) return '🥳 Player 1 wins. 🥳';
    if (scores['2'] > scores['1']) return '🥳 Player 2 wins. 🥳';
    return 'Draw';
  });

  showSettings = signal(false);
  showHelp = signal(false);

  restartGame() {
    this.gameService.restartGame(this.gameId).subscribe({
      next: (state) => {
        console.log('Game restarted:', state);
        this.errorMessage.set(null);
      },
      error: (err) => {
        console.error('Could not restart game:', err);
        this.showError(err);
      },
    });
    this.showSettings.set(false);
  }

  makeRandomMove() {
    const state = this.gameState();
    if (!state || state.finished) return;

    const availableMoves: MoveRequest[] = [];
    const localPlayerId = this.localPlayerId();

    state.edges.horizontal.forEach((row, x) => {
      row.forEach((value, y) => {
        if (value === 0)
          availableMoves.push({
            playerId: localPlayerId,
            x: x,
            y: y,
            orientation: 'horizontal',
          });
      });
    });

    state.edges.vertical.forEach((row, x) => {
      row.forEach((value, y) => {
        if (value === 0)
          availableMoves.push({
            playerId: localPlayerId,
            x: x,
            y: y,
            orientation: 'vertical',
          });
      });
    });

    if (availableMoves.length > 0) {
      const randomIndex = Math.floor(Math.random() * availableMoves.length);
      const randomMove = availableMoves[randomIndex];

      this.handleMove(randomMove);
    }
  }

  private showError(msg: string) {
    this.errorMessage.set(msg);
    setTimeout(() => this.errorMessage.set(null), 5000);
  }

  isLocalPlayerTurn = computed(() => {
    const state = this.gameState();
    return state?.currentPlayer === this.localPlayerId();
  });

  constructor() {
    this.gameService
      .createNewGame(this.gameId, {
        startingPlayer: 1,
        botModel: this.gameService.botModel(),
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
    }, this.botSpeed());
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
