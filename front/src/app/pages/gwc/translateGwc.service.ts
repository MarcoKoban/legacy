import { Injectable } from "@angular/core";
import translateGwc from "../../../assets/translate/translateGwc.json"
import { LanguageService } from "../../languagesService";

@Injectable({ providedIn: "root" })
export class TranslateGwcService {
  lang: string = 'en';
  dict: any = {};

  constructor(private languageService: LanguageService) {
    const supportedLangs = Object.keys(translateGwc);
    var langCode: string = this.languageService.getLang();

  
    this.lang = supportedLangs.includes(langCode) ? langCode : 'en';
    this.dict = (translateGwc as any)[this.lang];
  }
  t(key: string): string {
    return this.dict[key] || key;
  }
}