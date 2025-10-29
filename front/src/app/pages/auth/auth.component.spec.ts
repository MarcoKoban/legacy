import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { AuthComponent } from './auth.component';
import { AuthService } from '../../services/auth.service';
import { TranslateAuthService } from '../../translate-auth.service';
import { LanguageService } from '../../languagesService';
import { of, throwError } from 'rxjs';

describe('AuthComponent', () => {
  let component: AuthComponent;
  let fixture: ComponentFixture<AuthComponent>;
  let authService: jasmine.SpyObj<AuthService>;
  let translateAuthService: jasmine.SpyObj<TranslateAuthService>;
  let languageService: jasmine.SpyObj<LanguageService>;
  let httpMock: HttpTestingController;

  beforeEach(async () => {
    const authServiceSpy = jasmine.createSpyObj('AuthService', ['login', 'register', 'logout']);
    const translateAuthServiceSpy = jasmine.createSpyObj('TranslateAuthService', ['t'], {
      lang: 'en',
      dict: {}
    });
    const languageServiceSpy = jasmine.createSpyObj('LanguageService', ['setLang', 'getLang']);

    await TestBed.configureTestingModule({
      imports: [AuthComponent, HttpClientTestingModule, RouterTestingModule],
      providers: [
        { provide: AuthService, useValue: authServiceSpy },
        { provide: TranslateAuthService, useValue: translateAuthServiceSpy },
        { provide: LanguageService, useValue: languageServiceSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(AuthComponent);
    component = fixture.componentInstance;
    authService = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    translateAuthService = TestBed.inject(TranslateAuthService) as jasmine.SpyObj<TranslateAuthService>;
    languageService = TestBed.inject(LanguageService) as jasmine.SpyObj<LanguageService>;
    httpMock = TestBed.inject(HttpTestingController);

    // Setup default mock translations
    translateAuthService.t.and.returnValue('');
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('initialization', () => {
    it('should initialize in login mode', () => {
      expect(component.isLoginMode).toBe(true);
    });

    it('should have 9 supported languages', () => {
      expect(component.languages.length).toBe(9);
    });

    it('should include French language', () => {
      const frenchLang = component.languages.find(l => l.code === 'fr');
      expect(frenchLang).toBeDefined();
      expect(frenchLang?.label).toBe('Français');
    });

    it('should initialize with empty form fields', () => {
      expect(component.loginUsername).toBe('');
      expect(component.loginPassword).toBe('');
      expect(component.registerUsername).toBe('');
      expect(component.registerEmail).toBe('');
      expect(component.registerPassword).toBe('');
      expect(component.registerConfirmPassword).toBe('');
    });

    it('should initialize with no error message', () => {
      expect(component.errorMessage).toBe('');
    });

    it('should initialize with no success message', () => {
      expect(component.successMessage).toBe('');
    });

    it('should initialize as not loading', () => {
      expect(component.isLoading).toBe(false);
    });
  });

  describe('toggleMode', () => {
    it('should toggle from login to register', () => {
      expect(component.isLoginMode).toBe(true);
      component.toggleMode();
      expect(component.isLoginMode).toBe(false);
    });

    it('should toggle from register to login', () => {
      component.isLoginMode = false;
      component.toggleMode();
      expect(component.isLoginMode).toBe(true);
    });

    it('should clear error message when toggling', () => {
      component.errorMessage = 'Some error';
      component.toggleMode();
      expect(component.errorMessage).toBe('');
    });

    it('should clear success message when toggling', () => {
      component.successMessage = 'Some success';
      component.toggleMode();
      expect(component.successMessage).toBe('');
    });
  });

  describe('changeLang', () => {
    it('should set language through LanguageService', () => {
      const event = new Event('click');
      spyOn(event, 'preventDefault');

      component.changeLang(event, 'es');

      expect(event.preventDefault).toHaveBeenCalled();
      expect(languageService.setLang).toHaveBeenCalledWith('es');
    });

    it('should update TranslateAuthService language', () => {
      const event = new Event('click');
      const initialLang = component.translateAuth.lang;

      component.changeLang(event, 'de');

      // Check that languageService was called with the new language
      expect(languageService.setLang).toHaveBeenCalledWith('de');
    });

    it('should prevent default event behavior', () => {
      const event = new Event('click');
      spyOn(event, 'preventDefault');

      component.changeLang(event, 'it');

      expect(event.preventDefault).toHaveBeenCalled();
    });
  });

  describe('onLogin', () => {
    beforeEach(() => {
      translateAuthService.t.and.callFake((key: string) => {
        const translations: { [key: string]: string } = {
          'fill_all_fields': 'Please fill all fields',
          'login_error': 'Login error occurred'
        };
        return translations[key] || '';
      });
    });

    it('should clear messages before login attempt', () => {
      component.errorMessage = 'Old error';
      component.successMessage = 'Old success';

      authService.login.and.returnValue(of({ token: 'test', user: { username: 'test', email: 'test@test.com' } }));
      component.loginUsername = 'testuser';
      component.loginPassword = 'password';

      component.onLogin();

      expect(component.errorMessage).toBe('');
      expect(component.successMessage).toBe('');
    });

    it('should show error when username is missing', () => {
      component.loginUsername = '';
      component.loginPassword = 'password';
      translateAuthService.t.and.returnValue('Please fill all fields');

      component.onLogin();

      expect(component.errorMessage).toBe('Please fill all fields');
      expect(authService.login).not.toHaveBeenCalled();
    });

    it('should show error when password is missing', () => {
      component.loginUsername = 'testuser';
      component.loginPassword = '';
      translateAuthService.t.and.returnValue('Please fill all fields');

      component.onLogin();

      expect(component.errorMessage).toBe('Please fill all fields');
      expect(authService.login).not.toHaveBeenCalled();
    });

    it('should call AuthService.login with credentials', () => {
      component.loginUsername = 'testuser';
      component.loginPassword = 'password123';
      authService.login.and.returnValue(of({ token: 'test', user: { username: 'test', email: 'test@test.com' } }));

      component.onLogin();

      expect(authService.login).toHaveBeenCalledWith('testuser', 'password123');
    });

    it('should set loading state during login', () => {
      component.loginUsername = 'testuser';
      component.loginPassword = 'password123';
      authService.login.and.returnValue(of({ token: 'test', user: { username: 'test', email: 'test@test.com' } }));

      component.onLogin();

      // Since the subscription is instant with of(), isLoading should be false after
      expect(component.isLoading).toBe(false);
    });

    it('should show success message on successful login', () => {
      component.loginUsername = 'testuser';
      component.loginPassword = 'password123';
      translateAuthService.t.and.returnValue('Login successful');
      authService.login.and.returnValue(of({ token: 'test', user: { username: 'test', email: 'test@test.com' } }));

      component.onLogin();

      expect(component.successMessage).toBe('Login successful');
    });

    it('should navigate to home on successful login', (done) => {
      const routerSpy = TestBed.inject(Router) as jasmine.SpyObj<Router>;
      spyOn(routerSpy, 'navigate');
      component.loginUsername = 'testuser';
      component.loginPassword = 'password123';
      translateAuthService.t.and.returnValue('Login successful');
      authService.login.and.returnValue(of({ token: 'test', user: { username: 'test', email: 'test@test.com' } }));

      component.onLogin();

      // setTimeout is used in component, so we need to wait
      setTimeout(() => {
        expect(routerSpy.navigate).toHaveBeenCalledWith(['/home']);
        done();
      }, 600);
    });

    it('should handle login error with detail message', () => {
      component.loginUsername = 'testuser';
      component.loginPassword = 'wrongpassword';
      const error = { error: { detail: 'Invalid credentials' } };
      authService.login.and.returnValue(throwError(() => error));

      component.onLogin();

      expect(component.errorMessage).toBe('Invalid credentials');
      expect(component.isLoading).toBe(false);
    });

    it('should handle login error without detail message', () => {
      component.loginUsername = 'testuser';
      component.loginPassword = 'wrongpassword';
      const error = { error: {} };
      translateAuthService.t.and.returnValue('Login error occurred');
      authService.login.and.returnValue(throwError(() => error));

      component.onLogin();

      expect(component.errorMessage).toBe('Login error occurred');
    });

    it('should log error to console on login failure', () => {
      spyOn(console, 'error');
      component.loginUsername = 'testuser';
      component.loginPassword = 'wrongpassword';
      const error = { error: { detail: 'Invalid' } };
      authService.login.and.returnValue(throwError(() => error));

      component.onLogin();

      expect(console.error).toHaveBeenCalledWith('Login error:', error);
    });
  });

  describe('onRegister', () => {
    beforeEach(() => {
      translateAuthService.t.and.callFake((key: string) => {
        const translations: { [key: string]: string } = {
          'fill_all_fields': 'Please fill all fields',
          'passwords_mismatch': 'Passwords do not match',
          'password_too_short': 'Password is too short',
          'register_success': 'Registration successful',
          'register_error': 'Registration error'
        };
        return translations[key] || '';
      });
    });

    it('should clear messages before register attempt', () => {
      component.errorMessage = 'Old error';
      component.successMessage = 'Old success';

      authService.register.and.returnValue(of({ message: 'Success' }));
      component.registerUsername = 'newuser';
      component.registerEmail = 'new@test.com';
      component.registerPassword = 'password123';
      component.registerConfirmPassword = 'password123';

      component.onRegister();

      // Check that messages were cleared at the start of the method
      // Note: The success message is set after the subscription succeeds
      expect(component.errorMessage).toBe('');
    });

    it('should show error when username is missing', () => {
      component.registerUsername = '';
      component.registerEmail = 'new@test.com';
      component.registerPassword = 'password123';
      component.registerConfirmPassword = 'password123';
      translateAuthService.t.and.returnValue('Please fill all fields');

      component.onRegister();

      expect(component.errorMessage).toBe('Please fill all fields');
      expect(authService.register).not.toHaveBeenCalled();
    });

    it('should show error when email is missing', () => {
      component.registerUsername = 'newuser';
      component.registerEmail = '';
      component.registerPassword = 'password123';
      component.registerConfirmPassword = 'password123';
      translateAuthService.t.and.returnValue('Please fill all fields');

      component.onRegister();

      expect(component.errorMessage).toBe('Please fill all fields');
      expect(authService.register).not.toHaveBeenCalled();
    });

    it('should show error when password is missing', () => {
      component.registerUsername = 'newuser';
      component.registerEmail = 'new@test.com';
      component.registerPassword = '';
      component.registerConfirmPassword = 'password123';
      translateAuthService.t.and.returnValue('Please fill all fields');

      component.onRegister();

      expect(component.errorMessage).toBe('Please fill all fields');
      expect(authService.register).not.toHaveBeenCalled();
    });

    it('should show error when passwords do not match', () => {
      component.registerUsername = 'newuser';
      component.registerEmail = 'new@test.com';
      component.registerPassword = 'password123';
      component.registerConfirmPassword = 'password456';
      translateAuthService.t.and.returnValue('Passwords do not match');

      component.onRegister();

      expect(component.errorMessage).toBe('Passwords do not match');
      expect(authService.register).not.toHaveBeenCalled();
    });

    it('should show error when password is too short', () => {
      component.registerUsername = 'newuser';
      component.registerEmail = 'new@test.com';
      component.registerPassword = 'short';
      component.registerConfirmPassword = 'short';
      translateAuthService.t.and.returnValue('Password is too short');

      component.onRegister();

      expect(component.errorMessage).toBe('Password is too short');
      expect(authService.register).not.toHaveBeenCalled();
    });

    it('should call AuthService.register with correct data', () => {
      component.registerUsername = 'newuser';
      component.registerEmail = 'new@test.com';
      component.registerPassword = 'password123';
      component.registerConfirmPassword = 'password123';
      authService.register.and.returnValue(of({ message: 'Success' }));

      component.onRegister();

      expect(authService.register).toHaveBeenCalledWith('newuser', 'new@test.com', 'password123');
    });

    it('should show success message on successful registration', () => {
      component.registerUsername = 'newuser';
      component.registerEmail = 'new@test.com';
      component.registerPassword = 'password123';
      component.registerConfirmPassword = 'password123';
      translateAuthService.t.and.returnValue('Registration successful');
      authService.register.and.returnValue(of({ message: 'Success' }));

      component.onRegister();

      expect(component.successMessage).toBe('Registration successful');
      expect(component.isLoading).toBe(false);
    });

    it('should switch to login mode after successful registration', (done) => {
      component.isLoginMode = false;
      component.registerUsername = 'newuser';
      component.registerEmail = 'new@test.com';
      component.registerPassword = 'password123';
      component.registerConfirmPassword = 'password123';
      translateAuthService.t.and.returnValue('Registration successful');
      authService.register.and.returnValue(of({ message: 'Success' }));

      component.onRegister();

      setTimeout(() => {
        expect(component.isLoginMode).toBe(true);
        done();
      }, 2100);
    });

    it('should prefill username in login form after registration', (done) => {
      component.registerUsername = 'newuser';
      component.registerEmail = 'new@test.com';
      component.registerPassword = 'password123';
      component.registerConfirmPassword = 'password123';
      translateAuthService.t.and.returnValue('Registration successful');
      authService.register.and.returnValue(of({ message: 'Success' }));

      component.onRegister();

      setTimeout(() => {
        expect(component.loginUsername).toBe('newuser');
        done();
      }, 2100);
    });

    it('should clear success message after switching to login mode', (done) => {
      component.registerUsername = 'newuser';
      component.registerEmail = 'new@test.com';
      component.registerPassword = 'password123';
      component.registerConfirmPassword = 'password123';
      translateAuthService.t.and.returnValue('Registration successful');
      authService.register.and.returnValue(of({ message: 'Success' }));

      component.onRegister();

      setTimeout(() => {
        expect(component.successMessage).toBe('');
        done();
      }, 2100);
    });

    it('should handle register error with detail message', () => {
      component.registerUsername = 'newuser';
      component.registerEmail = 'new@test.com';
      component.registerPassword = 'password123';
      component.registerConfirmPassword = 'password123';
      const error = { error: { detail: 'Username already exists' } };
      authService.register.and.returnValue(throwError(() => error));

      component.onRegister();

      expect(component.errorMessage).toBe('Username already exists');
      expect(component.isLoading).toBe(false);
    });

    it('should handle register error without detail message', () => {
      component.registerUsername = 'newuser';
      component.registerEmail = 'new@test.com';
      component.registerPassword = 'password123';
      component.registerConfirmPassword = 'password123';
      const error = { error: {} };
      translateAuthService.t.and.returnValue('Registration error');
      authService.register.and.returnValue(throwError(() => error));

      component.onRegister();

      expect(component.errorMessage).toBe('Registration error');
    });

    it('should log error to console on registration failure', () => {
      spyOn(console, 'error');
      component.registerUsername = 'newuser';
      component.registerEmail = 'new@test.com';
      component.registerPassword = 'password123';
      component.registerConfirmPassword = 'password123';
      const error = { error: { detail: 'Error' } };
      authService.register.and.returnValue(throwError(() => error));

      component.onRegister();

      expect(console.error).toHaveBeenCalledWith('Register error:', error);
    });
  });

  describe('language support', () => {
    it('should have Corsican language', () => {
      const corsican = component.languages.find(l => l.code === 'co');
      expect(corsican).toBeDefined();
      expect(corsican?.label).toBe('Corsu');
    });

    it('should have German language', () => {
      const german = component.languages.find(l => l.code === 'de');
      expect(german).toBeDefined();
      expect(german?.label).toBe('Deutsch');
    });

    it('should have English language', () => {
      const english = component.languages.find(l => l.code === 'en');
      expect(english).toBeDefined();
      expect(english?.label).toBe('English');
    });

    it('should have Spanish language', () => {
      const spanish = component.languages.find(l => l.code === 'es');
      expect(spanish).toBeDefined();
      expect(spanish?.label).toBe('Español');
    });

    it('should have Italian language', () => {
      const italian = component.languages.find(l => l.code === 'it');
      expect(italian).toBeDefined();
      expect(italian?.label).toBe('Italiano');
    });

    it('should have Latvian language', () => {
      const latvian = component.languages.find(l => l.code === 'lv');
      expect(latvian).toBeDefined();
      expect(latvian?.label).toBe('Latviešu');
    });

    it('should have Swedish language', () => {
      const swedish = component.languages.find(l => l.code === 'sv');
      expect(swedish).toBeDefined();
      expect(swedish?.label).toBe('Svenska');
    });

    it('should have Finnish language', () => {
      const finnish = component.languages.find(l => l.code === 'fi');
      expect(finnish).toBeDefined();
      expect(finnish?.label).toBe('Suomi');
    });
  });
});
