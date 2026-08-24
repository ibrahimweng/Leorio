// Emits a script that grafts a few top-level subtrees onto a frame that is
// already in the file. A screen that is another screen plus a keyboard does
// not need the whole home feed sent again.
import fs from 'fs';
const SP = process.env.SP;
const [name, target, ...idx] = process.argv.slice(2);
const d = JSON.parse(fs.readFileSync(SP + '/figma/' + name + '.json', 'utf8'));
const want = idx.map(Number).map(i => d.k[i]);

// The extractor keeps the whole svg on the node. Pull the ones these subtrees
// use into a table of their own, so the graft carries no glyph it never draws.
const map = new Map(), V = [];
(function walk(n){ if(n.t===2){ const svg = n.s;
    if(!map.has(svg)){ map.set(svg, V.length); V.push(svg); }
    n.s = map.get(svg); }
  (n.k||[]).forEach(walk); })({k: want});

const RUNNER = fs.readFileSync(SP + '/figma/bundle/1.js', 'utf8').split('\n').slice(1).join('\n')
  .replace(/const PAGE_ID[\s\S]*$/, `
const fr = await figma.getNodeByIdAsync(TARGET);
if(!fr) throw new Error('no frame ' + TARGET);
if(NAME) fr.name = NAME;
// Anything the graft replaces goes first, so the new subtrees land in the
// same order the source had them.
if(typeof STRIP !== 'undefined') for(const i of STRIP.slice().sort((a,b)=>b-a)) if(fr.children[i]) fr.children[i].remove();
const base = fr.children.length;
for(const n of NODES) build(n, fr);
for(let i=0;i<NODES.length;i++) if(NODES[i].t===0 && fr.children[base+i]) tune(fr.children[base+i], NODES[i]);
return {mutatedNodeIds:[fr.id], name:fr.name, added:made, autoLayout:kept+'/'+autos, placedByHand:undone, errs:errs.slice(0,4)};
`);
const strip = process.env.STRIP ? `const STRIP=[${process.env.STRIP}];` : '';
const out = `const TARGET=${JSON.stringify(target)};const NAME=${JSON.stringify(name)};${strip}const TOL=1;`
  + `const V=${JSON.stringify(V)};const NODES=${JSON.stringify(want)};\n` + RUNNER;
fs.writeFileSync(SP + '/figma/graft-' + name + '.js', out);
console.log(name, '->', target, '| subtrees', want.length, '| glyphs', V.length, '| chars', out.length);
