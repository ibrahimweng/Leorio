// Contrast of every piece of text against what is actually behind it.
//
//   CHROME=/opt/pw-browsers/chromium node figma/contrast.mjs .. [out.json]
//
// Thresholds are Apple's, which are stricter than reading WCAG loosely: up to
// 17pt needs 4.5:1 and 18pt and over needs 3:1. Everything this product sets is
// 12, 14, 20 or 32, so only 20 and 32 get the lower bar.
//
// It walks up from each run for the first opaque background and composites any
// translucent layers it passes on the way, because a sheet sits on a scrim and
// a scrim sits on a page. Where something in that stack paints a gradient or an
// image it reports `gradient` and does not guess: an earlier version of this
// took the fallback white and produced fourteen impossible white-on-white
// failures at a ratio of 1.00.
import { chromium } from 'playwright-core';
import fs from 'fs'; import path from 'path';
const DIR = process.argv[2] || '.', OUTF = process.argv[3];
const b = await chromium.launch({ executablePath: process.env.CHROME });
const p = await b.newPage({ viewport: { width: 393, height: 852 } });
const rows = [];
for (const f of fs.readdirSync(DIR).filter(x => x.endsWith('.dc.html')).sort()) {
  const name = f.replace('.dc.html', '');
  if (name.startsWith('Iconsheet')) continue;
  const html = fs.readFileSync(path.join(DIR, f), 'utf8').replace(/\{\{accent\}\}/g, '#213ACA');
  await p.setContent(html, { waitUntil: 'load' });
  const got = await p.evaluate(() => {
    const parse = c => { const m = c.match(/rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\)/);
      return m ? [+m[1], +m[2], +m[3], m[4] === undefined ? 1 : +m[4]] : null; };
    const over = (fg, bg) => fg.slice(0, 3).map((v, i) => v * fg[3] + bg[i] * (1 - fg[3]));
    const lum = c => { const s = c.map(v => { v /= 255;
      return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); });
      return 0.2126 * s[0] + 0.7152 * s[1] + 0.0722 * s[2]; };
    const bgOf = el => {
      let stack = [], n = el;
      while (n && n !== document.documentElement) {
        const cs = getComputedStyle(n);
        if (cs.backgroundImage && cs.backgroundImage !== 'none') return null;
        const c = parse(cs.backgroundColor);
        if (c && c[3] > 0) { stack.push(c); if (c[3] === 1) break; }
        n = n.parentElement;
      }
      let base = [255, 255, 255];
      for (let i = stack.length - 1; i >= 0; i--) base = over(stack[i], base);
      return base;
    };
    const out = [];
    for (const el of document.querySelectorAll('span,div')) {
      const txt = Array.from(el.childNodes).filter(n => n.nodeType === 3)
                    .map(n => n.textContent.trim()).join('');
      if (!txt) continue;
      const cs = getComputedStyle(el);
      const fg = parse(cs.color); if (!fg) continue;
      const fs_ = parseFloat(cs.fontSize), fw = parseInt(cs.fontWeight) || 400;
      const bg = bgOf(el);
      if (!bg) { out.push({ t: txt.slice(0, 28), fs: fs_, fw, gradient: 1 }); continue; }
      const fgc = over(fg, bg), l1 = lum(fgc), l2 = lum(bg);
      out.push({ t: txt.slice(0, 28), fs: fs_, fw,
                 ratio: Math.round(((Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05)) * 100) / 100,
                 fg: fgc.map(Math.round), bg: bg.map(Math.round) });
    }
    return out;
  });
  for (const g of got) rows.push({ screen: name, ...g });
}
await b.close();
const need = fs_ => fs_ >= 18 ? 3.0 : 4.5;
const flat = rows.filter(r => !r.gradient);
const fail = flat.filter(r => r.ratio < need(r.fs));
const by = {};
for (const r of fail) {
  const k = '#' + r.fg.map(v => v.toString(16).padStart(2, '0')).join('') +
            ' on #' + r.bg.map(v => v.toString(16).padStart(2, '0')).join('') +
            '  ' + r.ratio + ':1 needs ' + need(r.fs);
  by[k] = (by[k] || 0) + 1;
}
console.log(rows.length + ' runs, ' + rows.filter(r => r.gradient).length + ' on a gradient, '
          + fail.length + ' of ' + flat.length + ' failing');
for (const k of Object.keys(by).sort((a, c) => by[c] - by[a]).slice(0, 12))
  console.log('  ' + String(by[k]).padStart(5) + '  ' + k);
if (OUTF) fs.writeFileSync(OUTF, JSON.stringify(rows));
