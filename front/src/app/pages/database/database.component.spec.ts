import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { DatabaseComponent } from './database.component';
import { LanguageService } from '../../languagesService';
import { TranslateDatabaseService } from '../../translate-database.service';
import { of } from 'rxjs';

describe('DatabaseComponent', () => {
  let component: DatabaseComponent;
  let fixture: ComponentFixture<DatabaseComponent>;
  let router: Router;
  let languageService: LanguageService;
  let translateService: TranslateDatabaseService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DatabaseComponent, RouterTestingModule],
      providers: [
        LanguageService,
        TranslateDatabaseService,
        {
          provide: ActivatedRoute,
          useValue: {
            params: of({ dbName: 'TestDB' })
          }
        }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(DatabaseComponent);
    component = fixture.componentInstance;
    router = TestBed.inject(Router);
    languageService = TestBed.inject(LanguageService);
    translateService = TestBed.inject(TranslateDatabaseService);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize with default values', () => {
    expect(component.personCount).toEqual(0);
    expect(component.showLanguageDropdown).toEqual(false);
  });

  it('should load database name from route params', () => {
    component.ngOnInit();
    expect(component.dbName).toEqual('TestDB');
    expect(component.getDatabaseTitle()).toContain('TestDB');
  });

  it('should initialize current language from languageService', () => {
    languageService.setLang('fr');
    const newComponent = new DatabaseComponent(router, TestBed.inject(ActivatedRoute), languageService, translateService);
    expect(newComponent.currentLanguage).toEqual('FR');
  });

  it('should have all supported languages', () => {
    expect(component.languages.length).toEqual(9);
    expect(component.languages).toContain(jasmine.objectContaining({ code: 'en', label: 'English' }));
    expect(component.languages).toContain(jasmine.objectContaining({ code: 'fr', label: 'Français' }));
    expect(component.languages).toContain(jasmine.objectContaining({ code: 'de', label: 'Deutsch' }));
  });

  describe('language dropdown', () => {
    it('should toggle language dropdown', () => {
      expect(component.showLanguageDropdown).toEqual(false);

      component.toggleLanguageDropdown();
      expect(component.showLanguageDropdown).toEqual(true);

      component.toggleLanguageDropdown();
      expect(component.showLanguageDropdown).toEqual(false);
    });

    it('should close dropdown on document click outside', () => {
      component.showLanguageDropdown = true;

      const event = { target: document.createElement('div') } as any;
      component.onDocumentClick(event);

      expect(component.showLanguageDropdown).toEqual(false);
    });

    it('should not close dropdown if clicking inside relative element', () => {
      component.showLanguageDropdown = true;

      const relativeDiv = document.createElement('div');
      relativeDiv.className = 'relative';
      const targetElement = document.createElement('span');
      relativeDiv.appendChild(targetElement);

      const event = { target: targetElement } as any;
      spyOn(targetElement, 'closest').and.returnValue(relativeDiv);

      component.onDocumentClick(event);

      expect(component.showLanguageDropdown).toEqual(true);
    });

    it('should change language and update display', () => {
      spyOn(languageService, 'setLang');
      spyOn(translateService, 'setLang');

      component.changeLanguage('es');

      expect(component.currentLanguage).toEqual('ES');
      expect(languageService.setLang).toHaveBeenCalledWith('es');
      expect(translateService.setLang).toHaveBeenCalledWith('es');
      expect(component.showLanguageDropdown).toEqual(false);
    });

    it('should change language to all supported languages', () => {
      const languages = ['co', 'de', 'en', 'es', 'fr', 'it', 'lv', 'sv', 'fi'];

      languages.forEach(lang => {
        component.changeLanguage(lang);
        expect(component.currentLanguage).toEqual(lang.toUpperCase());
      });
    });
  });

  describe('navigation methods', () => {
    it('should navigate to add-family with dbName', () => {
      spyOn(router, 'navigate');
      component.dbName = 'MyDatabase';

      component.onAddFamily();

      expect(router.navigate).toHaveBeenCalledWith(['/add-family', 'MyDatabase']);
    });

    it('should navigate to add-family without dbName', () => {
      spyOn(router, 'navigate');
      component.dbName = '';

      component.onAddFamily();

      expect(router.navigate).toHaveBeenCalledWith(['/add-family']);
    });

    it('should log when onAddChronicle is called', () => {
      spyOn(console, 'log');

      component.onAddChronicle();

      expect(console.log).toHaveBeenCalledWith('Saisir une chronique');
    });

    it('should log when onAdvancedSearch is called', () => {
      spyOn(console, 'log');

      component.onAdvancedSearch();

      expect(console.log).toHaveBeenCalledWith('Requête évoluée');
    });

    it('should log when onCalendars is called', () => {
      spyOn(console, 'log');

      component.onCalendars();

      expect(console.log).toHaveBeenCalledWith('Calendriers');
    });

    it('should navigate to configuration with dbName', () => {
      const navigateSpy = spyOn(router, 'navigate');
      component.dbName = 'TestDB';

      component.onConfiguration();

      expect(navigateSpy).toHaveBeenCalledWith(['/configuration', 'TestDB']);
    });

    it('should navigate to configuration without dbName', () => {
      const navigateSpy = spyOn(router, 'navigate');
      component.dbName = '';

      component.onConfiguration();

      expect(navigateSpy).toHaveBeenCalledWith(['/configuration']);
    });

    it('should log when onAddNote is called', () => {
      spyOn(console, 'log');

      component.onAddNote();

      expect(console.log).toHaveBeenCalledWith('Ajouter note');
    });
  });

  describe('route parameter handling', () => {
    it('should handle dbName from route params', () => {
      component.ngOnInit();

      expect(component.dbName).toEqual('TestDB');
      expect(component.getDatabaseTitle()).toContain('TestDB');
    });
  });

  describe('person count display', () => {
    it('should display person count correctly', () => {
      component.personCount = 42;
      fixture.detectChanges();

      expect(component.personCount).toEqual(42);
    });

    it('should handle zero person count', () => {
      component.personCount = 0;
      fixture.detectChanges();

      expect(component.personCount).toEqual(0);
    });

    it('should handle large person count', () => {
      component.personCount = 10000;
      fixture.detectChanges();

      expect(component.personCount).toEqual(10000);
    });
  });

  describe('integration with services', () => {
    it('should use translateService for translations', () => {
      translateService.dict = { database: 'Base de données' };

      const translation = translateService.t('database');
      expect(translation).toEqual('Base de données');
    });

    it('should sync language between services', () => {
      component.changeLanguage('it');

      expect(languageService.getLang()).toEqual('it');
      expect(translateService.lang).toEqual('it');
    });
  });
});
