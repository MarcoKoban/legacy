import { Injectable } from "@angular/core";
import translate from '../assets/translate/translateDatabase.json';
import { LanguageService } from "./languagesService";

@Injectable({ providedIn: 'root' })
export class TranslateDatabaseService {
  lang: string = 'fr';
  dict: any = {};

  constructor(private languageService: LanguageService) {
    this.lang = this.languageService.getLang();
    const supportedLangs = Object.keys(translate);
    if (!supportedLangs.includes(this.lang)) {
      this.lang = 'fr';
    }
    this.dict = (translate as any)[this.lang];
  }

  setLang(lang: string) {
    this.lang = lang;
    this.dict = (translate as any)[this.lang];
  }

  t(key: string): string {
    return this.dict[key] || key;
  }

  getPersonCount(count: number): string {
    if (count === 0) {
      return `${count} ${this.dict['person_count_zero'] || 'personne'}`;
    } else if (count === 1) {
      return `${count} ${this.dict['person_count_one'] || 'personne'}`;
    } else {
      return `${count} ${this.dict['person_count_other'] || 'personnes'}`;
    }
  }
}
