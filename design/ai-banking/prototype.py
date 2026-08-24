# Builds prototype.html, a walkable version of the same screens.
# The screen markup comes from build.py, so there is one source of truth.
# Motion is anime.js v3, which rides inside the file because a published page
# cannot load a script from anywhere else.
import os, build

OUT = os.path.dirname(os.path.abspath(__file__))
ACC = build.ACC_HEX
ANIME = open(os.path.join(OUT, "vendor", "anime.min.js")).read()

ORDER = ["Main", "Ask", "Chat", "Scan", "Pick", "Found", "Confirm", "Services",
         "Airtime", "PowerPay", "Power", "Bills", "Loan", "Card", "Answer",
         "Pay", "Rules", "Goal", "Done", "Settings", "History", "Paused",
         # The nine flows. The same three destinations reached three ways,
         # so most of these are the second step of one of them.
         "Typed", "TypedAsk", "TypedBuy", "ChatTyped", "RequestTyped", "BuyTyped",
         "AskReq", "AskSvc", "Request", "Sent", "MyCode",
         "Buy", "ConfirmBuy", "Meter", "ConfirmMeter", "DoneSend", "Receive",
         # A line you can still take apart, and the camera aimed at a bill
         # rather than at somebody's transfer message.
         "Draft", "ScanBill", "Amend", "Ways", "Rule",
         # The half of a bank that is not the happy path.
         "Short", "Pending", "Failed", "Reversed", "Wrong", "Recall",
         # One number for the habits, and the settings that build them: what
         # opens the app, what stops a transfer, and where else you are open.
         "Health", "Lock", "Limits", "LimitStop", "Devices", "SaveRule"]

def acc(html):
    return html.replace("{{accent}}", "var(--acc)")

screens = ""
for name in ORDER:
    screens += '<section class="screen" data-screen="' + name + '">\n' + acc(build.SCREENS[name]) + '\n</section>\n'

# Two things are not screens. They open on top of whichever screen you are on,
# so they are mounted once and shown over everything.
overlays = ('<div class="ovl" id="ovlActions">' + acc(build.FAB_SHEET) + '</div>\n'
            '<div class="ovl" id="ovlReceive">' + acc(build.RECEIVE_SHEET) + '</div>\n')

CSS = """
:root{
  --acc:""" + ACC + """;
  --ink:""" + build.INK + """;
  --ink2:""" + build.INK2 + """;
  --ink3:""" + build.INK3 + """;
  --ink4:""" + build.INK4 + """;
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
/* The Ask screen paints a copy of the home screen behind its sheet so the
   artboard reads on its own. In here the real screen is already behind it. */
.behind{display:none !important}
.screen[data-screen="Ask"]{background:transparent}

/* What the black circle opens, and the add money sheet. */
.ovl{position:absolute; inset:0; z-index:20; display:none}
.ovl.open{display:block}
.ovl .fabwrap,.ovl .fauxbg,.ovl .sheet{z-index:auto}

[data-go],[data-act],.slide{cursor:pointer; -webkit-tap-highlight-color:transparent;
  transition:transform .14s cubic-bezier(.22,1,.36,1), opacity .14s ease}
[data-go]:active,[data-act]:active{transform:scale(.972); opacity:.92}
.slide [data-go]:active,.knob{transform:none}
.knob{touch-action:none}

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
    if(pg) pg.style.paddingBottom = (dock ? dock.offsetHeight + 20 : 36) + 'px';
  });
}
window.addEventListener('resize', layout);
window.addEventListener('orientationchange', function(){ setTimeout(layout, 120); });

/* ---------- scrolling ---------- */
function resetScroll(sc){
  var pg = sc.querySelector('.pg:not(.behind .pg)');
  if(pg) pg.scrollTop = 0;
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
  if(name === 'Main'){ countBalance(); }
  if(name === 'Ask') startWave();
  if(name === 'Goal') animateRing();
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
          '<div style="display:flex;align-items:baseline;gap:0px">' +
          '<span class="num" style="font-size:36px;font-weight:800;letter-spacing:-.04em;line-height:1.05;color:var(--ink)">' +
          ng(whole) + '</span>' +
          '<span class="num" style="font-size:22px;font-weight:800;letter-spacing:-.03em;color:var(--ink4)">.' +
          (dec < 10 ? '0' : '') + dec + '</span></div>';
      } });
}

/* ---------- progress, which only ever moves on real behaviour ---------- */
function animateRing(){
  var r = screens.Goal.querySelector('.ring');
  var pct = document.getElementById('glPct');
  if(!r) return;
  // The ring is a path now, not a dashed circle, because a dash does not
  // survive the trip into Figma. It still draws itself on by dash, measured
  // off the path instead of read off an attribute.
  var circ = r.getTotalLength ? r.getTotalLength() : parseFloat(r.getAttribute('stroke-dasharray'));
  var target = 0;
  r.setAttribute('stroke-dasharray', circ);
  function land(){ A.remove(r); r.style.strokeDashoffset = target; if(pct) pct.textContent = '33%'; }
  if(REDUCED){ land(); return; }
  A.remove(r);
  A({ targets: r, strokeDashoffset: [circ, target], duration: 1100, easing: 'easeOutExpo' });
  var o = { v: 0 };
  A({ targets: o, v: 33, duration: 1100, easing: 'easeOutExpo', round: 1,
      update: function(){ if(pct) pct.textContent = o.v + '%'; } });
  setTimeout(land, 1500);
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
function setDot(el, on){
  if(!el) return;
  el.dataset.on = on ? '1' : '0';
  el.style.background = on ? 'var(--ink)' : 'transparent';
  el.style.border = on ? 'none' : '1.5px solid """ + build.LINE2 + """';
}
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

// Which receipt each passcode screen fills in, and where it goes. A null
// first entry means the screen it lands on writes itself.
var PINGO = {
  Confirm:      ['Chat', 'Done'],
  ConfirmBuy:   ['Buy', 'Done'],
  ConfirmMeter: [null, 'Power']
};

var DONE = {
  Airtime: function(){ return {
    amt: st.bundlePrice, what: st.bundle.split(' for ')[0] + ' sent to ' + st.who,
    rows: [['From','Everyday &#183; 0102 4457 88'],
           ['To your Holiday goal', ng(Math.round(st.bundlePrice * 0.01))]], offer: true }; },
  Pay: function(){ return {
    amt: 50000, what: 'Sent to Sarah Adeyemi',
    rows: [['From','Everyday &#183; 0102 4457 88'], ['Reference','Flat deposit']], offer: false }; },
  Chat: function(){ return {
    amt: 20000, what: 'Sent to Sarah Adeyemi',
    rows: [['From','Everyday &#183; 0102 4457 88'], ['Confirmed with','Your passcode']], offer: false }; },
  Buy: function(){ return {
    amt: 2500, what: '5GB sent to Mum',
    rows: [['From','Everyday &#183; 0102 4457 88'], ['Reference','MTN-88231-4471']], offer: true }; },
  Loan: function(){
    var total = st.loanAmt + Math.round(st.loanAmt * 0.04 * st.loanMonths) + 1500;
    return { amt: st.loanAmt, what: 'In your Everyday account',
      rows: [['You pay back', ng(total)], ['First payment', plusDays(30)]], offer: false }; }
};
function fillDone(kind){
  var d = DONE[kind]();
  var sc = screens.Done, loan = (kind === 'Loan');
  var head = sc.querySelector('.phead > div:first-child');
  var sub = sc.querySelector('.phead > div:last-child');
  var mark = document.getElementById('dnMark');
  var navT = sc.querySelector('.navtitle');
  // Borrowing money is not an achievement, so it gets no tick and no cheer.
  if(mark) mark.style.display = loan ? 'none' : 'flex';
  if(head) head.textContent = loan ? 'Loan taken' : 'All done';
  if(sub) sub.textContent = loan
    ? 'You owe this back by ' + plusDays(30) + '. Late costs \u20a62,000 a day.'
    : 'Your receipt is below, and in your messages';
  if(navT) navT.textContent = loan ? 'Loan taken' : 'All done';
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
  // Saying the month is tight is the one place the model changes how it behaves,
  // so the walkthrough takes you straight to what changed.
  tight: function(el){
    toggleSwitch(el);
    var on = el.classList.contains('on');
    toast(on ? 'Noted. I have stopped moving money out.' : 'Back to normal.');
    if(on) setTimeout(function(){ push('Paused', 'push'); }, 560);
  },
  // Four numbers, and only the fourth one moves money, so it is the only key
  // that navigates. Face ID is what was tried first, so it stays reachable.
  pin: function(el, a){
    // Three different things now end at a passcode, so the keypad reads its
    // own screen rather than always driving the transfer one, and each says
    // where the fourth number lands.
    var sc = el.closest('.screen');
    var dots = sc.querySelectorAll('.pindot');
    var after = PINGO[sc.dataset.screen] || PINGO.Confirm;
    var n = 0;
    for(var i = 0; i < dots.length; i++) if(dots[i].dataset.on === '1') n++;
    if(a[1] === 'del'){ if(n > 0) setDot(dots[n-1], false); return; }
    if(n >= dots.length) return;
    setDot(dots[n], true);
    pop(el);
    if(n + 1 >= dots.length){
      if(after[0]) fillDone(after[0]);
      setTimeout(function(){ for(var i = 0; i < dots.length; i++) setDot(dots[i], false); push(after[1], 'push'); }, 340);
    }
  },
  faceid: function(){ toast('Face ID is the quicker way through'); },
  // Two names that are not the same is the one thing a photograph cannot
  // settle, so the button that moves money stays grey until it is answered.
  fnwait: function(){ toast('Answer the name question first'); },
  sure: function(el){
    var go = document.getElementById('fnGo');
    if(go){
      go.removeAttribute('data-act');
      go.dataset.go = 'Confirm';
      go.style.background = 'var(--ink)';
      go.style.boxShadow = '0 8px 24px rgba(0,0,0,0.24)';
      var gs = go.querySelector('span'); if(gs) gs.style.color = '#FFFFFF';
      pop(go);
    }
    el.style.background = 'var(--fill)';
    el.style.boxShadow = 'none';
    var es = el.querySelector('span'); if(es) es.style.color = 'var(--ink)';
    toast('Noted. I will use the name GTBank gave.');
  },
  reveal: function(){ st.revealed = !st.revealed; renderCard(); pop(document.getElementById('cdNum')); },
  freeze: function(){ st.frozen = !st.frozen; renderCard(); toast(st.frozen ? 'Card frozen' : 'Card unfrozen'); },
  gb: function(el, a){ st.bundle = a[1]; st.bundlePrice = Number(a[2].replace(/,/g,'')); renderAirtime(); pop(el); },
  who: function(el, a){ st.who = a[1]; renderAirtime(); pop(el); },
  pw: function(el, a){ st.power = Number(a[1].replace(/,/g,'')); renderPower(); pop(el); },
  loan: function(el, a){
    st.loanAmt = Math.min(250000, Math.max(10000, st.loanAmt + (a[1] === '+' ? 10000 : -10000)));
    renderLoan(); pop(document.getElementById('lnAmt'));
  },
  term: function(el, a){ st.loanMonths = Number(a[1]); renderLoan(); pop(el); },
  actions: function(){ if(openOvl === ovlActions) ovlClose(); else ovlOpen(ovlActions); },
  receive: function(){ ovlOpen(ovlReceive); },
  seg: function(el){
    var track = el.parentNode;
    [].forEach.call(track.children, function(c){
      var on = (c === el), sp = c.querySelector('span');
      c.style.background = on ? '#FFFFFF' : 'transparent';
      c.style.boxShadow = on ? '0 2px 10px rgba(0,0,0,0.05), 0 8px 30px rgba(0,0,0,0.06)' : 'none';
      if(sp) sp.style.color = on ? 'var(--ink)' : 'var(--ink2)';
    });
  }
};


/* ---------- the two things that open on top of a screen ---------- */
var ovlActions = document.getElementById('ovlActions');
var ovlReceive = document.getElementById('ovlReceive');
var openOvl = null;

function ovlOpen(el){
  if(openOvl) ovlClose(true);
  openOvl = el;
  el.classList.add('open');
  var scrim = el.querySelector('.fabscrim') || el.querySelector('.fauxbg');
  var rows  = el.querySelectorAll('.fabrow');
  var panel = el.querySelector('.sheet');
  var fab   = el.querySelector('.fabclose');
  if(REDUCED) return;
  if(scrim){ A.remove(scrim); A({ targets: scrim, opacity: [0, 1], duration: 200, easing: 'linear',
    complete: function(){ scrim.style.opacity = ''; } }); }
  if(rows.length){
    A.remove(rows);
    A({ targets: rows, translateY: [30, 0], opacity: [0, 1], scale: [0.88, 1],
        delay: A.stagger(50, { from: 'last' }), duration: 420, easing: EASE,
        complete: function(){ clearInline(rows); } });
    clearTimeout(el.__fix);
    el.__fix = setTimeout(function(){ A.remove(rows); clearInline(rows); }, 1200);
  }
  if(fab){ A.remove(fab); A({ targets: fab, rotate: [-90, 0], scale: [0.7, 1], duration: 340, easing: EASE,
    complete: function(){ fab.style.transform = ''; } }); }
  if(panel){
    A.remove(panel);
    A({ targets: panel, translateY: [380, 0], duration: 460, easing: EASE,
        complete: function(){ panel.style.transform = ''; } });
    clearTimeout(el.__fix2);
    el.__fix2 = setTimeout(function(){ A.remove(panel); panel.style.transform = ''; }, 1200);
  }
}

function ovlClose(instant){
  var el = openOvl;
  if(!el) return;
  openOvl = null;
  function hide(){
    el.classList.remove('open');
    var scrim = el.querySelector('.fabscrim') || el.querySelector('.fauxbg');
    var panel = el.querySelector('.sheet');
    var rows  = el.querySelectorAll('.fabrow');
    var fab   = el.querySelector('.fabclose');
    A.remove(scrim); A.remove(panel); A.remove(rows); A.remove(fab);
    if(scrim) scrim.style.opacity = '';
    if(panel) panel.style.transform = '';
    if(fab) fab.style.transform = '';
    clearInline(rows);
  }
  if(instant || REDUCED){ hide(); return; }
  var scrim = el.querySelector('.fabscrim') || el.querySelector('.fauxbg');
  var panel = el.querySelector('.sheet');
  var rows  = el.querySelectorAll('.fabrow');
  var settled = false;
  function done(){ if(settled) return; settled = true; hide(); }
  if(rows.length){ A.remove(rows); A({ targets: rows, translateY: 18, opacity: 0, scale: 0.9,
    delay: A.stagger(26), duration: 180, easing: 'easeInQuad' }); }
  if(panel){ A.remove(panel); A({ targets: panel, translateY: 380, duration: 260, easing: 'easeInQuad' }); }
  if(scrim){ A.remove(scrim); A({ targets: scrim, opacity: 0, duration: 240, easing: 'linear', complete: done }); }
  setTimeout(done, 420);
}

function dropSheet(){
  var top = stack[stack.length-1];
  if(top.mode !== 'sheet') return;
  stack.pop();
  var el = screens[top.name];
  el.classList.remove('live'); el.style.transform = '';
}

function navigate(target){
  if(target === 'back'){ if(openOvl){ ovlClose(); return; } return back(); }
  if(openOvl) ovlClose();
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

document.addEventListener('keydown', function(e){
  if(e.key !== 'Escape') return;
  if(openOvl) ovlClose(); else back();
});

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

function popFab(){
  if(REDUCED) return;
  var f = current().querySelector('.dock .fab');
  if(!f) return;
  A.remove(f);
  A({ targets: f, scale: [0.4, 1], opacity: [0, 1], duration: 520, delay: 260, easing: 'spring(1, 78, 11, 0)',
      complete: function(){ f.style.transform = ''; f.style.opacity = ''; } });
  setTimeout(function(){ A.remove(f); f.style.transform = ''; f.style.opacity = ''; }, 1200);
}

renderAirtime(); renderPower(); renderLoan(); renderCard();
layout();
setTimeout(function(){ layout(); enter(screens.Main); countBalance(); popFab(); }, 60);
"""

HTML = ("<title>Banking Flow Prototype</title>\n<style>\n" + build.faces(True) + CSS + "\n</style>\n"
  '<div class="wrap">\n'
  '  <div class="device" id="device">\n'
  '    <div class="stage" id="stage">\n' + screens + overlays + '    </div>\n  </div>\n'
  '  <p class="legend" id="legend">Tap through it. The <b>black circle</b> at the bottom right opens send, receive, activity and bills over a blurred page. '
  'The <b>ask bar</b> beside it opens the voice sheet, and the <b>cog</b> opens settings. <b>Back</b> is the chevron at the bottom left, on every screen. '
  'Drag the black knob to confirm a payment, or just tap it. Every screen <b>scrolls</b>. The <b>bundle chips</b>, the <b>loan stepper</b>, the '
  '<b>switches</b> and the <b>All, In, Out</b> tabs all really change. Anything that answers <em>not wired up</em> is a screen this walkthrough does not include.</p>\n'
  '</div>\n<div id="toast"></div>\n'
  '<script>\n' + ANIME + '\n</script>\n'
  '<script>\n' + JS + '\n</script>\n')

open(os.path.join(OUT, "prototype.html"), "w").write(HTML)
print("prototype.html", os.path.getsize(os.path.join(OUT, "prototype.html")), "bytes,", len(ORDER), "screens")
