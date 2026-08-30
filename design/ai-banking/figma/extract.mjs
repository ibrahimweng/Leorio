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
    mcp: 'MCP panel', pinkey: 'Key', pindot: 'Dot',
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

  function stopsOf(parts) {
    return parts.map((p, i) => {
      const cm2 = p.match(/(rgba?\([^)]*\)|color\(srgb[^)]*\)|#[0-9a-fA-F]{3,8})/);
      const pos = p.match(/([\d.]+)%\s*$/);
      return { c: col(cm2 ? cm2[1] : null) || 'ffffff|0', p: pos ? +pos[1] / 100 : i / Math.max(1, parts.length - 1) };
    });
  }

  // radial-gradient(<rx>% <ry>% at <cx>% <cy>%, ...). Only the shape this repo
  // draws is read: an ellipse given in per cent of the box it sits in, which is
  // what a wash behind a screen is.
  function radial(bi) {
    const m = bi.match(/^radial-gradient\((.*)\)$/s);
    if (!m) return null;
    const parts = splitTop(m[1]);
    const head = parts[0].trim();
    const shape = head.match(/^([\d.]+)%\s+([\d.]+)%\s+at\s+([\d.-]+)%\s+([\d.-]+)%$/);
    if (!shape) return null;
    parts.shift();
    return { rad: 1, rx: +shape[1] / 100, ry: +shape[2] / 100,
             cx: +shape[3] / 100, cy: +shape[4] / 100, stops: stopsOf(parts) };
  }

  function gradient(bi) {
    const r = radial(bi);
    if (r) return r;
    const m = bi.match(/^linear-gradient\((.*)\)$/s);
    if (!m) return null;
    const parts = splitTop(m[1]);
    let deg = 180;
    if (/deg$/.test(parts[0])) deg = parseFloat(parts.shift());
    else if (/^to\s/.test(parts[0])) {
      const to = parts.shift();
      deg = { 'to top': 0, 'to right': 90, 'to bottom': 180, 'to left': 270 }[to.trim()] ?? 180;
    }
    return { deg, stops: stopsOf(parts) };
  }

  function typo(cs) {
    return {
      fs: Math.round(parseFloat(cs.fontSize) * 100) / 100,
      fw: parseInt(cs.fontWeight) || 400,
      // The family, but only when it is not the interface font. There is one
      // family now, so this should always come back undefined; it stays as the
      // tripwire. Anything it does catch reaches Figma unbound and named, which
      // is how a second face would announce itself rather than creep in.
      ff: (cs.fontFamily.split(',')[0].replace(/['"]/g, '').trim() === 'SF Pro Text')
            ? undefined : cs.fontFamily.split(',')[0].replace(/['"]/g, '').trim(),
      it: cs.fontStyle === 'italic' ? 1 : 0,
      c: col(cs.color),
      lh: cs.lineHeight === 'normal' ? 0 : Math.round(parseFloat(cs.lineHeight) * 100) / 100,
      ls: Math.round((parseFloat(cs.letterSpacing) || 0) * 100) / 100,
      ta: cs.textAlign
    };
  }
  // Two runs only merge into one text node if they agree on the family too --
  // a node in Figma carries one font, so a merged run would have to pick.
  const sameTypo = (a, b) => a.fs === b.fs && a.fw === b.fw && a.it === b.it
    && a.c === b.c && a.ff === b.ff;

  // The six named text styles in the Figma file, keyed by the size and weight
  // that build.py has already snapped every line onto. A pair that is not here
  // is one of the surfaces marked `chrome`, which opt out of the ramp: the
  // on-screen keyboard, the payment card and the meter token. Those stay
  // unbound, which is how you can tell them apart in the file.
  // Keyed size/weight, and the weights are the ones the ramp actually emits:
  // Semibold 600 carries the emphasis and Bold 700 survives only at 32.
  const STYLE = {
    '32/700': 'Display/Bold 32',
    '20/600': 'Heading/Semibold 20',
    '14/600': 'Label/Semibold 14',   '14/400': 'Label/Regular 14',
    '12/600': 'Caption/Semibold 12', '12/400': 'Caption/Regular 12'
  };
  // One family now. `ff` is still captured for anything that is not SF Pro, so a
  // stray face shows up as an unbound node rather than being coerced quietly.
  const styleOf = T => (T.ff ? null : STYLE[T.fs + '/' + T.fw]) || null;

  function textNode(str, b, T, op, clipW) {
    const s = str.replace(/\s+/g, ' ');
    if (!s.trim()) return null;
    if (!(b.width > 0) || !(b.height > 0)) return null;
    // A line the browser cuts off with an ellipsis measures its full length,
    // which would then overlap whatever sits beside it. Pin it to the box it
    // is actually allowed and let Figma do the cutting.
    if (clipW && b.width > clipW + 0.5) {
      const n = { t: 1, n: s.slice(0, 28), x: rx(b.left), y: ry(b.top),
                  w: Math.ceil(clipW), h: Math.ceil(b.height), tr: 1,
                  s, fs: T.fs, fw: T.fw, c: T.c || '000000' };
      if (T.ff) n.ff = T.ff;
      if (T.it) n.i = 1;
      if (T.lh) n.lh = T.lh;
      if (T.ls) n.ls = T.ls;
      if (T.ta === 'center' || T.ta === 'right') n.ta = T.ta;
      if (op < 1) n.o = r2(op);
      const sn = styleOf(T); if (sn) n.sn = sn;
      return n;
    }
    // Figma's metrics run a hair wider than the browser's, so a single line
    // pinned to a measured width re-wraps. Only text that already wrapped
    // gets a fixed width; everything else is left to size itself.
    const lh = T.lh || T.fs * 1.35;
    const n = { t: 1, n: s.slice(0, 28), x: rx(b.left), y: ry(b.top),
                w: Math.ceil(b.width) + 2, h: Math.ceil(b.height),
                s, fs: T.fs, fw: T.fw, c: T.c || '000000' };
    if (b.height > lh * 1.5) n.ml = 1;
    if (T.ff) n.ff = T.ff;
    if (T.it) n.i = 1;
    if (T.lh) n.lh = T.lh;
    if (T.ls) n.ls = T.ls;
    if (T.ta === 'center' || T.ta === 'right') n.ta = T.ta;
    if (op < 1) n.o = r2(op);
    const sn = styleOf(T); if (sn) n.sn = sn;
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
      // Take the colour and the style from a side that actually has width. A
      // side with none computes its colour as currentColor, so a rule set only
      // on the bottom would otherwise be read as black.
      const side = ['Top', 'Right', 'Bottom', 'Left'][bw.findIndex(v => v > 0)];
      p.sw = bw; p.sc = col(cs['border' + side + 'Color']) || '000000';
      if (cs['border' + side + 'Style'] === 'dashed') p.sd = 1;
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
      // Every svg build.py draws carries data-icon, so a glyph arrives in Figma
      // already knowing which icon it is. Without it the only way to tell two
      // glyphs apart is their geometry, and a three point chevron and a three
      // point check are the same shape to anything that compares loosely.
      const gname = el.getAttribute('data-icon');
      const n = { t: 2, n: gname ? 'Glyph · ' + gname : 'Glyph',
                  x: rx(b.left), y: ry(b.top), w: rw(b.width), h: rw(b.height),
                  s: el.outerHTML.replace(/currentColor/g, '#' + cc) };
      // The glow lives in a CSS filter, and the packer strips the style
      // attribute before Figma sees the drawing. So it travels as a shadow of
      // its own, the same shape a box-shadow takes, and is applied as an
      // effect on the imported frame.
      const dsh = (cs.filter && cs.filter !== 'none')
        ? cs.filter.match(/drop-shadow\(([^()]|\([^()]*\))*\)/g) : null;
      if (dsh) n.sh = dsh.map(f => shadow(f.slice(12, -1)));
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
        const clipped = cs.textOverflow === 'ellipsis'
          && (cs.overflow === 'hidden' || cs.overflowX === 'hidden');
        const tn = textNode(el.textContent, rg.getBoundingClientRect(), T, 1,
                            clipped ? b.width - (parseFloat(cs.paddingLeft) || 0) - (parseFloat(cs.paddingRight) || 0) : 0);
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
