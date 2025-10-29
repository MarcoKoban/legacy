import { Injectable } from "@angular/core";
import translateGed from "../../../assets/translate/translateGed2Gwb.json"
import { LanguageService } from "../../languagesService";

@Injectable({ providedIn: "root" })
export class TranslateGed2GwbService {
  lang: string = 'en';
  dict: any = {};

  constructor(private languageService: LanguageService) {
    const supportedLangs = Object.keys(translateGed);
    var langCode: string = this.languageService.getLang();

  
    this.lang = supportedLangs.includes(langCode) ? langCode : 'en';
    this.dict = (translateGed as any)[this.lang];
  }
  t(key: string): string {
    return this.dict[key] || key;
  }
}