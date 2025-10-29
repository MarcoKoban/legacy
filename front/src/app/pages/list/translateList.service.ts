import { Injectable } from "@angular/core";
import translateList from "../../../assets/translate/translateList.json"
import { LanguageService } from "../../languagesService";

@Injectable({ providedIn: "root" })
export class TranslateListService {
  lang: string = 'en';
  dict: any = {};

  constructor(private languageService: LanguageService) {
    if (typeof window !== 'undefined') {
        fetch('assets/translate/lang.txt')
        .then(response => response.text())
        .then(text => {
            const supportedLangs = Object.keys(translateList);
            var langCode: string = this.languageService.getLang();
            if (!supportedLangs.includes(langCode)) {
              langCode = text.trim();
            }
            this.lang = supportedLangs.includes(langCode) ? langCode : 'en';
            this.dict = (translateList as any)[this.lang];
        });
        this.dict = (translateList as any)[this.lang];
    }
  }
  t(key: string): string {
    return this.dict[key] || key;
  }
}