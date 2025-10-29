import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { PLATFORM_ID } from '@angular/core';
import { AuthService, User, LoginResponse } from './auth.service';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;
  let localStorageSpy: jasmine.Spy;
  const apiUrl = 'https://geneweb-api.fly.dev/api/v1/auth';

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        AuthService,
        { provide: PLATFORM_ID, useValue: 'browser' }
      ]
    });

    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);

    // Spy on localStorage
    spyOn(localStorage, 'getItem').and.callThrough();
    spyOn(localStorage, 'setItem').and.callThrough();
    spyOn(localStorage, 'removeItem').and.callThrough();

    // Clear localStorage before each test
    localStorage.clear();
  });

  afterEach(() => {
    httpMock.verify();
    localStorage.clear();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('login', () => {
    it('should send POST request to login endpoint', () => {
      const mockResponse: LoginResponse = {
        token: 'test-token',
        user: {
          id: '1',
          username: 'testuser',
          email: 'test@example.com'
        }
      };

      service.login('testuser', 'password123').subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(`${apiUrl}/login`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual({
        username: 'testuser',
        password: 'password123'
      });
      req.flush(mockResponse);
    });

    it('should save token to localStorage on successful login', (done) => {
      const mockResponse: LoginResponse = {
        token: 'test-token',
        user: {
          id: '1',
          username: 'testuser',
          email: 'test@example.com'
        }
      };

      service.login('testuser', 'password123').subscribe(response => {
        expect(localStorage.setItem).toHaveBeenCalledWith('auth_token', 'test-token');
        done();
      });

      const req = httpMock.expectOne(`${apiUrl}/login`);
      req.flush(mockResponse);
    });

    it('should save user to localStorage on successful login', (done) => {
      const mockUser: User = {
        id: '1',
        username: 'testuser',
        email: 'test@example.com'
      };
      const mockResponse: LoginResponse = {
        token: 'test-token',
        user: mockUser
      };

      service.login('testuser', 'password123').subscribe(response => {
        expect(localStorage.setItem).toHaveBeenCalledWith('user', JSON.stringify(mockUser));
        done();
      });

      const req = httpMock.expectOne(`${apiUrl}/login`);
      req.flush(mockResponse);
    });

    it('should update currentUserSubject on successful login', (done) => {
      const mockUser: User = {
        id: '1',
        username: 'testuser',
        email: 'test@example.com'
      };
      const mockResponse: LoginResponse = {
        token: 'test-token',
        user: mockUser
      };

      service.currentUser$.subscribe(user => {
        if (user !== null) {
          expect(user).toEqual(mockUser);
          done();
        }
      });

      service.login('testuser', 'password123').subscribe();

      const req = httpMock.expectOne(`${apiUrl}/login`);
      req.flush(mockResponse);
    });

    it('should handle access_token in response', (done) => {
      const mockResponse: LoginResponse = {
        access_token: 'access-token',
        user: {
          id: '1',
          username: 'testuser',
          email: 'test@example.com'
        }
      };

      service.login('testuser', 'password123').subscribe(response => {
        expect(localStorage.setItem).toHaveBeenCalledWith('auth_token', 'access-token');
        done();
      });

      const req = httpMock.expectOne(`${apiUrl}/login`);
      req.flush(mockResponse);
    });
  });

  describe('register', () => {
    it('should send POST request to register endpoint', () => {
      const mockResponse = { message: 'Registration successful' };

      service.register('newuser', 'new@example.com', 'password123').subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(`${apiUrl}/register`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual({
        username: 'newuser',
        email: 'new@example.com',
        password: 'password123',
        full_name: 'newuser'
      });
      req.flush(mockResponse);
    });

    it('should include fullName in register request', () => {
      const mockResponse = { message: 'Registration successful' };

      service.register('newuser', 'new@example.com', 'password123', 'John Doe').subscribe();

      const req = httpMock.expectOne(`${apiUrl}/register`);
      expect(req.request.body).toEqual({
        username: 'newuser',
        email: 'new@example.com',
        password: 'password123',
        full_name: 'John Doe'
      });
      req.flush(mockResponse);
    });
  });

  describe('logout', () => {
    it('should remove tokens from localStorage', () => {
      localStorage.setItem('auth_token', 'test-token');
      localStorage.setItem('user', JSON.stringify({ username: 'test' }));

      service.logout();

      expect(localStorage.removeItem).toHaveBeenCalledWith('auth_token');
      expect(localStorage.removeItem).toHaveBeenCalledWith('user');
    });

    it('should reset currentUserSubject to null', (done) => {
      localStorage.setItem('user', JSON.stringify({ username: 'test' }));

      // Reinitialize service to pick up the stored user
      TestBed.resetTestingModule();
      TestBed.configureTestingModule({
        imports: [HttpClientTestingModule],
        providers: [
          AuthService,
          { provide: PLATFORM_ID, useValue: 'browser' }
        ]
      });

      service = TestBed.inject(AuthService);

      service.currentUser$.subscribe(user => {
        if (user === null) {
          expect(user).toBeNull();
          done();
        }
      });

      service.logout();
    });
  });

  describe('isAuthenticated', () => {
    it('should return true when auth_token is in localStorage', () => {
      localStorage.setItem('auth_token', 'test-token');
      expect(service.isAuthenticated()).toBe(true);
    });

    it('should return false when auth_token is not in localStorage', () => {
      expect(service.isAuthenticated()).toBe(false);
    });

    it('should return false when auth_token is empty', () => {
      localStorage.setItem('auth_token', '');
      expect(service.isAuthenticated()).toBe(false);
    });
  });

  describe('getToken', () => {
    it('should return token from localStorage', () => {
      localStorage.setItem('auth_token', 'test-token');
      expect(service.getToken()).toBe('test-token');
    });

    it('should return null when no token in localStorage', () => {
      expect(service.getToken()).toBeNull();
    });
  });

  describe('getCurrentUser', () => {
    it('should return current user from BehaviorSubject', () => {
      const mockUser: User = {
        id: '1',
        username: 'testuser',
        email: 'test@example.com'
      };
      const mockResponse: LoginResponse = {
        token: 'test-token',
        user: mockUser
      };

      service.login('testuser', 'password123').subscribe();

      const req = httpMock.expectOne(`${apiUrl}/login`);
      req.flush(mockResponse);

      expect(service.getCurrentUser()).toEqual(mockUser);
    });

    it('should return null when no user is logged in', () => {
      expect(service.getCurrentUser()).toBeNull();
    });
  });

  describe('currentUser$ observable', () => {
    it('should emit user updates', (done) => {
      const mockUser: User = {
        id: '1',
        username: 'testuser',
        email: 'test@example.com'
      };
      const emittedValues: (User | null)[] = [];

      service.currentUser$.subscribe(user => {
        emittedValues.push(user);
        if (emittedValues.length === 2) {
          expect(emittedValues[0]).toBeNull();
          expect(emittedValues[1]).toEqual(mockUser);
          done();
        }
      });

      const mockResponse: LoginResponse = {
        token: 'test-token',
        user: mockUser
      };

      service.login('testuser', 'password123').subscribe();

      const req = httpMock.expectOne(`${apiUrl}/login`);
      req.flush(mockResponse);
    });
  });

  describe('initialization with stored user', () => {
    it('should load user from localStorage on initialization', () => {
      const storedUser: User = {
        id: '1',
        username: 'storeduser',
        email: 'stored@example.com'
      };

      localStorage.setItem('user', JSON.stringify(storedUser));

      TestBed.resetTestingModule();
      TestBed.configureTestingModule({
        imports: [HttpClientTestingModule],
        providers: [
          AuthService,
          { provide: PLATFORM_ID, useValue: 'browser' }
        ]
      });

      service = TestBed.inject(AuthService);

      expect(service.getCurrentUser()).toEqual(storedUser);
    });

    it('should handle invalid JSON in localStorage', () => {
      localStorage.setItem('user', 'invalid-json{');
      spyOn(console, 'error');

      TestBed.resetTestingModule();
      TestBed.configureTestingModule({
        imports: [HttpClientTestingModule],
        providers: [
          AuthService,
          { provide: PLATFORM_ID, useValue: 'browser' }
        ]
      });

      service = TestBed.inject(AuthService);

      expect(console.error).toHaveBeenCalled();
      expect(service.getCurrentUser()).toBeNull();
    });
  });

  describe('server-side rendering support', () => {
    it('should not use localStorage on server platform', () => {
      TestBed.resetTestingModule();
      TestBed.configureTestingModule({
        imports: [HttpClientTestingModule],
        providers: [
          AuthService,
          { provide: PLATFORM_ID, useValue: 'server' }
        ]
      });

      service = TestBed.inject(AuthService);

      expect(service.isAuthenticated()).toBe(false);
      expect(service.getToken()).toBeNull();
    });
  });
});
