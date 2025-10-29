/// <reference types="jasmine" />

import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { HttpClient, HttpClientModule, HttpErrorResponse } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { of, throwError } from 'rxjs';

import { RenameComponent } from './rename.component';
import { LanguageService } from '../../languagesService';
import { TranslateRenameService } from '../../translate-rename.service';

// Use the real API URL from environment
const API_URL = 'https://geneweb-api.fly.dev/api/v1';
const RENAME_API = `${API_URL}/database/databases`;
const expectJasmine = <T>(actual: T) => expect(actual) as unknown as jasmine.Matchers<T>;

describe('RenameComponent', () => {
  let fixture: ComponentFixture<RenameComponent>;
  let component: RenameComponent;
  let router: Router;
  let httpSpy: jasmine.SpyObj<HttpClient>;
  let alertSpy: jasmine.Spy;

  beforeEach(async () => {
    localStorage.clear();
    localStorage.setItem('lang', 'fr');
    localStorage.setItem('auth_token', 'test-token');

    httpSpy = jasmine.createSpyObj<HttpClient>('HttpClient', ['get', 'put']);

    await TestBed.configureTestingModule({
      imports: [RenameComponent, RouterTestingModule.withRoutes([]), FormsModule],
      providers: [
        LanguageService,
        TranslateRenameService,
        { provide: HttpClient, useValue: httpSpy }
      ]
    })
      .overrideComponent(RenameComponent, {
        remove: { imports: [HttpClientModule] }
      })
      .compileComponents();

    fixture = TestBed.createComponent(RenameComponent);
    component = fixture.componentInstance;
    router = TestBed.inject(Router);

    spyOn(router, 'navigate').and.returnValue(Promise.resolve(true) as any);
    alertSpy = spyOn(window, 'alert');
  });

  afterEach(() => {
    httpSpy.get.calls.reset();
    httpSpy.put.calls.reset();
    localStorage.clear();
  });

  function initWithLoad(body: any = { databases: [] }, options: { error?: boolean } = {}) {
    if (options.error) {
      httpSpy.get.and.returnValue(
        throwError(() => new HttpErrorResponse({
          status: 500,
          statusText: 'Server Error',
          error: body
        }))
      );
    } else {
      httpSpy.get.and.returnValue(of(body));
    }

    fixture.detectChanges();
  }

  it('loads databases and selects the first entry by default', () => {
    initWithLoad({ databases: [{ name: 'Alpha' }, { name: 'Beta' }] });

    expectJasmine(httpSpy.get).toHaveBeenCalledWith(RENAME_API, { headers: { Authorization: 'Bearer test-token' } });
    expectJasmine(component.loading).toBeFalse();
    expectJasmine(component.databases.length).toBe(2);
    expectJasmine(component.selectedDb).toBe('Alpha');
    expectJasmine(component.newName).toBe('Alpha');
  });

  it('surfaces an error message when the list fails to load', () => {
    initWithLoad({}, { error: true });

    expectJasmine(component.loading).toBeFalse();
    expectJasmine(component.errorMessage).toBe(component.translate.t('error_loading'));
  });

  it('keeps newName in sync with the selected database', () => {
    initWithLoad({ databases: [{ name: 'Alpha' }, { name: 'Beta' }] });

    component.selectedDb = 'Beta';
    component.onDatabaseChange();

    expectJasmine(component.newName).toBe('Beta');
  });

  it('warns when rename is triggered without selection or target name', () => {
    initWithLoad();

    component.selectedDb = '';
    component.newName = '';

    component.onRename();

    expectJasmine(alertSpy).toHaveBeenCalledWith(component.translate.t('alert_missing'));
  });

  it('warns when attempting to reuse the current database name', () => {
    initWithLoad({ databases: [{ name: 'Alpha' }] });

    component.selectedDb = 'Alpha';
    component.newName = 'Alpha';

    component.onRename();

    expectJasmine(alertSpy).toHaveBeenCalledWith(component.translate.t('alert_same_name'));
  });

  it('sends the rename request and navigates home on success', () => {
    initWithLoad({ databases: [{ name: 'Alpha' }] });

    httpSpy.put.and.returnValue(of({ ok: true }));

    component.selectedDb = 'Alpha';
    component.newName = 'Renamed';

    component.onRename();

    expectJasmine(httpSpy.put).toHaveBeenCalledWith(
      `${RENAME_API}/Alpha/rename`,
      { new_name: 'Renamed', rename_files: false },
      { headers: { Authorization: 'Bearer test-token' } }
    );
    expectJasmine(alertSpy).toHaveBeenCalledWith(
      component.translate.t('alert_success', { oldName: 'Alpha', newName: 'Renamed' })
    );
    expectJasmine(router.navigate).toHaveBeenCalledWith(['/home']);
  });

  it('surfaces the backend error message when rename fails with detail', () => {
    initWithLoad({ databases: [{ name: 'Alpha' }] });
    httpSpy.put.and.returnValue(
      throwError(() => new HttpErrorResponse({
        status: 400,
        statusText: 'Bad Request',
        error: { detail: 'Already exists' }
      }))
    );

    component.selectedDb = 'Alpha';
    component.newName = 'Renamed';

    component.onRename();

    expectJasmine(httpSpy.put).toHaveBeenCalled();
    expectJasmine(alertSpy).toHaveBeenCalledWith('Already exists');
  });

  it('falls back to translated error when backend provides no detail', () => {
    initWithLoad({ databases: [{ name: 'Alpha' }] });
    httpSpy.put.and.returnValue(
      throwError(() => new HttpErrorResponse({ status: 500, statusText: 'Server Error', error: {} }))
    );

    component.selectedDb = 'Alpha';
    component.newName = 'Renamed';

    component.onRename();

    expectJasmine(httpSpy.put).toHaveBeenCalled();
    expectJasmine(alertSpy).toHaveBeenCalledWith(component.translate.t('alert_error'));
  });

  it('updates language related state when changeLanguage is called', () => {
    initWithLoad();

    component.changeLanguage('en');

    const languageService = TestBed.inject(LanguageService);
    const translateService = TestBed.inject(TranslateRenameService);
    expectJasmine(component.currentLanguage).toBe('EN');
    expectJasmine(languageService.getLang()).toBe('en');
    expectJasmine(translateService.lang).toBe('en');
  });

  it('navigates back to home when goBack is invoked', () => {
    initWithLoad();

    component.goBack();

    expectJasmine(router.navigate).toHaveBeenCalledWith(['/home']);
  });
});
