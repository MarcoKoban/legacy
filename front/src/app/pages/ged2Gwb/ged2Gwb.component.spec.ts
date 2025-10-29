import { TestBed, ComponentFixture } from '@angular/core/testing';
import { Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { By } from '@angular/platform-browser';

import { Ged2GwbComponent } from './ged2Gwb.component';
import { TranslateGed2GwbService } from './translateGed2Gwb.service';

describe('Ged2GwbComponent', () => {
  let fixture: ComponentFixture<Ged2GwbComponent>;
  let component: Ged2GwbComponent;
  let router: Router;

  const mockTranslate = {
    t: (k: string) => {
      const map: Record<string, string> = {
        title: 'Test Title',
        selectSourceFile: 'Select a GEDCOM file',
        enterDbFolder: 'Enter DB folder',
        enterDbName: 'Enter DB name',
        selectOptions: 'Select options',
        creationPeople: 'Creation people',
        firstNameOption: 'First name option',
        publicName: 'Public name',
        GEDCOMStandard: 'GEDCOM Standard',
        year: 'For these dates, extract only the "year" part.',
        dayMonthYear: 'Interpret as day/month/year.',
        monthDayYear: 'Interpret as month/day/year.',
        GEDCOM: 'Follow GEDCOM header',
        Ansel: 'ANSEL encoding',
        Ansi: 'ANSI encoding',
        ASCII: 'ASCII encoding',
        MSDOS: 'MSDOS encoding',
        footer: 'Footer text',
        thenClickButton: 'Then click the button'
      };
      return map[k] ?? k;
    }
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Ged2GwbComponent, RouterTestingModule.withRoutes([])],
      providers: [{ provide: TranslateGed2GwbService, useValue: mockTranslate }]
    }).compileComponents();

    fixture = TestBed.createComponent(Ged2GwbComponent);
    component = fixture.componentInstance;
    router = TestBed.inject(Router);
    spyOn(router, 'navigate').and.returnValue(Promise.resolve(true) as any);
    fixture.detectChanges();
  });

  it('should create the component and have empty logs', () => {
    expect(component).toBeTruthy();
    expect(component.commLog).toBe('');
    expect(component.gwsetupLog).toBe('');
  });

  it('should render translated title', () => {
    const h1 = fixture.debugElement.query(By.css('h1')).nativeElement as HTMLHeadingElement;
    expect(h1.textContent).toContain('Test Title');
  });

  it('should render form inputs and option groups', () => {
    const inputBd = fixture.debugElement.query(By.css('input[name="bd"]'));
    const inputO = fixture.debugElement.query(By.css('input[name="o"]'));
    expect(inputBd).toBeTruthy();
    expect(inputO).toBeTruthy();

    const checkboxes = fixture.debugElement.queryAll(By.css('input[type="checkbox"]'));
    expect(checkboxes.length).toBeGreaterThan(0);

    const dateRadios = fixture.debugElement.queryAll(By.css('input[name="date_format"]'));
    expect(dateRadios.length).toBe(3);

    const charsetRadios = fixture.debugElement.queryAll(By.css('input[name="lang"]'));
    expect(charsetRadios.length).toBeGreaterThanOrEqual(1);
  });

  it('should have default date radio "y" checked', () => {
    const radioY = fixture.debugElement.query(By.css('input[name="date_format"][value="y"]')).nativeElement as HTMLInputElement;
    expect(radioY.checked).toBeTrue();
  });

  it('should have default charset "gedcom" checked', () => {
    const charset = fixture.debugElement.query(By.css('input[name="lang"][value="gedcom"]')).nativeElement as HTMLInputElement;
    expect(charset.checked).toBeTrue();
  });

  it('goToLink should navigate for internal empty url to nothingToSeeHere', () => {
    const evt = { preventDefault: () => {} } as any;
    component.goToLink(evt, '');
    expect(router.navigate).toHaveBeenCalledWith(['/nothingToSeeHere']);
  });

  it('goToLink should navigate to given route', () => {
    const evt = { preventDefault: () => {} } as any;
    component.goToLink(evt, 'list');
    expect(router.navigate).toHaveBeenCalledWith(['list']);
  });
});