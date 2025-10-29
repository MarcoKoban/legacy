import { Component } from '@angular/core';
import { RouterOutlet, Router } from '@angular/router';
import { TranslateTracesService } from './translateTraces.service';

@Component({
  selector: 'app-traces',
  standalone: true,
  templateUrl: './traces.component.html',
  styleUrl: './traces.component.css'
})
export class TracesComponent {
    commLog: string = '';
    gwsetupLog: string = '';

  constructor(private router: Router, public translate: TranslateTracesService) {
    if (typeof window !== 'undefined') {
      fetch('assets/logs/comm.log')
      .then(response => {
        if (!response.ok) {
            this.commLog = this.translate.t('no_commLog');
        }
        response.text().then(text => text.trim() ? text : this.commLog = this.translate.t('no_commLog'));
      }).catch(() => this.commLog = this.translate.t('no_commLog'));
      fetch('assets/logs/gwsetup.log')
      .then(response => {
        if (!response.ok) {
            this.gwsetupLog = this.translate.t('no_gwsetupLog');
        }
        response.text().then(text => text.trim() ? text : this.gwsetupLog = this.translate.t('no_gwsetupLog'));
      }).catch(() => this.gwsetupLog = this.translate.t('no_gwsetupLog'));
    }
  }

   goToLink(event: Event, url: string = '') {
    event.preventDefault();
    if (url.startsWith('https')) window.location.href = url;
    else if (url === '') this.router.navigate(['/nothingToSeeHere']);
    else this.router.navigate([`${url}`]);
  }
}