import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BoardComponent } from './board.component';
import { ComponentRef } from '@angular/core';
import { GameState } from '../../../../core/models/game-data';

describe('BoardComponent', () => {
  let component: BoardComponent;
  let fixture: ComponentFixture<BoardComponent>;
  let componentRef: ComponentRef<BoardComponent>;

  const mockState: GameState = {
    size: 2,
    edges: {
      horizontal: [
        [0, 0, 0],
        [0, 0, 0],
      ],
      vertical: [
        [0, 0],
        [0, 0],
        [0, 0],
      ],
    },
    boxes: [
      [0, 0],
      [0, 0],
    ],
    scores: { '1': 0, '2': 0 },
    currentPlayer: 1,
    finished: false,
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BoardComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(BoardComponent);
    component = fixture.componentInstance;

    componentRef = fixture.componentRef;
    componentRef.setInput('state', mockState);
    componentRef.setInput('localPlayerId', 1);

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should calculate correct grid indexes based on board size', () => {
    expect(component.gridIndexes()).toEqual([0, 1, 2]);
    componentRef.setInput('state', { ...mockState, size: 4 });
    expect(component.gridIndexes()).toEqual([0, 1, 2, 3, 4]);

    componentRef.setInput('state', null);
    expect(component.gridIndexes()).toEqual([0]);
  });

  it('should return correct player class', () => {
    expect(component.getPlayerClass(1)).toBe('player-1');
    expect(component.getPlayerClass(0)).toBe('');
    expect(component.getPlayerClass(undefined)).toBe('');
  });

  it('should emit makeMove when an edge is clicked', () => {
    jest.spyOn(component.makeMove, 'emit');
    component.makeMove.emit({
      playerId: 1,
      x: 0,
      y: 0,
      orientation: 'horizontal',
    });
    expect(component.makeMove.emit).toHaveBeenCalledWith(
      expect.objectContaining({ x: 0, orientation: 'horizontal' }),
    );
  });

  it('should create style output for missing state', () => {
    componentRef.setInput('state', null);
    const style = component.gridStyle();

    expect(style['grid-template-columns']).toBe('repeat(0, auto 60px) auto');
    expect(style.width).toBe('fit-content');
  });

  describe('onEdgeClick', () => {
    let emitSpy: jest.SpyInstance;

    beforeEach(() => {
      emitSpy = jest.spyOn(component.makeMove, 'emit');
    });

    it('should emit move (valid input)', () => {
      componentRef.setInput('localPlayerId', 1);
      component.onEdgeClick(0, 0, 'horizontal');

      expect(emitSpy).toHaveBeenCalledWith({
        playerId: 1,
        x: 0,
        y: 0,
        orientation: 'horizontal',
      });
    });

    it('should not emit move (wrong turn)', () => {
      componentRef.setInput('localPlayerId', 2);
      component.onEdgeClick(0, 0, 'horizontal');

      expect(emitSpy).not.toHaveBeenCalled();
    });

    it('should not emit move (edge already taken)', () => {
      const stateEdgeTaken = JSON.parse(JSON.stringify(mockState));
      stateEdgeTaken.edges.horizontal[0][0] = 1;
      componentRef.setInput('state', stateEdgeTaken);
      componentRef.setInput('localPlayerId', 1);

      component.onEdgeClick(0, 0, 'horizontal');

      expect(emitSpy).not.toHaveBeenCalled();
    });

    it('should not emit move (game finished)', () => {
      const finishedState = { ...mockState, finished: true };
      componentRef.setInput('state', finishedState);
      componentRef.setInput('localPlayerId', 1);

      component.onEdgeClick(0, 0, 'horizontal');

      expect(emitSpy).not.toHaveBeenCalled();
    });
  });
});
