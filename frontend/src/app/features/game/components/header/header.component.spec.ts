import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HeaderComponent } from './header.component';

describe('HeaderComponent', () => {
  let component: HeaderComponent;
  let fixture: ComponentFixture<HeaderComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HeaderComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(HeaderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should emit settingsRequest when openSettings is called', () => {
    const emitSpy = jest.spyOn(component.settingsRequest, 'emit');
    component.openSettings();
    expect(emitSpy).toHaveBeenCalled();
  });

  it('should emit helpRequest when openHelp is called', () => {
    const emitSpy = jest.spyOn(component.helpRequest, 'emit');
    component.openHelp();
    expect(emitSpy).toHaveBeenCalled();
  });
});
