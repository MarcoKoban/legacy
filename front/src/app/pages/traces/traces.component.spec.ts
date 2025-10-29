import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { By } from '@angular/platform-browser';

import { TracesComponent } from './traces.component';
import { TranslateTracesService } from './translateTraces.service';

describe('TracesComponent', () => {
  let fixture: ComponentFixture<TracesComponent>;
  let component: TracesComponent;
  let router: Router;

  const mockTranslate = {
    t: (k: string) => {
      const map: Record<string, string> = {
        title: 'Traces Title',
        commLogContent: 'Comm Log',
        gwsetupLogContent: 'GWSetup Log',
        no_commLog: 'No comm log available',
        no_gwsetupLog: 'No gwsetup log available',
        welcome: 'Welcome',
        footer: 'Footer'
      };
      return map[k] ?? k;
    }
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TracesComponent, RouterTestingModule.withRoutes([])],
      providers: [{ provide: TranslateTracesService, useValue: mockTranslate }]
    }).compileComponents();

    router = TestBed.inject(Router);
  });

  afterEach(() => {
    // restore any overwritten globals
    if ((window as any)._originalLocation) {
      (window as any).location = (window as any)._originalLocation;
      delete (window as any)._originalLocation;
    }
    // ensure fetch restored if necessary
    if ((window as any).fetch && (window as any).fetch.and && (window as any).fetch.and.originalFn) {
      (window as any).fetch.and.callThrough();
    }
  });

  function mockFetchResponses(commResp: any, gwResp: any) {
    // jasmine spy on fetch
    spyOn(window as any, 'fetch').and.callFake((url: string) => {
      if (url.includes('comm.log')) return Promise.resolve(commResp);
      if (url.includes('gwsetup.log')) return Promise.resolve(gwResp);
      return Promise.reject(new Error('unknown'));
    });
  }

//   it('should create and render title and logs when fetch returns text', async () => {
//     const commResp = { ok: true, text: () => Promise.resolve('COMM LOG CONTENT\n') };
//     const gwResp = { ok: true, text: () => Promise.resolve('GWSETUP LOG CONTENT\n') };

//     mockFetchResponses(commResp, gwResp);

//     fixture = TestBed.createComponent(TracesComponent);
//     component = fixture.componentInstance;
//     fixture.detectChanges();
//     await fixture.whenStable();
//     fixture.detectChanges();

//     expect(component).toBeTruthy();
//     // logs populated
//     expect(component.commLog).toContain('COMM LOG CONTENT');
//     expect(component.gwsetupLog).toContain('GWSETUP LOG CONTENT');

//     // template shows title
//     const titleEl = fixture.debugElement.query(By.css('h1')).nativeElement as HTMLElement;
//     expect(titleEl.textContent).toContain('Traces Title');

//     // pre elements contain the logs (with the "- " prefix)
//     const pres = fixture.debugElement.queryAll(By.css('pre'));
//     expect(pres.length).toBeGreaterThanOrEqual(2);
//     expect(pres[0].nativeElement.textContent).toContain('COMM LOG CONTENT');
//     expect(pres[1].nativeElement.textContent).toContain('GWSETUP LOG CONTENT');
//   });

//   it('should set no_commLog / no_gwsetupLog when fetch returns ok but empty text', async () => {
//     const commResp = { ok: true, text: () => Promise.resolve('   \n') }; // empty after trim
//     const gwResp = { ok: true, text: () => Promise.resolve('') };

//     mockFetchResponses(commResp, gwResp);

//     fixture = TestBed.createComponent(TracesComponent);
//     component = fixture.componentInstance;
//     fixture.detectChanges();
//     await fixture.whenStable();
//     fixture.detectChanges();

//     expect(component.commLog).toBe(mockTranslate.t('no_commLog'));
//     expect(component.gwsetupLog).toBe(mockTranslate.t('no_gwsetupLog'));

//     const pres = fixture.debugElement.queryAll(By.css('pre'));
//     expect(pres[0].nativeElement.textContent).toContain(mockTranslate.t('no_commLog'));
//     expect(pres[1].nativeElement.textContent).toContain(mockTranslate.t('no_gwsetupLog'));
//   });

  it('should set no_commLog / no_gwsetupLog when fetch response is not ok', async () => {
    const commResp = { ok: false, text: () => Promise.resolve('ignored') };
    const gwResp = { ok: false, text: () => Promise.resolve('ignored') };

    mockFetchResponses(commResp, gwResp);

    fixture = TestBed.createComponent(TracesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();

    expect(component.commLog).toBe(mockTranslate.t('no_commLog'));
    expect(component.gwsetupLog).toBe(mockTranslate.t('no_gwsetupLog'));
  });

//   it('should handle fetch rejection gracefully', async () => {
//     spyOn(window as any, 'fetch').and.callFake(() => Promise.reject(new Error('network')));

//     fixture = TestBed.createComponent(TracesComponent);
//     component = fixture.componentInstance;
//     fixture.detectChanges();
//     await fixture.whenStable();
//     fixture.detectChanges();

//     expect(component.commLog).toBe(mockTranslate.t('no_commLog'));
//     expect(component.gwsetupLog).toBe(mockTranslate.t('no_gwsetupLog'));
//   });

  it('goToLink should navigate to nothingToSeeHere when url is empty', () => {
    fixture = TestBed.createComponent(TracesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    spyOn(router, 'navigate').and.returnValue(Promise.resolve(true) as any);

    const evt = { preventDefault: () => {} } as any;
    component.goToLink(evt, '');
    expect(router.navigate).toHaveBeenCalledWith(['/nothingToSeeHere']);
  });

  it('goToLink should navigate to a route when url is internal', () => {
    fixture = TestBed.createComponent(TracesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    spyOn(router, 'navigate').and.returnValue(Promise.resolve(true) as any);

    const evt = { preventDefault: () => {} } as any;
    component.goToLink(evt, 'list');
    expect(router.navigate).toHaveBeenCalledWith(['list']);
  });
});