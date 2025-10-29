import { Injectable } from "@angular/core";
import translate from '../assets/translate/translateAuth.json';
import { LanguageService } from "./languagesService";

@Injectable({ providedIn: 'root' })
export class TranslateAuthService {
  lang: string = 'fr';
  dict: any = {};

  constructor(private languageService: LanguageService) {
    const supportedLangs = Object.keys(translate);
    let langCode = this.languageService.getLang();
    if (!supportedLangs.includes(langCode)) langCode = 'fr';

    this.lang = langCode;
    this.dict = (translate as any)[this.lang];
  }

  t(key: string): string {
    return this.dict[key] || key;
  }
}
