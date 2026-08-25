// Where every control that leads somewhere sits, and where it leads.
//
// The Figma prototype needs its links on the buttons and rows rather than on
// whole screens, and the markup already knows which element leads where: every
// one of them carries data-go, and the ones the prototype handles itself carry
// data-act. What Figma needs on top of that is a way to find the same element
// again in a tree that has no attributes on it.
//
// The answer is the box. Figma's nodes were built from these measurements, so
// an element and its node agree on x, y, width and height to within a pixel,
// and matching on all four is specific enough to be safe.
//
//   sh figma/rev.sh $SP
//   SP=$SP node figma/hotspots.mjs        # $SP/figma/hotspots.json
//
// The result is keyed by screen: [x, y, w, h, where] per control. `where` is a
// screen name, or `back`, or an act prefixed with @, which means the prototype
// does something in place and the Figma version should simply go on.
import { chromium } from 'playwright-core';
import fs from 'fs';

const SP = process.env.SP;
const REV = SP + '/rev';
const only = process.argv.slice(2);
const names = fs.readdirSync(REV).filter(f => f.endsWith('.html')).map(f => f.replace('.html', ''))
  .filter(n => !only.length || only.indexOf(n) >= 0);

// Seven screens are the founder's home with something on top of it. In Figma
// that backdrop is an instance of their component, laid out differently, so
// anything measured up there would match nothing or, worse, the wrong thing.
const OVERLAY = new Set(['Ask', 'AskReq', 'AskSvc', 'Typed', 'TypedAsk', 'TypedBuy',
                         'Receive', 'Actions', 'Draft']);
const SHEET_TOP = 440;

const b = await chromium.launch({ executablePath: process.env.CHROME || '/opt/pw-browsers/chromium' });
const out = {};
for (const n of names) {
  const pg = await b.newPage({ viewport: { width: 393, height: 852 } });
  await pg.goto('file://' + fs.realpathSync(REV + '/' + n + '.html'));
  await pg.waitForTimeout(120);
  const spots = await pg.evaluate(() => {
    const root = document.querySelector('x-dc > div') || document.body.firstElementChild;
    const rb = root.getBoundingClientRect();
    const seen = [];
    for (const el of document.querySelectorAll('[data-go], [data-act]')) {
      const go = el.dataset.go || '';
      const act = el.dataset.act || '';
      if (act === 'soon' && !go) continue;
      if (go === 'soon') continue;
      const r = el.getBoundingClientRect();
      if (r.width < 6 || r.height < 6) continue;
      seen.push([Math.round(r.left - rb.left), Math.round(r.top - rb.top),
                 Math.round(r.width), Math.round(r.height), go || ('@' + act)]);
    }
    return seen;
  });
  await pg.close();
  const keep = OVERLAY.has(n) ? spots.filter(s => s[1] >= SHEET_TOP) : spots;
  if (keep.length) out[n] = keep;
}
await b.close();
fs.mkdirSync(SP + '/figma', { recursive: true });
fs.writeFileSync(SP + '/figma/hotspots.json', JSON.stringify(out));
console.log('screens', Object.keys(out).length,
            'controls', Object.values(out).reduce((a, v) => a + v.length, 0));
