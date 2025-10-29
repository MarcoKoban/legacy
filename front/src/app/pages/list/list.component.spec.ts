/// <reference types="jasmine" />

import { ComponentFixture, TestBed, fakeAsync, tick, waitForAsync } from '@angular/core/testing';
import { Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { By } from '@angular/platform-browser';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { HttpClientModule } from '@angular/common/http';

import { ListComponent } from './list.component';
import { LanguageService } from '../../languagesService';
import { TranslateListService } from './translateList.service';

const expectJasmine = <T>(actual: T) => ((globalThis as any).expect(actual)) as jasmine.Matchers<T>;

// Use the real API URL from environment
const API_URL = 'https://geneweb-api.fly.dev/api/v1';

// Mock HttpClient pour éviter les problèmes d'interception
import { HttpClient } from '@angular/common/http';
import { of, throwError } from 'rxjs';

describe('ListComponent', () => {
  let fixture: ComponentFixture<ListComponent>;
  let component: ListComponent;
  let router: Router;
  let httpMock: HttpTestingController;

  const mockTranslate = {
    t: (key: string) => {
      const map: Record<string, string> = {
        title: 'Test Title',
        firstText: 'First text',
        secondText: 'Second text',
        footer: 'Footer text'
      };
      return map[key] ?? key;
    }
  };

  const mockLangService = {
    lang: 'en',
    getLang: () => 'en'
  };

  beforeEach(async () => {
    localStorage.clear();
    localStorage.setItem('auth_token', 'test-token');

    await TestBed.configureTestingModule({
      imports: [ListComponent, RouterTestingModule.withRoutes([]), HttpClientTestingModule],
      providers: [
        { provide: TranslateListService, useValue: mockTranslate },
        { provide: LanguageService, useValue: mockLangService }
      ]
    })
    .overrideComponent(ListComponent, {
      remove: { imports: [HttpClientModule] },
      add: { imports: [HttpClientTestingModule] }
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListComponent);
    component = fixture.componentInstance;
    router = TestBed.inject(Router);
    httpMock = TestBed.inject(HttpTestingController);

    spyOn(router, 'navigate').and.returnValue(Promise.resolve(true) as any);
  });

  afterEach(() => {
    httpMock.verify(); // Ensure no outstanding HTTP requests
    localStorage.clear();
  });

  it('should navigate to external URLs by calling navigateExternal', () => {
    const navigateExternalSpy = spyOn<any>(component, 'navigateExternal');
    const externalUrl = 'https://example.com/path';

    component.goToLink({ preventDefault: () => {} } as any, externalUrl);

    expectJasmine(navigateExternalSpy).toHaveBeenCalledWith(externalUrl);
  });

  it('should set loading=true and clear errorMessage when loadDatabases is called', () => {
    component.errorMessage = 'Previous error';
    component.loading = false;

    component.loadDatabases();

    // Verify immediate state changes (loading flag is set synchronously before HTTP call)
    expectJasmine(component.loading).toBeTrue();
    expectJasmine(component.errorMessage).toBe('');
  });

  it('should create', () => {
    expectJasmine(component).toBeTruthy();
  });

  it('should render translated title', () => {
    fixture.detectChanges();
    const reqs = httpMock.match(`${API_URL}/database/databases`);
    reqs.forEach(req => req.flush({ databases: [] }));

    const h1 = fixture.debugElement.query(By.css('h1')).nativeElement as HTMLHeadingElement;
    expectJasmine(h1.textContent?.trim()).toBe('Test Title');
  });

  it('should show first and second translated texts', () => {
    fixture.detectChanges();
    const reqs = httpMock.match(`${API_URL}/database/databases`);
    reqs.forEach(req => req.flush({ databases: [] }));

    const container = fixture.nativeElement as HTMLElement;
    expectJasmine(container.textContent).toContain('First text');
    expectJasmine(container.textContent).toContain('Second text');
  });

  it('should navigate to "nothingToSeeHere" when first link (gwd_info) clicked', () => {
    fixture.detectChanges();
    const reqs = httpMock.match(`${API_URL}/database/databases`);
    reqs.forEach(req => req.flush({ databases: [] }));

    const anchors = fixture.debugElement.queryAll(By.css('a'));
    // first anchor is gwd_info -> goToLink($event) with default '' -> navigate to /nothingToSeeHere
    const firstAnchor = anchors[0];
    firstAnchor.triggerEventHandler('click', { preventDefault: () => {} });
    expectJasmine(router.navigate).toHaveBeenCalledWith(['/nothingToSeeHere']);
  });

  it('should navigate to "/" when welcome link clicked', () => {
    fixture.detectChanges();
    const reqs = httpMock.match(`${API_URL}/database/databases`);
    reqs.forEach(req => req.flush({ databases: [] }));

    const anchors = fixture.debugElement.queryAll(By.css('a'));
    // second anchor has url '/home'
    const secondAnchor = anchors[1];
    secondAnchor.triggerEventHandler('click', { preventDefault: () => {} });
    expectJasmine(router.navigate).toHaveBeenCalledWith(['/home']);
  });

  describe('component state', () => {
    it('should initialize with empty databases array', () => {
      expectJasmine(component.databases).toEqual([]);
    });

    it('should initialize with loading false', () => {
      expectJasmine(component.loading).toEqual(false);
    });

    it('should initialize with empty error message', () => {
      expectJasmine(component.errorMessage).toEqual('');
    });
  });

  describe('navigation to database', () => {
    beforeEach(() => {
      fixture.detectChanges();
      const reqs = httpMock.match(`${API_URL}/database/databases`);
      reqs.forEach(req => req.flush({ databases: [] }));
    });

    it('should navigate to specific database', () => {
      let called = false;
      const event = {
        preventDefault: () => { called = true; }
      };
      component.goToDatabase(event as any, 'MyDatabase');

      expectJasmine(called).toEqual(true);
      expectJasmine(router.navigate).toHaveBeenCalledWith(['/database', 'MyDatabase']);
    });

    it('should handle database name with special characters', () => {
      let called = false;
      const event = {
        preventDefault: () => { called = true; }
      };
      component.goToDatabase(event as any, 'Test-DB_123');

      expectJasmine(called).toEqual(true);
      expectJasmine(router.navigate).toHaveBeenCalledWith(['/database', 'Test-DB_123']);
    });
  });

  describe('goToLink method', () => {
    beforeEach(() => {
      fixture.detectChanges();
      const reqs = httpMock.match(`${API_URL}/database/databases`);
      reqs.forEach(req => req.flush({ databases: [] }));
    });

    it('should navigate to nothingToSeeHere for empty URL', () => {
      let preventDefaultCalled = false;
      const event = {
        preventDefault: () => { preventDefaultCalled = true; }
      };

      component.goToLink(event as any, '');

      expectJasmine(preventDefaultCalled).toEqual(true);
      expectJasmine(router.navigate).toHaveBeenCalledWith(['/nothingToSeeHere']);
    });

    it('should navigate to relative URL', () => {
      let preventDefaultCalled = false;
      const event = {
        preventDefault: () => { preventDefaultCalled = true; }
      };

      component.goToLink(event as any, '/some-path');

      expectJasmine(preventDefaultCalled).toEqual(true);
      expectJasmine(router.navigate).toHaveBeenCalledWith(['/some-path']);
    });

    it('should redirect https links using window location', () => {
      const preventDefault = jasmine.createSpy('preventDefault');
      const navigateSpy = router.navigate as jasmine.Spy;
      const externalSpy = spyOn<any>(component, 'navigateExternal').and.stub();

      component.goToLink({ preventDefault } as any, 'https://example.com/path');

      expectJasmine(preventDefault).toHaveBeenCalled();
      expectJasmine(navigateSpy).not.toHaveBeenCalledWith(['/nothingToSeeHere']);
      expectJasmine(externalSpy).toHaveBeenCalledWith('https://example.com/path');
    });
  });
});