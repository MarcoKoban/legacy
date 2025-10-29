// src/test.ts
/***************************************************************************************************
 * Zone JS est requis par les tests Angular.
 */

// Polyfill pour les erreurs Karma liées à global/importMeta
if (typeof (globalThis as any).global === 'undefined') {
  (globalThis as any).global = globalThis;
}

if (typeof import.meta === 'undefined') {
  // @ts-ignore
  globalThis.importMeta = {};
}

import 'zone.js/testing';
import { getTestBed } from '@angular/core/testing';
import {
  BrowserDynamicTestingModule,
  platformBrowserDynamicTesting
} from '@angular/platform-browser-dynamic/testing';

// Initialise l’environnement de test Angular
getTestBed().initTestEnvironment(
  BrowserDynamicTestingModule,
  platformBrowserDynamicTesting(),
);
