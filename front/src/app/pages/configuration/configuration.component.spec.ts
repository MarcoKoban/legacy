import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';
import { BehaviorSubject } from 'rxjs';

import { ConfigurationComponent } from './configuration.component';
import { LanguageService } from '../../languagesService';
import { TranslateConfigurationService } from '../../translate-configuration.service';

class MockActivatedRoute {
  private readonly paramsSubject = new BehaviorSubject<Record<string, any>>({});
  readonly params = this.paramsSubject.asObservable();

  setParams(params: Record<string, any>) {
    this.paramsSubject.next(params);
  }
}

class MockLocation {
  back = jasmine.createSpy('back');
}

describe('ConfigurationComponent', () => {
  let fixture: ComponentFixture<ConfigurationComponent>;
  let component: ConfigurationComponent;
  let router: Router;
  let route: MockActivatedRoute;
  let location: MockLocation;
  let languageService: LanguageService;
  let translateService: TranslateConfigurationService;

  beforeEach(async () => {
    localStorage.clear();
    localStorage.setItem('lang', 'fr');

    route = new MockActivatedRoute();
    location = new MockLocation();

    await TestBed.configureTestingModule({
      imports: [ConfigurationComponent, RouterTestingModule.withRoutes([])],
      providers: [
        { provide: ActivatedRoute, useValue: route },
        { provide: Location, useValue: location },
        LanguageService,
        TranslateConfigurationService
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(ConfigurationComponent);
    component = fixture.componentInstance;
    router = TestBed.inject(Router);
    languageService = TestBed.inject(LanguageService);
    translateService = TestBed.inject(TranslateConfigurationService);

    spyOn(router, 'navigate').and.returnValue(Promise.resolve(true) as any);
  });

  afterEach(() => {
    localStorage.clear();
  });

  function triggerRoute(params: Record<string, any>) {
    route.setParams(params);
    fixture.detectChanges();
  }

  it('initialises configuration when a database name is provided', () => {
    triggerRoute({ dbName: 'SampleDB' });

    expect(component.dbName).toBe('SampleDB');
    expect(component.configFile).toBe('SampleDB.gwf');
    expect(component.prefix).toBe('SampleDB?lang=fr&');
    expect(component.bvarList).toContain('prefix: SampleDB?lang=fr&');
  });

  it('falls back to default prefix when no database name is present', () => {
    triggerRoute({});

    expect(component.dbName).toBe('');
    expect(component.prefix).toBe('base?lang=fr&');
    expect(component.bvarList).toContain('prefix: base?lang=fr&');
  });

  it('updates language related state when changeLanguage is called', () => {
    triggerRoute({ dbName: 'SampleDB' });

    component.changeLanguage('en');

    expect(component.currentLanguage).toBe('EN');
    expect(languageService.getLang()).toBe('en');
    expect(component.langFull).toBe('english (en)');
    expect(component.prefix).toBe('SampleDB?lang=en&');
    expect(component.bvarList).toContain('prefix: SampleDB?lang=en&');
    expect(component.showLanguageDropdown).toBeFalse();
  });

  it('updates prefix and language labels when no database is selected', () => {
    triggerRoute({});

    component.changeLanguage('de');

    expect(component.prefix).toBe('base?lang=de&');
    expect(component.langFull).toBe('deutsch (de)');
  });

  it('toggles the language dropdown visibility', () => {
    triggerRoute({});

    expect(component.showLanguageDropdown).toBeFalse();
    component.toggleLanguageDropdown();
    expect(component.showLanguageDropdown).toBeTrue();
    component.toggleLanguageDropdown();
    expect(component.showLanguageDropdown).toBeFalse();
  });

  it('closes the dropdown when clicking outside', () => {
    triggerRoute({});
    component.showLanguageDropdown = true;

    const outsideClick = new MouseEvent('click', { bubbles: true });
    Object.defineProperty(outsideClick, 'target', { value: document.createElement('div') });

    component.onDocumentClick(outsideClick);
    expect(component.showLanguageDropdown).toBeFalse();
  });

  it('keeps the dropdown open when clicking inside the language dropdown', () => {
    triggerRoute({});
    component.showLanguageDropdown = true;

    const wrapper = document.createElement('div');
    wrapper.className = 'language-dropdown';
    const child = document.createElement('span');
    wrapper.appendChild(child);

    const insideClick = new MouseEvent('click', { bubbles: true });
    Object.defineProperty(insideClick, 'target', { value: child });

    component.onDocumentClick(insideClick);
    expect(component.showLanguageDropdown).toBeTrue();
  });

  it('navigates back via the Location service', () => {
    triggerRoute({});

    component.goBack();
    expect(location.back).toHaveBeenCalled();
  });

  it('navigates to the database route when dbName is present', () => {
    triggerRoute({ dbName: 'SampleDB' });
    (router.navigate as jasmine.Spy).calls.reset();

    component.goHome();
    expect(router.navigate).toHaveBeenCalledWith(['/database', 'SampleDB']);
  });

  it('navigates to the root when no dbName is present', () => {
    triggerRoute({});
    (router.navigate as jasmine.Spy).calls.reset();

    component.goHome();
    expect(router.navigate).toHaveBeenCalledWith(['/']);
  });

  it('includes build information from translate service', () => {
    triggerRoute({});

    expect(translateService.getLang()).toBe('fr');
    expect(component.branchName).toBeTruthy();
    expect(component.commitId).toBeTruthy();
  });
});
