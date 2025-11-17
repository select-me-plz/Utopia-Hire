import { Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class LoadingService {
  private readonly loadingSignal = signal(false);

  readonly isLoading = this.loadingSignal.asReadonly();

  show() {
    this.loadingSignal.set(true);
  }

  hide() {
    this.loadingSignal.set(false);
  }
}

