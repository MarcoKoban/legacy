import { Injectable } from '@angular/core';
import translationsData from '../assets/translate/translateAddFamily.json';

@Injectable({
  providedIn: 'root'
})
export class TranslateAddFamilyService {
  private currentLang: string = 'fr';
  private translations: any = translationsData;

  constructor() {
    // Initialize with French by default
    this.currentLang = 'fr';
  }

  setLang(lang: string): void {
    this.currentLang = lang.toLowerCase();
  }

  getLang(): string {
    return this.currentLang;
  }

  t(key: string): string {
    const langTranslations = this.translations[this.currentLang];
    if (langTranslations && langTranslations[key]) {
      return langTranslations[key];
    }
    // Fallback to French if translation not found
    return this.translations['fr'][key] || key;
  }
}
