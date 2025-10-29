import { Component } from '@angular/core';
import { RouterOutlet, Router } from '@angular/router';

@Component({
  selector: 'app-nothingToSeeHere',
  standalone: true,
  templateUrl: './nothing.component.html',
  styleUrl: './nothing.component.css'
})
export class NothingComponent {
    
  constructor(private router: Router) {
  }
}