// Node for node, in place. Where a Figma frame holds exactly as many text nodes
// as the screen it was built from, every one of them can be brought up to date
// without touching a single frame: the style binding first, then the words, the
// colour and the box. Nothing is created and nothing is removed, so every
// reaction on the page survives. Fails loudly when the counts do not agree.
//
// Typography goes to whichever node owns it. A line inside a shared part -- the
// ask bar, the keyboard, a button -- has its size and weight set on the part
// itself, so the part is brought up to date once instead of being overridden on
// every screen that uses it. The words, the colour and the box stay on the
// screen, because that is where they differ.
import fs from 'fs';
const SP = process.env.SP;
const ST = w => w >= 700 ? 'Bold' : w >= 600 ? 'Semibold' : w >= 500 ? 'Medium' : 'Regular';
const WT = ['Regular', 'Medium', 'Semibold', 'Bold'];
export const SN = ['Display/Bold 32', 'Heading/Semibold 20', 'Body/Semibold 16', 'Body/Regular 16',
                   'Label/Semibold 14', 'Label/Regular 14', 'Caption/Semibold 12', 'Caption/Regular 12'];
// One line, as short as it can be written. A line with a style needs nothing
// said about its size, weight, leading or tracking -- the style is all four --
// so those are only spelled out for the handful that have no style. The box
// only travels with lines that wrapped or were cut off; the rest size to fit.
const row = n => {
  const f = (n.ml ? 1 : 0) | (n.tr ? 2 : 0);
  const r = [n.s, n.c, SN.indexOf(n.sn || ''), f];
  if (f) r.push(Math.round(n.w), Math.round(n.h));
  if (r[2] < 0) { while (r.length < 6) r.push(0);
                  r.push(n.fs, WT.indexOf(ST(n.fw)), n.lh || 0, +(n.ls || 0).toFixed(2),
                         n.ff || '', n.i ? 1 : 0); }
  return r;
};
const rows = d => { const o = []; (function w(n) {
  if (n.t === 1) o.push(row(n));
  (n.k || []).forEach(w); })({ k: d.k }); return o; };

// What a line already is, written down the same way from either side. Ask Figma
// for this before sending anything and most lines turn out to be right already,
// so the payload carries only the ones that are not. A line with a style needs
// no size, weight, leading or tracking in the record -- the style is all four.
// Only a box that was measured is compared; a line that sizes itself has no box
// worth arguing about.
const H = s => { let h = 2166136261 >>> 0;
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619) >>> 0; }
  return ('00000' + h.toString(36)).slice(-5); };

// The build's side of the record.
const want = n => {
  const ty = n.sn ? n.sn : [n.fs, ST(n.fw), n.lh || 0, (+(n.ls || 0)).toFixed(2), n.ff || '', n.i ? 1 : 0].join('/');
  return H([n.s, ty, n.c].join('~|~'));
};

// Figma's side of the same record, as source, because it has to run over there.
export const READ =
`const SNM={}; for(const st of await figma.getLocalTextStylesAsync()) SNM[String(st.id).replace(/,$/,'')]=st.name;
const H=s=>{let h=2166136261>>>0;
  for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}
  return ('00000'+h.toString(36)).slice(-5);};
const X=v=>v===figma.mixed?'~':v;
function hex(nd){const f=nd.fills; if(!Array.isArray(f)||!f.length||f[0].type!=='SOLID')return '~';
  const c=f[0].color,p=v=>('0'+Math.round(v*255).toString(16)).slice(-2),o=f[0].opacity===undefined?1:f[0].opacity;
  return p(c.r)+p(c.g)+p(c.b)+(o<1?'|'+(+o.toFixed(2)):'');}
function rec(nd){
  const sn=SNM[String(nd.textStyleId).replace(/,\$/,'')]||'';
  const fn=nd.fontName,ls=nd.letterSpacing,lh=nd.lineHeight;
  const ty=sn?sn:[X(nd.fontSize),fn===figma.mixed?'~':fn.style,
    lh===figma.mixed?'~':lh.unit==='PIXELS'?lh.value:0,
    (ls===figma.mixed?0:ls.unit==='PIXELS'?ls.value:ls.value/100*(nd.fontSize||0)).toFixed(2),
    fn===figma.mixed?'':fn.family==='SF Pro Text'?'':fn.family,
    fn!==figma.mixed&&fn.style==='Italic'?1:0].join('/');
  return H([nd.characters,ty,hex(nd)].join('~|~'));}
const D={};
for(const [n,t] of Object.entries(TG)){
  const fr=await figma.getNodeByIdAsync(t);
  D[n]=fr?fr.findAll(x=>x.type==='TEXT').map(rec).join(''):'missing';}
return D;
`;

// A screen may carry a line the build does not: Figma nests the whole home
// screen, dock and all, where the build draws the page without it. Those are
// named by their Figma index and simply stepped over, so everything after them
// still lines up.
export function payload(name, target, digest, skip) {
  const d = JSON.parse(fs.readFileSync(SP + '/figma/' + name + '.json', 'utf8'));
  const all = [];
  (function w(n) { if (n.t === 1) all.push(n); (n.k || []).forEach(w); })({ k: d.k });
  skip = skip || [];
  const n = all.length + skip.length;
  if (digest && digest.length !== n * 5)
    throw new Error(name + ': digest has ' + digest.length / 5 + ' lines, build has ' + n);
  const fig = []; for (let i = 0, j = 0; i < n; i++) if (!skip.includes(i)) fig[j++] = i;
  // Only the lines that are not already right travel. The rest are already
  // saying the right thing in the right size and do not need touching.
  const R = all.map((b, i) => (digest && digest.substr(fig[i] * 5, 5) === want(b)) ? null : [fig[i]].concat(row(b)))
               .filter(Boolean);
  return { name, target, n, rows: R, edits: R.length,
           js: `await go(${JSON.stringify(target)},${JSON.stringify(name)},${n},${JSON.stringify(R)});\n` };
}

// The head is shared by every screen in a batch: the style table, the colours,
// the font loader, the rule for finding the node that owns a line's typography
// -- the nearest instance above it, mapped back to its component -- and the
// walk itself, written once instead of once per screen.
export const head = pg =>
`await figma.setCurrentPageAsync(figma.root.children.find(p=>p.name===${JSON.stringify(pg)}));
const SN=${JSON.stringify(SN)},WT=${JSON.stringify(WT)};
const SID={}; for(const st of await figma.getLocalTextStylesAsync()) SID[st.name]=st.id;
for(const n of SN) if(!SID[n]) throw new Error('no text style ' + n);
function C(h){const a=String(h).split('|'),v=a[0];
  return {c:{r:parseInt(v.slice(0,2),16)/255,g:parseInt(v.slice(2,4),16)/255,b:parseInt(v.slice(4,6),16)/255},o:a[1]!==undefined?+a[1]:1};}
const OUT={},MUT=[],SKIP=[],SEEN={};
async function load(fn){const k=fn.family+'|'+fn.style; if(SEEN[k])return; await figma.loadFontAsync(fn); SEEN[k]=1;}
async function face(nd){for(const g of nd.getStyledTextSegments(['fontName'])) await load(g.fontName);}
const OWN=new Map();
async function own(nd,root){
  let p=nd.parent,inst=null;
  while(p&&p!==root){ if(p.type==='INSTANCE'){ inst=p; break; } p=p.parent; }
  if(!inst) return nd;
  let m=OWN.get(inst.id);
  if(m===undefined){ const mc=await inst.getMainComponentAsync();
    m=mc?{a:inst.findAll(x=>x.type==='TEXT'),b:mc.findAll(x=>x.type==='TEXT')}:null;
    if(m&&m.a.length!==m.b.length) m=null;
    OWN.set(inst.id,m); }
  if(!m) return nd;
  const i=m.a.indexOf(nd);
  return i>=0?m.b[i]:nd;
}
async function go(T,N,COUNT,R){
  const fr=await figma.getNodeByIdAsync(T);
  if(!fr) throw new Error('no node '+T+' for '+N);
  const t=fr.findAll(n=>n.type==='TEXT');
  if(t.length!==COUNT) throw new Error(N+': expected '+COUNT+' texts, found '+t.length);
  let styled=0,sized=0,worded=0,filled=0,boxed=0,part=0;
  for(const [i,s,hx,si,f,w,h,fs,fw,lh,ls,ff,it] of R){
    const nd=t[i];
    const ty=await own(nd,fr); if(ty!==nd) part++;
    await face(ty); await face(nd);
    // The style carries size, weight, leading and tracking together, so where a
    // line has one the binding is the whole of its typography.
    if(si>=0){
      for(const q of (ty===nd?[nd]:[ty,nd])){
        if(q.textStyleId!==SID[SN[si]]){ await q.setTextStyleIdAsync(SID[SN[si]]); styled++; }
      }
    }
    else {
      const fn={family:ff||'SF Pro Text',style:it?'Italic':WT[fw]};
      await load(fn);
      for(const q of (ty===nd?[nd]:[ty,nd])){
        const cur=q.fontName;
        if(cur===figma.mixed||cur.family!==fn.family||cur.style!==fn.style){ q.fontName=fn; sized++; }
        if(q.fontSize!==fs){ q.fontSize=fs; sized++; }
        if(lh&&(q.lineHeight.unit!=='PIXELS'||Math.abs(q.lineHeight.value-lh)>0.01)) q.lineHeight={unit:'PIXELS',value:lh};
        if(q.letterSpacing.unit!=='PIXELS'||Math.abs(q.letterSpacing.value-ls)>0.02) q.letterSpacing={unit:'PIXELS',value:ls};
      }
    }
    if(nd.characters!==s){ nd.characters=s; worded++; }
    const cc=C(hx), fl=nd.fills;
    const eq=(a,b)=>Math.round(a*255)===Math.round(b*255);
    const same=Array.isArray(fl)&&fl.length===1&&fl[0].type==='SOLID'
      &&eq(fl[0].color.r,cc.c.r)&&eq(fl[0].color.g,cc.c.g)&&eq(fl[0].color.b,cc.c.b)
      &&Math.abs((fl[0].opacity===undefined?1:fl[0].opacity)-cc.o)<0.01;
    if(!same){ nd.fills=[{type:'SOLID',color:cc.c,opacity:cc.o}]; filled++; }
    // A line the browser cut off keeps the width it was allowed and Figma does
    // the cutting; a line that wrapped keeps its width and finds its own height;
    // everything else is left to size itself, which is what type wants to do.
    const wa=(f&2)?'NONE':(f&1)?'HEIGHT':'WIDTH_AND_HEIGHT';
    try{
      if(nd.textAutoResize!==wa){ nd.textAutoResize=wa; boxed++; }
      if(f&2){ if(Math.abs(nd.width-w)>0.5||Math.abs(nd.height-h)>0.5){ nd.resize(w,h); boxed++; }
               try{ nd.textTruncation='ENDING'; }catch(_){} }
      else { try{ nd.textTruncation='DISABLED'; }catch(_){}
             if((f&1)&&Math.abs(nd.width-(w+4))>0.5){ nd.resize(w+4,nd.height); boxed++; } }
    }catch(e){ SKIP.push(N+' #'+i+' '+String(e.message||e).slice(0,50)); }
    if(nd.name.length<32){ const nn=s.slice(0,30); if(nd.name!==nn) nd.name=nn; }
  }
  OUT[N]={texts:t.length,edits:R.length,styled,sized,worded,filled,boxed,part};
  MUT.push(fr.id);
}
`;
export const VERIFY = READ.split('const D={};')[0] + `const OFF={},BAD={};
for(const [n,[t,total,spec]] of Object.entries(W)){
  const fr=await figma.getNodeByIdAsync(t);
  if(!fr){ BAD[n]='missing'; continue; }
  const nodes=fr.findAll(x=>x.type==='TEXT');
  if(nodes.length!==total){ BAD[n]='has '+nodes.length+' lines, wanted '+total; continue; }
  const off=[];
  for(const pair of spec.split(',')){ const j=pair.indexOf(':');
    const i=+pair.slice(0,j), h=pair.slice(j+1);
    if(rec(nodes[i])!==h) off.push(i+' '+JSON.stringify(nodes[i].characters.slice(0,28))); }
  if(off.length) OFF[n]=off;
}
return {screens:Object.keys(W).length, wrongShape:BAD,
        offCount:Object.values(OFF).reduce((a,b)=>a+b.length,0), off:OFF};
`;

export const TAIL = `return {mutatedNodeIds:MUT,screens:OUT,skipped:SKIP};`;

// Run directly: node retype.mjs <targets.json> [maxChars]. Writes retype-N.js
// batches into $SP/figma, smallest first, holding each one under Figma's limit.
// Screens that sit inside other screens go first, so the container finds them
// already right and writes nothing.
const ALIAS = { Main: 'Home screen' };
const page = e => e[1] === 'MAIN' ? 'Components' : 'Flows';

if (process.argv[1] && process.argv[1].endsWith('retype.mjs')) {
  const T = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  // The proof: send what every line ought to be and let Figma say which ones
  // are not. A short answer to a long question.
  // Put right exactly the lines the check named, and nothing else.
  if (process.argv[3] === '--fix') {
    const FIX = JSON.parse(fs.readFileSync(SP + '/fix.json', 'utf8'));
    const SKIP = fs.existsSync(SP + '/skip.json') ? JSON.parse(fs.readFileSync(SP + '/skip.json', 'utf8')) : {};
    for (const pg of ['Components', 'Flows']) {
      const parts = [];
      for (const [n, want] of Object.entries(FIX)) {
        const e = T[ALIAS[n] || n]; if (!e || page(e) !== pg) continue;
        const p = payload(n, e[0], null, SKIP[n]);
        const rows = p.rows.filter(r => want.includes(r[0]));
        parts.push(`await go(${JSON.stringify(e[0])},${JSON.stringify(n)},${p.n},${JSON.stringify(rows)});\n`);
      }
      if (!parts.length) continue;
      fs.writeFileSync(SP + '/figma/fix-' + pg + '.js', head(pg) + parts.join('') + TAIL);
      console.log(pg + ': ' + parts.length + ' screens, ' + (head(pg).length + parts.join('').length) + ' chars');
    }
    process.exit(0);
  }
  if (process.argv[3] === '--verify') {
    const counts = JSON.parse(fs.readFileSync(SP + '/counts.json', 'utf8'));
    const SKIP = fs.existsSync(SP + '/skip.json') ? JSON.parse(fs.readFileSync(SP + '/skip.json', 'utf8')) : {};
    for (const pg of ['Flows', 'Components']) {
      const W = {};
      for (const n of Object.keys(counts)) {
        const e = T[ALIAS[n] || n]; if (!e || page(e) !== pg) continue;
        const d = JSON.parse(fs.readFileSync(SP + '/figma/' + n + '.json', 'utf8'));
        const all = []; (function w(x) { if (x.t === 1) all.push(x); (x.k || []).forEach(w); })({ k: d.k });
        const skip = SKIP[n] || [], total = all.length + skip.length;
        const fig = []; for (let i = 0, j = 0; i < total; i++) if (!skip.includes(i)) fig[j++] = i;
        W[n] = [e[0], total, fig.map((f, i) => f + ':' + want(all[i])).join(',')];
      }
      fs.writeFileSync(SP + '/figma/verify-' + pg + '.js',
        "await figma.setCurrentPageAsync(figma.root.children.find(p=>p.name===" + JSON.stringify(pg) + "));\n"
        + 'const W=' + JSON.stringify(W) + ';\n' + VERIFY);
      console.log(pg + ': ' + Object.keys(W).length + ' screens');
    }
    process.exit(0);
  }
  if (process.argv[3] === '--read') {
    const counts = JSON.parse(fs.readFileSync(SP + '/counts.json', 'utf8'));
    for (const pg of ['Flows', 'Components']) {
      const TG = {};
      for (const n of Object.keys(counts)) { const e = T[ALIAS[n] || n]; if (e && page(e) === pg) TG[n] = e[0]; }
      fs.writeFileSync(SP + '/figma/digest-' + pg + '.js',
        "await figma.setCurrentPageAsync(figma.root.children.find(p=>p.name===" + JSON.stringify(pg) + "));\n"
        + 'const TG=' + JSON.stringify(TG) + ';\n' + READ);
      console.log(pg + ': ' + Object.keys(TG).length + ' screens');
    }
    process.exit(0);
  }
  const MAX = +(process.argv[3] || 44000);
  const counts = JSON.parse(fs.readFileSync(SP + '/counts.json', 'utf8'));
  const DG = JSON.parse(fs.readFileSync(SP + '/digest.json', 'utf8'));
  const SKIP = fs.existsSync(SP + '/skip.json') ? JSON.parse(fs.readFileSync(SP + '/skip.json', 'utf8')) : {};
  const inner = n => /^(Done|Power$|Confirm)/.test(n) ? 0 : /^(Share|NoFace)/.test(n) ? 2 : 1;
  const names = Object.keys(counts).filter(n => T[ALIAS[n] || n] && DG[n]
                        && DG[n].length / 5 === counts[n] + ((SKIP[n] || []).length))
                      .sort((a, b) => inner(a) - inner(b) || a.localeCompare(b));
  const skipped = Object.keys(counts).filter(n => !names.includes(n));
  const batches = []; let live = 0, total = 0;
  for (const pg of ['Components', 'Flows']) {
    let cur = [], len = 4000;
    for (const n of names.filter(n => page(T[ALIAS[n] || n]) === pg)) {
      const p = payload(n, T[ALIAS[n] || n][0], DG[n], SKIP[n]);
      total += p.n; live += p.edits;
      if (!p.edits) continue;
      if (cur.length && len + p.js.length > MAX) { batches.push([pg, cur]); cur = []; len = 4000; }
      cur.push(p); len += p.js.length;
    }
    if (cur.length) batches.push([pg, cur]);
  }
  batches.forEach(([pg, b], i) => {
    const js = head(pg) + b.map(p => p.js).join('') + TAIL;
    fs.writeFileSync(SP + '/figma/retype-' + (i + 1) + '.js', js);
    console.log('batch ' + String(i + 1).padStart(2) + '  ' + pg.padEnd(11) + String(b.length).padStart(2)
                + ' screens  ' + String(js.length).padStart(6) + ' chars  ' + b.map(p => p.name).join(' '));
  });
  console.log('\n' + live + ' of ' + total + ' lines need sending');
  console.log('not sent (' + skipped.length + '): ' + skipped.join(' '));
}
