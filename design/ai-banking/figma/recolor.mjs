// A change that is only colour does not need the screens sending again.
//
// Two extractions of the same screen, one from before the change and one from
// after, have the same shape node for node. So walk them together and write
// down every place a fill, a stroke or a glyph's colour differs, as a path of
// child indices from the screen frame. emit-recolor turns that into a script
// that walks the same path in Figma and paints what it finds.
//
// The path is checked as it is walked: every step names the node it expects,
// and a step that lands somewhere else stops and reports rather than painting
// the wrong thing. That is what makes this safe on a page where some screens
// are instances of components and some are not.
import fs from 'fs';
const SP = process.env.SP, OLD = process.env.OLD;
const names = fs.readdirSync(SP + '/rev').filter(f => f.endsWith('.html')).map(f => f.slice(0, -5)).sort();

// The one colour in a glyph, and how thick it is drawn.
const glyph = s => {
  const st = [...s.matchAll(/stroke="(#[0-9a-fA-F]{3,8})"/g)].map(m => m[1].toLowerCase());
  const fl = [...s.matchAll(/fill="(#[0-9a-fA-F]{3,8})"/g)].map(m => m[1].toLowerCase());
  const w = s.match(/stroke-width="([\d.]+)"/);
  return { st: [...new Set(st)], fl: [...new Set(fl)], w: w ? +w[1] : 0 };
};
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

const out = {}, broken = [];
let total = 0;
for (const n of names) {
  const A = JSON.parse(fs.readFileSync(OLD + '/figma/' + n + '.json', 'utf8'));
  const B = JSON.parse(fs.readFileSync(SP + '/figma/' + n + '.json', 'utf8'));
  const edits = [];
  let bad = false;
  (function walk(a, b, path) {
    if (a.t !== b.t) { bad = true; return; }
    if (b.t === 1) {
      if (a.c !== b.c) edits.push([path, 1, b.c, (b.s || '').slice(0, 24)]);
      return;
    }
    if (b.t === 2) {
      const ga = glyph(a.s), gb = glyph(b.s);
      if (!same(ga, gb)) edits.push([path, 2, [ga.st, gb.st, ga.fl, gb.fl, ga.w, gb.w], 'Glyph']);
      return;
    }
    if (a.bg !== b.bg) edits.push([path, 0, b.bg || null, b.n || 'Frame']);
    if (a.sc !== b.sc) edits.push([path, 3, b.sc || null, b.n || 'Frame']);
    const ka = a.k || [], kb = b.k || [];
    if (ka.length !== kb.length) { bad = true; return; }
    for (let i = 0; i < kb.length; i++) walk(ka[i], kb[i], path.concat(i));
  })({ t: 0, k: A.k }, { t: 0, k: B.k }, []);
  // The overlay screens had their leading children swapped for one instance of
  // the home, so a top level index counted here can be one out over there. The
  // name of the child the path starts at travels with the edit, and the script
  // uses it to find its footing before descending.
  for (const e of edits) e.push((B.k[e[0][0]] || {}).n || '');
  if (bad) { broken.push(n); continue; }
  if (edits.length) { out[n] = edits; total += edits.length; }
}
fs.writeFileSync(SP + '/figma/recolor.json', JSON.stringify(out));
console.log('screens changed', Object.keys(out).length, '| edits', total,
            '| shapes differ', broken.length ? broken.join(',') : 'none');
for (const [k, v] of Object.entries(out)) console.log('  ' + k.padEnd(14), v.length);
