// Binds the screens on the Flows page to the components in this file.
//
// A screen that is sent again arrives as a plain frame, so the instances in it
// go back to being copies. This script puts them back: anything on Flows whose
// tree matches a component becomes an instance of that component.
//
// It works from the smallest component up. The keypad inside a fresh Confirm
// has to become an instance before the Confirm itself can match the Confirm
// component, because the component holds an instance there, not a copy.
//
// Paste this whole file into the Figma MCP use_figma tool, with the file key in
// ./README.md, after sending anything to Flows. It is safe to run twice: a
// subtree that is already an instance is left alone, so a clean file reports
// nothing swapped.

// The founder's home screen is the component for the home. It lives on the test
// page where they drew it, not with the rest, so it is named here. If the id
// ever goes stale the script recovers it from any instance still on Flows.
const HOME_ID = '193:1566';
const HOME_IN = ['Main', 'Home behind'];

const H = s => { let h = 5381; for (let i = 0; i < s.length; i++) h = ((h * 33) ^ s.charCodeAt(i)) >>> 0; return h; };
const fills = n => { try { return !Array.isArray(n.fills) ? '' : n.fills.map(f => f.type === 'SOLID'
  ? Math.round(f.color.r * 255) + ',' + Math.round(f.color.g * 255) + ',' + Math.round(f.color.b * 255)
    + ',' + (f.opacity === undefined ? 1 : f.opacity).toFixed(2)
  : f.type).join(';'); } catch (e) { return ''; } };

// A component and the frame it was made from are the same shape under different
// type names, and an instance stands for whatever it is an instance of. Both
// have to hash alike or nothing would ever match.
const kind = t => (t === 'COMPONENT' || t === 'INSTANCE') ? 'FRAME' : t;
function sig(n) {
  if (n.type === 'INSTANCE') return H('=' + n.name);
  const kids = ('children' in n ? n.children : []).map(sig);
  return H(kind(n.type) + '|' + Math.round(n.width) + 'x' + Math.round(n.height) + '|'
    + (n.type === 'TEXT' ? n.characters : '') + '|' + fills(n) + '(' + kids.join(',') + ')');
}
const size = n => 1 + ('children' in n ? n.children.reduce((a, c) => a + size(c), 0) : 0);

function swap(old, comp, name) {
  const p = old.parent, at = p.children.indexOf(old);
  const lp = old.layoutPositioning, x = old.x, y = old.y;
  const lsh = old.layoutSizingHorizontal, lsv = old.layoutSizingVertical;
  const la = old.layoutAlign, lg = old.layoutGrow, cons = old.constraints;
  const w = old.width, h = old.height;
  const inst = comp.createInstance();
  if (Math.round(inst.width) !== Math.round(w) || Math.round(inst.height) !== Math.round(h)) inst.resize(w, h);
  p.insertChild(at, inst);
  inst.name = name;
  if (p.layoutMode && p.layoutMode !== 'NONE') {
    try { inst.layoutPositioning = lp; } catch (e) {}
    if (lp === 'ABSOLUTE') { inst.x = x; inst.y = y; }
    else { try { inst.layoutAlign = la; } catch (e) {} try { inst.layoutGrow = lg; } catch (e) {}
           try { inst.layoutSizingHorizontal = lsh; } catch (e) {} try { inst.layoutSizingVertical = lsv; } catch (e) {} }
  } else { inst.x = x; inst.y = y; }
  try { inst.constraints = cons; } catch (e) {}
  old.remove();
  return inst;
}

const flows = figma.root.children.find(p => p.name === 'Flows');
if (!flows) throw new Error('no Flows page');
await figma.setCurrentPageAsync(flows);

// Everything on the Components page, smallest first.
const cpage = figma.root.children.find(p => p.name === 'Components');
const lib = [];
if (cpage) for (const sec of (await figma.getNodeByIdAsync(cpage.id)).children)
  for (const c of (sec.children || [])) if (c.type === 'COMPONENT') lib.push(c);
lib.sort((a, b) => size(a) - size(b));

const report = [], missing = [];
for (const comp of lib) {
  const want = sig(comp);
  const hits = [];
  for (const sec of flows.children) if (sec.type === 'SECTION')
    for (const fr of sec.children)
      (function walk(n) {
        if (n.type === 'INSTANCE') return;
        if (sig(n) === want) { hits.push(n); return; }
        if ('children' in n) n.children.forEach(walk);
      })(fr);
  for (const old of hits) swap(old, comp, comp.name);
  if (hits.length) report.push(comp.name + ' x' + hits.length);
}

// The home is matched by name, not by shape: it is the only thing that ever
// sits at the foot of those seven screens, and it is far too big to hash on
// every pass.
let home = await figma.getNodeByIdAsync(HOME_ID);
if (!home || home.type !== 'COMPONENT') {
  home = null;
  for (const sec of flows.children) if (sec.type === 'SECTION')
    for (const fr of sec.children) if (fr.type === 'INSTANCE' && HOME_IN.indexOf(fr.name) >= 0)
      home = home || await fr.getMainComponentAsync();
}
let homes = 0;
if (home) {
  const targets = [];
  for (const sec of flows.children) if (sec.type === 'SECTION')
    for (const fr of sec.children) {
      if (fr.name === 'Main') targets.push(fr);
      else if ('children' in fr && fr.children[0] && fr.children[0].name === 'Home behind') targets.push(fr.children[0]);
    }
  for (const old of targets) { if (old.type === 'INSTANCE') continue; swap(old, home, old.name); homes++; }
  if (homes) report.push('Home screen x' + homes);
} else missing.push('Home screen');

return { components: lib.length, swapped: report, missing,
         mutatedNodeIds: flows.children.filter(c => c.type === 'SECTION').map(c => c.id) };
