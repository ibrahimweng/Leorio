// Walks each rendered screen and writes a tree of nodes per screen.
//
// Geometry and style come from the browser's own computed values, so what
// lands in Figma is what the screen actually renders, not a re-reading of
// the source. The DOM tree is kept, because a flat pile of rectangles is not
// a design file. A button, a card, an icon's coloured square and a row of
// items each come out as a frame holding its own contents.
import { chromium } from 'playwright-core';
import fs from 'fs';

const SP = process.env.SP;
const REV = SP + '/rev';
const OUT = SP + '/figma';
fs.mkdirSync(OUT, { recursive: true });

// Whatever build.py wrote is what gets extracted. A second hand written list
// here would go stale the moment a screen is added, and it did.
const ORDER = fs.readdirSync(REV).filter(f => f.endsWith('.html')).map(f => f.slice(0, -5)).sort();

const EXTRACT = () => {
  const root = document.querySelector('x-dc > div');
  const R = root.getBoundingClientRect();
  const rx = v => Math.round((v - R.left) * 100) / 100;
  const ry = v => Math.round((v - R.top) * 100) / 100;
  const rw = v => Math.round(v * 100) / 100;
  const r2 = v => Math.round(v * 100) / 100;

  // What the markup already calls a thing is a better layer name than anything
  // that could be guessed from its shape, so those names win.
  const CLASSNAME = {
    dock: 'Dock', askpill: 'Ask bar', fab: 'Action button', fabclose: 'Close',
    fabwrap: 'Actions', fabscrim: 'Scrim', fabrow: 'Action', sheet: 'Sheet',
    fauxbg: 'Scrim', pg: 'Page', pgin: 'Content', pbtn: 'Button',
    segcell: 'Segment item', backBtn: 'Back', qcell: 'Shortcut', dtile: 'Tile',
    slide: 'Slide to confirm', knob: 'Knob', phead: 'Page head',
  };

  function col(s) {
    if (!s) return null;
    let r, g, b, a = 1;
    // Chromium resolves color-mix() to this form, and its channels run from
    // zero to one. Read as bytes they would all come out black.
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

  function textNode(str, b, T, op) {
    const s = str.replace(/\s+/g, ' ');
    if (!s.trim()) return null;
    if (!(b.width > 0) || !(b.height > 0)) return null;
    // Figma's metrics run a hair wider than the browser's, so a single line
    // pinned to a measured width re-wraps. Only text that already wrapped
    // gets a fixed width; everything else is left to size itself.
    const lh = T.lh || T.fs * 1.35;
    const n = { t: 1, n: s.slice(0, 28), x: rx(b.left), y: ry(b.top),
                w: Math.ceil(b.width) + 2, h: Math.ceil(b.height),
                s, fs: T.fs, fw: T.fw, c: T.c || '000000' };
    if (b.height > lh * 1.5) n.ml = 1;
    if (T.it) n.i = 1;
    if (T.lh) n.lh = T.lh;
    if (T.ls) n.ls = T.ls;
    if (T.ta === 'center' || T.ta === 'right') n.ta = T.ta;
    if (op < 1) n.o = r2(op);
    return n;
  }

  // Everything a rectangle needs to look like the element it came from.
  function paintOf(cs, b) {
    const bg = col(cs.backgroundColor);
    const bi = (cs.backgroundImage && cs.backgroundImage !== 'none') ? cs.backgroundImage : null;
    const bw = ['Top', 'Right', 'Bottom', 'Left'].map(s => Math.round((parseFloat(cs['border' + s + 'Width']) || 0) * 100) / 100);
    const shRaw = (cs.boxShadow && cs.boxShadow !== 'none') ? cs.boxShadow : null;
    const bfRaw = (cs.backdropFilter && cs.backdropFilter !== 'none') ? cs.backdropFilter
                : (cs.webkitBackdropFilter && cs.webkitBackdropFilter !== 'none') ? cs.webkitBackdropFilter : null;
    const g = bi ? gradient(bi) : null;
    if (!bg && !g && !bw.some(v => v > 0) && !shRaw && !bfRaw) return null;
    const p = {};
    if (bg) p.bg = bg;
    if (g) p.g = g;
    const rr = [cs.borderTopLeftRadius, cs.borderTopRightRadius, cs.borderBottomRightRadius, cs.borderBottomLeftRadius]
      .map(v => Math.min(parseFloat(v) || 0, Math.min(b.width, b.height) / 2));
    if (rr.some(v => v > 0)) p.r = rr.map(v => Math.round(v * 100) / 100);
    if (bw.some(v => v > 0)) {
      p.sw = bw; p.sc = col(cs.borderTopColor) || '000000';
      if (cs.borderTopStyle === 'dashed') p.sd = 1;
    }
    if (shRaw) p.sh = splitTop(shRaw).map(shadow);
    if (bfRaw) { const m = bfRaw.match(/blur\(([\d.]+)px\)/); if (m) p.bl = +m[1]; }
    return p;
  }

  const ALIGN = { 'flex-start': 'MIN', start: 'MIN', center: 'CENTER', 'flex-end': 'MAX', end: 'MAX', baseline: 'BASELINE' };
  const JUSTIFY = { 'flex-start': 'MIN', start: 'MIN', center: 'CENTER', 'flex-end': 'MAX', end: 'MAX', 'space-between': 'SPACE_BETWEEN' };

  // Flexbox and auto layout are the same idea, so a flex container carries its
  // rule across rather than being flattened into placed boxes.
  function layoutOf(cs) {
    if (cs.display !== 'flex') return null;
    const L = { d: cs.flexDirection === 'column' ? 'V' : 'H' };
    const gap = parseFloat(cs.flexDirection === 'column' ? cs.rowGap : cs.columnGap);
    if (gap > 0) L.gap = Math.round(gap * 100) / 100;
    const pad = ['Top', 'Right', 'Bottom', 'Left'].map(s => Math.round((parseFloat(cs['padding' + s]) || 0) * 100) / 100);
    if (pad.some(v => v > 0)) L.p = pad;
    L.ai = ALIGN[cs.alignItems] || 'MIN';
    L.ji = JUSTIFY[cs.justifyContent] || 'MIN';
    return L;
  }

  function nameOf(el, cs, node, kids) {
    for (const c of el.classList) if (CLASSNAME[c]) return CLASSNAME[c];
    const w = node.w, h = node.h, min = Math.min(w, h);
    const rad = node.r ? Math.max.apply(null, node.r) : 0;
    const svgOnly = kids.length === 1 && kids[0].t === 2;
    const text = (kids.find(k => k.t === 1) || {}).s;
    const pill = rad >= min / 2 - 0.6 && min > 0;
    if (node.bg && svgOnly && Math.abs(w - h) < 2 && w <= 72) return 'Icon';
    if (node.bg && pill && text) return (h >= 44 ? 'Button · ' : 'Chip · ') + text.slice(0, 20);
    if (node.bg && pill && svgOnly) return 'Icon';
    if ((node.bg || node.sw) && rad >= 14 && w >= 160) return 'Card';
    if (node.bl) return 'Scrim';
    if (!node.L) return node.bg || node.sw ? 'Box' : 'Group';
    if (node.L.d === 'V') return 'Column';
    return text ? 'Row · ' + text.slice(0, 20) : 'Row';
  }

  // Returns a list, because an element with nothing of its own to draw hands
  // its children straight up rather than leaving an empty box behind.
  function walk(el) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return [];
    const op = parseFloat(cs.opacity);
    if (!(op > 0.01)) return [];
    const b = el.getBoundingClientRect();

    if (el.tagName.toLowerCase() === 'svg') {
      if (!(b.width > 0)) return [];
      const cc = (col(cs.color) || '000000').split('|')[0];
      const n = { t: 2, n: 'Glyph', x: rx(b.left), y: ry(b.top), w: rw(b.width), h: rw(b.height),
                  s: el.outerHTML.replace(/currentColor/g, '#' + cc) };
      if (op < 1) n.o = r2(op);
      return [n];
    }

    const nodes = Array.from(el.childNodes);
    const elKids = nodes.filter(k => k.nodeType === 1);
    const txtKids = nodes.filter(k => k.nodeType === 3 && k.textContent.trim());
    const paint = paintOf(cs, b);
    let kids = [], everyKidKept = true;

    if (txtKids.length) {
      const T = typo(cs);
      const mergeable = elKids.length > 0 && elKids.every(k => {
        if (k.tagName.toLowerCase() === 'svg') return false;
        const ks = getComputedStyle(k);
        return sameTypo(typo(ks), T) && !col(ks.backgroundColor) && ks.display.startsWith('inline');
      });
      if (elKids.length === 0 || mergeable) {
        const rg = document.createRange(); rg.selectNodeContents(el);
        const tn = textNode(el.textContent, rg.getBoundingClientRect(), T, 1);
        if (!tn) return [];
        if (!paint) { if (op < 1) tn.o = r2(op); return [tn]; }
        kids = [tn];
      } else {
        for (const tn of txtKids) {
          const rg = document.createRange(); rg.selectNodeContents(tn);
          const t = textNode(tn.textContent, rg.getBoundingClientRect(), T, 1);
          if (t) kids.push(t);
        }
        for (const k of elKids) {
          const got = walk(k);
          if (got.length !== 1) everyKidKept = false;
          // A child the browser told to grow must grow in Figma too, or the thing
          // pinned to the far end of the row lands in the wrong place.
          if (got.length === 1 && parseFloat(getComputedStyle(k).flexGrow) > 0) got[0].gr = 1;
          kids = kids.concat(got);
        }
      }
    } else {
      for (const k of elKids) {
        const got = walk(k);
        if (got.length !== 1) everyKidKept = false;
        // A child the browser told to grow must grow in Figma too, or the thing
        // pinned to the far end of the row lands in the wrong place.
        if (got.length === 1 && parseFloat(getComputedStyle(k).flexGrow) > 0) got[0].gr = 1;
        kids = kids.concat(got);
      }
    }

    const named = Array.from(el.classList).some(c => CLASSNAME[c]);
    const clip = cs.overflow === 'hidden';
    // A wrapper that draws nothing and holds one thing is not a layer worth
    // having, so it is folded away and its child moves up.
    if (!paint && !clip && !named && kids.length < 2) return kids;
    if (!(b.width > 0.5) || !(b.height > 0.5)) return kids;

    const node = Object.assign({ t: 0, x: rx(b.left), y: ry(b.top), w: rw(b.width), h: rw(b.height) }, paint || {});
    if (clip) node.clip = 1;
    if (op < 1) node.o = r2(op);

    // Auto layout is only safe when the children still line up with the flex
    // children they came from, and when none of them is placed absolutely.
    const absKid = elKids.some(k => /absolute|fixed/.test(getComputedStyle(k).position));
    if (everyKidKept && !absKid && kids.length >= 2 && !txtKids.length) {
      const L = layoutOf(cs);
      if (L) node.L = L;
    }
    node.n = nameOf(el, cs, node, kids);
    node.k = kids.map(k => Object.assign({}, k, { x: r2(k.x - node.x), y: r2(k.y - node.y) }));
    return [node];
  }

  const out = [];
  for (const k of Array.from(root.childNodes)) if (k.nodeType === 1) out.push(...walk(k));
  const rootCs = getComputedStyle(root);
  return { w: rw(R.width), h: rw(R.height), bg: col(rootCs.backgroundColor) || 'ffffff', k: out };
};

// Playwright is not asked to download a browser here. CHROME points at one that
// is already installed, and without it playwright-core resolves its own.
const exe = process.env.CHROME || undefined;
const b = await chromium.launch(exe ? { executablePath: exe, args: ['--no-sandbox'] }
                                    : { args: ['--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 393, height: 900 } });
const summary = [];
const tally = n => {
  let frames = 0, texts = 0, svgs = 0, auto = 0, depth = 0;
  (function go(list, d) {
    depth = Math.max(depth, d);
    for (const k of list) {
      if (k.t === 1) texts++;
      else if (k.t === 2) svgs++;
      else { frames++; if (k.L) auto++; go(k.k || [], d + 1); }
    }
  })(n.k, 1);
  return { frames, texts, svgs, auto, depth };
};
for (const name of ORDER) {
  await p.goto('file://' + REV + '/' + name + '.html');
  await p.waitForTimeout(320);
  const data = await p.evaluate(EXTRACT);
  const json = JSON.stringify(data);
  fs.writeFileSync(OUT + '/' + name + '.json', json);
  summary.push(Object.assign({ name, kb: Math.round(json.length / 1024) }, tally(data)));
}
await b.close();
console.log(JSON.stringify(summary, null, 0));
console.log('total kb', summary.reduce((a, s) => a + s.kb, 0));
