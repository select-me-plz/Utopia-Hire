import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

export interface AuthUser {
  id: string;
  fullName: string;
  email: string;
  role?: string;
}

export interface LoginResponse {
  token: string;
  user: AuthUser;
}

export interface RegisterResponse {
  message: string;
  token: string;
  user: AuthUser;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly API_BASE_URL = 'http://localhost:3000';

  constructor(private readonly http: HttpClient) {}

  login(email: string, password: string): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(`${this.API_BASE_URL}/api/auth/login`, { email, password })
      .pipe(tap((res) => this.persistAuth(res.token, res.user)));
  }

  register(fullName: string, email: string, password: string, role?: string): Observable<RegisterResponse> {
    return this.http
      .post<RegisterResponse>(`${this.API_BASE_URL}/api/auth/register`, { fullName, email, password, role })
      .pipe(tap((res) => this.persistAuth(res.token, res.user)));
  }

  logout(): void {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
  }

  getToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  getUser(): AuthUser | null {
    const raw = localStorage.getItem('auth_user');
    return raw ? (JSON.parse(raw) as AuthUser) : null;
  }

  isAuthenticated(): boolean {
    const token = this.getToken();
    if (!token) {
      return false;
    }

    // Check if token is expired
    if (this.isTokenExpired(token)) {
      // Clear expired token
      this.logout();
      return false;
    }

    return true;
  }

  private isTokenExpired(token: string): boolean {
    try {
      const payload = this.decodeToken(token);
      if (!payload || !payload.exp) {
        return true; // If no expiration, consider it expired
      }

      // exp is in seconds, Date.now() is in milliseconds
      const expirationTime = payload.exp * 1000;
      const currentTime = Date.now();

      return currentTime >= expirationTime;
    } catch (error) {
      console.error('Error decoding token:', error);
      return true; // If can't decode, consider expired
    }
  }

  private decodeToken(token: string): any {
    try {
      // JWT format: header.payload.signature
      const parts = token.split('.');
      if (parts.length !== 3) {
        throw new Error('Invalid token format');
      }

      // Decode base64url encoded payload
      const payload = parts[1];
      // Convert base64url to base64
      const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
      // Add padding if needed
      const padded = base64 + '='.repeat((4 - (base64.length % 4)) % 4);
      // Decode base64
      const decoded = atob(padded);
      // Parse JSON
      return JSON.parse(decoded);
    } catch (error) {
      throw new Error('Failed to decode token');
    }
  }

  private persistAuth(token: string, user: AuthUser): void {
    localStorage.setItem('auth_token', token);
    localStorage.setItem('auth_user', JSON.stringify(user));
  }
}


