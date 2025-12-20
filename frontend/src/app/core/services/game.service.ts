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

  checkStatus(): Observable<StatusInfo> {
    return this.http.get<StatusInfo>(`${API_BASE_URL}/`);
  }

  resetData() {
    this._gameState.set(null);
    this._lastBotMove.set(null);
  }

  create_new_game(
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

  restart_game(gameId: string): Observable<GameState> {
    return this.http
      .get<GameResponse>(
        `${API_BASE_URL}/${API_VERSION}/games/${gameId}/restart`,
      )
      .pipe(
        tap((response) => this._gameState.set(response.state)),
        map((response) => response.state),
      );
  }

  get_game_state(gameId: string): Observable<GameState> {
    return this.http
      .get<GameResponse>(`${API_BASE_URL}/${API_VERSION}/games/${gameId}/state`)
      .pipe(
        tap((response) => this._gameState.set(response.state)),
        map((response) => response.state),
      );
  }

  make_move(gameId: string, move: MoveRequest): Observable<GameState> {
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

  get_bot_move(gameId: string): Observable<BotGameState> {
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
