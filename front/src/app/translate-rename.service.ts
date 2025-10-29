import { Injectable } from "@angular/core";
import translate from '../assets/translate/translateRename.json';
import { LanguageService } from "./languagesService";

@Injectable({ providedIn: 'root' })
export class TranslateRenameService {
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

  t(key: string, params?: any): string {
    let text = this.dict[key] || key;
    
    // Replace placeholders like {oldName} and {newName}
    if (params) {
      Object.keys(params).forEach(param => {
        text = text.replace(`{${param}}`, params[param]);
      });
    }
    
    return text;
  }
}
