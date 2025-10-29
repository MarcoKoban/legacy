import { Injectable } from "@angular/core";
import translateErrors from "../../../assets/translate/translateTraces.json"
import { LanguageService } from "../../languagesService";

@Injectable({ providedIn: "root" })
export class TranslateTracesService {
  lang: string = 'en';
  dict: any = {};

  constructor(private languageService: LanguageService) {
    const supportedLangs = Object.keys(translateErrors);
    var langCode: string = this.languageService.getLang();

  
    this.lang = supportedLangs.includes(langCode) ? langCode : 'en';
    this.dict = (translateErrors as any)[this.lang];

    // if (typeof window !== 'undefined') {
    //     fetch('assets/translate/lang.txt')
    //     .then(response => response.text())
    //     .then(text => {
    //         const supportedLangs = Object.keys(translateErrors);
    //         var langCode: string = this.languageService.getLang();
    //         if (!supportedLangs.includes(langCode)) {
    //           langCode = text.trim();
    //         }
    //         this.lang = supportedLangs.includes(langCode) ? langCode : 'en';
    //         this.dict = (translateErrors as any)[this.lang];
    //     });
    //     this.dict = (translateErrors as any)[this.lang];
    // }
  }
  t(key: string): string {
    return this.dict[key] || key;
  }
}