import { LanguageService } from './languagesService';

describe('LanguageService', () => {
  let service: LanguageService;

  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    service = new LanguageService();
  });

  afterEach(() => {
    // Clean up localStorage after each test
    localStorage.clear();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should initialize with empty lang', () => {
    expect(service.lang).toBe('');
  });

  it('should set language and store in localStorage', () => {
    const testLang = 'fr';
    service.setLang(testLang);
    
    expect(service.lang).toBe(testLang);
    expect(localStorage.getItem('lang')).toBe(testLang);
  });

  it('should get language from property if already set', () => {
    service.lang = 'es';
    const result = service.getLang();
    
    expect(result).toBe('es');
  });

  it('should get language from localStorage if property is empty', () => {
    localStorage.setItem('lang', 'de');
    service.lang = ''; // Reset to empty
    
    const result = service.getLang();
    
    expect(result).toBe('de');
    expect(service.lang).toBe('de'); // Should update the property
  });

  it('should default to "en" if no language is set anywhere', () => {
    service.lang = '';
    // localStorage is already empty from beforeEach
    
    const result = service.getLang();
    
    expect(result).toBe('en');
    expect(service.lang).toBe('en');
  });

  it('should update both property and localStorage when setting language', () => {
    service.setLang('it');
    
    expect(service.lang).toBe('it');
    expect(localStorage.getItem('lang')).toBe('it');
    
    // Change to another language
    service.setLang('sv');
    
    expect(service.lang).toBe('sv');
    expect(localStorage.getItem('lang')).toBe('sv');
  });

  it('should handle multiple language changes correctly', () => {
    // Set initial language
    service.setLang('fr');
    expect(service.getLang()).toBe('fr');
    
    // Change language
    service.setLang('co');
    expect(service.getLang()).toBe('co');
    
    // Verify localStorage is updated
    expect(localStorage.getItem('lang')).toBe('co');
  });
});