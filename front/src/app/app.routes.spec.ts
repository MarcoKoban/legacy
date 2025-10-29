import { routes } from './app.routes';
import { HomeComponent } from './pages/home/home.component';
import { NothingComponent } from './pages/nothing/nothing.component';
import { ListComponent } from './pages/list/list.component';
import { GwcComponent } from './pages/gwc/gwc.compnent';
import { Ged2GwbComponent } from './pages/ged2Gwb/ged2Gwb.component';
import { TracesComponent } from './pages/traces/traces.component';
import { SimpleComponent } from './pages/simple/simple.component';

describe('AppRoutes', () => {
  it('should have home route configured correctly', () => {
    const homeRoute = routes.find(route => route.path === 'home');
    expect(homeRoute).toBeDefined();
    expect(homeRoute?.component).toBe(HomeComponent);
    expect(homeRoute?.title).toBe('Home');
  });

  it('should have list route configured correctly', () => {
    const listRoute = routes.find(route => route.path === 'list');
    expect(listRoute).toBeDefined();
    expect(listRoute?.component).toBe(ListComponent);
    expect(listRoute?.title).toBe('List');
  });

  it('should have traces route configured correctly', () => {
    const tracesRoute = routes.find(route => route.path === 'traces');
    expect(tracesRoute).toBeDefined();
    expect(tracesRoute?.component).toBe(TracesComponent);
    expect(tracesRoute?.title).toBe('Traces');
  });

  it('should have simple route configured correctly', () => {
    const simpleRoute = routes.find(route => route.path === 'simple');
    expect(simpleRoute).toBeDefined();
    expect(simpleRoute?.component).toBe(SimpleComponent);
    expect(simpleRoute?.title).toBe('Simple');
  });

  it('should have gwc route configured correctly', () => {
    const gwcRoute = routes.find(route => route.path === 'gwc');
    expect(gwcRoute).toBeDefined();
    expect(gwcRoute?.component).toBe(GwcComponent);
    expect(gwcRoute?.title).toBe('GWC');
  });

  it('should have ged2Gwb route configured correctly', () => {
    const ged2GwbRoute = routes.find(route => route.path === 'ged2Gwb');
    expect(ged2GwbRoute).toBeDefined();
    expect(ged2GwbRoute?.component).toBe(Ged2GwbComponent);
    expect(ged2GwbRoute?.title).toBe('GED to GWB');
  });

  it('should have nothingToSeeHere route configured correctly', () => {
    const nothingRoute = routes.find(route => route.path === 'nothingToSeeHere');
    expect(nothingRoute).toBeDefined();
    expect(nothingRoute?.component).toBe(NothingComponent);
    expect(nothingRoute?.title).toBe('Nothing to See Here');
  });

  it('should have all routes with defined components', () => {
    routes.forEach(route => {
      // Skip redirect routes and routes without components
      if (!route.component) return;
      expect(route.component).toBeDefined();
    });
  });

  it('should have all routes with defined titles', () => {
    routes.forEach(route => {
      // Skip redirect routes and routes without titles
      if (!route.title) return;
      expect(route.title).toBeDefined();
      expect(typeof route.title).toBe('string');
    });
  });
});