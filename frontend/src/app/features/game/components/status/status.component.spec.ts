import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StatusComponent } from './status.component';
import { GameState } from '../../../../core/models/game-data';

describe('StatusComponent', () => {
  let component: StatusComponent;
  let fixture: ComponentFixture<StatusComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StatusComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(StatusComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('Winner Calculation', () => {
    const mockState = (s1: number, s2: number): GameState => ({
      scores: { '1': s1, '2': s2 },
      currentPlayer: 1,
      finished: false,
      size: 0,
      edges: { horizontal: [], vertical: [] },
      boxes: [],
    });

    it('should return null if game is not finished', () => {
      fixture.componentRef.setInput('gameState', mockState(5, 2));
      fixture.componentRef.setInput('isFinished', false);
      expect(component.winner()).toBeNull();
    });

    it('should return "Player 1" when Player 1 has more points', () => {
      fixture.componentRef.setInput('gameState', mockState(10, 5));
      fixture.componentRef.setInput('isFinished', true);
      expect(component.winner()).toBe('Player 1');
    });

    it('should return "Player 2" when Player 2 has more points', () => {
      fixture.componentRef.setInput('gameState', mockState(3, 8));
      fixture.componentRef.setInput('isFinished', true);
      expect(component.winner()).toBe('Player 2');
    });

    it('should return "Draw" when scores are equal', () => {
      fixture.componentRef.setInput('gameState', mockState(5, 5));
      fixture.componentRef.setInput('isFinished', true);
      expect(component.winner()).toBe('Draw');
    });

    it('should return null if gameState is missing', () => {
      fixture.componentRef.setInput('gameState', null);
      fixture.componentRef.setInput('isFinished', true);
      expect(component.winner()).toBeNull();
    });
  });

  it('should allow autoBot to be toggled (model)', () => {
    component.autoBot.set(true);
    expect(component.autoBot()).toBe(true);

    component.autoBot.set(false);
    expect(component.autoBot()).toBe(false);
  });
});
