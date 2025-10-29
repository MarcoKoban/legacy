import { TestBed } from '@angular/core/testing';
import { TranslateDatabaseService } from './translate-database.service';
import { LanguageService } from './languagesService';

describe('TranslateDatabaseService', () => {
  let service: TranslateDatabaseService;
  let languageService: LanguageService;

  beforeEach(() => {
    localStorage.clear();

    TestBed.configureTestingModule({
      providers: [TranslateDatabaseService, LanguageService]
    });

    languageService = TestBed.inject(LanguageService);
    service = TestBed.inject(TranslateDatabaseService);
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should initialize with default language from languageService', () => {
    languageService.setLang('en');
    const newService = new TranslateDatabaseService(languageService);
    expect(newService.lang).toEqual('en');
  });

  it('should fallback to "fr" if unsupported language', () => {
    languageService.setLang('zh'); // unsupported language
    const newService = new TranslateDatabaseService(languageService);
    expect(newService.lang).toEqual('fr');
  });

  it('should translate a key using the dict', () => {
    service.dict = {
      database: 'Base de données',
      person: 'Personne'
    };

    const result = service.t('database');
    expect(result).toEqual('Base de données');
  });

  it('should return the key itself if translation not found', () => {
    service.dict = { database: 'Database' };

    const result = service.t('unknownKey');
    expect(result).toEqual('unknownKey');
  });

  it('should change language with setLang', () => {
    service.setLang('en');
    expect(service.lang).toEqual('en');

    service.setLang('de');
    expect(service.lang).toEqual('de');
  });

  describe('getPersonCount', () => {
    beforeEach(() => {
      service.dict = {
        person_count_zero: 'personne',
        person_count_one: 'personne',
        person_count_other: 'personnes'
      };
    });

    it('should return correct format for zero persons', () => {
      const result = service.getPersonCount(0);
      expect(result).toEqual('0 personne');
    });

    it('should return correct format for one person', () => {
      const result = service.getPersonCount(1);
      expect(result).toEqual('1 personne');
    });

    it('should return correct format for multiple persons', () => {
      const result = service.getPersonCount(5);
      expect(result).toEqual('5 personnes');
    });

    it('should handle large numbers', () => {
      const result = service.getPersonCount(1000);
      expect(result).toEqual('1000 personnes');
    });

    it('should handle two persons', () => {
      const result = service.getPersonCount(2);
      expect(result).toEqual('2 personnes');
    });

    it('should fallback to default if dict keys are missing', () => {
      service.dict = {};
      const result = service.getPersonCount(5);
      expect(result).toContain('5');
    });
  });

  describe('language switching', () => {
    it('should update dict when changing language to French', () => {
      service.setLang('fr');
      expect(service.lang).toEqual('fr');
      expect(service.dict).toBeDefined();
    });

    it('should update dict when changing language to English', () => {
      service.setLang('en');
      expect(service.lang).toEqual('en');
      expect(service.dict).toBeDefined();
    });

    it('should update dict when changing language to German', () => {
      service.setLang('de');
      expect(service.lang).toEqual('de');
      expect(service.dict).toBeDefined();
    });

    it('should persist language change across multiple calls', () => {
      service.setLang('es');
      expect(service.lang).toEqual('es');

      service.setLang('it');
      expect(service.lang).toEqual('it');

      service.setLang('fr');
      expect(service.lang).toEqual('fr');
    });
  });

  describe('edge cases', () => {
    it('should handle empty dict gracefully', () => {
      service.dict = {};
      const result = service.t('anyKey');
      expect(result).toEqual('anyKey');
    });

    it('should handle special characters in translation keys', () => {
      service.dict = {
        'key.with.dots': 'Value',
        'key-with-dashes': 'Another Value'
      };

      expect(service.t('key.with.dots')).toEqual('Value');
      expect(service.t('key-with-dashes')).toEqual('Another Value');
    });

    it('should handle negative person count', () => {
      service.dict = {
        person_count_zero: 'personne',
        person_count_one: 'personne',
        person_count_other: 'personnes'
      };

      const result = service.getPersonCount(-1);
      expect(result).toContain('-1');
    });

    it('should handle person count with empty dict', () => {
      service.dict = {};
      const result = service.getPersonCount(3);
      expect(result).toContain('3');
    });
  });
});
