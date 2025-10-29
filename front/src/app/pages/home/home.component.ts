import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { NgForOf } from '@angular/common';
import { LanguageService } from '../../languagesService';
import { TranslateService } from '../../translate.service';
import { AuthService } from '../../services/auth.service';
import translate from '../../../assets/translate/translateHome.json';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [NgForOf],
  templateUrl: './home.component.html',
})
export class HomeComponent {

  constructor(
    private router: Router, 
    public languageService: LanguageService, 
    public translate: TranslateService,
    public authService: AuthService
  ) {
  }

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

  changeLang(event: Event, lang: string) {
    event.preventDefault();
    this.languageService.setLang(lang);
    // Mettre à jour le dictionnaire de traduction
    this.translate.lang = lang;
    this.translate.dict = (translate as any)[lang];
  }

  openNewTab(url: string) {
    window.open(url, '_blank');
  }

  goToLink(event: Event, url: string = '') {
    event.preventDefault();
    if (url.startsWith('https')) window.location.href = url;
    else if (url === '') this.router.navigate(['/nothingToSeeHere']);
    else this.router.navigate([`${url}`]);
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/']);
  }
}