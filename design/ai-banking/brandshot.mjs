// Cuts the icon sheet brand.py writes into one PNG per size.
//
//   CHROME=/opt/pw-browsers/chromium node brandshot.mjs
import { chromium } from 'playwright-core';
import path from 'path';
import fs from 'fs';

const OUT = path.join(path.dirname(new URL(import.meta.url).pathname), 'brand');
const b = await chromium.launch({ executablePath: process.env.CHROME });
const p = await b.newPage({ viewport: { width: 1400, height: 1400 }, deviceScaleFactor: 1 });
await p.goto('file://' + path.join(OUT, '_sheet.html'));
await p.waitForTimeout(150);
const names = [];
for (const el of await p.$$('.s')) {
  const name = await el.getAttribute('data-name');
  await el.screenshot({ path: path.join(OUT, name + '.png'), omitBackground: true });
  names.push(name);
}
await b.close();
fs.unlinkSync(path.join(OUT, '_sheet.html'));
console.log(names.join(' '));
