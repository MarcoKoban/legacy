import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { By } from '@angular/platform-browser';

import { SimpleComponent } from './simple.component';
import { TranslateSimpleService } from './translateSimple.service';

describe('SimpleComponent', () => {
  let fixture: ComponentFixture<SimpleComponent>;
  let component: SimpleComponent;
  let router: Router;

  const mockTranslate = {
    t: (key: string) => {
      const map: Record<string, string> = {
        title: 'Test Title',
        firstLine: 'First line text',
        firstButton: 'First button label',
        SecondLine: 'Second line text',
        secondeButton: 'Submit',
        footer: 'Footer text'
      };
      return map[key] ?? key;
    }
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SimpleComponent, RouterTestingModule.withRoutes([])],
      providers: [{ provide: TranslateSimpleService, useValue: mockTranslate }]
    }).compileComponents();

    fixture = TestBed.createComponent(SimpleComponent);
    component = fixture.componentInstance;
    router = TestBed.inject(Router);
    spyOn(router, 'navigate').and.returnValue(Promise.resolve(true) as any);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render translated title', () => {
    const h1 = fixture.debugElement.query(By.css('h1')).nativeElement as HTMLHeadingElement;
    expect(h1.textContent?.trim()).toBe('Test Title');
  });

  it('should render input "o" with default value', () => {
    const input = fixture.debugElement.query(By.css('input[name="o"]')).nativeElement as HTMLInputElement;
    expect(input).toBeTruthy();
    expect(input.value).toBe('base');
  });

  it('should toggle reorg checkbox', () => {
    const checkboxDe = fixture.debugElement.query(By.css('input#reorgMode'));
    expect(checkboxDe).toBeTruthy();
    const checkbox = checkboxDe.nativeElement as HTMLInputElement;

    // initial unchecked
    expect(checkbox.checked).toBeFalse();

    // click to check
    checkbox.click();
    fixture.detectChanges();
    expect(checkbox.checked).toBeTrue();

    // click to uncheck
    checkbox.click();
    fixture.detectChanges();
    expect(checkbox.checked).toBeFalse();
  });

  it('should render submit button with translated label', () => {
    const btn = fixture.debugElement.query(By.css('button[type="submit"]')).nativeElement as HTMLButtonElement;
    expect(btn).toBeTruthy();
    expect(btn.textContent?.trim()).toBe('Submit');
  });

  it('goToLink should navigate to nothingToSeeHere when url is empty', () => {
    const evt = { preventDefault: () => {} } as any;
    component.goToLink(evt, '');
    expect(router.navigate).toHaveBeenCalledWith(['/nothingToSeeHere']);
  });

  it('goToLink should navigate to route when url is internal', () => {
    const evt = { preventDefault: () => {} } as any;
    component.goToLink(evt, 'list');
    expect(router.navigate).toHaveBeenCalledWith(['list']);
  });
});