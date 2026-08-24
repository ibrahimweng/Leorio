// Where a new screen has exactly the same shape as one already in the file,
// it does not need sending again. Compare the two trees with the words taken
// out; if they match, emit a script that walks the text nodes in order and
// sets the new words and colours. Fails loudly when the shapes differ.
import fs from 'fs';
const SP = process.env.SP;
const [base, next, target] = process.argv.slice(2);
const A = JSON.parse(fs.readFileSync(SP + '/figma/' + base + '.json', 'utf8'));
const B = JSON.parse(fs.readFileSync(SP + '/figma/' + next + '.json', 'utf8'));

const shape = n => ({ t: n.t, L: n.L ? n.L.d : 0, bg: n.bg || 0, r: n.r ? 1 : 0,
                      k: (n.k || []).map(shape) });
const sa = JSON.stringify(shape({ k: A.k })), sb = JSON.stringify(shape({ k: B.k }));
if (sa !== sb) { console.error('SHAPES DIFFER: ' + base + ' vs ' + next); process.exit(2); }

const texts = d => { const o = []; (function w(n){ if(n.t===1)
    o.push({ s:n.s, c:n.c, x:n.x, y:n.y, w:n.w, h:n.h, ml:n.ml||0, tr:n.tr||0 });
  (n.k||[]).forEach(w); })({k:d.k}); return o; };
const ta = texts(A), tb = texts(B);
// The geometry travels with the words. A line that was sized for "Free" will
// wrap the moment it is asked to say "Rent balance", so the new box goes too.
const edits = tb.map((t, i) => (t.s === ta[i].s && t.c === ta[i].c) ? null
  : [i, t.s, t.c, t.x, t.y, t.w, t.h, t.ml, t.tr]).filter(Boolean);

const out = `const TARGET=${JSON.stringify(target)};const NAME=${JSON.stringify(next)};
const EDITS=${JSON.stringify(edits)};
const F='Plus Jakarta Sans';
for(const s of ['Regular','Bold','ExtraBold','Italic']) await figma.loadFontAsync({family:F,style:s});
function C(h){const a=String(h).split('|'),v=a[0];
  return {c:{r:parseInt(v.slice(0,2),16)/255,g:parseInt(v.slice(2,4),16)/255,b:parseInt(v.slice(4,6),16)/255},o:a[1]!==undefined?+a[1]:1};}
const fr = await figma.getNodeByIdAsync(TARGET);
if(!fr) throw new Error('no frame ' + TARGET);
fr.name = NAME;
const t = fr.findAll(n => n.type === 'TEXT');
if(t.length !== ${tb.length}) throw new Error('expected ${tb.length} texts, found ' + t.length);
const done = [];
for(const [i, s, c, x, y, w, h, ml, tr] of EDITS){
  const nd = t[i];
  if(nd.characters !== s) nd.characters = s;
  const cc = C(c);
  nd.fills = [{type:'SOLID', color: cc.c, opacity: cc.o}];
  if(nd.name.length < 32) nd.name = s.slice(0, 30);
  // The box travels with the words. A line sized for "Free" wraps to three
  // lines the moment it is asked to say "Rent balance", so the new sizing
  // mode and measured box go on with the new string.
  if(tr){ nd.textAutoResize = 'NONE'; nd.resize(w, h);
          try{ nd.textTruncation = 'ENDING'; }catch(_){} }
  else { try{ nd.textTruncation = 'DISABLED'; }catch(_){}
         if(ml){ nd.textAutoResize = 'HEIGHT'; nd.resize(w + 4, h); }
         else  { nd.textAutoResize = 'WIDTH_AND_HEIGHT'; } }
  // Only a hand placed line needs putting back. Inside auto layout the frame
  // decides where its children sit, and writing x/y there fights it.
  const p = nd.parent;
  if(p && p.layoutMode === 'NONE'){ nd.x = x; nd.y = y; }
  done.push(i);
}
return {mutatedNodeIds:[fr.id], name:fr.name, texts:t.length, edited:done.length};
`;
fs.writeFileSync(SP + '/figma/repatch-' + next + '.js', out);
console.log(next.padEnd(13), 'from', base.padEnd(9), '| texts', tb.length, '| edits', edits.length, '| chars', out.length);
