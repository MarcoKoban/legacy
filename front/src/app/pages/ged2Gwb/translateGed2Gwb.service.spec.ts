import { TestBed } from '@angular/core/testing';
import { TranslateGed2GwbService } from './translateGed2Gwb.service';
import { LanguageService } from '../../languagesService';

const expectJasmine = <T>(actual: T) => ((globalThis as any).expect(actual)) as jasmine.Matchers<T>;

class MockLanguageService {
  private lang = 'en';
  setLang(l: string) { this.lang = l; }
  getLang() { return this.lang; }
}

describe('TranslateGed2GwbService', () => {
  let service: TranslateGed2GwbService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        TranslateGed2GwbService,
        { provide: LanguageService, useClass: MockLanguageService }
      ]
    });
    service = TestBed.inject(TranslateGed2GwbService);
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
