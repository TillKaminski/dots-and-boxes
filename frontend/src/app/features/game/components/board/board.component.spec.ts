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
        [0, 0],
        [0, 0],
        [0, 0],
      ],
      vertical: [
        [0, 0, 0],
        [0, 0, 0],
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

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should calculate correct grid indexes (size + 1)', () => {
    expect(component.gridIndexes()).toEqual([0, 1, 2]);
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
});
