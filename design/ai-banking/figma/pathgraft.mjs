// graft.mjs adds subtrees to the top of an artboard. This one reaches inside,
// which is where a screen usually grows: a new card between two others, a new
// button at the foot of one that is already there. Each graft names a subtree
// by its path through the built screen, the frame in Figma it belongs in, and
// the place among that frame's children it takes. Everything already in the
// file keeps its identity, so nothing loses a reaction.
import fs from 'fs';
const SP = process.env.SP;
const [name, ...specs] = process.argv.slice(2);   // path@parentId@index
const d = JSON.parse(fs.readFileSync(SP + '/figma/' + name + '.json', 'utf8'));

const at = p => p.split('.').map(Number).reduce((n, i) => (n.k || n)[i], { k: d.k });
const want = [], where = [];
for (const s of specs) {
  const [p, parent, idx] = s.split('@');   // node ids have colons in them
  want.push(at(p)); where.push([parent, +idx]);
}

// The extractor keeps the whole svg on every glyph. Lift the ones these
// subtrees actually draw into a table of their own.
const map = new Map(), V = [];
(function walk(n) { if (n.t === 2) { const svg = n.s.replace(/\s*style="[^"]*"/g, '');
    if (!map.has(svg)) { map.set(svg, V.length); V.push(svg); }
    n.s = map.get(svg); }
  (n.k || []).forEach(walk); })({ k: want });

const RUNNER = fs.readFileSync(SP + '/figma/bundle/1.js', 'utf8').split('\n').slice(1).join('\n')
  .replace(/const PAGE_ID[\s\S]*$/, `
await figma.setCurrentPageAsync(figma.root.children.find(p=>p.name===PAGE));
const out=[], ids=[];
for(let i=0;i<NODES.length;i++){
  const [pid, idx] = WHERE[i];
  const host = await figma.getNodeByIdAsync(pid);
  if(!host) throw new Error('no parent ' + pid);
  const before = host.children.length;
  binds=[]; bound=0; unstyled=0; errs=[]; made=0; autos=0; kept=0; undone=0;
  build(NODES[i], host);
  const nd = host.children[host.children.length-1];
  host.insertChild(Math.min(idx, before), nd);
  for(const [t,id] of binds){ try{ await t.setTextStyleIdAsync(id); bound++; }catch(e){ errs.push('style: '+String(e.message||e).slice(0,60)); } }
  if(NODES[i].t===0) tune(nd, NODES[i]);
  // Inside auto layout the parent decides where a child sits, and a hand
  // placed x and y only fights it.
  if(host.layoutMode && host.layoutMode!=='NONE'){ try{ nd.layoutSizingHorizontal='FIXED'; nd.layoutSizingVertical='FIXED'; }catch(_){} }
  ids.push(nd.id);
  out.push({into:host.name, at:idx, node:nd.name, made, autoLayout:kept+'/'+autos,
            placedByHand:undone, styled:bound+'/'+(bound+unstyled), errs:errs.slice(0,3)});
}
return {createdNodeIds:ids, grafts:out};
`);
// One graft to a line, so the payload can be read and checked a piece at a
// time instead of as one unbroken kilometre of JSON.
const out = `const PAGE=${JSON.stringify(process.env.PAGE || 'Components')};const TOL=1;\n`
  + `const WHERE=${JSON.stringify(where)};\n`
  + 'const V=[\n' + V.map(v => JSON.stringify(v)).join(',\n') + '\n];\n'
  + 'const NODES=[\n' + want.map(n => JSON.stringify(n)).join(',\n') + '\n];\n' + RUNNER;
fs.writeFileSync(SP + '/figma/pathgraft-' + name + '.js', out);
console.log(name, '| grafts', want.length, '| glyphs', V.length, '| chars', out.length);
