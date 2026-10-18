import {
  Component,
  computed,
  effect,
  inject,
  signal,
  untracked,
} from '@angular/core';
import { MoveRequest } from '../../../../core/models/game-data';
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

  isProcessing = signal(false);
  isOffline = this.gameService.isOffline;

  isInteractionDisabled = computed(
    () =>
      this.isOffline() ||
      this.isProcessing() ||
      this.isBotThinking() ||
      this.isFinished(),
  );

  gameState = this.gameService.state;

  startingPlayer = signal<number>(1);
  newBoardSize = signal<number>(4);

  botSpeed = signal<number>(1000);

  autoBot = signal(true); // Checkbox state
  isBotThinking = signal(false);
  localPlayerId = this.gameService.localPlayerId;
  isFinished = this.gameService.isFinished;
  boardSize = this.gameService.boardSize;

  boardSizes = signal<number[]>([3, 4, 5]);

  botTurn = computed(() => {
    return this.gameState()?.currentPlayer != this.localPlayerId();
  });

  errorMessage = signal<string | null>(null);
  gameMessage = signal<string | null>(null);

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
    if (this.isProcessing()) return;
    this.isProcessing.set(true);

    this.gameService
      .restartGame(this.gameId, {
        startingPlayer: this.startingPlayer(),
        boardSize: this.newBoardSize(),
      })
      .subscribe({
        next: (state) => {
          console.log('Game restarted:', state);
          this.errorMessage.set(null);
          this.showMessage(
            'Game restarted. Player ' + this.startingPlayer() + ' begins.',
            false,
          );
          this.isProcessing.set(false);
        },
        error: (err) => {
          console.error('Could not restart game:', err);
          this.showMessage('Could not restart game.');
          this.isProcessing.set(false);
        },
      });
    this.showSettings.set(false);
  }

  makeRandomMove() {
    if (this.isProcessing()) return;

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

  private showMessage(msg: string, isError = true) {
    if (isError) {
      this.errorMessage.set(msg);
      setTimeout(() => this.errorMessage.set(null), 5000);
    } else {
      this.gameMessage.set(msg);
      setTimeout(() => this.gameMessage.set(null), 3000);
    }
  }

  isLocalPlayerTurn = computed(() => {
    const state = this.gameState();
    return state?.currentPlayer === this.localPlayerId();
  });

  constructor() {
    this.isProcessing.set(true);
    this.gameService
      .createNewGame(this.gameId, {
        startingPlayer: this.startingPlayer(),
        boardSize: this.newBoardSize(),
        botModel: this.gameService.botModel(),
      })
      .pipe(
        catchError((error) => {
          console.warn('Error occurred, attempting restart...' + error);
          this.showMessage('Try to restart current Game.', false);
          return this.gameService.restartGame(this.gameId, {
            startingPlayer: this.startingPlayer(),
            boardSize: this.newBoardSize(),
          });
        }),
      )
      .subscribe({
        next: (state) => {
          console.log('Game initialized:', state);
          this.isProcessing.set(false);
          this.showMessage(
            'Game started. Player ' +
              this.startingPlayer() +
              ' begins. Have fun!',
            false,
          );
        },
        error: (err) => {
          console.error('Could not initialize game:', err);
          this.isProcessing.set(false);
          this.showMessage('Connection Error. Show offline Preview-Mode.');
          this.gameService.isOffline.set(true);
        },
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

  triggerBotMove() {
    if (this.isBotThinking() || this.isProcessing()) return;

    this.isBotThinking.set(true);
    this.isProcessing.set(true);

    // Delay Bot Move
    setTimeout(() => {
      this.gameService.getBotMove(this.gameId).subscribe({
        next: () => {
          this.isBotThinking.set(false);
          this.isProcessing.set(false);
        },
        error: () => {
          this.isBotThinking.set(false);
          this.isProcessing.set(false);
        },
      });
    }, this.botSpeed());
  }

  /**
   * Receives move requests from the board.
   * The board will update automatically (service uses a signal).
   */
  handleMove(move: MoveRequest) {
    if (this.isProcessing() || this.errorMessage()) return;

    this.isProcessing.set(true);
    this.gameService.makeMove(this.gameId, move).subscribe({
      next: (newState) => {
        console.log('Move successful:', newState);
        this.isProcessing.set(false);
      },
      error: (err) => {
        console.error('Move failed:', err);
        this.showMessage('Error Sending Move to Server.');
        this.isProcessing.set(false);
      },
    });
  }
}
