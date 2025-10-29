import { Component } from '@angular/core';
import { RouterOutlet, Router } from '@angular/router';
import { TranslateListService } from './translateList.service';
import { LanguageService } from '../../languagesService';
import { HttpClientModule, HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-list',
  standalone: true,
  templateUrl: './list.component.html',
  styleUrl: './list.component.css',
  imports: [HttpClientModule, RouterOutlet, CommonModule],
})
export class ListComponent {
  databases: any[] = []; // ✅ liste des DBs
  loading = false;
  errorMessage = '';

  constructor(private router: Router, public languageService: LanguageService, public translate: TranslateListService, private http: HttpClient) {
  }

  ngOnInit(): void {
    this.loadDatabases();
  }

  loadDatabases(): void {
    this.loading = true;
    this.errorMessage = '';

    const token = localStorage.getItem('auth_token') || '';
    const headers = { 'Authorization': `Bearer ${token}` };

    this.http.get(`${environment.apiUrl}/database/databases`, { headers }).subscribe({
      next: (data: any) => {
        this.databases = data.databases || [];
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur lors du chargement des bases de données', err);
        this.errorMessage = 'Impossible de charger les bases de données.';
        this.loading = false;
      },
    });
  }

   goToLink(event: Event, url: string = '') {
    event.preventDefault();
    if (url.startsWith('https')) this.navigateExternal(url);
    else if (url === '') this.router.navigate(['/nothingToSeeHere']);
    else this.router.navigate([`${url}`]);
  }

  private navigateExternal(url: string) {
    window.location.href = url;
  }

  goToDatabase(event: Event, dbName: string) {
    event.preventDefault();
    this.router.navigate(['/database', dbName]);
  }
}