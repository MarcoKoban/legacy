import { Component } from '@angular/core';
import { RouterOutlet, Router } from '@angular/router';
import { TranslateGwcService } from './translateGwc.service';

@Component({
  selector: 'app-gwc',
  standalone: true,
  templateUrl: './gwc.component.html',
  styleUrl: './gwc.component.css'
})
export class GwcComponent {
    commLog: string = '';
    gwsetupLog: string = '';

  constructor(private router: Router, public translate: TranslateGwcService) {
  }

   goToLink(event: Event, url: string = '') {
    event.preventDefault();
    if (url.startsWith('https')) window.location.href = url;
    else if (url === '') this.router.navigate(['/nothingToSeeHere']);
    else this.router.navigate([`${url}`]);
  }
}