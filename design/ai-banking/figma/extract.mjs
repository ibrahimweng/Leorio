// Walks each rendered screen and writes a compact node list per screen.
// Geometry and style come from the browser's own computed values, so what
// lands in Figma is what the screen actually renders, not a re-reading of
// the source.
import { chromium } from 'playwright-core';
import fs from 'fs';

const SP = process.env.SP;
const REV = SP + '/rev';
const OUT = SP + '/figma';
fs.mkdirSync(OUT, { recursive: true });

const ORDER = ['Main','Actions','Receive','Ask','Answer','Pay','Done','History','Settings',
               'Services','Airtime','PowerPay','Power','Bills','Loan','Card','Goal','Rules'];

const EXTRACT = () => {
  const root = document.querySelector('x-dc > div');
  const R = root.getBoundingClientRect();
  const out = [];
  const rx = v => Math.round((v - R.left) * 100) / 100;
  const ry = v => Math.round((v - R.top) * 100) / 100;
  const rw = v => Math.round(v * 100) / 100;

  function col(s) {
    if (!s) return null;
    let r, g, b, a = 1;
    const cm = s.match(/color\(srgb\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)(?:\s*\/\s*([\d.]+))?/);
    if (cm) { r = +cm[1] * 255; g = +cm[2] * 255; b = +cm[3] * 255; if (cm[4] !== undefined) a = +cm[4]; }
    else {
      const m = s.match(/rgba?\(([^)]+)\)/);
      if (!m) return null;
      const p = m[1].split(',').map(x => parseFloat(x));
      r = p[0]; g = p[1]; b = p[2]; a = p.length > 3 ? p[3] : 1;
    }
    if (!(a > 0)) return null;
    const h = [r, g, b].map(v => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, '0')).join('');
    return a < 1 ? h + '|' + Math.round(a * 1000) / 1000 : h;
  }

  function splitTop(s) {
    const parts = []; let d = 0, cur = '';
    for (const ch of s) {
      if (ch === '(') d++;
      if (ch === ')') d--;
      if (ch === ',' && d === 0) { parts.push(cur); cur = ''; } else cur += ch;
    }
    if (cur.trim()) parts.push(cur);
    return parts.map(p => p.trim()).filter(Boolean);
  }

  function shadow(p) {
    const cm = p.match(/(rgba?\([^)]*\)|color\(srgb[^)]*\))/);
    const c = col(cm ? cm[1] : null);
    const nums = p.replace(/(rgba?\([^)]*\)|color\(srgb[^)]*\))/, '')
      .replace(/inset/, '').trim().split(/\s+/).map(parseFloat).filter(v => !isNaN(v));
    return { c: c || '000000|0.2', x: nums[0] || 0, y: nums[1] || 0, b: nums[2] || 0, s: nums[3] || 0 };
  }

  function gradient(bi) {
    const m = bi.match(/^linear-gradient\((.*)\)$/s);
    if (!m) return null;
    const parts = splitTop(m[1]);
    let deg = 180;
    if (/deg$/.test(parts[0])) deg = parseFloat(parts.shift());
    else if (/^to\s/.test(parts[0])) {
      const to = parts.shift();
      deg = { 'to top': 0, 'to right': 90, 'to bottom': 180, 'to left': 270 }[to.trim()] ?? 180;
    }
    const stops = parts.map((p, i) => {
      const cm2 = p.match(/(rgba?\([^)]*\)|color\(srgb[^)]*\)|#[0-9a-fA-F]{3,8})/);
      const pos = p.match(/([\d.]+)%\s*$/);
      return { c: col(cm2 ? cm2[1] : null) || 'ffffff|0', p: pos ? +pos[1] / 100 : i / Math.max(1, parts.length - 1) };
    });
    return { deg, stops };
  }

  function typo(cs) {
    return {
      fs: Math.round(parseFloat(cs.fontSize) * 100) / 100,
      fw: parseInt(cs.fontWeight) || 400,
      it: cs.fontStyle === 'italic' ? 1 : 0,
      c: col(cs.color),
      lh: cs.lineHeight === 'normal' ? 0 : Math.round(parseFloat(cs.lineHeight) * 100) / 100,
      ls: Math.round((parseFloat(cs.letterSpacing) || 0) * 100) / 100,
      ta: cs.textAlign
    };
  }
  const sameTypo = (a, b) => a.fs === b.fs && a.fw === b.fw && a.it === b.it && a.c === b.c;

  function pushText(str, b, T, op) {
    const s = str.replace(/\s+/g, ' ');
    if (!s.trim()) return;
    if (!(b.width > 0) || !(b.height > 0)) return;
    // Figma's metrics run a hair wider than the browser's, so a single line
    // pinned to a measured width re-wraps. Only text that already wrapped
    // gets a fixed width; everything else is left to size itself.
    const lh = T.lh || T.fs * 1.35;
    const n = { t: 1, x: rx(b.left), y: ry(b.top), w: Math.ceil(b.width) + 2, h: Math.ceil(b.height),
                s, fs: T.fs, fw: T.fw, c: T.c || '000000' };
    if (b.height > lh * 1.5) n.ml = 1;
    if (T.it) n.i = 1;
    if (T.lh) n.lh = T.lh;
    if (T.ls) n.ls = T.ls;
    if (T.ta === 'center' || T.ta === 'right') n.ta = T.ta;
    if (op < 1) n.o = Math.round(op * 100) / 100;
    out.push(n);
  }

  function walk(el, inheritedOp) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return;
    const op = (parseFloat(cs.opacity) || 0) * inheritedOp;
    if (op <= 0.01) return;
    const tag = el.tagName.toLowerCase();

    if (tag === 'svg') {
      const b = el.getBoundingClientRect();
      if (!(b.width > 0)) return;
      const cc = (col(cs.color) || '000000').split('|')[0];
      out.push({ t: 2, x: rx(b.left), y: ry(b.top), w: rw(b.width), h: rw(b.height),
                 s: el.outerHTML.replace(/currentColor/g, '#' + cc), o: op < 1 ? Math.round(op * 100) / 100 : undefined });
      return;
    }

    const bg = col(cs.backgroundColor);
    const bi = (cs.backgroundImage && cs.backgroundImage !== 'none') ? cs.backgroundImage : null;
    const bw = ['Top', 'Right', 'Bottom', 'Left'].map(s => Math.round((parseFloat(cs['border' + s + 'Width']) || 0) * 100) / 100);
    const shRaw = (cs.boxShadow && cs.boxShadow !== 'none') ? cs.boxShadow : null;
    const bfRaw = (cs.backdropFilter && cs.backdropFilter !== 'none') ? cs.backdropFilter
                : (cs.webkitBackdropFilter && cs.webkitBackdropFilter !== 'none') ? cs.webkitBackdropFilter : null;

    if (bg || bi || bw.some(v => v > 0) || shRaw || bfRaw) {
      const b = el.getBoundingClientRect();
      if (b.width > 0.5 && b.height > 0.5) {
        const n = { t: 0, x: rx(b.left), y: ry(b.top), w: rw(b.width), h: rw(b.height) };
        if (bg) n.bg = bg;
        if (bi) { const g = gradient(bi); if (g) n.g = g; }
        const rr = [cs.borderTopLeftRadius, cs.borderTopRightRadius, cs.borderBottomRightRadius, cs.borderBottomLeftRadius]
          .map(v => Math.min(parseFloat(v) || 0, Math.min(b.width, b.height) / 2));
        if (rr.some(v => v > 0)) n.r = rr.map(v => Math.round(v * 100) / 100);
        if (bw.some(v => v > 0)) {
          n.sw = bw; n.sc = col(cs.borderTopColor) || '000000';
          if (cs.borderTopStyle === 'dashed') n.sd = 1;
        }
        if (shRaw) n.sh = splitTop(shRaw).map(shadow);
        if (bfRaw) { const m = bfRaw.match(/blur\(([\d.]+)px\)/); if (m) n.bl = +m[1]; }
        if (op < 1) n.o = Math.round(op * 100) / 100;
        if (cs.overflow === 'hidden') n.clip = 1;
        out.push(n);
      }
    }

    const kids = Array.from(el.childNodes);
    const elKids = kids.filter(k => k.nodeType === 1);
    const txtKids = kids.filter(k => k.nodeType === 3 && k.textContent.trim());

    if (txtKids.length) {
      const T = typo(cs);
      const mergeable = elKids.length > 0 && elKids.every(k => {
        if (k.tagName.toLowerCase() === 'svg') return false;
        const ks = getComputedStyle(k);
        return sameTypo(typo(ks), T) && !col(ks.backgroundColor) && ks.display.startsWith('inline');
      });
      if (elKids.length === 0 || mergeable) {
        const rg = document.createRange(); rg.selectNodeContents(el);
        pushText(el.textContent, rg.getBoundingClientRect(), T, op);
        return;
      }
      for (const tn of txtKids) {
        const rg = document.createRange(); rg.selectNodeContents(tn);
        pushText(tn.textContent, rg.getBoundingClientRect(), T, op);
      }
    }
    for (const k of elKids) walk(k, op);
  }

  for (const k of Array.from(root.childNodes)) if (k.nodeType === 1) walk(k, 1);
  const rootCs = getComputedStyle(root);
  return { w: rw(R.width), h: rw(R.height), bg: col(rootCs.backgroundColor) || 'ffffff', nodes: out };
};

// Playwright is not asked to download a browser here. CHROME points at one that
// is already installed, and without it playwright-core resolves its own.
const exe = process.env.CHROME || undefined;
const b = await chromium.launch(exe ? { executablePath: exe, args: ['--no-sandbox'] }
                                    : { args: ['--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 393, height: 900 } });
const summary = [];
for (const name of ORDER) {
  await p.goto('file://' + REV + '/' + name + '.html');
  await p.waitForTimeout(320);
  const data = await p.evaluate(EXTRACT);
  const json = JSON.stringify(data);
  fs.writeFileSync(OUT + '/' + name + '.json', json);
  summary.push({ name, nodes: data.nodes.length, kb: Math.round(json.length / 1024),
                 rects: data.nodes.filter(n => n.t === 0).length,
                 texts: data.nodes.filter(n => n.t === 1).length,
                 svgs: data.nodes.filter(n => n.t === 2).length });
}
await b.close();
console.log(JSON.stringify(summary, null, 0));
console.log('total kb', summary.reduce((a, s) => a + s.kb, 0));
