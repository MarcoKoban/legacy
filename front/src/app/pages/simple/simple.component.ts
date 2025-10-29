import { Component } from '@angular/core';
import { RouterOutlet, Router } from '@angular/router';
import { TranslateSimpleService } from './translateSimple.service';
import { HttpClientModule, HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-simple',
  standalone: true,
  templateUrl: './simple.component.html',
  styleUrls: ['./simple.component.css'],
  imports: [FormsModule, HttpClientModule, RouterOutlet],
})
export class SimpleComponent {
  dbName = 'base';
  reorg = false;
  constructor(private router: Router, public translate: TranslateSimpleService, private http: HttpClient) {
  }

   async onSubmit(event: Event) {
    event.preventDefault();

    const payload = {
      name: this.dbName,
      set_active: this.reorg
    };

    try {
      console.log('Creating database with payload:', payload);
      const token = localStorage.getItem('auth_token') || '';
      const headers = { 'Authorization': `Bearer ${token}` };
      const result: any = await this.http.post(`${environment.apiUrl}/database/databases`, payload, { headers }).toPromise();
      console.log('Database created:', result);
      this.router.navigate(['/list']); // ou vers la page que tu veux
    } catch (error) {
      console.error('Erreur lors de la création de la DB', error);
    }
  }

   goToLink(event: Event, url: string = '') {
    event.preventDefault();
    if (url.startsWith('https')) window.location.href = url;
    else if (url === '') this.router.navigate(['/nothingToSeeHere']);
    else this.router.navigate([`${url}`]);
  }
}