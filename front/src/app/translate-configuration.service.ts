import { Injectable } from '@angular/core';
import translationsData from '../assets/translate/translateConfiguration.json';

@Injectable({
  providedIn: 'root'
})
export class TranslateConfigurationService {
  private translations: any = translationsData;
  private currentLang: string = 'fr';

  setLang(lang: string): void {
    this.currentLang = lang.toLowerCase();
  }

  getLang(): string {
    return this.currentLang;
  }

  t(key: string): string {
    return this.translations[this.currentLang][key] || this.translations['fr'][key] || key;
  }
}
