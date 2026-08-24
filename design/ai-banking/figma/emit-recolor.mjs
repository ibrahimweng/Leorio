// Packs the colour edits into scripts small enough for one use_figma call.
//
// TARGETS says where to look. Given a page, it walks the sections and matches
// a frame by its name; given a map of node ids, it works on exactly those, so
// a component master can be painted once instead of every instance of it.
import fs from 'fs';
const SP = process.env.SP;
const PLAN = JSON.parse(fs.readFileSync(SP + '/figma/recolor.json', 'utf8'));
const ONLY = (process.env.ONLY || '').split(',').filter(Boolean);
const IDS = process.env.IDS || '';          // id=Name,id=Name
const PAGE = process.env.PAGE || '';
const CAP = 40000;

const RUNNER = `
function C(h){const a=String(h).split('|'),v=a[0];
  return {type:'SOLID',color:{r:parseInt(v.slice(0,2),16)/255,g:parseInt(v.slice(2,4),16)/255,b:parseInt(v.slice(4,6),16)/255},
          opacity:a[1]!==undefined?+a[1]:1};}
const HX=s=>String(s).replace('#','').toLowerCase();
// A glyph came in as a frame of vectors. Repainting it is cheaper and safer
// than importing the drawing again, and it leaves the layer where it is.
function reglyph(nd,[oSt,nSt,oFl,nFl,oW,nW]){
  const vs = nd.type==='VECTOR' ? [nd] : nd.findAll(k=>k.type==='VECTOR'||k.type==='LINE'||k.type==='ELLIPSE'||k.type==='RECTANGLE');
  let hit=0;
  for(const v of vs){
    try{ if(nSt.length && Array.isArray(v.strokes) && v.strokes.length){ v.strokes=[C(HX(nSt[0]))]; hit++; } }catch(_){}
    try{ if(nFl.length && Array.isArray(v.fills) && v.fills.length){ v.fills=[C(HX(nFl[0]))]; hit++; } }catch(_){}
    try{ if(oW && nW && oW!==nW && typeof v.strokeWeight==='number') v.strokeWeight=v.strokeWeight*(nW/oW); }catch(_){}
  }
  return hit;
}
let applied=0, blocked=[], astray=[], seen=0;
function run(frame,name){
  seen++;
  for(const [path,kind,val,nm,top] of PLAN[name]){
    let nd=frame, ok=true, first=true;
    for(const i of path){
      // The first step is allowed to look for its child by name, because a
      // screen whose backdrop was rebuilt has one fewer child than the tree
      // this path was counted from.
      if(first){ first=false;
        const c=nd.children||[];
        if(top && (!c[i] || c[i].name!==top)){
          const j=c.findIndex(k=>k.name===top);
          if(j<0){ astray.push(name+' no top '+top); ok=false; break; }
          nd=c[j]; continue;
        }
      }
      if(nd.type==='INSTANCE'){ blocked.push(name+' '+path.join('.')); ok=false; break; }
      if(!nd.children || !nd.children[i]){ astray.push(name+' '+path.join('.')+' missing'); ok=false; break; }
      nd=nd.children[i];
    }
    if(!ok) continue;
    // The last step names what it expects to find. Anything else and this
    // path has drifted, so it is reported instead of painted over.
    const want=String(nm).slice(0,12), got=String(nd.name).slice(0,12);
    if(kind!==2 && want && got!==want && !got.startsWith(want.slice(0,8))){ astray.push(name+' '+path.join('.')+' is '+got); continue; }
    try{
      if(kind===0) nd.fills = val ? [C(val)] : [];
      else if(kind===1) nd.fills = [C(val)];
      else if(kind===3) nd.strokes = val ? [C(val)] : [];
      else reglyph(nd,val);
      applied++;
    }catch(e){ astray.push(name+' '+path.join('.')+' '+String(e.message||e).slice(0,40)); }
  }
}
`;

function script(names, targets) {
  const plan = {}; for (const n of names) plan[n] = PLAN[n];
  let tail;
  if (targets.page) {
    tail = `
const pg = await figma.getNodeByIdAsync(${JSON.stringify(targets.page)});
await figma.setCurrentPageAsync(pg);
const done=[];
for(const s of pg.children){ if(s.type!=='SECTION') continue;
  for(const f of s.children){ if(PLAN[f.name]){ if(f.type==='INSTANCE'){ blocked.push(f.name+' whole frame'); continue; } run(f,f.name); done.push(f.name); } } }
return {applied, frames:seen, painted:done.length, blocked:blocked.slice(0,12), astray:astray.slice(0,12), nBlocked:blocked.length, nAstray:astray.length};`;
  } else {
    tail = `
const IDS=${JSON.stringify(targets.ids)};
for(const [id,name] of Object.entries(IDS)){
  const nd=await figma.getNodeByIdAsync(id);
  if(!nd){ astray.push('no node '+id); continue; }
  if(!PLAN[name]){ astray.push('no plan '+name); continue; }
  run(nd,name);
}
return {applied, frames:seen, blocked:blocked.slice(0,12), astray:astray.slice(0,12), nBlocked:blocked.length, nAstray:astray.length};`;
  }
  return 'const PLAN=' + JSON.stringify(plan) + ';' + RUNNER + tail;
}

let targets;
if (IDS) {
  const ids = {}; for (const p of IDS.split(',')) { const [a, b] = p.split('='); ids[a] = b; }
  targets = { ids };
} else targets = { page: PAGE || '127:2' };

const names = (ONLY.length ? ONLY : Object.keys(PLAN)).filter(n => PLAN[n]);
const dir = SP + '/figma/recolor';
fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
let batch = [], out = [];
const flush = () => { if (!batch.length) return; const s = script(batch, targets);
  out.push({ n: out.length + 1, names: batch.slice(), chars: s.length });
  fs.writeFileSync(dir + '/' + (out.length) + '.js', s); batch = []; };
for (const n of names) {
  batch.push(n);
  if (script(batch, targets).length > CAP) { batch.pop(); flush(); batch.push(n); }
}
flush();
for (const b of out) console.log(String(b.n).padStart(2), String(b.chars).padStart(6), b.names.join(' '));
