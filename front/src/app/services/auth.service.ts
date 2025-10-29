import { Injectable, PLATFORM_ID, Inject } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';

export interface User {
  id?: string;
  username: string;
  email: string;
}

export interface LoginResponse {
  token?: string;
  access_token?: string;
  user: User;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl: string;
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();
  private isBrowser: boolean;

  constructor(
    private http: HttpClient,
    @Inject(PLATFORM_ID) platformId: Object
  ) {
    this.isBrowser = isPlatformBrowser(platformId);
    
    // Utiliser l'API Fly.io en production
    // Pour développement local avec API locale, changer vers 'http://localhost:8000/api/v1/auth'
    this.apiUrl = 'https://geneweb-api.fly.dev/api/v1/auth';
    
    // Charger l'utilisateur depuis le localStorage au démarrage (uniquement côté navigateur)
    if (this.isBrowser) {
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        try {
          this.currentUserSubject.next(JSON.parse(storedUser));
        } catch (e) {
          console.error('Error parsing stored user:', e);
        }
      }
    }
  }

  login(username: string, password: string): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.apiUrl}/login`, { username, password })
      .pipe(
        tap(response => {
          if (this.isBrowser) {
            const token = response.token || response.access_token;
            if (token) {
              localStorage.setItem('auth_token', token);
            }
            localStorage.setItem('user', JSON.stringify(response.user));
          }
          this.currentUserSubject.next(response.user);
        })
      );
  }

  register(username: string, email: string, password: string, fullName: string = ''): Observable<any> {
    return this.http.post(`${this.apiUrl}/register`, { 
      username, 
      email, 
      password,
      full_name: fullName || username 
    });
  }

  logout(): void {
    if (this.isBrowser) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
    }
    this.currentUserSubject.next(null);
  }

  isAuthenticated(): boolean {
    if (!this.isBrowser) {
      return false;
    }
    return !!localStorage.getItem('auth_token');
  }

  getToken(): string | null {
    if (!this.isBrowser) {
      return null;
    }
    return localStorage.getItem('auth_token');
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }
}
