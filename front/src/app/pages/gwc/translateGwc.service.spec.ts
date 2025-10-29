import { TestBed } from '@angular/core/testing';
import { TranslateGwcService } from './translateGwc.service';
import { LanguageService } from '../../languagesService';

const expectJasmine = <T>(actual: T) => ((globalThis as any).expect(actual)) as jasmine.Matchers<T>;

class MockLanguageService {
  private lang = 'en';
  setLang(l: string) { this.lang = l; }
  getLang() { return this.lang; }
}

describe('TranslateGwcService', () => {
  let service: TranslateGwcService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        TranslateGwcService,
        { provide: LanguageService, useClass: MockLanguageService }
      ]
    });
    service = TestBed.inject(TranslateGwcService);
  });

  it('should be created', () => {
    expectJasmine(service).toBeTruthy();
  });

  it('should return the key if not found in dictionary', () => {
    const result = service.t('non_existent_key');
    expectJasmine(result).toBe('non_existent_key');
  });

  it('should return translated value if key exists', () => {
    service.dict = { 'test_key': 'test_value' };
    const result = service.t('test_key');
    expectJasmine(result).toBe('test_value');
  });

  it('should have default language as en', () => {
    expectJasmine(service.lang).toBe('en');
  });
});
