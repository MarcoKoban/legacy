import { Component, HostListener, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
import { LanguageService } from '../../languagesService';
import { TranslateDatabaseService } from '../../translate-database.service';

@Component({
  selector: 'app-database',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './database.component.html',
  styleUrls: ['./database.component.css']
})
export class DatabaseComponent implements OnInit {
  databaseName = '';
  dbName: string = '';
  personCount = 0;
  currentLanguage = 'FR';
  showLanguageDropdown = false;

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
    private route: ActivatedRoute,
    public languageService: LanguageService,
    public translate: TranslateDatabaseService
  ) {
    // Initialize current language display
    const currentLang = this.languageService.getLang();
    this.currentLanguage = currentLang.toUpperCase();
  }

  ngOnInit() {
    // Récupérer le nom de la base de données depuis les paramètres de route
    this.route.params.subscribe(params => {
      const dbName = params['dbName'];
      if (dbName) {
        this.dbName = dbName;
      }
    });
  }

  getDatabaseTitle(): string {
    if (this.dbName) {
      return `${this.translate.t('genealogical_database')} ${this.dbName}`;
    }
    return this.translate.t('genealogical_database');
  }

  // Close dropdown when clicking outside
  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (!target.closest('.relative')) {
      this.showLanguageDropdown = false;
    }
  }

  onAddChronicle() {
    console.log('Saisir une chronique');
  }

  onAdvancedSearch() {
    console.log('Requête évoluée');
  }

  onCalendars() {
    console.log('Calendriers');
  }

  onConfiguration() {
    if (this.dbName) {
      this.router.navigate(['/configuration', this.dbName]);
    } else {
      this.router.navigate(['/configuration']);
    }
  }

  onAddNote() {
    console.log('Ajouter note');
  }

  onAddFamily() {
    if (this.dbName) {
      this.router.navigate(['/add-family', this.dbName]);
    } else {
      this.router.navigate(['/add-family']);
    }
  }

  toggleLanguageDropdown() {
    this.showLanguageDropdown = !this.showLanguageDropdown;
  }

  changeLanguage(lang: string) {
    this.currentLanguage = lang.toUpperCase();
    this.languageService.setLang(lang);
    this.translate.setLang(lang);
    this.showLanguageDropdown = false;
  }

  getCurrentLanguageLabel(): string {
    const lang = this.languages.find(l => l.code.toUpperCase() === this.currentLanguage);
    return lang ? lang.label : 'Français';
  }
}
