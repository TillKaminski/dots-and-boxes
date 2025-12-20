import { HttpClient } from '@angular/common/http';
import { computed, inject, Injectable, signal } from '@angular/core';
import { map, Observable, tap } from 'rxjs';
import {
  BotGameState,
  BotMoveOutput,
  GameResponse,
  GameState,
  MoveRequest,
  NewGameRequest,
  StatusInfo,
} from '../models/game-data';

const API_BASE_URL = 'http://localhost:8000';
const API_VERSION = 'v1';

@Injectable({
  providedIn: 'root',
})
export class GameService {
  private http = inject(HttpClient);

  private _gameState = signal<GameState | null>(null);
  private _lastBotMove = signal<BotMoveOutput | null>(null);

  readonly state = computed(() => this._gameState());
  readonly botMove = computed(() => this._lastBotMove());

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
        tap((response) => this._gameState.set(response.state)),
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
        }),
      );
  }
}
