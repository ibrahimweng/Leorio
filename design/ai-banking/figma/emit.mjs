// Turns the extracted screens into the JavaScript that use_figma runs.
//
// Screens are packed several to a script, because the code that rebuilds them
// is the same for all of them and the tool takes the script as one string.
import fs from 'fs';
const SP = process.env.SP;
const ORDER = ['Main','Actions','Receive','Ask','Answer','Pay','Done','History','Settings',
               'Services','Airtime','PowerPay','Power','Bills','Loan','Card','Goal','Rules',
               'Paused','Chat','Confirm','Scan','Pick','Found'];

// How far a child may move when auto layout takes over, in pixels. Below one
// pixel nothing is visible, and anything that drifts further gets placed by
// hand instead, so the screen always looks like the screen.
const TOL = 1;
// The tool caps a script at 50,000 characters. This sits well under it so a
// whole script can also be read in one go while working on it.
const CAP = 40000;

const RUNNER = `
const F='Plus Jakarta Sans';
const ST=w=>w>=800?'ExtraBold':w>=700?'Bold':'Regular';
for(const s of ['Regular','Bold','ExtraBold','Italic']) await figma.loadFontAsync({family:F,style:s});
function C(h){const a=String(h).split('|'),v=a[0];
  return {c:{r:parseInt(v.slice(0,2),16)/255,g:parseInt(v.slice(2,4),16)/255,b:parseInt(v.slice(4,6),16)/255},o:a[1]!==undefined?+a[1]:1};}
function P(h){const x=C(h);return {type:'SOLID',color:x.c,opacity:x.o};}
function GT(d){const r=(d-90)*Math.PI/180,cs=Math.cos(r),sn=Math.sin(r);
  return [[cs,sn,0.5-0.5*cs-0.5*sn],[-sn,cs,0.5+0.5*sn-0.5*cs]];}

let errs=[], made=0, autos=0, kept=0, undone=0;

// Paint, edge and depth. Everything a frame needs to look like the element it
// came from.
function dress(nd,n){
  const fl=[];
  if(n.bg) fl.push(P(n.bg));
  if(n.g) fl.push({type:'GRADIENT_LINEAR',gradientTransform:GT(n.g.deg),
    gradientStops:n.g.stops.map(s=>{const c=C(s.c);return {position:s.p,color:{r:c.c.r,g:c.c.g,b:c.c.b,a:c.o}};})});
  nd.fills=fl;
  if(n.r){nd.topLeftRadius=n.r[0];nd.topRightRadius=n.r[1];nd.bottomRightRadius=n.r[2];nd.bottomLeftRadius=n.r[3];}
  if(n.sw){
    nd.strokes=[P(n.sc)]; nd.strokeAlign='INSIDE';
    const u=n.sw.every(v=>v===n.sw[0]);
    if(u){ nd.strokeWeight=n.sw[0]||0.01; }
    else { nd.strokeWeight=Math.max.apply(null,n.sw)||0.01;
      nd.strokeTopWeight=n.sw[0];nd.strokeRightWeight=n.sw[1];nd.strokeBottomWeight=n.sw[2];nd.strokeLeftWeight=n.sw[3]; }
    if(n.sd) nd.dashPattern=[4,4];
  }
  const ef=[];
  if(n.sh) for(const s of n.sh){const c=C(s.c);
    ef.push({type:'DROP_SHADOW',color:{r:c.c.r,g:c.c.g,b:c.c.b,a:c.o},offset:{x:s.x,y:s.y},radius:s.b,spread:s.s,visible:true,blendMode:'NORMAL'});}
  if(n.bl) ef.push({type:'BACKGROUND_BLUR',radius:n.bl,visible:true});
  if(ef.length) nd.effects=ef;
}

// Builds one node and everything under it, placed by hand. Nothing reflows
// yet, so at the end of this the screen is exactly what the browser drew.
function build(n,parent){
  let nd=null;
  try{
    if(n.t===2){
      nd=figma.createNodeFromSvg(V[n.s]);
      nd.name=n.n||'Glyph';
      if(Math.abs(nd.width-n.w)>0.5 && nd.width>0) nd.rescale(n.w/nd.width);
    } else if(n.t===1){
      nd=figma.createText();
      nd.fontName={family:F,style:n.i?'Italic':ST(n.fw)};
      nd.characters=n.s;
      nd.fontSize=n.fs;
      const cc=C(n.c);
      nd.fills=[{type:'SOLID',color:cc.c,opacity:cc.o}];
      if(n.lh) nd.lineHeight={unit:'PIXELS',value:n.lh};
      if(n.ls) nd.letterSpacing={unit:'PIXELS',value:n.ls};
      nd.textAlignVertical='TOP';
      // Figma sets type a hair wider than the browser, so a line pinned to a
      // measured width would re-wrap. Only text that already wrapped is pinned.
      // A line the browser cut off keeps the width it was allowed, and Figma
      // does the cutting, so it cannot run over what sits beside it.
      if(n.tr){ nd.textAutoResize='NONE'; nd.resize(n.w,n.h);
        try{ nd.textTruncation='ENDING'; }catch(_){}
        if(n.ta) nd.textAlignHorizontal=n.ta.toUpperCase(); }
      else if(n.ml){ nd.textAutoResize='HEIGHT'; nd.resize(n.w+4,n.h); if(n.ta) nd.textAlignHorizontal=n.ta.toUpperCase(); }
      else { nd.textAutoResize='WIDTH_AND_HEIGHT'; }
      nd.name=n.n||n.s.slice(0,30);
    } else {
      nd=figma.createFrame();
      nd.name=n.n||'Frame';
      nd.resize(n.w,n.h);
      nd.fills=[];
      // A frame clips by default and CSS does not, so only the ones that said
      // overflow hidden clip. The artboard itself is handled by the caller.
      nd.clipsContent=!!n.clip;
      dress(nd,n);
      parent.appendChild(nd);
      nd.x=n.x; nd.y=n.y;
      if(n.o!==undefined&&n.o<1) nd.opacity=n.o;
      made++;
      for(const k of (n.k||[])) build(k,nd);
      return nd;
    }
    if(n.o!==undefined&&n.o<1) nd.opacity=n.o;
    parent.appendChild(nd);
    nd.x=n.x; nd.y=n.y;
    made++;
  }catch(e){ if(nd&&nd.parent) nd.remove(); errs.push(String(e.message||e).slice(0,110)); }
  return nd;
}

// Then the layout pass. A flex container becomes an auto layout frame, and
// every child is checked against where the browser put it. If anything moved,
// that one frame goes back to placing its children by hand. So the file gets
// auto layout wherever auto layout is honest, and never at the cost of the
// design.
function tune(nd,n){
  const kids=n.k||[];
  for(let i=0;i<kids.length;i++){
    if(kids[i].t===0 && nd.children[i]) tune(nd.children[i],kids[i]);
  }
  if(!n.L || nd.children.length!==kids.length || !nd.children.length) return;
  autos++;
  const save=nd.children.map(c=>({x:c.x,y:c.y,w:c.width,h:c.height}));
  try{
    nd.layoutMode = n.L.d==='V' ? 'VERTICAL' : 'HORIZONTAL';
    nd.itemSpacing=n.L.gap||0;
    nd.paddingTop=n.L.p?n.L.p[0]:0; nd.paddingRight=n.L.p?n.L.p[1]:0;
    nd.paddingBottom=n.L.p?n.L.p[2]:0; nd.paddingLeft=n.L.p?n.L.p[3]:0;
    nd.primaryAxisAlignItems=n.L.ji;
    // BASELINE is only a thing on a row.
    nd.counterAxisAlignItems=(n.L.ai==='BASELINE'&&nd.layoutMode!=='HORIZONTAL')?'MIN':n.L.ai;
    // resize first: it resets both sizing modes, so setting them after is what
    // makes the frame hold the size the browser gave it.
    nd.resize(n.w,n.h);
    nd.primaryAxisSizingMode='FIXED';
    nd.counterAxisSizingMode='FIXED';
    // Every child holds the size it measured. Text is left hugging, because a
    // pinned width is what makes it wrap.
    for(let i=0;i<nd.children.length;i++){
      const c=nd.children[i], g=kids[i].gr;
      if(c.type!=='TEXT'){ c.layoutSizingHorizontal='FIXED'; c.layoutSizingVertical='FIXED'; }
      // The one child that grows takes the slack, which is what puts the
      // chevron against the right edge instead of beside the label.
      if(g){ try{ c[nd.layoutMode==='HORIZONTAL'?'layoutSizingHorizontal':'layoutSizingVertical']='FILL'; }catch(_){} }
    }
    let drift=0;
    for(let i=0;i<nd.children.length;i++){
      drift=Math.max(drift,Math.abs(nd.children[i].x-kids[i].x),Math.abs(nd.children[i].y-kids[i].y));
    }
    if(drift>TOL) throw new Error('drift');
    kept++;
  }catch(e){
    nd.layoutMode='NONE';
    for(let i=0;i<nd.children.length;i++){
      const c=nd.children[i],s=save[i];
      try{ if(Math.abs(c.width-s.w)>0.01||Math.abs(c.height-s.h)>0.01) c.resize(s.w,s.h); }catch(_){}
      c.x=s.x; c.y=s.y;
    }
    undone++;
  }
}

// Where the screens land. A file somebody has arranged by hand should keep
// its arrangement, and a name is not a safe way to find a frame once there
// are copies of it, so a caller may name the page and hand each screen the
// exact node it replaces and the spot it sits in. Without that it falls back
// to matching on name and to the grid.
const PAGE_ID = (typeof PAGE !== 'undefined') ? PAGE : null;
const AT = (typeof PLACE !== 'undefined') ? PLACE : {};
const page = PAGE_ID ? await figma.getNodeByIdAsync(PAGE_ID) : figma.currentPage;
if(PAGE_ID) await figma.setCurrentPageAsync(page);
const out=[], ids=[];
for(const S of SCREENS){
  errs=[]; made=0; autos=0; kept=0; undone=0;
  const at=AT[S.name];
  const old = (at && at.id) ? await figma.getNodeByIdAsync(at.id)
                            : page.children.find(n=>n.name===S.name);
  const took = old ? old.id : null;
  if(old) old.remove();
  const fr=figma.createFrame();
  fr.name=S.name; fr.resize(S.D.w,S.D.h);
  fr.x = at ? at.x : S.X; fr.y = at ? at.y : S.Y;
  fr.fills=[P(S.D.bg)]; fr.clipsContent=true; fr.cornerRadius=0;
  page.appendChild(fr);
  for(const n of S.D.k) build(n,fr);
  for(let i=0;i<S.D.k.length;i++) if(S.D.k[i].t===0 && fr.children[i]) tune(fr.children[i],S.D.k[i]);
  ids.push(fr.id);
  out.push({name:S.name, frame:fr.id, replaced:took, at:[fr.x,fr.y], made,
            autoLayout:kept+'/'+autos, placedByHand:undone, errs:errs.slice(0,4)});
}
return {createdNodeIds:ids, page:page.name, screens:out};
`;

const STEP_X = 493, STEP_Y = 972, COLS = 9;

const which = process.argv.slice(2);
const list = which.length ? which : ORDER;

// The comments are for whoever reads this file, not for the tool.
const CODE = RUNNER.split('\n').filter(l => !/^\s*\/\//.test(l)).join('\n');

const loaded = list.map(name => {
  const i = ORDER.indexOf(name);
  const data = JSON.parse(fs.readFileSync(SP + '/figma/' + name + '.json', 'utf8'));
  (function go(nodes) {
    for (const n of nodes) {
      for (const k of ['x','y','w','h']) if (typeof n[k] === 'number') n[k] = Math.round(n[k] * 10) / 10;
      if (n.k) go(n.k);
    }
  })(data.k);
  return { name, X: (i % COLS) * STEP_X, Y: Math.floor(i / COLS) * STEP_Y, D: data };
});

// One script. Every glyph in it is lifted into a lookup shared by the screens
// in this script and no others, because a lookup covering all eighteen would
// cost more than it saves.
function render(group) {
  const V = [], seen = new Map();
  const screens = JSON.parse(JSON.stringify(group));
  for (const s of screens) {
    (function go(nodes) {
      for (const n of nodes) {
        if (n.t === 2) {
          const svg = n.s.replace(/\s*style="[^"]*"/g, '');
          if (!seen.has(svg)) { seen.set(svg, V.length); V.push(svg); }
          n.s = seen.get(svg);
        }
        if (n.k) go(n.k);
      }
    })(s.D.k);
  }
  return 'const TOL=' + TOL + ';const V=' + JSON.stringify(V)
       + ';const SCREENS=' + JSON.stringify(screens) + ';' + CODE;
}

// Grow a script one screen at a time and measure it each time, since how much
// the lookup saves depends on which screens ended up together.
const bundles = [];
let group = [];
for (const s of loaded) {
  const tryIt = group.concat([s]);
  if (group.length && render(tryIt).length > CAP) { bundles.push(group); group = [s]; }
  else group = tryIt;
}
if (group.length) bundles.push(group);

fs.mkdirSync(SP + '/figma/bundle', { recursive: true });
bundles.forEach((b, i) => {
  const js = render(b);
  fs.writeFileSync(SP + '/figma/bundle/' + (i + 1) + '.js', js);
  console.log((i + 1) + '  ' + String(js.length).padStart(6) + '  ' + b.map(s => s.name).join(' '));
});
