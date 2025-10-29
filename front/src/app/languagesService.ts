import { Injectable } from "@angular/core";

@Injectable({ providedIn: 'root' })
export class LanguageService {
  lang: string = '';

  setLang(newLang: string) {
    this.lang = newLang;
    localStorage.setItem('lang', newLang);
  }

  getLang(): string {
    if (this.lang === '') this.lang = localStorage.getItem('lang') || 'en';
    return this.lang;
  }
}