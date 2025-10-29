import { Component } from '@angular/core';
import { RouterOutlet, Router } from '@angular/router';
import { TranslateGed2GwbService } from './translateGed2Gwb.service';

@Component({
  selector: 'app-ged2Gwb',
  standalone: true,
  templateUrl: './ged2Gwb.component.html',
  styleUrl: './ged2Gwb.component.css'
})
export class Ged2GwbComponent {
    commLog: string = '';
    gwsetupLog: string = '';

  constructor(private router: Router, public translate: TranslateGed2GwbService) {
  }

   goToLink(event: Event, url: string = '') {
    event.preventDefault();
    if (url.startsWith('https')) window.location.href = url;
    else if (url === '') this.router.navigate(['/nothingToSeeHere']);
    else this.router.navigate([`${url}`]);
  }
}