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
import { of } from 'rxjs';
import { GameState } from '../../../../core/models/game-data';

describe('GamePageComponent', () => {
  let component: GamePageComponent;
  let fixture: ComponentFixture<GamePageComponent>;
  let mockGameService: GameService;

  const mockState = signal<GameState | null>(null);
  const mockIsFinished = signal(false);

  beforeEach(async () => {
    const mockValue = {
      state: signal({
        currentPlayer: 1,
        finished: false,
        size: 0,
        edges: { horizontal: [], vertical: [] },
        boxes: [],
        scores: { '1': 0, '2': 0 },
      }),
      localPlayerId: signal(1),
      isFinished: signal(false),
      botModel: signal('random'),
      isOffline: signal(false),
      createNewGame: jest.fn().mockReturnValue(of({ success: true })),
      restartGame: jest.fn().mockReturnValue(of({ success: true })),
      getBotMove: jest.fn().mockReturnValue(of({ success: true })),
      makeMove: jest.fn().mockReturnValue(of({ success: true })),
    };
    mockGameService = mockValue as unknown as GameService;
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
      'initial-game',
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

    tick(800);
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
});
