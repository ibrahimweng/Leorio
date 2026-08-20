# Builds prototype.html, a walkable version of the same screens.
# The screen markup comes from build.py, so there is one source of truth.
# Motion is anime.js v3, which rides inside the file because a published page
# cannot load a script from anywhere else.
import os, build

OUT = os.path.dirname(os.path.abspath(__file__))
ACC = build.ACC_HEX
ANIME = open(os.path.join(OUT, "vendor", "anime.min.js")).read()

ORDER = ["Main", "Ask", "Services", "Airtime", "PowerPay", "Power", "Bills",
         "Loan", "Card", "Answer", "Pay", "Rules", "Done"]

screens = ""
for name in ORDER:
    inner = build.SCREENS[name].replace("{{accent}}", "var(--acc)")
    screens += '<section class="screen" data-screen="' + name + '">\n' + inner + '\n</section>\n'

CSS = """
:root{
  --acc:""" + ACC + """;
  --ink:""" + build.INK + """;
  --ink2:""" + build.INK2 + """;
  --ink3:""" + build.INK3 + """;
  --fill:""" + build.FILL + """;
  --line:""" + build.LINE + """;
  --page:""" + build.BG + """;
  --sur-bg:#E9EBEC; --sur-card:#FFFFFF; --sur-ink:#20242A;
  --sur-mid:#6B7178; --sur-line:#D9DCDF; --sur-shadow:0 26px 64px rgba(15,18,22,.16);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --sur-bg:#0C0F11; --sur-card:#171B1D; --sur-ink:#E2E6E8;
    --sur-mid:#8A9298; --sur-line:#242A2D; --sur-shadow:0 26px 64px rgba(0,0,0,.55);
  }
}
:root[data-theme="dark"]{
  --sur-bg:#0C0F11; --sur-card:#171B1D; --sur-ink:#E2E6E8;
  --sur-mid:#8A9298; --sur-line:#242A2D; --sur-shadow:0 26px 64px rgba(0,0,0,.55);
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  background:var(--sur-bg); color:var(--sur-ink);
  font-family:'Plus Jakarta Sans',-apple-system,'Helvetica Neue',Arial,sans-serif;
  -webkit-font-smoothing:antialiased; overflow:hidden;
  min-height:100vh; min-height:100dvh;
}
.wrap{display:flex; flex-direction:column; align-items:center; justify-content:center;
  gap:22px; height:100vh; height:100dvh}
body.desk .wrap{padding:24px 20px}
.device{position:relative; flex-shrink:0; overflow:hidden; background:var(--page)}
body.desk .device{border-radius:44px;
  box-shadow:var(--sur-shadow), 0 0 0 9px #0F1216, 0 0 0 10px #2B3238}
.stage{width:393px; transform-origin:top left; position:relative}
.screen{position:absolute; inset:0; display:none; will-change:transform; background:var(--page)}
.screen.live{display:block}
/* The screens carry an inline position:relative for the artboard canvas.
   It has to be overridden here or the page never becomes a scroll container. */
.screen .pg{position:absolute !important; top:0 !important; left:0 !important;
  right:0 !important; bottom:0 !important; overflow-y:auto; overflow-x:hidden;
  -webkit-overflow-scrolling:touch; overscroll-behavior:contain; scrollbar-width:none}
.screen .pg::-webkit-scrollbar{width:0;height:0}
.screen[data-screen="Ask"] .fauxbg{
  position:absolute; inset:0; opacity:1 !important; padding:0 !important;
  background:rgba(15,18,22,.34); overflow:hidden}
.screen[data-screen="Ask"] .fauxbg > *{display:none !important}

[data-go],[data-act],.slide{cursor:pointer; -webkit-tap-highlight-color:transparent;
  transition:transform .14s cubic-bezier(.22,1,.36,1), opacity .14s ease}
[data-go]:active,[data-act]:active{transform:scale(.972); opacity:.92}
.slide [data-go]:active,.knob{transform:none}
.knob{touch-action:none}
.nav{pointer-events:none}
.nav > *{pointer-events:auto}
.nav .navbg{pointer-events:none}

.legend{max-width:560px; color:var(--sur-mid); font-size:13.5px; line-height:1.6;
  text-align:center; display:none; margin:0}
.legend b{color:var(--sur-ink); font-weight:600}
#toast{position:fixed; left:50%; bottom:36px; transform:translate(-50%,18px);
  background:#0F1216; color:#F4F6F7; font-size:13.5px; font-weight:500;
  padding:11px 18px; border-radius:22px; opacity:0; pointer-events:none;
  z-index:60; max-width:80vw; text-align:center}
@media (prefers-reduced-motion: reduce){ *{animation:none !important} }
"""

JS = r"""
(function(){
  var m = document.querySelector('meta[name=viewport]');
  if(!m){ m = document.createElement('meta'); m.name='viewport'; document.head.appendChild(m); }
  m.content = 'width=device-width,initial-scale=1,viewport-fit=cover,maximum-scale=1,user-scalable=no';
})();

var A = window.anime;
var REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
var EASE = 'cubicBezier(.22,1,.36,1)';
function D(n){ return REDUCED ? 0 : n; }

var stage = document.getElementById('stage');
var device = document.getElementById('device');
var toastEl = document.getElementById('toast');
var legendEl = document.getElementById('legend');
var screens = {};
[].forEach.call(document.querySelectorAll('.screen'), function(el){ screens[el.dataset.screen] = el; });

/* ---------- sizing ---------- */
function layout(){
  var W = window.innerWidth, H = window.innerHeight, s, sh;
  var desk = W >= 460;
  var showLegend = desk && H >= 780;
  document.body.classList.toggle('desk', desk);
  legendEl.style.display = showLegend ? 'block' : 'none';
  if(desk){
    s = Math.max(0.5, Math.min(1, (H - (showLegend ? 156 : 52)) / 852));
    sh = 852;
  } else {
    s = Math.min(1.15, W / 393);
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

/* ---------- the title collapsing into the bar ---------- */
function clamp(v){ return v < 0 ? 0 : (v > 1 ? 1 : v); }
[].forEach.call(document.querySelectorAll('.screen'), function(sc){
  var pg = sc.querySelector('.pg'), nav = sc.querySelector('.nav');
  if(!pg || !nav) return;
  var bg = nav.querySelector('.navbg'), tt = nav.querySelector('.navtitle');
  pg.addEventListener('scroll', function(){
    var y = pg.scrollTop;
    bg.style.opacity = String(clamp((y - 4) / 34));
    tt.style.opacity = String(clamp((y - 24) / 26));
  }, { passive: true });
});
function resetScroll(sc){
  var pg = sc.querySelector('.pg'), nav = sc.querySelector('.nav');
  if(pg) pg.scrollTop = 0;
  if(nav){
    nav.querySelector('.navbg').style.opacity = '0';
    nav.querySelector('.navtitle').style.opacity = '0';
  }
}

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

function clearInline(list){
  [].forEach.call(list, function(k){ k.style.opacity = ''; k.style.transform = ''; });
}

function enter(sc){
  if(REDUCED) return;
  var kids = sc.querySelectorAll('.pgin > *');
  if(!kids.length) return;
  A.remove(kids);
  A({ targets: kids, translateY: [14, 0], opacity: [0, 1],
      delay: A.stagger(42, { start: 70 }), duration: 520, easing: EASE,
      complete: function(){ clearInline(kids); } });
  // If the frame loop is throttled the animation may never tick, and anime
  // has already set opacity to 0. Never leave a screen blank because of that.
  clearTimeout(sc.__enterFix);
  sc.__enterFix = setTimeout(function(){ A.remove(kids); clearInline(kids); }, 1400);
}

function push(name, mode){
  if(busy || !screens[name]) return;
  var from = current(), to = screens[name];
  if(from === to) return;
  busy = true;
  resetScroll(to);
  to.classList.add('live');
  padDocks();
  var settled = false;
  function done(){
    if(settled) return;
    settled = true;
    A.remove(to); A.remove(from);          // stop it before clearing, or it is put straight back
    to.style.transform = ''; to.style.opacity = '';
    if(mode !== 'sheet'){
      from.classList.remove('live');
      from.style.transform = ''; from.style.opacity = '';
    }
    busy = false;
  }
  if(mode === 'sheet'){
    to.style.transform = 'translateY(100%)';
    A({ targets: to, translateY: ['100%','0%'], duration: D(460), easing: EASE, complete: done });
  } else {
    A({ targets: to, translateX: ['100%','0%'], duration: D(440), easing: EASE });
    A({ targets: from, translateX: ['0%','-24%'], opacity: [1, .6], duration: D(440), easing: EASE, complete: done });
    enter(to);
  }
  setTimeout(done, D(460) + 320);          // never leave a screen stuck mid slide
  stack.push({ name:name, mode:mode||'push' });
  if(name === 'Main') countBalance();
  if(name === 'Ask') startWave();
}

function back(){
  if(busy || stack.length < 2) return;
  busy = true;
  var top = stack.pop(), leaving = screens[top.name], under = current();
  under.classList.add('live');
  padDocks();
  var settled = false;
  function done(){
    if(settled) return;
    settled = true;
    A.remove(leaving); A.remove(under);
    leaving.classList.remove('live');
    leaving.style.transform = ''; leaving.style.opacity = '';
    under.style.transform = ''; under.style.opacity = '';
    busy = false;
  }
  if(top.mode === 'sheet'){
    A({ targets: leaving, translateY: ['0%','100%'], duration: D(380), easing: EASE, complete: done });
  } else {
    A({ targets: under, translateX: ['-24%','0%'], opacity: [.6, 1], duration: D(420), easing: EASE });
    A({ targets: leaving, translateX: ['0%','100%'], duration: D(420), easing: EASE, complete: done });
  }
  setTimeout(done, D(440) + 320);
}

function home(){
  while(stack.length > 1){
    var t = stack.pop();
    screens[t.name].classList.remove('live');
    screens[t.name].style.transform = ''; screens[t.name].style.opacity = '';
  }
  screens.Main.classList.add('live');
  screens.Main.style.transform = ''; screens.Main.style.opacity = '';
  resetScroll(screens.Main);
  padDocks(); enter(screens.Main); countBalance();
}

var toastTimer;
function toast(msg){
  toastEl.textContent = msg;
  A.remove(toastEl);
  toastEl.style.opacity = '1';
  A({ targets: toastEl, translateY: [18, 0], duration: D(260), easing: EASE });
  clearTimeout(toastTimer);
  toastTimer = setTimeout(function(){
    A({ targets: toastEl, opacity: 0, translateY: 18, duration: D(240), easing: 'easeInQuad' });
  }, 1900);
}

/* ---------- the balance counting up ---------- */
var counted = false;
function countBalance(){
  var el = document.getElementById('mBal');
  if(!el || REDUCED){ return; }
  if(counted) return;
  counted = true;
  var o = { v: 0 };
  A({ targets: o, v: 248320.75, duration: 1200, easing: 'easeOutExpo', round: 100,
      update: function(){
        var whole = Math.floor(o.v), dec = Math.round((o.v - whole) * 100);
        el.innerHTML =
          '<div style="display:flex;align-items:baseline;gap:1px">' +
          '<span class="num" style="font-size:44px;font-weight:700;letter-spacing:-.04em;line-height:1;color:var(--ink)">' +
          ng(whole) + '</span>' +
          '<span class="num" style="font-size:22px;font-weight:700;letter-spacing:-.025em;color:var(--ink3)">.' +
          (dec < 10 ? '0' : '') + dec + '</span></div>';
      } });
}

/* ---------- the voice waveform ---------- */
var waving = false;
function startWave(){
  if(waving || REDUCED) return;
  waving = true;
  A({ targets: screens.Ask.querySelectorAll('.wv'),
      scaleY: [{ value: 0.3, duration: 420 }, { value: 1, duration: 420 }],
      delay: A.stagger(38, { from: 'center' }),
      loop: true, direction: 'alternate', easing: 'easeInOutSine' });
}

/* ---------- state ---------- */
var st = {
  bundle:'5GB for 30 days', bundlePrice:2500, who:'Mum',
  power:8000, loanAmt:150000, loanMonths:3,
  revealed:false, frozen:false
};
function setText(id, html){ var e = document.getElementById(id); if(e) e.innerHTML = html; }
function pop(el){
  if(REDUCED || !el) return;
  A.remove(el);
  A({ targets: el, scale: [0.94, 1], duration: 380, easing: 'easeOutBack' });
}

function paintChips(screenName, on){
  [].forEach.call(screens[screenName].querySelectorAll('.bchip'), function(c){
    var live = on(c.dataset.act.split('|'));
    c.style.background = live ? 'color-mix(in srgb, var(--acc) 12%, #FFFFFF)' : 'var(--fill)';
    c.style.boxShadow = live ? 'inset 0 0 0 1.5px var(--acc)' : 'none';
    c.firstElementChild.style.color = live ? 'var(--acc)' : 'var(--ink)';
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
  setText('lnAmt', '<span class="num" style="font-size:30px;font-weight:700;letter-spacing:-.04em;line-height:1">' + ng(st.loanAmt) + '</span>');
  var bar = document.getElementById('lnBar');
  if(bar) A({ targets: bar, width: Math.round((st.loanAmt - 10000) / 240000 * 100) + '%', duration: D(420), easing: EASE });
  setText('lnGet', ng(st.loanAmt));
  setText('lnInt', ng(interest));
  setText('lnTot', ng(total));
  setText('lnPer', ng(per));
  setText('lnPerK', words[st.loanMonths]);
  setText('lnDate', plusDays(30));
  setText('lnSlide', 'Slide to take ' + ng(st.loanAmt));
  [].forEach.call(screens.Loan.querySelectorAll('.dchip'), function(c, i){
    var on = (i + 1) === st.loanMonths;
    c.style.background = on ? '#0F1216' : 'var(--fill)';
    c.style.color = on ? '#FFFFFF' : 'var(--ink2)';
    c.style.fontWeight = on ? '700' : '600';
  });
}
function renderCard(){
  setText('cdNum', st.revealed ? '5399 4412 8890 4471'
    : '5399 &#8226;&#8226;&#8226;&#8226; &#8226;&#8226;&#8226;&#8226; 4471');
  var face = document.getElementById('cdFace');
  A({ targets: face, opacity: st.frozen ? 0.42 : 1, duration: D(280), easing: EASE });
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
  setText('dnAmt', '<span class="num" style="font-size:36px;font-weight:700;letter-spacing:-.04em;line-height:1">' + ng(d.amt) + '</span>');
  setText('dnWhat', d.what);
  var rows = '';
  d.rows.forEach(function(r, i){
    var last = i === d.rows.length - 1;
    rows += '<div style="' + (last ? '' : 'border-bottom:1px solid var(--line);')
      + 'display:flex;align-items:center;height:54px;padding:0 16px;gap:10px">'
      + '<span style="flex-grow:1;font-size:15px;font-weight:500;color:var(--ink2)">' + r[0] + '</span>'
      + '<span class="num" style="font-size:15px;font-weight:700;color:var(--ink)">' + r[1] + '</span></div>';
  });
  document.getElementById('dnCard').innerHTML = rows;
  document.getElementById('dnOffer').style.display = d.offer ? 'block' : 'none';
}

/* ---------- taps ---------- */
function toggleSwitch(el){
  var on = el.classList.toggle('on');
  var knob = el.firstElementChild;
  el.style.justifyContent = on ? 'flex-end' : 'flex-start';
  A({ targets: el, backgroundColor: on ? getComputedStyle(document.documentElement).getPropertyValue('--acc').trim() : '#DCDEE2',
      duration: D(260), easing: EASE });
  if(!REDUCED) A({ targets: knob, scale: [1, 1.14, 1], duration: 320, easing: EASE });
  toast(on ? 'Instruction switched on' : 'Instruction switched off');
}

var ACTIONS = {
  soon: function(){ toast('Not wired up in this walkthrough'); },
  dismiss: function(){
    var c = document.getElementById('mBill');
    if(!c) return;
    A({ targets: c, opacity: 0, translateX: 40, height: 0, marginTop: 0, duration: D(360), easing: EASE,
        complete: function(){ c.style.display = 'none'; padDocks(); } });
    toast('Put away for today');
  },
  copy: function(){ toast('Token copied'); },
  toggle: function(el){ toggleSwitch(el); },
  reveal: function(){ st.revealed = !st.revealed; renderCard(); pop(document.getElementById('cdNum')); },
  freeze: function(){ st.frozen = !st.frozen; renderCard(); toast(st.frozen ? 'Card frozen' : 'Card unfrozen'); },
  gb: function(el, a){ st.bundle = a[1]; st.bundlePrice = Number(a[2].replace(/,/g,'')); renderAirtime(); pop(el); },
  who: function(el, a){ st.who = a[1]; renderAirtime(); pop(el); },
  pw: function(el, a){ st.power = Number(a[1].replace(/,/g,'')); renderPower(); pop(el); },
  loan: function(el, a){
    st.loanAmt = Math.min(250000, Math.max(10000, st.loanAmt + (a[1] === '+' ? 10000 : -10000)));
    renderLoan(); pop(document.getElementById('lnAmt'));
  },
  term: function(el, a){ st.loanMonths = Number(a[1]); renderLoan(); pop(el); }
};

function dropSheet(){
  var top = stack[stack.length-1];
  if(top.mode !== 'sheet') return;
  stack.pop();
  var el = screens[top.name];
  el.classList.remove('live'); el.style.transform = '';
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
  if(a && g){ if(g.contains(a)) g = null; else a = null; }
  if(a){
    var arg = a.dataset.act.split('|');
    var fn = ACTIONS[arg[0]];
    if(fn) fn(a, arg);
    return;
  }
  if(g) navigate(g.dataset.go);
});

document.addEventListener('keydown', function(e){ if(e.key === 'Escape') back(); });

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
  function set(v){
    knob.style.transform = 'translateX(' + v + 'px)';
    if(label) label.style.opacity = String(Math.max(0, 1 - v / span() * 1.6));
  }
  function glide(to, cb){
    A.remove(knob);
    A({ targets: knob, translateX: to, duration: D(320), easing: EASE,
        update: function(){ if(label) label.style.opacity = String(Math.max(0, 1 - (parseFloat(knob.style.transform.replace(/[^-0-9.]/g,'')) || 0) / span() * 1.6)); },
        complete: cb });
  }
  function commit(){
    glide(span(), function(){
      navigate(target);
      setTimeout(function(){ knob.style.transform = 'translateX(0px)'; if(label) label.style.opacity = '1'; }, 460);
    });
  }
  knob.addEventListener('pointerdown', function(e){
    down = true; moved = 0; startX = e.clientX; A.remove(knob); knob.setPointerCapture(e.pointerId);
  });
  knob.addEventListener('pointermove', function(e){
    if(!down) return;
    x = Math.max(0, Math.min(span(), e.clientX - startX));
    moved = Math.max(moved, Math.abs(e.clientX - startX));
    set(x);
  });
  function end(){
    if(!down) return;
    down = false;
    if(moved < 8){ commit(); return; }
    if(x > span() * 0.6){ commit(); }
    else { glide(0, function(){ if(label) label.style.opacity = '1'; }); }
    x = 0;
  }
  knob.addEventListener('pointerup', end);
  knob.addEventListener('pointercancel', end);
});

renderAirtime(); renderPower(); renderLoan(); renderCard();
layout();
setTimeout(function(){ layout(); enter(screens.Main); countBalance(); }, 60);
"""

HTML = ("<title>Banking Flow Prototype</title>\n<style>\n" + build.faces(True) + CSS + "\n</style>\n"
  '<div class="wrap">\n'
  '  <div class="device" id="device">\n'
  '    <div class="stage" id="stage">\n' + screens + '    </div>\n  </div>\n'
  '  <p class="legend" id="legend">Tap through it. <b>Airtime</b>, <b>Data</b> and <b>Power</b> on the home screen open a prepared purchase. '
  'The <b>ask bar</b> at the bottom of any screen opens the voice sheet. Drag the black knob to confirm a payment, or just tap it. '
  '<b>Scroll any screen</b> and the big title folds into the bar. The <b>bundle chips</b>, the <b>loan stepper</b> and the '
  '<b>switches</b> all really change. Anything that answers <em>not wired up</em> is a screen this walkthrough does not include.</p>\n'
  '</div>\n<div id="toast"></div>\n'
  '<script>\n' + ANIME + '\n</script>\n'
  '<script>\n' + JS + '\n</script>\n')

open(os.path.join(OUT, "prototype.html"), "w").write(HTML)
print("prototype.html", os.path.getsize(os.path.join(OUT, "prototype.html")), "bytes,", len(ORDER), "screens")
