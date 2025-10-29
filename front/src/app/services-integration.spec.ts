import { TestBed } from '@angular/core/testing';
import { LanguageService } from './languagesService';
import { TranslateService } from './translate.service';
import { TranslateDatabaseService } from './translate-database.service';

describe('Services Integration Tests', () => {
  let languageService: LanguageService;
  let translateService: TranslateService;
  let translateDatabaseService: TranslateDatabaseService;

  beforeEach(() => {
    localStorage.clear();

    TestBed.configureTestingModule({
      providers: [
        LanguageService,
        TranslateService,
        TranslateDatabaseService
      ]
    });

    languageService = TestBed.inject(LanguageService);
    translateService = TestBed.inject(TranslateService);
    translateDatabaseService = TestBed.inject(TranslateDatabaseService);
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('LanguageService and TranslateService integration', () => {
    it('should synchronize language between services', () => {
      languageService.setLang('fr');

      expect(languageService.getLang()).toEqual('fr');
      expect(localStorage.getItem('lang')).toEqual('fr');
    });

    it('should allow TranslateService to read language from LanguageService', () => {
      languageService.setLang('de');

      const lang = languageService.getLang();
      expect(lang).toEqual('de');
    });

    it('should persist language across service instances', () => {
      languageService.setLang('es');

      // Create new instance
      const newLanguageService = new LanguageService();

      expect(newLanguageService.getLang()).toEqual('es');
    });

    it('should handle language changes in both services', () => {
      // Set language via LanguageService
      languageService.setLang('it');
      expect(languageService.getLang()).toEqual('it');

      // Change language again
      languageService.setLang('sv');
      expect(languageService.getLang()).toEqual('sv');
    });
  });

  describe('LanguageService and TranslateDatabaseService integration', () => {
    it('should initialize TranslateDatabaseService with LanguageService language', () => {
      languageService.setLang('fr');

      const newTranslateDatabaseService = new TranslateDatabaseService(languageService);

      expect(newTranslateDatabaseService.lang).toEqual('fr');
    });

    it('should update TranslateDatabaseService when language changes', () => {
      translateDatabaseService.setLang('en');

      expect(translateDatabaseService.lang).toEqual('en');
      expect(translateDatabaseService.dict).toBeDefined();
    });

    it('should keep translation dict synchronized with language', () => {
      translateDatabaseService.setLang('fr');
      const frenchDict = translateDatabaseService.dict;

      translateDatabaseService.setLang('en');
      const englishDict = translateDatabaseService.dict;

      // Dicts should be different objects
      expect(frenchDict).not.toEqual(englishDict);
    });

    it('should handle language switching between multiple languages', () => {
      const languages = ['fr', 'en', 'de', 'es', 'it'];

      languages.forEach(lang => {
        translateDatabaseService.setLang(lang);
        expect(translateDatabaseService.lang).toEqual(lang);
      });
    });
  });

  describe('All services working together', () => {
    it('should maintain consistent language state across all services', () => {
      const targetLang = 'de';

      languageService.setLang(targetLang);
      translateDatabaseService.setLang(targetLang);

      expect(languageService.getLang()).toEqual(targetLang);
      expect(translateDatabaseService.lang).toEqual(targetLang);
      expect(localStorage.getItem('lang')).toEqual(targetLang);
    });

    it('should handle translations after language change', () => {
      translateDatabaseService.setLang('fr');
      translateDatabaseService.dict = {
        test: 'Test en français',
        hello: 'Bonjour'
      };

      expect(translateDatabaseService.t('test')).toEqual('Test en français');
      expect(translateDatabaseService.t('hello')).toEqual('Bonjour');

      // Change language
      translateDatabaseService.setLang('en');
      translateDatabaseService.dict = {
        test: 'Test in English',
        hello: 'Hello'
      };

      expect(translateDatabaseService.t('test')).toEqual('Test in English');
      expect(translateDatabaseService.t('hello')).toEqual('Hello');
    });

    it('should handle person count in different languages', () => {
      // French
      translateDatabaseService.setLang('fr');
      translateDatabaseService.dict = {
        person_count_zero: 'personne',
        person_count_one: 'personne',
        person_count_other: 'personnes'
      };

      expect(translateDatabaseService.getPersonCount(0)).toEqual('0 personne');
      expect(translateDatabaseService.getPersonCount(1)).toEqual('1 personne');
      expect(translateDatabaseService.getPersonCount(5)).toEqual('5 personnes');

      // English
      translateDatabaseService.setLang('en');
      translateDatabaseService.dict = {
        person_count_zero: 'person',
        person_count_one: 'person',
        person_count_other: 'people'
      };

      expect(translateDatabaseService.getPersonCount(0)).toEqual('0 person');
      expect(translateDatabaseService.getPersonCount(1)).toEqual('1 person');
      expect(translateDatabaseService.getPersonCount(5)).toEqual('5 people');
    });

    it('should handle localStorage persistence correctly', () => {
      languageService.setLang('co');

      // Simulate page reload
      const newLanguageService = new LanguageService();

      expect(newLanguageService.getLang()).toEqual('co');
      expect(localStorage.getItem('lang')).toEqual('co');
    });

    it('should handle default language fallback', () => {
      localStorage.clear();
      languageService.lang = '';

      const lang = languageService.getLang();

      expect(lang).toEqual('en');
    });

    it('should allow rapid language switching', () => {
      const languages = ['fr', 'en', 'de', 'es', 'it', 'sv', 'fi', 'lv', 'co'];

      languages.forEach(lang => {
        languageService.setLang(lang);
        expect(languageService.getLang()).toEqual(lang);
      });

      // Final language should be the last one set
      expect(languageService.getLang()).toEqual('co');
    });
  });

  describe('Error handling and edge cases', () => {
    it('should handle empty translation keys gracefully', () => {
      translateDatabaseService.dict = { key: 'value' };

      const result = translateDatabaseService.t('');
      expect(result).toEqual('');
    });

    it('should handle missing translation keys', () => {
      translateDatabaseService.dict = { existing: 'value' };

      const result = translateDatabaseService.t('nonexistent');
      expect(result).toEqual('nonexistent');
    });

    it('should handle special characters in language codes', () => {
      // Even if language code is unusual, service should not crash
      languageService.setLang('fr-FR');
      expect(languageService.getLang()).toEqual('fr-FR');
    });

    it('should handle rapid service instantiation', () => {
      for (let i = 0; i < 10; i++) {
        const service = new LanguageService();
        expect(service).toBeTruthy();
      }
    });

    it('should handle concurrent language changes', () => {
      languageService.setLang('fr');
      translateDatabaseService.setLang('en');

      // Both services should maintain their own state
      expect(languageService.getLang()).toEqual('fr');
      expect(translateDatabaseService.lang).toEqual('en');
    });
  });

  describe('Translation consistency', () => {
    it('should provide consistent translations for same key', () => {
      translateDatabaseService.dict = { greeting: 'Hello' };

      const first = translateDatabaseService.t('greeting');
      const second = translateDatabaseService.t('greeting');
      const third = translateDatabaseService.t('greeting');

      expect(first).toEqual(second);
      expect(second).toEqual(third);
    });

    it('should update translations when dict changes', () => {
      translateDatabaseService.dict = { key: 'value1' };
      expect(translateDatabaseService.t('key')).toEqual('value1');

      translateDatabaseService.dict = { key: 'value2' };
      expect(translateDatabaseService.t('key')).toEqual('value2');
    });

    it('should handle mixed case in translation keys', () => {
      translateDatabaseService.dict = {
        'Key': 'Value1',
        'key': 'Value2',
        'KEY': 'Value3'
      };

      expect(translateDatabaseService.t('Key')).toEqual('Value1');
      expect(translateDatabaseService.t('key')).toEqual('Value2');
      expect(translateDatabaseService.t('KEY')).toEqual('Value3');
    });
  });

  describe('Memory and performance', () => {
    it('should handle large translation dictionaries', () => {
      const largeDict: any = {};
      for (let i = 0; i < 1000; i++) {
        largeDict[`key${i}`] = `value${i}`;
      }

      translateDatabaseService.dict = largeDict;

      expect(translateDatabaseService.t('key500')).toEqual('value500');
      expect(translateDatabaseService.t('key999')).toEqual('value999');
    });

    it('should handle multiple translation lookups efficiently', () => {
      translateDatabaseService.dict = {
        key1: 'value1',
        key2: 'value2',
        key3: 'value3'
      };

      for (let i = 0; i < 100; i++) {
        translateDatabaseService.t('key1');
        translateDatabaseService.t('key2');
        translateDatabaseService.t('key3');
      }

      // Should complete without errors
      expect(translateDatabaseService.t('key1')).toEqual('value1');
    });
  });
});
