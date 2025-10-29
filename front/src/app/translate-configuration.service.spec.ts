/// <reference types="jasmine" />

import { TranslateConfigurationService } from './translate-configuration.service';
import translations from '../assets/translate/translateConfiguration.json';

describe('TranslateConfigurationService', () => {
  let service: TranslateConfigurationService;
  let originalTranslations: Record<string, Record<string, string>>;
  const expectJasmine = <T>(actual: T) => expect(actual) as unknown as jasmine.Matchers<T>;

  beforeEach(() => {
    service = new TranslateConfigurationService();
    originalTranslations = (service as any).translations;
  });

  afterEach(() => {
    (service as any).translations = originalTranslations;
    service.setLang('fr');
  });

  it('provides French translations by default', () => {
    expectJasmine(service.getLang()).toBe('fr');
    expectJasmine(service.t('geneweb_parameters')).toBe(translations.fr.geneweb_parameters);
  });

  it('switches language using lowercase codes', () => {
    service.setLang('EN');
    expectJasmine(service.getLang()).toBe('en');
    expectJasmine(service.t('geneweb_parameters')).toBe(translations.en.geneweb_parameters);
  });

  it('falls back to French when a key is missing for the active language', () => {
    (service as any).translations = {
      fr: { fallback_key: 'valeur francaise' },
      en: {}
    };

    service.setLang('en');
    expectJasmine(service.t('fallback_key')).toBe('valeur francaise');
  });

  it('returns the key itself when no translation is available', () => {
    (service as any).translations = { fr: {}, en: {} };

    service.setLang('en');
    expectJasmine(service.t('missing_key')).toBe('missing_key');
  });
});