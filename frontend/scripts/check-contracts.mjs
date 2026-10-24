import { readFileSync } from 'node:fs';
import openapiTS, { astToString } from 'openapi-typescript';
const expected = astToString(await openapiTS(new URL('../../shared/openapi.json', import.meta.url)));
const actual = readFileSync(new URL('../src/generated/api.ts', import.meta.url), 'utf8');
// CLI adds a generated-file banner; compare the declarations themselves.
if (actual.slice(actual.indexOf('export interface paths')) !== expected.slice(expected.indexOf('export interface paths'))) {
  throw new Error('Generated TypeScript drift. Run npm run contracts.');
}
console.log('Generated TypeScript synchronized.');
