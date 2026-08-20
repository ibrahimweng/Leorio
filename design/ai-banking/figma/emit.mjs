// Turns one extracted screen into the JavaScript that use_figma runs.
import fs from 'fs';
const SP = process.env.SP;
const ORDER = ['Main','Actions','Receive','Ask','Answer','Pay','Done','History','Settings',
               'Services','Airtime','PowerPay','Power','Bills','Loan','Card','Goal','Rules'];

const RUNNER = `
const F='Plus Jakarta Sans';
const ST=w=>w>=800?'ExtraBold':w>=700?'Bold':'Regular';
for(const s of ['Regular','Bold','ExtraBold','Italic']) await figma.loadFontAsync({family:F,style:s});
function C(h){const a=String(h).split('|'),v=a[0];
  return {c:{r:parseInt(v.slice(0,2),16)/255,g:parseInt(v.slice(2,4),16)/255,b:parseInt(v.slice(4,6),16)/255},o:a[1]!==undefined?+a[1]:1};}
function P(h){const x=C(h);return {type:'SOLID',color:x.c,opacity:x.o};}
function GT(d){const r=(d-90)*Math.PI/180,cs=Math.cos(r),sn=Math.sin(r);
  return [[cs,sn,0.5-0.5*cs-0.5*sn],[-sn,cs,0.5+0.5*sn-0.5*cs]];}
const page=figma.currentPage;
const old=page.children.find(n=>n.name===NAME); if(old) old.remove();
const fr=figma.createFrame();
fr.name=NAME; fr.resize(D.w,D.h); fr.x=X; fr.y=Y;
fr.fills=[P(D.bg)]; fr.clipsContent=true;
fr.cornerRadius=0;
page.appendChild(fr);
let made=0, errs=[];
for(const n of D.nodes){
  let nd=null;
  try{
    if(n.t===2){
      nd=figma.createNodeFromSvg(typeof n.s==='number'?V[n.s]:n.s);
      nd.name='icon';
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
      if(n.ml){ nd.textAutoResize='HEIGHT'; nd.resize(n.w+4,n.h); if(n.ta) nd.textAlignHorizontal=n.ta.toUpperCase(); }
      else { nd.textAutoResize='WIDTH_AND_HEIGHT'; }
      nd.name=n.s.slice(0,30);
    } else {
      nd=figma.createRectangle();
      nd.resize(n.w,n.h);
      nd.name='shape';
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
        else { nd.strokeWeight=Math.max(...n.sw)||0.01;
          nd.strokeTopWeight=n.sw[0];nd.strokeRightWeight=n.sw[1];nd.strokeBottomWeight=n.sw[2];nd.strokeLeftWeight=n.sw[3]; }
        if(n.sd) nd.dashPattern=[4,4];
      }
      const ef=[];
      if(n.sh) for(const s of n.sh){const c=C(s.c);
        ef.push({type:'DROP_SHADOW',color:{r:c.c.r,g:c.c.g,b:c.c.b,a:c.o},offset:{x:s.x,y:s.y},radius:s.b,spread:s.s,visible:true,blendMode:'NORMAL'});}
      if(n.bl) ef.push({type:'BACKGROUND_BLUR',radius:n.bl,visible:true});
      if(ef.length) nd.effects=ef;
    }
    if(n.o!==undefined&&n.o<1) nd.opacity=n.o;
    fr.appendChild(nd);
    nd.x=n.x; nd.y=n.y;
    made++;
  }catch(e){ if(nd&&nd.parent) nd.remove(); errs.push(String(e.message||e).slice(0,120)); }
}
return {frame:fr.id, name:NAME, made, of:D.nodes.length, errs:errs.slice(0,6)};
`;

const STEP_X = 493, STEP_Y = 972, COLS = 9;
const which = process.argv.slice(2);
const list = which.length ? which : ORDER;
for (const name of list) {
  const i = ORDER.indexOf(name);
  const data = JSON.parse(fs.readFileSync(SP + '/figma/' + name + '.json', 'utf8'));
  const seen = new Map(), V = [];
  for (const n of data.nodes) {
    if (n.t !== 2) continue;
    // the same glyph shows up four or five times a screen, so store it once
    const svg = n.s.replace(/\s*style="[^"]*"/g, '');
    if (!seen.has(svg)) { seen.set(svg, V.length); V.push(svg); }
    n.s = seen.get(svg);
  }
  const round = o => { for (const k of ['x','y','w','h']) if (typeof o[k] === 'number') o[k] = Math.round(o[k] * 10) / 10; };
  data.nodes.forEach(round);
  const code = 'const NAME=' + JSON.stringify(name)
    + ';const X=' + ((i % COLS) * STEP_X) + ';const Y=' + (Math.floor(i / COLS) * STEP_Y) + ';'
    + 'const V=' + JSON.stringify(V) + ';'
    + 'const D=' + JSON.stringify(data) + ';' + RUNNER;
  fs.writeFileSync(SP + '/figma/' + name + '.js', code);
  console.log(name, code.length);
}
