import { Injectable } from "@angular/core";
import translateSimple from "../../../assets/translate/translateSimple.json"
import { LanguageService } from "../../languagesService";

@Injectable({ providedIn: "root" })
export class TranslateSimpleService {
  lang: string = 'en';
  dict: any = {};

  constructor(private languageService: LanguageService) {
    const supportedLangs = Object.keys(translateSimple);
    var langCode: string = this.languageService.getLang();

  
    this.lang = supportedLangs.includes(langCode) ? langCode : 'en';
    this.dict = (translateSimple as any)[this.lang];
  }
  t(key: string): string {
    return this.dict[key] || key;
  }
}