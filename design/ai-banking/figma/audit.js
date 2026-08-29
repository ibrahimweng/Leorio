// Invariants and design audit for the Figma file. Paste into use_figma, setting
// PAGE to the page you want. Run it once before a bulk change and once after,
// and compare the numbers. It only reads; it never writes.
//
// The scales come from tokens.py. Keep them in step: if SPACE, RADII or the icon
// sizes move there, move them here too, or this will report the old system.
const PAGE = 'Flows';

const SPACE  = [0, 4, 8, 12, 16, 20, 24, 32, 40, 56, 72];
const RADII  = [0, 12, 16, 20, 24, 28, 999];
const TYPE   = [12, 14, 20, 32, 36];
const ICON   = [11, 12, 15, 16, 18, 20, 24, 28, 32, 34, 36, 40, 48, 56, 64];
const STROKE = [1.5, 1.7, 2];          // apparent px, what the eye sees
const HOLDER = { FRAME: 1, COMPONENT: 1, INSTANCE: 1, GROUP: 1, COMPONENT_SET: 1, SECTION: 1 };
const near = (v, list) => list.some(x => Math.abs(x - v) < 0.51);

const page = figma.root.children.find(p => p.name === PAGE);
await figma.setCurrentPageAsync(page);

// ---- wiring -------------------------------------------------------------
const ids = {};
(function idx(n) { ids[n.id] = 1; if (n.children) n.children.forEach(idx); })(page);
let reactions = 0, dead = 0;
(function walk(n) {
  if (n.reactions) for (const r of n.reactions) {
    reactions++;
    const a = r.action || (r.actions && r.actions[0]);
    if (a && a.type === 'NODE' && (!a.destinationId || !ids[a.destinationId])) dead++;
  }
  if (n.children) n.children.forEach(walk);
})(page);

// ---- type ---------------------------------------------------------------
const styleName = {};
for (const s of await figma.getLocalTextStylesAsync()) styleName[s.id] = s.name;
let texts = 0, bound = 0;
const fonts = {}, unbound = {};
for (const t of page.findAllWithCriteria({ types: ['TEXT'] })) {
  texts++;
  const sid = t.textStyleId;
  if (sid && typeof sid === 'string' && styleName[sid]) { bound++; continue; }
  const fn = t.fontName;
  if (fn === figma.mixed) { fonts.MIXED = (fonts.MIXED || 0) + 1; continue; }
  fonts[fn.family] = (fonts[fn.family] || 0) + 1;
  if (fn.family !== 'SF Pro Text') continue;
  const k = Math.round(t.fontSize) + '/' + fn.style;
  unbound[k] = (unbound[k] || 0) + 1;
}

// ---- layout, shape and icons -------------------------------------------
const noAuto = {}, offGap = {}, offPad = {}, offRadius = {}, offIcon = {}, offStroke = {}, retired = {};
function isIcon(n) {
  return n.type === 'INSTANCE' && n.mainComponent && n.mainComponent.parent
    && n.mainComponent.parent.type === 'COMPONENT_SET'
    && n.mainComponent.parent.name.indexOf('Icon') === 0;
}
function bump(store, key, where) {
  const g = store[key] || (store[key] = { n: 0, where: [] });
  g.n++; if (g.where.length < 3) g.where.push(where);
}
for (const sec of page.children) {
  if (!HOLDER[sec.type]) continue;
  const roots = sec.type === 'SECTION' ? sec.children : [sec];
  for (const scr of roots) {
    if (!HOLDER[scr.type]) continue;
    const where = scr.name;
    for (const f of scr.findAllWithCriteria({ types: ['FRAME', 'COMPONENT', 'INSTANCE'] })) {
      let c = f.parent, inInst = false;
      while (c && c.type !== 'PAGE') { if (c.type === 'INSTANCE') { inInst = true; break; } c = c.parent; }
      if (isIcon(f)) {
        const w = Math.round(f.width * 10) / 10;
        if (!near(w, ICON)) bump(offIcon, String(w), where);
        for (const v of f.findAll(x => x.strokes && x.strokes.length && x.strokeWeight)) {
          // strokeWeight on a resized instance is already what the eye sees.
          // Figma scales it with the instance; do not scale it a second time.
          const apparent = Math.round(v.strokeWeight * 100) / 100;
          if (!near(apparent, STROKE)) bump(offStroke, apparent + ' at ' + w + 'px', where);
        }
        continue;
      }
      if (f.type === 'INSTANCE' && f.mainComponent && f.mainComponent.parent
          && f.mainComponent.parent.name === 'Icon (old — superseded)')
        bump(retired, f.mainComponent.name, where);
      if (inInst) continue;
      if (f.type === 'INSTANCE') continue;
      if (f.layoutMode === 'NONE' && f.children.length > 1) bump(noAuto, f.children.length + ' children', where);
      if (f.layoutMode !== 'NONE' && !near(f.itemSpacing, SPACE)) bump(offGap, String(f.itemSpacing), where);
      if (f.layoutMode !== 'NONE') for (const p of [f.paddingTop, f.paddingRight, f.paddingBottom, f.paddingLeft])
        if (!near(p, SPACE)) bump(offPad, String(p), where);
      const r = f.cornerRadius;
      if (typeof r === 'number' && !near(r, RADII) && !(Math.abs(f.height / 2 - r) < 1)) bump(offRadius, String(r), where);
    }
  }
}
const top = (o, n) => Object.keys(o).sort((a, b) => o[b].n - o[a].n).slice(0, n)
  .map(k => k + ' x' + o[k].n + ' (' + o[k].where.join(', ') + ')');
return {
  page: PAGE,
  wiring: { reactions, deadDestinations: dead },
  type: { texts, bound, unbound: texts - bound, fonts, unboundSFPro: unbound },
  layout: { framesWithoutAutoLayout: top(noAuto, 8), offGridGaps: top(offGap, 8), offGridPadding: top(offPad, 8) },
  shape: { offScaleRadii: top(offRadius, 8) },
  icons: { offScaleSizes: top(offIcon, 10), offScaleStrokes: top(offStroke, 12),
           stillOnRetiredSet: top(retired, 5) }
};
