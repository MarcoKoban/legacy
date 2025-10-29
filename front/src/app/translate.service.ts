import { Injectable } from "@angular/core";
import translate from '../assets/translate/translateHome.json';
import { LanguageService } from "./languagesService";

@Injectable({ providedIn: 'root' })
export class TranslateService {
  lang: string = 'en';
  dict: any = {};

  constructor(private languageService: LanguageService) {
    if (typeof window !== 'undefined') {
      Promise.all([
        fetch('assets/translate/boot.txt').then(r => r.text()).catch(() => ''),
        fetch('assets/translate/lang.txt').then(r => r.text()).catch(() => 'en')
      ]).then(([bootRaw, langRaw]) => {
        const bootId = bootRaw.trim();
        const startupLang = langRaw.trim() || 'en';
        const storedBoot = localStorage.getItem('bootId');

        // If new session -> reset language to startupLang
        if (!storedBoot || storedBoot !== bootId) {
          localStorage.setItem('bootId', bootId);
          localStorage.setItem('firstChoice', startupLang);
          localStorage.setItem('lang', startupLang);
          this.languageService.setLang(startupLang);
        } else {
          // Same session -> keep user-chosen lang if exists
          const current = localStorage.getItem('lang') || startupLang;
          this.languageService.setLang(current);
        }

        const supportedLangs = Object.keys(translate);
        let langCode = this.languageService.getLang();
        if (!supportedLangs.includes(langCode)) langCode = startupLang;

        this.lang = langCode;
        this.dict = (translate as any)[this.lang];
      });

      // Fallback initial dict (will be updated asynchronously)
      this.dict = (translate as any)[this.lang];
    }
  }
  t(key: string): string {
    return this.dict[key] || key;
  }
}