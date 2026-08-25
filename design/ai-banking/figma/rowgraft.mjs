// Grafts a few rows from a built screen into a frame that already exists.
//
// The home screen in the file is the founder's, not the one this repo draws.
// When something is added to home it has to be added to theirs, and the honest
// way to do that is to build the row here, where the design system is, and put
// that node into their frame rather than redrawing it by hand in Figma.
//
//   SRC=Main PICK=4,5 TARGET=<node-id> AT=0 node figma/rowgraft.mjs
//
// PICK is indices into the screen's Content column, which is where a page's
// own rows live. AT is where they go in the target's children.
import fs from 'fs';
const SP = process.env.SP;
const SRC = process.env.SRC || 'Main';
const PICK = (process.env.PICK || '').split(',').filter(Boolean).map(Number);
const TARGET = process.env.TARGET;
const AT = +(process.env.AT || 0);
if (!TARGET) { console.error('TARGET is required'); process.exit(2); }

const data = JSON.parse(fs.readFileSync(SP + '/figma/' + SRC + '.json', 'utf8'));
// A page's own rows live in its Content column, which is where PICK counts
// from by default. A sheet keeps its rows somewhere else, so ROOT is a path of
// child indices down to whatever holds them.
const ROOT = (process.env.ROOT || '0/0').split('/').filter(Boolean).map(Number);
const content = ROOT.reduce((n, i) => {
  if (!n || !n.k || !n.k[i]) { console.error('no child ' + i + ' on the way to ' + ROOT.join('/')); process.exit(2); }
  return n.k[i];
}, data);
const nodes = PICK.map(i => {
  const n = content.k[i];
  if (!n) { console.error('no child ' + i + ' in ' + SRC); process.exit(2); }
  return JSON.parse(JSON.stringify(n));
});

const V = [], seen = new Map();
(function go(list) {
  for (const n of list) {
    for (const k of ['x','y','w','h']) if (typeof n[k] === 'number') n[k] = Math.round(n[k] * 10) / 10;
    if (n.t === 2) {
      const svg = n.s.replace(/\s*style="[^"]*"/g, '');
      if (!seen.has(svg)) { seen.set(svg, V.length); V.push(svg); }
      n.s = seen.get(svg);
    }
    if (n.k) go(n.k);
  }
})(nodes);

// The same builder the whole pipeline uses, so a grafted row is made the way
// every other row in the file was made.
const RUNNER = fs.readFileSync('figma/emit.mjs', 'utf8')
  .match(/^const RUNNER = `\n([\s\S]*?)\nconst PAGE_ID/m)[1]
  .split('\n').filter(l => !/^\s*\/\//.test(l)).join('\n');

const out = `const TOL=1;const V=${JSON.stringify(V)};const NODES=${JSON.stringify(nodes)};
const TARGET=${JSON.stringify(TARGET)};const AT=${AT};const PAGE=${JSON.stringify(process.env.PAGE || '70:1340')};
${RUNNER}
const page = await figma.getNodeByIdAsync(PAGE);
await figma.setCurrentPageAsync(page);
const host = await figma.getNodeByIdAsync(TARGET);
if(!host) throw new Error('no target ' + TARGET);
const ids=[];
for(let i=0;i<NODES.length;i++){
  const n=NODES[i];
  const nd=figma.createFrame();
  nd.name=n.n||'Frame'; nd.resize(n.w,n.h); nd.fills=[]; nd.clipsContent=!!n.clip;
  dress(nd,n);
  host.insertChild(AT+i, nd);
  for(const k of (n.k||[])) build(k,nd);
  tune(nd,n);
  try{ nd.layoutSizingHorizontal='FIXED'; nd.layoutSizingVertical='FIXED'; }catch(_){}
  nd.resize(n.w,n.h);
  ids.push(nd.id);
}
return {createdNodeIds:ids, into:host.name, at:AT, errs:errs.slice(0,6),
        order:host.children.map((c,i)=>i+' '+c.name)};
`;
fs.mkdirSync(SP + '/figma', { recursive: true });
fs.writeFileSync(SP + '/figma/rowgraft.js', out);
console.log('rows', nodes.length, '| chars', out.length, '->', SP + '/figma/rowgraft.js');
