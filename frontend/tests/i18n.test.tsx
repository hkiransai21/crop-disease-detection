import { describe, it, expect } from 'vitest';
import i18n from '../src/i18n/i18n';
import en from '../src/i18n/locales/en.json';
import hi from '../src/i18n/locales/hi.json';
import te from '../src/i18n/locales/te.json';
import ta from '../src/i18n/locales/ta.json';
import kn from '../src/i18n/locales/kn.json';

describe('Frontend i18n Localization Integrity', () => {
  const bundles: Record<string, any> = { en, hi, te, ta, kn };
  const languages = Object.keys(bundles);

  it('supports only five supported languages', () => {
    expect(languages).toEqual(['en', 'hi', 'te', 'ta', 'kn']);
  });

  function getKeys(obj: any, prefix = ''): string[] {
    let keys: string[] = [];
    for (const k of Object.keys(obj)) {
      const full = prefix ? `${prefix}.${k}` : k;
      if (typeof obj[k] === 'object' && obj[k] !== null && !Array.isArray(obj[k])) {
        keys = keys.concat(getKeys(obj[k], full));
      } else {
        keys.push(full);
      }
    }
    return keys;
  }

  const enKeys = getKeys(en);

  languages.forEach((lang) => {
    it(`locale '${lang}' contains non-empty translations for all core UI keys`, () => {
      const langBundle = bundles[lang];
      const langKeys = getKeys(langBundle);

      expect(langKeys.length).toBeGreaterThanOrEqual(enKeys.length);
      enKeys.forEach((key) => {
        const parts = key.split('.');
        let curr = langBundle;
        for (const p of parts) {
          expect(curr).toBeDefined();
          curr = curr[p];
        }
        expect(typeof curr).toBe('string');
        expect((curr as string).trim().length).toBeGreaterThan(0);
      });
    });
  });

  it('allows dynamic language switching via i18n.changeLanguage', async () => {
    await i18n.changeLanguage('te');
    expect(i18n.language).toBe('te');
    expect(i18n.t('nav.diagnose')).toBe('పంట నిర్ధారణ');

    await i18n.changeLanguage('hi');
    expect(i18n.language).toBe('hi');
    expect(i18n.t('nav.diagnose')).toBe('फसल जांचें');

    await i18n.changeLanguage('en');
    expect(i18n.language).toBe('en');
    expect(i18n.t('nav.diagnose')).toBe('Diagnose Crop');
  });
});
