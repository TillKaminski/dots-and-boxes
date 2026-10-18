/* eslint-disable @typescript-eslint/no-explicit-any */
import {
  ComponentFixture,
  fakeAsync,
  TestBed,
  tick,
} from '@angular/core/testing';

import { GamePageComponent } from './game-page.component';
import { provideHttpClient } from '@angular/common/http';
import { GameService } from '../../../../core/services/game.service';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { signal, WritableSignal } from '@angular/core';
import { of, throwError } from 'rxjs';
import { GameState, MoveRequest } from '../../../../core/models/game-data';

describe('GamePageComponent', () => {
  let component: GamePageComponent;
  let fixture: ComponentFixture<GamePageComponent>;
  let mockGameService: any;

  const mockState = signal<GameState | null>(null);
  const mockIsFinished = signal(false);

  const gameId = 'initial-game';

  beforeEach(async () => {
    mockGameService = {
      state: signal({
        currentPlayer: 1,
        finished: false,
        size: 0,
        edges: { horizontal: [], vertical: [] },
        boxes: [],
        scores: { '1': 0, '2': 0 },
      }),
      localPlayerId: signal(1),
      boardSize: signal(0),
      isFinished: signal(false),
      botModel: signal('random'),
      isOffline: signal(false),
      createNewGame: jest.fn().mockReturnValue(of({ success: true })),
      restartGame: jest.fn().mockReturnValue(of({ success: true })),
      getBotMove: jest.fn().mockReturnValue(of({ success: true })),
      makeMove: jest.fn().mockReturnValue(of({ success: true })),
    };
    await TestBed.configureTestingModule({
      imports: [GamePageComponent],
      providers: [
        { provide: GameService, useValue: mockGameService },
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(GamePageComponent);
    component = fixture.componentInstance;
    // fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should create and initialize game on start', () => {
    fixture.detectChanges();
    expect(mockGameService.createNewGame).toHaveBeenCalledWith(
      gameId,
      expect.any(Object),
    );
  });

  it('should calculate isLocalPlayerTurn correctly', () => {
    fixture.detectChanges();
    expect(component.isLocalPlayerTurn()).toBe(true);

    (mockGameService.state as unknown as WritableSignal<GameState>).set({
      currentPlayer: 2,
      finished: false,
      size: 0,
      edges: { horizontal: [], vertical: [] },
      boxes: [],
      scores: { '1': 0, '2': 0 },
    });
    fixture.detectChanges();
    expect(component.isLocalPlayerTurn()).toBe(false);
  });

  it('should not trigger bot move if autoBot is disabled', fakeAsync(() => {
    fixture.detectChanges();
    component.autoBot.set(false);

    (mockGameService.state as unknown as WritableSignal<GameState>).set({
      currentPlayer: 2,
      finished: false,
      size: 0,
      edges: { horizontal: [], vertical: [] },
      boxes: [],
      scores: { '1': 0, '2': 0 },
    });
    fixture.detectChanges();

    tick(component.botSpeed());
    expect(mockGameService.getBotMove).not.toHaveBeenCalled();
  }));

  it('should open settings and close them on restart', () => {
    component.showSettings.set(true);

    component.restartGame();

    expect(mockGameService.restartGame).toHaveBeenCalled();
    expect(component.showSettings()).toBe(false);
  });

  it('should not allow random move if game is finished', () => {
    const handleMoveSpy = jest.spyOn(component, 'handleMove');
    mockIsFinished.set(true);
    mockState.set({
      finished: true,
      size: 0,
      edges: {
        horizontal: [],
        vertical: [],
      },
      boxes: [],
      scores: { '1': 0, '2': 0 },
      currentPlayer: 0,
    });

    component.makeRandomMove();

    expect(handleMoveSpy).not.toHaveBeenCalled();
  });

  it('should calculate winner correctly for Player 1', () => {
    mockGameService.isFinished.set(true);
    (mockGameService.state as WritableSignal<any>).set({
      scores: { '1': 10, '2': 5 },
    });
    expect(component.winner()).toBe('🥳 Player 1 wins. 🥳');
  });

  it('should calculate winner correctly for Player 2', () => {
    mockGameService.isFinished.set(true);
    (mockGameService.state as WritableSignal<any>).set({
      scores: { '1': 5, '2': 10 },
    });
    expect(component.winner()).toBe('🥳 Player 2 wins. 🥳');
  });

  it('should return Draw if scores are equal', () => {
    mockGameService.isFinished.set(true);
    (mockGameService.state as WritableSignal<any>).set({
      scores: { '1': 5, '2': 5 },
    });
    expect(component.winner()).toBe('Draw');
  });

  it('should handle error during game restart', () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
    mockGameService.restartGame.mockReturnValue(
      throwError(() => new Error('Mock restart error')),
    );

    component.restartGame();

    expect(component.errorMessage()).toBe('Could not restart game.');
    expect(component.isProcessing()).toBe(false);
    consoleSpy.mockRestore();
  });

  it('should restart if createNewGame fails', () => {
    const warnSpy = jest.spyOn(console, 'warn').mockImplementation();
    mockGameService.createNewGame.mockReturnValue(
      throwError(() => new Error('Mock createNewGame error')),
    );

    // trigger constructor call
    fixture = TestBed.createComponent(GamePageComponent);

    expect(mockGameService.restartGame).toHaveBeenCalled();
    warnSpy.mockRestore();
  });

  it('should set offline mode if createGame and restart fail', () => {
    mockGameService.createNewGame.mockReturnValue(
      throwError(() => new Error('Mock Fail')),
    );
    mockGameService.restartGame.mockReturnValue(
      throwError(() => new Error('Mock Fail')),
    );

    fixture = TestBed.createComponent(GamePageComponent);
    component = fixture.componentInstance;

    expect(mockGameService.isOffline()).toBe(true);
    expect(component.errorMessage()).toBe(
      'Connection Error. Show offline Preview-Mode.',
    );
  });

  it('should handle bot move error', fakeAsync(() => {
    component.isBotThinking.set(false);
    mockGameService.getBotMove.mockReturnValue(
      throwError(() => new Error('Bot error')),
    );

    component.triggerBotMove();
    tick(component.botSpeed());

    expect(component.isBotThinking()).toBe(false);
    expect(component.isProcessing()).toBe(false);
  }));

  it('should handle bot move', fakeAsync(() => {
    component.isBotThinking.set(false);

    const mockBotMove = {
      move: {
        x: 0,
        y: 0,
        orientation: 'horizontal',
      },
      state: {
        finished: true,
        size: 0,
        edges: {
          horizontal: [],
          vertical: [],
        },
        boxes: [],
        scores: { '1': 0, '2': 0 },
        currentPlayer: 0,
      },
    };

    mockGameService.getBotMove.mockReturnValue(of(mockBotMove));

    expect(component.isBotThinking()).toBe(false);
    expect(component.isProcessing()).toBe(false);

    component.triggerBotMove();

    expect(component.isBotThinking()).toBe(true);
    expect(component.isProcessing()).toBe(true);

    tick(component.botSpeed());

    expect(component.isBotThinking()).toBe(false);
    expect(component.isProcessing()).toBe(false);
  }));

  it('should set processing to false and log error if handleMove fails', () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
    mockGameService.makeMove.mockReturnValue(
      throwError(() => new Error('Move Error')),
    );

    component.handleMove({
      playerId: 1,
      x: 0,
      y: 0,
      orientation: 'horizontal',
    });

    expect(component.isProcessing()).toBe(false);
    expect(component.errorMessage()).toBe('Error Sending Move to Server.');
    consoleSpy.mockRestore();
  });

  it('should clear error message after timeout', fakeAsync(() => {
    component['showMessage']('Test Error', true);
    expect(component.errorMessage()).toBe('Test Error');
    tick(5000);
    expect(component.errorMessage()).toBeNull();
  }));

  it('should disable interaction when bot is thinking or processing', () => {
    fixture.detectChanges();

    component.isProcessing.set(true);
    expect(component.isInteractionDisabled()).toBe(true);

    component.isProcessing.set(false);
    component.isBotThinking.set(true);
    expect(component.isInteractionDisabled()).toBe(true);
  });

  it('should block actions if isProcessing is true', () => {
    const handleMoveSpy = jest.spyOn(component, 'handleMove');
    component.isProcessing.set(true);

    component.makeRandomMove();

    expect(handleMoveSpy).not.toHaveBeenCalled();
  });

  it('should not handle moves if gameState is null', () => {
    const handleMoveSpy = jest.spyOn(component, 'handleMove');
    (mockGameService.state as WritableSignal<any>).set(null);

    component.makeRandomMove();

    expect(handleMoveSpy).not.toHaveBeenCalled();
  });

  it('should pick one of the available moves when making a random move', () => {
    const handleMoveSpy = jest
      .spyOn(component, 'handleMove')
      .mockImplementation();

    // Setup game state
    // Available positions: x=0 y=1 horizontal, x=0 y=0 vertical
    (mockGameService.state as WritableSignal<any>).set({
      finished: false,
      edges: {
        horizontal: [[1, 0]],
        vertical: [[0, 1]],
      },
    });
    mockGameService.localPlayerId.set(1);

    component.makeRandomMove();

    expect(handleMoveSpy).toHaveBeenCalled();

    const moveSent = handleMoveSpy.mock.calls[0][0];
    const possibleMoves = [
      { playerId: 1, x: 0, y: 1, orientation: 'horizontal' },
      { playerId: 1, x: 0, y: 0, orientation: 'vertical' },
    ];

    expect(possibleMoves).toContainEqual(moveSent);
  });

  it('should not call handleMove if no moves are available', () => {
    const handleMoveSpy = jest.spyOn(component, 'handleMove');

    (mockGameService.state as WritableSignal<any>).set({
      finished: false,
      edges: {
        horizontal: [
          [1, 1],
          [1, 1],
        ],
        vertical: [
          [1, 1],
          [1, 1],
        ],
      },
    });

    component.makeRandomMove();

    expect(handleMoveSpy).not.toHaveBeenCalled();
  });

  it('should use the correct localPlayerId in the move request', () => {
    const handleMoveSpy = jest
      .spyOn(component, 'handleMove')
      .mockImplementation();
    const TEST_PLAYER_ID = 99;
    mockGameService.localPlayerId.set(TEST_PLAYER_ID);

    (mockGameService.state as WritableSignal<any>).set({
      finished: false,
      edges: {
        horizontal: [[0]],
        vertical: [[1]],
      },
    });

    component.makeRandomMove();

    expect(handleMoveSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        playerId: TEST_PLAYER_ID,
      }),
    );
  });

  it('should not call makeMove if isProcessing is true or errorMessage set', () => {
    const move: MoveRequest = {
      playerId: 1,
      x: 0,
      y: 0,
      orientation: 'horizontal',
    };

    component.isProcessing.set(true);
    component.handleMove(move);
    expect(mockGameService.makeMove).not.toHaveBeenCalled();

    component.isProcessing.set(false);
    mockGameService.makeMove.mockClear();

    // set error message
    component.errorMessage.set('Test Message.');
    component.handleMove(move);
    expect(mockGameService.makeMove).not.toHaveBeenCalled();
  });

  it('should set isProcessing to false on successful move', () => {
    const move: MoveRequest = {
      playerId: 1,
      x: 0,
      y: 0,
      orientation: 'horizontal',
    };
    const mockResponse = { success: true };
    mockGameService.makeMove.mockReturnValue(of(mockResponse));

    component.handleMove(move);

    expect(component.isProcessing()).toBe(false);
    expect(mockGameService.makeMove).toHaveBeenCalledWith(gameId, move);
  });

  it('should not trigger bot move if bot is thinking or game is processing', () => {
    component.isBotThinking.set(true);
    component.triggerBotMove();

    expect(mockGameService.getBotMove).not.toHaveBeenCalled();

    component.isBotThinking.set(false);
    component.isProcessing.set(true);
    component.triggerBotMove();

    expect(mockGameService.getBotMove).not.toHaveBeenCalled();
  });
});
