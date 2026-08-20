# Builds prototype.html, a walkable version of the same screens.
# The screen markup comes from build.py, so there is one source of truth.
import os, build

OUT = os.path.dirname(os.path.abspath(__file__))
ACC = "#1B3B6F"

ORDER = ["Main", "Ask", "Services", "Airtime", "PowerPay", "Power", "Bills",
         "Loan", "Card", "Answer", "Pay", "Rules", "Done"]

screens = ""
for name in ORDER:
    inner = build.SCREENS[name].replace("{{accent}}", "var(--acc)")
    screens += '<section class="screen" data-screen="' + name + '">\n' + inner + '\n</section>\n'

CSS = """
:root{
  --acc:""" + ACC + """;
  --sur-bg:#E9EBEF; --sur-card:#FFFFFF; --sur-ink:#2B3340; --sur-ink2:#69738220;
  --sur-mid:#6B7686; --sur-line:#D6DAE1; --sur-shadow:0 24px 60px rgba(15,21,33,.16);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --sur-bg:#0F1216; --sur-card:#171B21; --sur-ink:#DCE0E7;
    --sur-mid:#8B94A2; --sur-line:#262C34; --sur-shadow:0 24px 60px rgba(0,0,0,.5);
  }
}
:root[data-theme="dark"]{
  --sur-bg:#0F1216; --sur-card:#171B21; --sur-ink:#DCE0E7;
  --sur-mid:#8B94A2; --sur-line:#262C34; --sur-shadow:0 24px 60px rgba(0,0,0,.5);
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  background:var(--sur-bg); color:var(--sur-ink);
  font-family:'Libre Franklin','Helvetica Neue',Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased; overflow:hidden;
  min-height:100vh; min-height:100dvh;
}
.wrap{display:flex; flex-direction:column; align-items:center; justify-content:center;
  gap:22px; height:100vh; height:100dvh; padding:0}
body.desk .wrap{padding:24px 20px}
.device{position:relative; flex-shrink:0; overflow:hidden; background:#F4F5F7}
body.desk .device{border-radius:42px; box-shadow:var(--sur-shadow), 0 0 0 9px #14171C, 0 0 0 10px #2B313A}
.stage{width:393px; transform-origin:top left; position:relative}
.screen{position:absolute; inset:0; display:none; will-change:transform; background:#F4F5F7}
.screen.live{display:block}
.screen .pg{position:absolute; inset:0; overflow-y:auto; overflow-x:hidden; -webkit-overflow-scrolling:touch}
.screen .pg::-webkit-scrollbar{width:0;height:0}
.screen[data-screen="Ask"] .fauxbg{
  position:absolute; inset:0; opacity:1 !important; padding:0 !important;
  background:rgba(15,21,33,.32); overflow:hidden}
.screen[data-screen="Ask"] .fauxbg > *{display:none !important}
[data-go],[data-act],.slide{cursor:pointer; -webkit-tap-highlight-color:transparent}
[data-go]:active,[data-act]:active{opacity:.62}
.knob{touch-action:none}
.legend{max-width:560px; color:var(--sur-mid); font-size:13.5px; line-height:1.6; text-align:center; display:none; margin:0}
.legend b{color:var(--sur-ink); font-weight:600}
.legend .row{margin-top:6px}
kbd{font:inherit; background:var(--sur-card); border:1px solid var(--sur-line);
  border-radius:6px; padding:1px 6px; color:var(--sur-ink)}
#toast{position:fixed; left:50%; bottom:36px; transform:translate(-50%,20px);
  background:#14171C; color:#F3F5F8; font-size:13.5px; font-weight:500;
  padding:11px 18px; border-radius:22px; opacity:0; pointer-events:none;
  transition:opacity .22s ease, transform .22s ease; z-index:60; max-width:80vw; text-align:center}
#toast.on{opacity:1; transform:translate(-50%,0)}
@media (prefers-reduced-motion: reduce){
  .screen,#toast{transition:none !important; animation:none !important}
}
"""

JS = r"""
(function(){
  var m = document.querySelector('meta[name=viewport]');
  if(!m){ m = document.createElement('meta'); m.name='viewport'; document.head.appendChild(m); }
  m.content = 'width=device-width,initial-scale=1,viewport-fit=cover,maximum-scale=1,user-scalable=no';
})();

var stage = document.getElementById('stage');
var device = document.getElementById('device');
var toastEl = document.getElementById('toast');
var screens = {};
[].forEach.call(document.querySelectorAll('.screen'), function(el){ screens[el.dataset.screen] = el; });

var REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
var EASE = 'cubic-bezier(.32,.72,0,1)';
var DUR = REDUCED ? 0 : 340;

/* ---------- sizing ---------- */
var legendEl = document.getElementById('legend');
function layout(){
  var W = window.innerWidth, H = window.innerHeight, s, sh;
  var desk = W >= 460;                       // anything wider than a phone gets the device frame
  var showLegend = desk && H >= 780;
  document.body.classList.toggle('desk', desk);
  legendEl.style.display = showLegend ? 'block' : 'none';
  if(desk){
    s = Math.max(0.5, Math.min(1, (H - (showLegend ? 156 : 52)) / 852));
    sh = 852;
  } else {
    s = Math.min(1.15, W / 393);             // a bigger phone gets a bigger app, but not a blown up one
    sh = Math.max(620, Math.round(H / s));
  }
  stage.style.transform = 'scale(' + s + ')';
  stage.style.height = sh + 'px';
  device.style.width = Math.round(393 * s) + 'px';
  device.style.height = Math.round(sh * s) + 'px';
  padDocks();
}
function padDocks(){
  [].forEach.call(document.querySelectorAll('.screen.live'), function(sc){
    var pg = sc.querySelector('.pg'), dock = sc.querySelector('.dock');
    if(pg) pg.style.paddingBottom = (dock ? dock.offsetHeight + 18 : 34) + 'px';
  });
}
window.addEventListener('resize', layout);
window.addEventListener('orientationchange', function(){ setTimeout(layout, 120); });

/* ---------- money ---------- */
var NG = '<span style="margin:0 0.09em 0 0.05em">&#8358;</span>';
function ng(n){ return NG + Number(n).toLocaleString('en-US'); }
function plusDays(n){
  var d = new Date(); d.setDate(d.getDate() + n);
  var M = ['January','February','March','April','May','June','July',
           'August','September','October','November','December'];
  return d.getDate() + ' ' + M[d.getMonth()];
}

/* ---------- navigation ---------- */
var stack = [{ name:'Main', mode:'push' }];
screens.Main.classList.add('live');
var busy = false;

function current(){ return screens[stack[stack.length-1].name]; }

function animate(el, from, to, done){
  el.style.transition = 'none';
  el.style.transform = from;
  el.offsetHeight;
  requestAnimationFrame(function(){
    el.style.transition = 'transform ' + DUR + 'ms ' + EASE;
    el.style.transform = to;
    setTimeout(function(){ el.style.transition=''; if(done) done(); }, DUR + 20);
  });
}

function push(name, mode){
  if(busy || !screens[name]) return;
  var from = current(), to = screens[name];
  if(from === to) return;
  busy = true;
  to.classList.add('live');
  padDocks();
  if(mode === 'sheet'){
    animate(to, 'translateY(100%)', 'translateY(0)', function(){ busy=false; });
  } else {
    animate(to, 'translateX(100%)', 'translateX(0)');
    animate(from, 'translateX(0)', 'translateX(-26%)', function(){
      from.classList.remove('live'); from.style.transform=''; busy=false;
    });
  }
  stack.push({ name:name, mode:mode||'push' });
}

function back(){
  if(busy || stack.length < 2) return;
  busy = true;
  var top = stack.pop(), leaving = screens[top.name], under = current();
  under.classList.add('live');
  if(top.mode === 'sheet'){
    animate(leaving, 'translateY(0)', 'translateY(100%)', function(){
      leaving.classList.remove('live'); leaving.style.transform=''; busy=false;
    });
  } else {
    animate(under, 'translateX(-26%)', 'translateX(0)');
    animate(leaving, 'translateX(0)', 'translateX(100%)', function(){
      leaving.classList.remove('live'); leaving.style.transform=''; busy=false;
    });
  }
}

function home(){
  while(stack.length > 1){ var t = stack.pop(); screens[t.name].classList.remove('live'); screens[t.name].style.transform=''; }
  screens.Main.classList.add('live'); screens.Main.style.transform='';
  var pg = screens.Main.querySelector('.pg'); if(pg) pg.scrollTop = 0;
}

var toastTimer;
function toast(msg){
  toastEl.textContent = msg;
  toastEl.classList.add('on');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(function(){ toastEl.classList.remove('on'); }, 1900);
}

/* ---------- state ---------- */
var st = {
  bundle:'5GB for 30 days', bundlePrice:2500, who:'Mum',
  power:8000, loanAmt:150000, loanMonths:3,
  revealed:false, frozen:false
};

function setText(id, html){ var e = document.getElementById(id); if(e) e.innerHTML = html; }

function paintChips(screenName, on){
  [].forEach.call(screens[screenName].querySelectorAll('.bchip'), function(c){
    var live = on(c.dataset.act.split('|'));
    c.style.border = live ? '1px solid var(--acc)' : '1px solid #D5DAE2';
    c.style.background = live ? 'color-mix(in srgb, var(--acc) 7%, #FFFFFF)' : '#FFFFFF';
    c.firstElementChild.style.color = live ? 'var(--acc)' : '#0F1521';
  });
}
function renderAirtime(){
  setText('bSize', st.bundle);
  setText('bPrice', ng(st.bundlePrice));
  setText('bWho', st.who);
  setText('bAv', st.who.charAt(0));
  setText('bBack', ng(Math.round(st.bundlePrice * 0.01)));
  setText('aLine', st.bundle + ', on ' + st.who + '&#8217;s MTN line.');
  setText('aSlide', 'Slide to buy ' + ng(st.bundlePrice));
  paintChips('Airtime', function(a){ return a[1] === st.bundle; });
}
function renderPower(){
  setText('pwAmt', ng(st.power));
  setText('pwSlide', 'Slide to pay ' + ng(st.power));
  paintChips('PowerPay', function(a){ return Number(a[1].replace(/,/g,'')) === st.power; });
}
function renderLoan(){
  var interest = Math.round(st.loanAmt * 0.04 * st.loanMonths);
  var total = st.loanAmt + interest + 1500;
  var per = Math.round(total / st.loanMonths / 100) * 100;
  var words = ['', 'One payment of', 'Two payments of', 'Three payments of'];
  setText('lnAmt', '<span class="num" style="font-size:32px;font-weight:600;letter-spacing:-.035em;line-height:1">' + ng(st.loanAmt) + '</span>');
  document.getElementById('lnBar').style.width = Math.round((st.loanAmt - 10000) / 240000 * 100) + '%';
  setText('lnGet', ng(st.loanAmt));
  setText('lnInt', ng(interest));
  setText('lnTot', ng(total));
  setText('lnPer', ng(per));
  setText('lnPerK', words[st.loanMonths]);
  setText('lnDate', plusDays(30));
  setText('lnSlide', 'Slide to take ' + ng(st.loanAmt));
  var chips = screens.Loan.querySelectorAll('.dchip');
  [].forEach.call(chips, function(c, i){
    var on = (i + 1) === st.loanMonths;
    c.style.background = on ? 'var(--acc)' : '#FFFFFF';
    c.style.color = on ? '#FFFFFF' : '#5A6472';
    c.style.fontWeight = on ? '600' : '500';
    c.style.border = on ? '1px solid var(--acc)' : '1px solid #D5DAE2';
  });
}
function renderCard(){
  setText('cdNum', st.revealed ? '5399 4412 8890 4471'
    : '5399 &#8226;&#8226;&#8226;&#8226; &#8226;&#8226;&#8226;&#8226; 4471');
  var face = document.getElementById('cdFace');
  face.style.opacity = st.frozen ? '.45' : '1';
  face.style.transition = 'opacity .25s ease';
}

var DONE = {
  Airtime: function(){ return {
    amt: st.bundlePrice, what: st.bundle.split(' for ')[0] + ' sent to ' + st.who,
    rows: [['From','Everyday &#183; 0102 4457 88'], ['Reference','MTN-88231-4471']], offer: true }; },
  Pay: function(){ return {
    amt: 50000, what: 'Sent to Sarah Adeyemi',
    rows: [['From','Everyday &#183; 0102 4457 88'], ['Reference','Flat deposit']], offer: false }; },
  Loan: function(){
    var total = st.loanAmt + Math.round(st.loanAmt * 0.04 * st.loanMonths) + 1500;
    return { amt: st.loanAmt, what: 'In your Everyday account',
      rows: [['You pay back', ng(total)], ['First payment', plusDays(30)]], offer: false }; }
};

function fillDone(kind){
  var d = DONE[kind]();
  setText('dnAmt', '<span class="num" style="font-size:40px;font-weight:600;letter-spacing:-.035em;line-height:1">' + ng(d.amt) + '</span>');
  setText('dnWhat', d.what);
  var rows = '';
  d.rows.forEach(function(r, i){
    var last = i === d.rows.length - 1;
    rows += '<div style="' + (last ? '' : 'border-bottom:1px solid #E2E6EC;')
      + 'display:flex;align-items:center;height:50px;padding:0 15px;gap:10px">'
      + '<span style="flex-grow:1;font-size:13.5px;color:#5A6472">' + r[0] + '</span>'
      + '<span class="num" style="font-size:14.5px;font-weight:500;color:#0F1521">' + r[1] + '</span></div>';
  });
  document.getElementById('dnCard').innerHTML = rows;
  document.getElementById('dnOffer').style.display = d.offer ? 'block' : 'none';
}

/* ---------- taps ---------- */
function toggleSwitch(el){
  var on = el.classList.toggle('on');
  var knob = el.firstElementChild;
  el.style.background = on ? 'var(--acc)' : '#D7DCE4';
  el.style.justifyContent = on ? 'flex-end' : 'flex-start';
  knob.style.border = on ? 'none' : '1px solid #D5DAE2';
  toast(on ? 'Instruction switched on' : 'Instruction switched off');
}

var ACTIONS = {
  soon: function(){ toast('Not wired up in this walkthrough'); },
  dismiss: function(){
    var c = document.getElementById('mBill');
    if(!c) return;
    c.style.transition = 'opacity .2s ease';
    c.style.opacity = '0';
    setTimeout(function(){ c.style.display = 'none'; padDocks(); }, 200);
    toast('Put away for today');
  },
  copy: function(){ toast('Token copied'); },
  toggle: function(el){ toggleSwitch(el); },
  reveal: function(){ st.revealed = !st.revealed; renderCard(); },
  freeze: function(){ st.frozen = !st.frozen; renderCard(); toast(st.frozen ? 'Card frozen' : 'Card unfrozen'); },
  gb: function(el, a){ st.bundle = a[1]; st.bundlePrice = Number(a[2].replace(/,/g,'')); renderAirtime(); },
  who: function(el, a){ st.who = a[1]; renderAirtime(); },
  pw: function(el, a){ st.power = Number(a[1].replace(/,/g,'')); renderPower(); },
  loan: function(el, a){
    st.loanAmt = Math.min(250000, Math.max(10000, st.loanAmt + (a[1] === '+' ? 10000 : -10000)));
    renderLoan();
  },
  term: function(el, a){ st.loanMonths = Number(a[1]); renderLoan(); }
};

function dropSheet(){
  var top = stack[stack.length-1];
  if(top.mode !== 'sheet') return;
  stack.pop();
  var el = screens[top.name];
  el.classList.remove('live');
  el.style.transform = '';
}

function navigate(target){
  if(target === 'back') return back();
  if(target === 'ask'){
    if(stack[stack.length-1].name === 'Ask') return back();
    return push('Ask', 'sheet');
  }
  dropSheet();
  var parts = target.split('|');
  if(parts[0] === 'done'){ fillDone(parts[1]); return push('Done', 'push'); }
  if(target === 'Main') return home();
  push(target, 'push');
}

document.addEventListener('click', function(e){
  if(busy) return;
  var a = e.target.closest('[data-act]');
  var g = e.target.closest('[data-go]');
  if(a && g){                       // whichever sits closer to the tap wins
    if(g.contains(a)) g = null; else a = null;
  }
  if(a){
    var arg = a.dataset.act.split('|');
    var fn = ACTIONS[arg[0]];
    if(fn) fn(a, arg);
    return;
  }
  if(g) navigate(g.dataset.go);
});

document.addEventListener('keydown', function(e){
  if(e.key === 'Escape') back();
});

/* swipe in from the left edge to go back, the way iOS does */
(function(){
  var x0 = null, y0 = null;
  document.addEventListener('touchstart', function(e){
    var t = e.touches[0];
    x0 = t.clientX < 28 ? t.clientX : null; y0 = t.clientY;
  }, {passive:true});
  document.addEventListener('touchend', function(e){
    if(x0 === null) return;
    var t = e.changedTouches[0];
    if(t.clientX - x0 > 60 && Math.abs(t.clientY - y0) < 70) back();
    x0 = null;
  }, {passive:true});
})();

/* ---------- slide to confirm ---------- */
[].forEach.call(document.querySelectorAll('.slide'), function(track){
  var knob = track.querySelector('.knob');
  var label = track.querySelector('.slideLabel');
  var target = track.dataset.go;
  var down = false, startX = 0, x = 0, moved = 0;
  function span(){ return track.clientWidth - knob.offsetWidth - 10; }
  function set(v, anim){
    knob.style.transition = anim ? 'transform .22s ease' : 'none';
    knob.style.transform = 'translateX(' + v + 'px)';
    if(label) label.style.opacity = String(Math.max(0, 1 - v / span() * 1.6));
  }
  function commit(){
    set(span(), true);
    setTimeout(function(){ navigate(target); }, REDUCED ? 0 : 200);
    setTimeout(function(){ set(0, false); if(label) label.style.opacity = '1'; }, DUR + 320);
  }
  knob.addEventListener('pointerdown', function(e){
    down = true; moved = 0; startX = e.clientX; knob.setPointerCapture(e.pointerId);
  });
  knob.addEventListener('pointermove', function(e){
    if(!down) return;
    x = Math.max(0, Math.min(span(), e.clientX - startX));
    moved = Math.max(moved, Math.abs(e.clientX - startX));
    set(x, false);
  });
  function end(){
    if(!down) return;
    down = false;
    if(moved < 8){ commit(); return; }
    if(x > span() * 0.62){ commit(); } else { set(0, true); if(label) label.style.opacity='1'; }
    x = 0;
  }
  knob.addEventListener('pointerup', end);
  knob.addEventListener('pointercancel', end);
});

renderAirtime(); renderPower(); renderLoan(); renderCard();
layout();
setTimeout(layout, 200);
"""

HTML = ("<title>Banking Flow Prototype</title>\n<style>\n" + build.faces(True) + CSS + "\n</style>\n"
  '<div class="wrap">\n'
  '  <div class="device" id="device">\n'
  '    <div class="stage" id="stage">\n' + screens + '    </div>\n  </div>\n'
  '  <p class="legend" id="legend">Tap through it. <b>Airtime</b>, <b>Data</b> and <b>Power</b> on the home screen open a prepared purchase. '
  'The <b>ask bar</b> at the bottom of any screen opens the voice sheet. Drag the blue knob to confirm a payment, or just tap it. '
  'The <b>bundle chips</b>, the <b>loan stepper</b> and the <b>switches</b> all really change. '
  'Anything that answers <em>not wired up</em> is a screen this walkthrough does not include.</p>\n'
  '</div>\n<div id="toast"></div>\n<script>\n' + JS + '\n</script>\n')

open(os.path.join(OUT, "prototype.html"), "w").write(HTML)
print("prototype.html", os.path.getsize(os.path.join(OUT, "prototype.html")), "bytes,", len(ORDER), "screens")
