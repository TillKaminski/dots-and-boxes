import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';

import { GameService } from './game.service';
import { StatusInfo } from '../models/game-data';

describe('GameService', () => {
  let service: GameService;
  let httpTestingController: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule], 
      providers: [GameService]
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

  it('should return StatusInfo object from the root API', (done) => {
    const mockStatus: StatusInfo = {
      'root-message': 'Fast-API Entrypoint.',
      'api-version': 'v1',
      status: 'running',
    };
    
    service.checkStatus().subscribe(data => {
      expect(data).toEqual(mockStatus);
      expect(data.status).toBe('running');
      expect(data['api-version']).toBe('v1');
      done();
    });
    
    const req = httpTestingController.expectOne('http://localhost:8000/');
    
    expect(req.request.method).toEqual('GET'); 
      req.flush(mockStatus); 
  });
});
