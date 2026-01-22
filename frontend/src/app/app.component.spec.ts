import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AppComponent } from './app.component';
import { GameService } from './core/services/game.service';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { of, throwError } from 'rxjs';

describe('AppComponent', () => {
  let component: AppComponent;
  let fixture: ComponentFixture<AppComponent>;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let gameServiceMock: any;

  beforeEach(async () => {
    gameServiceMock = {
      checkStatus: jest.fn(),
      isOffline: {
        set: jest.fn(),
      },
    };

    await TestBed.configureTestingModule({
      imports: [AppComponent, HttpClientTestingModule],
      providers: [{ provide: GameService, useValue: gameServiceMock }],
    }).compileComponents();

    fixture = TestBed.createComponent(AppComponent);
    component = fixture.componentInstance;
  });

  it('should set status message if startup is successful and isOffline(false)', () => {
    const mockData = { 'api-version': 'v1', 'root-message': 'Test-Message' };
    gameServiceMock.checkStatus.mockReturnValue(of(mockData));

    fixture.detectChanges();

    expect(component.backendStatus).toBe('Backend running: v1 - Test-Message');
    expect(gameServiceMock.isOffline.set).toHaveBeenCalledWith(false);
  });

  it('should set error message if isOffline(true)', () => {
    gameServiceMock.checkStatus.mockReturnValue(
      throwError(() => new Error('Fail')),
    );

    fixture.detectChanges();

    expect(component.backendStatus).toBe(
      'ERROR: Failed to connect to backend.',
    );
    expect(gameServiceMock.isOffline.set).toHaveBeenCalledWith(true);
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.componentInstance;
    expect(app).toBeTruthy();
  });

  it(`should have the 'dots-and-boxes-frontend' title`, () => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.componentInstance;
    expect(app.title).toEqual('dots-and-boxes-frontend');
  });
});
