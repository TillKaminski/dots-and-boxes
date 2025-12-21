import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: 'game',
    loadComponent: () =>
      import('./features/game/pages/game-page/game-page.component').then(
        (m) => m.GamePageComponent,
      ),
  },
  { path: '', redirectTo: 'game', pathMatch: 'full' },
];
