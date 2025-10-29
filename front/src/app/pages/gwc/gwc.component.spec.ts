import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { By } from '@angular/platform-browser';

import { GwcComponent } from './gwc.compnent';
import { TranslateGwcService } from './translateGwc.service';

describe('GwcComponent', () => {
  let fixture: ComponentFixture<GwcComponent>;
  let component: GwcComponent;
  let router: Router;

  const mockTranslate = {
    t: (k: string) => {
      const map: Record<string, string> = {
        title: 'Test Title',
        selectSourceFile: 'Select a GEDCOM file',
        selectSourceOrBrowse: 'Select source or browse',
        orProvideDirectly: 'Or provide directly',
        enterDbFolder: 'Enter DB folder',
        defaultDot: 'Default: .',
        enterDbName: 'Enter DB name',
        deducedFromSource: 'Deduced from source',
        selectOptions: 'Select options',
        displayStats: 'Display stats',
        noCheckConsistency: 'No consistency check',
        endWithConsang: 'End with consang',
        deleteIfExists: 'Delete if exists',
        deleteGwo: 'Delete GWO',
        reorgMode: 'Reorg mode',
        thenClickButton: 'Then click the button',
        footer: 'Footer text',
        note: 'Note',
        noteText: 'Some important note'
      };
      return map[k] ?? k;
    }
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GwcComponent, RouterTestingModule.withRoutes([])],
      providers: [{ provide: TranslateGwcService, useValue: mockTranslate }]
    }).compileComponents();

    fixture = TestBed.createComponent(GwcComponent);
    component = fixture.componentInstance;
    router = TestBed.inject(Router);
    spyOn(router, 'navigate').and.returnValue(Promise.resolve(true) as any);
    fixture.detectChanges();
  });

  it('should create the component', () => {
    expect(component).toBeTruthy();
    expect(component.commLog).toBeDefined();
    expect(component.gwsetupLog).toBeDefined();
  });

  it('should render the translated title in header', () => {
    const h1 = fixture.debugElement.query(By.css('h1')).nativeElement as HTMLHeadingElement;
    expect(h1.textContent?.trim()).toBe('Test Title');
  });

  it('should render form inputs for fname, bd and o', () => {
    const fname = fixture.debugElement.query(By.css('input[name="fname"]'));
    const bd = fixture.debugElement.query(By.css('input[name="bd"]'));
    const o = fixture.debugElement.query(By.css('input[name="o"]'));

    expect(fname).toBeTruthy();
    expect(bd).toBeTruthy();
    expect(o).toBeTruthy();
  });

  it('should render several option checkboxes', () => {
    const checkboxes = fixture.debugElement.queryAll(By.css('input[type="checkbox"]'));
    expect(checkboxes.length).toBeGreaterThanOrEqual(5);
  });

  it('should render submit button with label', () => {
    const button = fixture.debugElement.query(By.css('button[type="submit"]')).nativeElement as HTMLButtonElement;
    expect(button).toBeTruthy();
    expect(button.textContent?.toLowerCase()).toContain('ok');
  });

  it('goToLink navigates to nothingToSeeHere on empty url', () => {
    const evt = { preventDefault: () => {} } as any;
    component.goToLink(evt, '');
    expect(router.navigate).toHaveBeenCalledWith(['/nothingToSeeHere']);
  });

  it('goToLink navigates to provided internal route', () => {
    const evt = { preventDefault: () => {} } as any;
    component.goToLink(evt, 'list');
    expect(router.navigate).toHaveBeenCalledWith(['list']);
  });
});