import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { authGuard } from './auth.guard';
import { AuthService } from '../services/auth.service';
import { runInInjectionContext, inject } from '@angular/core';

describe('authGuard', () => {
  let authService: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;

  beforeEach(() => {
    const authServiceSpy = jasmine.createSpyObj('AuthService', ['isAuthenticated']);
    const routerSpy = jasmine.createSpyObj('Router', ['navigate']);

    TestBed.configureTestingModule({
      providers: [
        { provide: AuthService, useValue: authServiceSpy },
        { provide: Router, useValue: routerSpy }
      ]
    });

    authService = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    router = TestBed.inject(Router) as jasmine.SpyObj<Router>;
  });

  it('should allow access when user is authenticated', () => {
    authService.isAuthenticated.and.returnValue(true);

    const injector = TestBed.inject;
    let result: boolean = false;

    TestBed.runInInjectionContext(() => {
      result = authGuard();
    });

    expect(result).toBe(true);
  });

  it('should deny access when user is not authenticated', () => {
    authService.isAuthenticated.and.returnValue(false);

    let result: boolean = true;

    TestBed.runInInjectionContext(() => {
      result = authGuard();
    });

    expect(result).toBe(false);
  });

  it('should navigate to login page when user is not authenticated', () => {
    authService.isAuthenticated.and.returnValue(false);

    TestBed.runInInjectionContext(() => {
      authGuard();
    });

    expect(router.navigate).toHaveBeenCalledWith(['/']);
  });

  it('should not navigate when user is authenticated', () => {
    authService.isAuthenticated.and.returnValue(true);

    TestBed.runInInjectionContext(() => {
      authGuard();
    });

    expect(router.navigate).not.toHaveBeenCalled();
  });

  it('should return true to allow route activation for authenticated users', () => {
    authService.isAuthenticated.and.returnValue(true);

    let canActivate: boolean = false;

    TestBed.runInInjectionContext(() => {
      canActivate = authGuard();
    });

    expect(canActivate).toBe(true);
  });

  it('should return false to prevent route activation for unauthenticated users', () => {
    authService.isAuthenticated.and.returnValue(false);

    let canActivate: boolean = true;

    TestBed.runInInjectionContext(() => {
      canActivate = authGuard();
    });

    expect(canActivate).toBe(false);
  });
});
