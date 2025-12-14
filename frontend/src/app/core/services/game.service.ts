import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { StatusInfo } from '../models/game-data';

const API_BASE_URL = 'http://localhost:8000'

@Injectable({
  providedIn: 'root'
})
export class GameService {

  private http = inject(HttpClient)

  checkStatus(): Observable<StatusInfo> {
    return this.http.get<StatusInfo>(`${API_BASE_URL}/`)
  }


}
