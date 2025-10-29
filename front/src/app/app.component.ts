import { Component, OnInit } from '@angular/core';
import { Router, RouterLink, RouterOutlet } from '@angular/router';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  template: `
    <router-outlet />
  `
})
export class AppComponent implements OnInit {
  title = 'Geneweb';

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    // Vérifier si l'utilisateur est connecté au démarrage
    // Si non connecté et pas sur la page d'auth ou racine, rediriger vers /
    const currentUrl = this.router.url;
    const isAuthPage = currentUrl === '/' || currentUrl === '/auth' || currentUrl.startsWith('/auth');
    
    if (!this.authService.isAuthenticated() && !isAuthPage) {
      this.router.navigate(['/']);
    }
  }
}
