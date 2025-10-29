/// <reference types="jasmine" />

import { TranslateAddFamilyService } from './translate-add-family.service';
import translations from '../assets/translate/translateAddFamily.json';

describe('TranslateAddFamilyService', () => {
  let service: TranslateAddFamilyService;
  let originalTranslations: Record<string, Record<string, string>>;
  const expectJasmine = <T>(actual: T) => expect(actual) as unknown as jasmine.Matchers<T>;

  beforeEach(() => {
    service = new TranslateAddFamilyService();
    originalTranslations = (service as any).translations;
  });

  afterEach(() => {
    (service as any).translations = originalTranslations;
    service.setLang('fr');
  });

  it('defaults to French translations', () => {
    expectJasmine(service.getLang()).toBe('fr');
    expectJasmine(service.t('add_family_title')).toBe(translations.fr.add_family_title);
  });

  it('switches language while normalizing the code', () => {
    service.setLang('EN');
    expectJasmine(service.getLang()).toBe('en');
    expectJasmine(service.t('add_family_title')).toBe(translations.en.add_family_title);
  });

  it('falls back to French when a language is not supported', () => {
    service.setLang('pt');
    expectJasmine(service.t('add_family_title')).toBe(translations.fr.add_family_title);
  });

  it('falls back to French when the key is missing for the active language', () => {
    (service as any).translations = {
      fr: { fallback_key: 'cle francaise' },
      en: {}
    };

    service.setLang('en');
    expectJasmine(service.t('fallback_key')).toBe('cle francaise');
  });

  it('returns the key when no translation exists anywhere', () => {
    (service as any).translations = { fr: {}, en: {} };

    service.setLang('en');
    expectJasmine(service.t('missing_key')).toBe('missing_key');
  });
});