import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { LanguageService } from '../../languagesService';
import { TranslateRenameService } from '../../translate-rename.service';
import { environment } from '../../../environments/environment.prod';

@Component({
  selector: 'app-rename',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './rename.component.html',
  styleUrls: ['./rename.component.css']
})
export class RenameComponent implements OnInit {
  databases: any[] = [];
  loading = false;
  errorMessage = '';
  selectedDb: string = '';
  newName: string = '';
  currentLanguage = 'FR';
  token = '';

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
    public languageService: LanguageService,
    public translate: TranslateRenameService
  ) {
    // Initialize current language display
    const currentLang = this.languageService.getLang();
    this.currentLanguage = currentLang.toUpperCase();
    this.token = localStorage.getItem('auth_token') || '';
  }

  ngOnInit() {
    this.loadDatabases();
  }

  loadDatabases(): void {
    this.loading = true;
    this.errorMessage = '';
    const headers = { 'Authorization': `Bearer ${this.token}` };

    this.http.get(`${environment.apiUrl}/database/databases`, { headers }).subscribe({
      next: (data: any) => {
        this.databases = data.databases || [];
        if (this.databases.length > 0) {
          this.selectedDb = this.databases[0].name;
          this.newName = this.databases[0].name;
        }
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur lors du chargement des bases de données', err);
        this.errorMessage = 'Impossible de charger les bases de données.';
        this.loading = false;
      },
    });
  }

  onDatabaseChange() {
    // Update newName input with selected database name
    this.newName = this.selectedDb;
  }

  onRename() {
    if (!this.selectedDb || !this.newName) {
      alert(this.translate.t('alert_missing'));
      return;
    }

    if (this.selectedDb === this.newName) {
      alert(this.translate.t('alert_same_name'));
      return;
    }

    const renameData = {
      new_name: this.newName,
      rename_files: false
    };

    const headers = {
        'Authorization': `Bearer ${this.token}`
    }

    this.http.put(
      `${environment.apiUrl}/database/databases/${this.selectedDb}/rename`,
      renameData,
      { headers }
    ).subscribe({
      next: (response: any) => {
        alert(this.translate.t('alert_success', { oldName: this.selectedDb, newName: this.newName }));
        this.router.navigate(['/home']);
      },
      error: (err) => {
        console.error('Erreur lors du renommage', err);
        const errorMsg = err.error?.detail || this.translate.t('alert_error');
        alert(errorMsg);
      }
    });
  }

  changeLanguage(lang: string) {
    this.currentLanguage = lang.toUpperCase();
    this.languageService.setLang(lang);
    this.translate.setLang(lang);
  }

  goBack() {
    this.router.navigate(['/home']);
  }
}
