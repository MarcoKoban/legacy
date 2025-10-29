import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { HomeComponent } from './home.component';
import { LanguageService } from '../../languagesService';
import { TranslateService } from '../../translate.service';
import { AuthService } from '../../services/auth.service';
import { HttpClientTestingModule } from '@angular/common/http/testing';

const expectJasmine = <T>(actual: T) => ((globalThis as any).expect(actual)) as jasmine.Matchers<T>;

class MockLanguageService {
  private lang = 'en';
  setLang(l: string) { this.lang = l; }
  getLang() { return this.lang; }
}

class MockTranslateService {
  dict: Record<string, string> = {
    title: 'GeneWeb Home',
    consult: 'Consult',
    footer: 'Footer text'
  };
  lang = 'en';
  t(key: string): string {
    return this.dict[key] || key;
  }
}

class MockAuthService {
  logout() { }
}

describe('HomeComponent', () => {
  let component: HomeComponent;
  let fixture: ComponentFixture<HomeComponent>;
  let router: Router;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HomeComponent, RouterTestingModule.withRoutes([]), HttpClientTestingModule],
      providers: [
        { provide: LanguageService, useClass: MockLanguageService },
        { provide: TranslateService, useClass: MockTranslateService },
        { provide: AuthService, useClass: MockAuthService }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(HomeComponent);
    component = fixture.componentInstance;
    router = TestBed.inject(Router);
    spyOn(router, 'navigate').and.returnValue(Promise.resolve(true) as any);
  });

  it('should create', () => {
    expectJasmine(component).toBeTruthy();
  });

  it('should have 9 languages defined', () => {
    expectJasmine(component.languages.length).toBe(9);
  });

  it('should open URL in new tab with openNewTab', () => {
    const openSpy = spyOn(window, 'open').and.returnValue(null);
    component.openNewTab('https://example.com');

    expectJasmine(openSpy).toHaveBeenCalledWith('https://example.com', '_blank');
  });

  it('should navigate to nothingToSeeHere when goToLink gets empty URL', () => {
    const event = { preventDefault: () => {} } as any;
    component.goToLink(event, '');

    expectJasmine(router.navigate).toHaveBeenCalledWith(['/nothingToSeeHere']);
  });

  it('should navigate to provided path in goToLink', () => {
    const event = { preventDefault: () => {} } as any;
    component.goToLink(event, '/database/test');

    expectJasmine(router.navigate).toHaveBeenCalledWith(['/database/test']);
  });
});
