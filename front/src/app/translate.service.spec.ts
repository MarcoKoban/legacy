import { TestBed } from '@angular/core/testing';
import { TranslateService } from './translate.service';
import { LanguageService } from './languagesService';

describe('TranslateService', () => {
  let service: TranslateService;
  let languageService: LanguageService;

  beforeEach(() => {
    localStorage.clear();

    TestBed.configureTestingModule({
      providers: [TranslateService, LanguageService]
    });

    languageService = TestBed.inject(LanguageService);
    service = TestBed.inject(TranslateService);
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should initialize with default language "en"', () => {
    expect(service.lang).toBe('en');
  });

  it('should translate a key using the dict', () => {
    service.dict = { hello: 'Hello World', goodbye: 'Goodbye' };

    const result = service.t('hello');
    expect(result).toBe('Hello World');
  });

  it('should return the key itself if translation not found', () => {
    service.dict = { hello: 'Hello World' };

    const result = service.t('unknownKey');
    expect(result).toBe('unknownKey');
  });

  it('should handle empty dict gracefully', () => {
    service.dict = {};

    const result = service.t('anyKey');
    expect(result).toBe('anyKey');
  });

  it('should update language from languageService', () => {
    languageService.setLang('fr');
    expect(languageService.getLang()).toBe('fr');
  });

  describe('translation with different languages', () => {
    it('should handle French translations', () => {
      service.lang = 'fr';
      service.dict = {
        title: 'Gestion et création',
        welcome: 'Bienvenue'
      };

      expect(service.t('title')).toBe('Gestion et création');
      expect(service.t('welcome')).toBe('Bienvenue');
    });

    it('should handle German translations', () => {
      service.lang = 'de';
      service.dict = {
        title: 'Verwaltung und Erstellung',
        welcome: 'Willkommen'
      };

      expect(service.t('title')).toBe('Verwaltung und Erstellung');
      expect(service.t('welcome')).toBe('Willkommen');
    });

    it('should handle Spanish translations', () => {
      service.lang = 'es';
      service.dict = {
        title: 'Gestión y creación',
        welcome: 'Bienvenido'
      };

      expect(service.t('title')).toBe('Gestión y creación');
      expect(service.t('welcome')).toBe('Bienvenido');
    });

    it('should handle Italian translations', () => {
      service.lang = 'it';
      service.dict = {
        title: 'Gestione e creazione',
        welcome: 'Benvenuto'
      };

      expect(service.t('title')).toBe('Gestione e creazione');
      expect(service.t('welcome')).toBe('Benvenuto');
    });
  });

  describe('edge cases', () => {
    it('should handle special characters in keys', () => {
      service.dict = {
        'key.with.dots': 'Value with dots',
        'key-with-dashes': 'Value with dashes',
        'key_with_underscores': 'Value with underscores'
      };

      expect(service.t('key.with.dots')).toBe('Value with dots');
      expect(service.t('key-with-dashes')).toBe('Value with dashes');
      expect(service.t('key_with_underscores')).toBe('Value with underscores');
    });

    it('should handle empty string keys', () => {
      service.dict = { '': 'Empty key value' };

      expect(service.t('')).toBe('Empty key value');
    });

    it('should return key when dict is empty object', () => {
      service.dict = {};
      expect(service.t('missing')).toBe('missing');
    });

    it('should handle multiple sequential translations', () => {
      service.dict = {
        first: 'First Value',
        second: 'Second Value',
        third: 'Third Value'
      };

      expect(service.t('first')).toBe('First Value');
      expect(service.t('second')).toBe('Second Value');
      expect(service.t('third')).toBe('Third Value');
    });
  });
});
