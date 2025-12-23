import { HttpClient } from '@angular/common/http';
import {
  computed,
  inject,
  Injectable,
  signal,
  WritableSignal,
} from '@angular/core';
import { catchError, map, Observable, tap, throwError } from 'rxjs';
import {
  BotGameState,
  BotMoveOutput,
  DataRequestState,
  GameResponse,
  GameState,
  MoveRequest,
  NewGameRequest,
  StatusInfo,
} from '../models/game-data';
import { environment } from '../../../environments/environment';

const API_BASE_URL = `${environment.apiUrl}`;
const API_VERSION = `${environment.apiVersion}`;

@Injectable({
  providedIn: 'root',
})
/**
 * Service for communication with the backend API.
 * Manages game state, bot moves, and HTTP request status using Signals.
 */
export class GameService {
  private http = inject(HttpClient);

  private _gameState = signal<GameState | null>(null);
  private _lastBotMove = signal<BotMoveOutput | null>(null);
  private _dataState = signal<DataRequestState>({
    status: 'INITIAL',
    error: null,
  });
  private _localPlayerId = signal<number>(1); // Local Player always Id: 1
  private _finished = signal<boolean>(false);
  private _botModel = signal<string>('rule');

  readonly state = computed(() => this._gameState());
  readonly botMove = computed(() => this._lastBotMove());
  readonly dataStatus = computed(() => this._dataState());
  readonly localPlayerId = computed(() => this._localPlayerId());
  readonly isFinished = computed(() => this._gameState()?.finished ?? false);

  readonly botModel = computed(() => this._botModel());

  /**
   * Setter for Local Player Id.
   */
  setLocalPlayer(id: number) {
    this._localPlayerId.set(id);
  }

  /**
   * Checks the API connection and returns server status information.
   */
  checkStatus(): Observable<StatusInfo> {
    return this.http.get<StatusInfo>(`${API_BASE_URL}/`);
  }

  /**
   * Clears the current game state and bot move signals.
   */
  resetData() {
    this._gameState.set(null);
    this._lastBotMove.set(null);
    this._dataState.set({ status: 'INITIAL', error: null });
    this._finished.set(false);
  }

  /**
   * Helper Function to track the state of an HTTP Request.
   */
  trackState<T>(statusSignal: WritableSignal<DataRequestState>) {
    return (source: Observable<T>) => {
      statusSignal.set({ status: 'LOADING', error: null });

      return source.pipe(
        tap(() => {
          statusSignal.set({ status: 'COMPLETE', error: null });
        }),
        catchError((error) => {
          const errorMessage = error.error?.detail || 'Error unknown.';
          statusSignal.set({ status: 'ERROR', error: errorMessage });
          return throwError(() => error);
        }),
      );
    };
  }

  /**
   * Creates a new game instance on the server and updates the local state.
   * @param gameId Unique identifier for the game.
   * @param newGameData Configuration for the new game.
   */
  createNewGame(
    gameId: string,
    newGameData: NewGameRequest,
  ): Observable<GameState> {
    return this.http
      .post<GameResponse>(
        `${API_BASE_URL}/${API_VERSION}/games/new_game/${gameId}`,
        newGameData,
      )
      .pipe(
        this.trackState(this._dataState),
        tap((response) => this._gameState.set(response.state)),
        map((response) => response.state),
      );
  }

  /**
   * Resets the game with the given ID to its starting state.
   * @param gameId Unique identifier for the game.
   */
  restartGame(gameId: string): Observable<GameState> {
    return this.http
      .get<GameResponse>(
        `${API_BASE_URL}/${API_VERSION}/games/${gameId}/restart`,
      )
      .pipe(
        this.trackState(this._dataState),
        tap((response) => this._gameState.set(response.state)),
        map((response) => response.state),
      );
  }

  /**
   * Fetches the current state of a game from the server.
   * @param gameId Unique identifier for the game.
   */
  getGameState(gameId: string): Observable<GameState> {
    return this.http
      .get<GameResponse>(`${API_BASE_URL}/${API_VERSION}/games/${gameId}/state`)
      .pipe(
        this.trackState(this._dataState),
        tap((response) => this._gameState.set(response.state)),
        map((response) => response.state),
      );
  }

  /**
   * Sends a player's move to the server and updates the local state.
   * @param gameId Unique identifier for the game.
   * @param move The coordinates and orientation of the line.
   * @returns New game state for valid moves, error otherwise.
   */
  makeMove(gameId: string, move: MoveRequest): Observable<GameState> {
    return this.http
      .post<GameResponse>(
        `${API_BASE_URL}/${API_VERSION}/games/${gameId}/move`,
        move,
      )
      .pipe(
        this.trackState(this._dataState),
        tap((response) => {
          this._gameState.set(response.state);
          this._finished.set(response.state.finished);
        }),
        map((response) => response.state),
      );
  }

  /**
   * Requests a move from the AI bot and updates the local state and last bot move.
   * @param gameId Unique identifier for the game.
   * @throws Error if the server response does not contain move details.
   */
  getBotMove(gameId: string): Observable<BotGameState> {
    return this.http
      .get<GameResponse>(
        `${API_BASE_URL}/${API_VERSION}/games/${gameId}/bot_move`,
      )
      .pipe(
        this.trackState(this._dataState),
        // Transform data before Signal-update
        map((response) => {
          if (!response.move) {
            throw new Error("Response should contain 'move' details.");
          }
          return {
            state: response.state,
            move: response.move,
          } as BotGameState;
        }),
        tap((response) => {
          this._gameState.set(response.state);
          this._lastBotMove.set(response.move);
          this._finished.set(response.state.finished);
        }),
      );
  }
}
