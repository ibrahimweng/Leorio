// Screenshots rendered screens to PNG, so a change can be looked at before it
// is sent anywhere. Reads <work>/rev/<Name>.html, writes <work>/shot/<Name>.png.
//
//   CHROME=/opt/pw-browsers/chromium SP=<work> node shot.mjs Name [Name...]
import { chromium } from 'playwright-core';
import fs from 'fs';

const SP = process.env.SP, REV = SP + '/rev', OUT = SP + '/shot';
fs.mkdirSync(OUT, { recursive: true });
const names = process.argv.slice(2);
const b = await chromium.launch({ executablePath: process.env.CHROME });
const p = await b.newPage({ viewport: { width: 393, height: 852 }, deviceScaleFactor: 2 });
for (const n of names) {
  await p.goto('file://' + REV + '/' + n + '.html');
  await p.waitForTimeout(220);
  const el = await p.$('x-dc > div');
  await (el || p).screenshot({ path: OUT + '/' + n + '.png' });
  console.log(n);
}
await b.close();
