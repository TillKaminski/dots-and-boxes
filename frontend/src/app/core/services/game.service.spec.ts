import { fakeAsync, TestBed, tick } from '@angular/core/testing';
import {
  HttpClientTestingModule,
  HttpTestingController,
} from '@angular/common/http/testing';

import { GameService } from './game.service';
import {
  BotGameState,
  BotMoveOutput,
  GameResponse,
  GameState,
  MoveRequest,
  NewGameRequest,
  StatusInfo,
} from '../models/game-data';
import { HttpErrorResponse } from '@angular/common/http';

describe('GameService', () => {
  let service: GameService;
  let httpTestingController: HttpTestingController;

  const API_BASE_URL = 'http://localhost:8000/';
  const API_VERSION = 'v1';

  const API_URL = API_BASE_URL + API_VERSION;

  const mockGameState: GameState = {
    size: 4,
    edges: { horizontal: [], vertical: [] },
    boxes: [],
    scores: { '1': 0, '2': 0 },
    currentPlayer: 1,
    finished: false,
  };

  const mockGameResponse: GameResponse = {
    meta: { gameId: 'test_game', version: 'v1' },
    state: mockGameState,
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [GameService],
    });
    service = TestBed.inject(GameService);
    httpTestingController = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpTestingController.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('Status and Initialization APIs', () => {
    it('should return StatusInfo object (GET /)', fakeAsync(() => {
      const mockStatus: StatusInfo = {
        'root-message': 'Fast-API Entrypoint.',
        'api-version': 'v1',
        status: 'running',
      };

      let receivedData: StatusInfo | undefined;

      service.checkStatus().subscribe((data) => {
        receivedData = data;
      });

      const req = httpTestingController.expectOne(API_BASE_URL);

      expect(req.request.method).toEqual('GET');
      req.flush(mockStatus);

      tick();

      expect(receivedData).toEqual(mockStatus);
      expect(receivedData!.status).toBe('running');
      expect(receivedData!['api-version']).toBe('v1');
    }));

    it('should send NewGameRequest and return GameState (Post /new_game)', fakeAsync(() => {
      const gameId = 'test_game';
      const newGameRequest: NewGameRequest = {
        startingPlayer: 1,
        botModel: 'bot_model',
      };

      let receivedData: GameState | undefined;

      service.createNewGame(gameId, newGameRequest).subscribe((data) => {
        receivedData = data;
      });
      const URL = API_URL + '/games/new_game/test_game';
      const req = httpTestingController.expectOne(URL);

      expect(req.request.method).toEqual('POST');
      req.flush(mockGameResponse);

      tick();

      expect(req.request.body).toEqual(newGameRequest);
      expect(receivedData).toEqual(mockGameState);
      expect(receivedData?.size).toBe(4);
    }));

    it('should update the signal state and dataStatus when a new game is created', fakeAsync(() => {
      const gameId = 'test_game';
      const newGameRequest: NewGameRequest = {
        startingPlayer: 1,
        botModel: 'random',
      };

      // Signal should be 'null'
      expect(service.state()).toBeNull();
      expect(service.dataStatus()).toEqual({ status: 'INITIAL', error: null });

      service.createNewGame(gameId, newGameRequest).subscribe();

      // Data status should be 'LOADING' before flush
      expect(service.dataStatus()).toEqual({ status: 'LOADING', error: null });

      const req = httpTestingController.expectOne(
        `http://localhost:8000/v1/games/new_game/${gameId}`,
      );
      req.flush(mockGameResponse);

      tick();

      expect(service.dataStatus()).toEqual({ status: 'COMPLETE', error: null });
      expect(service.state()).toEqual(mockGameState);
      expect(service.state()?.size).toBe(4);
    }));

    it('should fetch GameState on restart (GET /restart)', fakeAsync(() => {
      const gameId = 'test_game';

      let receivedData: GameState | undefined;

      service.restartGame(gameId).subscribe((data) => {
        receivedData = data;
      });

      const req = httpTestingController.expectOne(
        'http://localhost:8000/v1/games/test_game/restart',
      );
      expect(req.request.method).toEqual('GET');
      req.flush(mockGameResponse);

      // end Observable Subscription
      tick();

      expect(receivedData).toEqual(mockGameState);
    }));

    it('should fetch GameState (GET /state)', fakeAsync(() => {
      const gameId = 'test_game';

      let receivedData: GameState | undefined;

      service.getGameState(gameId).subscribe((data) => {
        receivedData = data;
      });

      const req = httpTestingController.expectOne(
        'http://localhost:8000/v1/games/test_game/state',
      );

      expect(req.request.method).toEqual('GET');
      req.flush(mockGameResponse);

      tick();

      expect(receivedData).toEqual(mockGameState);
    }));
  });

  describe('Game Interaction APIs', () => {
    it('should send MoveRequest and return new GameState (POST /move)', fakeAsync(() => {
      const gameId = 'test_game';
      const mockMove: MoveRequest = {
        playerId: 1,
        x: 0,
        y: 0,
        orientation: 'horizontal',
      };

      let receivedData: GameState | undefined;

      service.makeMove(gameId, mockMove).subscribe((data) => {
        receivedData = data;
      });

      const req = httpTestingController.expectOne(
        'http://localhost:8000/v1/games/test_game/move',
      );

      expect(req.request.method).toEqual('POST');
      expect(req.request.body).toEqual(mockMove);

      req.flush(mockGameResponse);

      tick();

      expect(receivedData).toEqual(mockGameState);
    }));

    it('should return GameState (GET /bot_move)', fakeAsync(() => {
      const gameId = 'test_game';
      const mockMove: BotMoveOutput = {
        x: 0,
        y: 0,
        orientation: 'horizontal',
      };
      const mockBotState: BotGameState = {
        state: mockGameState,
        move: mockMove,
      };

      let receivedData: BotGameState | undefined;

      expect(service.botMove()).toBeNull();

      service.getBotMove(gameId).subscribe((data) => {
        receivedData = data;
      });

      const req = httpTestingController.expectOne(
        'http://localhost:8000/v1/games/test_game/bot_move',
      );

      expect(req.request.method).toEqual('GET');
      req.flush(mockBotState);

      tick();

      expect(receivedData?.state).toEqual(mockGameState);
      expect(receivedData?.move).toEqual(mockMove);
      expect(receivedData?.move).toBeDefined();

      // Check signal
      expect(service.botMove()).toEqual(mockMove);

      // Test reset()
      service.resetData();
      expect(service.state()).toBeNull();
      expect(service.botMove()).toBeNull();
    }));
  });
  describe('Error Handling APIs', () => {
    it('should handle error for create_new_game', fakeAsync(() => {
      const gameId = 'test_game';
      const newGameRequest = { startingPlayer: 1, botModel: 'bot_model' };

      const mockErrorResponse = {
        status: 500,
        statusText: 'Internal Server Error',
      };
      const errorMessage = 'Simulated 500 Error';

      let receivedError: HttpErrorResponse | undefined;

      service.createNewGame(gameId, newGameRequest).subscribe({
        next: () => {
          fail('Should not be called.');
        },
        error: (error: HttpErrorResponse) => {
          receivedError = error;
        },
        complete: () => {
          fail('Should not be called.');
        },
      });

      const req = httpTestingController.expectOne(
        'http://localhost:8000/v1/games/new_game/test_game',
      );

      req.flush(errorMessage, mockErrorResponse);

      tick();

      // Data status signal should be set
      expect(service.dataStatus().status).toBe('ERROR');
      expect(service.dataStatus().error).toBeDefined();

      expect(receivedError).toBeDefined();
      expect(receivedError!.status).toEqual(mockErrorResponse.status);
      expect(receivedError!.statusText).toEqual(mockErrorResponse.statusText);
      expect(receivedError!.error).toEqual(errorMessage);
    }));
  });

  it('should throw an Error for get_bot_move without state in GameResponse', fakeAsync(() => {
    const gameId = 'test_game';

    const mockErrorResponse: GameResponse = {
      meta: { gameId: gameId, version: 'v1' },
      state: mockGameState,
    };

    let receivedError: Error | undefined;

    service.getBotMove(gameId).subscribe({
      next: () => {
        fail('Should not be called.');
      },
      error: (error: Error) => {
        receivedError = error;
      },
      complete: () => {
        fail('Should not be called.');
      },
    });

    const req = httpTestingController.expectOne(
      'http://localhost:8000/v1/games/test_game/bot_move',
    );

    expect(req.request.method).toEqual('GET');
    req.flush(mockErrorResponse);

    tick();

    expect(receivedError).toBeDefined();
    expect(receivedError instanceof Error).toBe(true);
  }));
});
