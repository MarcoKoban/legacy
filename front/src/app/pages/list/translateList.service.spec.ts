import { TestBed } from '@angular/core/testing';
import { TranslateListService } from './translateList.service';
import { LanguageService } from '../../languagesService';

const expectJasmine = <T>(actual: T) => ((globalThis as any).expect(actual)) as jasmine.Matchers<T>;

class MockLanguageService {
  private lang = 'en';
  setLang(l: string) { this.lang = l; }
  getLang() { return this.lang; }
}

describe('TranslateListService', () => {
  let service: TranslateListService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        TranslateListService,
        { provide: LanguageService, useClass: MockLanguageService }
      ]
    });
    service = TestBed.inject(TranslateListService);
  });

  it('should be created', () => {
    expectJasmine(service).toBeTruthy();
  });

  it('should return the key if not found in dictionary', () => {
    const result = service.t('non_existent_key');
    expectJasmine(result).toBe('non_existent_key');
  });

  it('should return translated value if key exists', () => {
    // Set a value in the dict manually for testing
    service.dict = { 'test_key': 'test_value' };
    const result = service.t('test_key');
    expectJasmine(result).toBe('test_value');
  });

  it('should have default language as en', () => {
    expectJasmine(service.lang).toBe('en');
  });
});
