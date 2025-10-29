import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './pages/home/home.component';
import { NothingComponent } from './pages/nothing/nothing.component';
import { ListComponent } from './pages/list/list.component';
import { GwcComponent } from './pages/gwc/gwc.compnent';
import { Ged2GwbComponent } from './pages/ged2Gwb/ged2Gwb.component';
import { TracesComponent } from './pages/traces/traces.component';
import { SimpleComponent } from './pages/simple/simple.component';
import { DatabaseComponent } from './pages/database/database.component';
import { AddFamilyComponent } from './pages/add-family/add-family.component';
import { RenameComponent } from './pages/rename/rename.component';
import { ConfigurationComponent } from './pages/configuration/configuration.component';
import { AuthComponent } from './pages/auth/auth.component';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
    {
        path: '',
        title: 'Connexion',
        component: AuthComponent
    },
    {
        path: 'auth',
        title: 'Connexion',
        component: AuthComponent
    },
    {
        path: 'home',
        title: 'Home',
        component: HomeComponent,
        canActivate: [authGuard]
    },
    {
        path: 'list',
        title: 'List',
        component: ListComponent,
        canActivate: [authGuard]
    },
    {
        path: 'traces',
        title: 'Traces',
        component: TracesComponent,
        canActivate: [authGuard]
    },
    {
        path: 'simple',
        title: 'Simple',
        component: SimpleComponent,
        canActivate: [authGuard]
    },
    {
        path: 'gwc',
        title: 'GWC',
        component: GwcComponent,
        canActivate: [authGuard]
    },
    {
        path: 'ged2Gwb',
        title: 'GED to GWB',
        component: Ged2GwbComponent,
        canActivate: [authGuard]
    },
    {
        path: 'nothingToSeeHere',
        title: 'Nothing to See Here',
        component: NothingComponent,
        canActivate: [authGuard]
    },
    {
        path: 'database/:dbName',
        title: 'Base généalogique',
        component: DatabaseComponent,
        canActivate: [authGuard]
    },
    {
        path: 'database',
        title: 'Base généalogique',
        component: DatabaseComponent,
        canActivate: [authGuard]
    },
    {
        path: 'add-family/:dbName',
        title: 'Ajouter famille',
        component: AddFamilyComponent,
        canActivate: [authGuard]
    },
    {
        path: 'add-family',
        title: 'Ajouter famille',
        component: AddFamilyComponent,
        canActivate: [authGuard]
    },
    {
        path: 'rename',
        title: 'Renommage',
        component: RenameComponent,
        canActivate: [authGuard]
    },
    {
        path: 'configuration/:dbName',
        title: 'Configuration',
        component: ConfigurationComponent,
        canActivate: [authGuard]
    },
    {
        path: 'configuration',
        title: 'Configuration',
        component: ConfigurationComponent,
        canActivate: [authGuard]
    },
    {
        path: '**',
        redirectTo: ''
    }
];

export class AppRoutingModule {}