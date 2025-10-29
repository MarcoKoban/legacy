import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { TranslateAuthService } from '../../translate-auth.service';
import { LanguageService } from '../../languagesService';
import { AuthService } from '../../services/auth.service';
import translate from '../../../assets/translate/translateAuth.json';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './auth.component.html',
  styleUrls: ['./auth.component.css']
})
export class AuthComponent {
  isLoginMode = true;
  
  // Login fields
  loginUsername = '';
  loginPassword = '';
  
  // Register fields
  registerUsername = '';
  registerEmail = '';
  registerPassword = '';
  registerConfirmPassword = '';
  
  errorMessage = '';
  successMessage = '';
  isLoading = false;

  // List of supported languages
  languages = [
    { code: 'co', label: 'Corsu' },
    { code: 'de', label: 'Deutsch' },
    { code: 'en', label: 'English' },
    { code: 'es', label: 'Español' },
    { code: 'fr', label: 'Français' },
    { code: 'it', label: 'Italiano' },
    { code: 'lv', label: 'Latviešu' },
    { code: 'sv', label: 'Svenska' },
    { code: 'fi', label: 'Suomi' },
  ];

  constructor(
    private router: Router,
    private http: HttpClient,
    private authService: AuthService,
    public translateAuth: TranslateAuthService,
    public languageService: LanguageService
  ) {}

  toggleMode() {
    this.isLoginMode = !this.isLoginMode;
    this.errorMessage = '';
    this.successMessage = '';
  }

  changeLang(event: Event, lang: string) {
    event.preventDefault();
    this.languageService.setLang(lang);
    // Mettre à jour le dictionnaire de traduction
    this.translateAuth.lang = lang;
    this.translateAuth.dict = (translate as any)[lang];
  }

  onLogin() {
    this.errorMessage = '';
    this.successMessage = '';
    
    if (!this.loginUsername || !this.loginPassword) {
      this.errorMessage = this.translateAuth.t('fill_all_fields');
      return;
    }

    this.isLoading = true;
    
    // Utilisation du service AuthService pour se connecter à l'API
    this.authService.login(this.loginUsername, this.loginPassword)
      .subscribe({
        next: (response) => {
          this.isLoading = false;
          this.successMessage = this.translateAuth.t('login_success');
          
          // Rediriger vers la page d'accueil
          setTimeout(() => {
            this.router.navigate(['/home']);
          }, 500);
        },
        error: (error) => {
          this.isLoading = false;
          this.errorMessage = error.error?.detail || this.translateAuth.t('login_error') || 'Erreur de connexion. Vérifiez vos identifiants.';
          console.error('Login error:', error);
        }
      });
  }

  onRegister() {
    this.errorMessage = '';
    this.successMessage = '';
    
    if (!this.registerUsername || !this.registerEmail || !this.registerPassword || !this.registerConfirmPassword) {
      this.errorMessage = this.translateAuth.t('fill_all_fields');
      return;
    }

    if (this.registerPassword !== this.registerConfirmPassword) {
      this.errorMessage = this.translateAuth.t('passwords_mismatch');
      return;
    }

    if (this.registerPassword.length < 8) {
      this.errorMessage = this.translateAuth.t('password_too_short');
      return;
    }

    this.isLoading = true;
    
    // Utilisation du service AuthService pour s'enregistrer
    this.authService.register(this.registerUsername, this.registerEmail, this.registerPassword)
      .subscribe({
        next: (response) => {
          this.isLoading = false;
          this.successMessage = this.translateAuth.t('register_success');
          
          // Basculer vers le mode login après 2 secondes
          setTimeout(() => {
            this.isLoginMode = true;
            this.loginUsername = this.registerUsername;
            this.successMessage = '';
          }, 2000);
        },
        error: (error) => {
          this.isLoading = false;
          this.errorMessage = error.error?.detail || this.translateAuth.t('register_error');
          console.error('Register error:', error);
        }
      });
  }
}
