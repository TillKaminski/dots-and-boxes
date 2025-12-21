export type Orientation = 'horizontal' | 'vertical';

export interface MetaModel {
  gameId: string;
  version: string;
}

export interface StatusInfo {
  'root-message': string;
  'api-version': string;
  status: string;
}

export type PlayerScore = Record<string, number>;

export interface EdgesState {
  horizontal: number[][];
  vertical: number[][];
}

export interface GameState {
  size: number;
  edges: EdgesState;
  boxes: number[][];
  scores: PlayerScore;
  currentPlayer: number;
  finished: boolean;
}

export interface MoveRequest {
  playerId: number;
  x: number;
  y: number;
  orientation: Orientation;
}

export interface BotMoveOutput {
  x: number;
  y: number;
  orientation: Orientation;
}

export interface BotGameState {
  move: BotMoveOutput;
  state: GameState;
}

export interface NewGameRequest {
  startingPlayer: number;
  botModel: string;
}

export interface GameResponse {
  meta: MetaModel;
  state: GameState;
  move?: BotMoveOutput;
}

export type RequestStatus = 'INITIAL' | 'LOADING' | 'COMPLETE' | 'ERROR';

export interface DataRequestState {
  status: RequestStatus;
  error: string | null;
}
