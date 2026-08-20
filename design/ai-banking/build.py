# Generates the .dc.html artboards for the AI banking design canvas.
# Look and feel live in tokens.py. Run: python3 build.py
import os, re
OUT = os.path.dirname(os.path.abspath(__file__))

from tokens import *

import base64
_FDIR = os.path.join(OUT, "fonts")
_FCACHE = {}
def _b64(name):
    if name not in _FCACHE:
        _FCACHE[name] = base64.b64encode(open(os.path.join(_FDIR, name), "rb").read()).decode("ascii")
    return _FCACHE[name]

def faces(italic=False):
    # Google's webfont subsets leave out the Naira sign, so the font rides
    # inside each screen instead. See fonts/README.md.
    out = ("    @font-face { font-family: '" + FONT_NAME + "'; font-style: normal; font-weight: " + FONT_WGHT + ";"
           " src: url(data:font/woff2;base64," + _b64(FONT_FILE) + ") format('woff2'); font-display: block; }\n")
    if italic:
        out += ("    @font-face { font-family: '" + FONT_NAME + "'; font-style: italic; font-weight: 400;"
                " src: url(data:font/woff2;base64," + _b64(FONT_ITAL) + ") format('woff2'); font-display: block; }\n")
    return out

def head(anim="", italic=False):
    return ('<!doctype html>\n<html>\n<head>\n  <meta charset="utf-8">\n'
      '  <script src="./support.js"></script>\n</head>\n<body>\n<x-dc>\n<helmet>\n'
      '  <style>\n' + faces(italic) +
      '    * { box-sizing: border-box; }\n'
      '    body { margin: 0; background: ' + BG + '; font-family: ' + FONT_UI + '; -webkit-font-smoothing: antialiased; }\n'
      '    a { color: ' + ACC_HEX + '; } a:hover { color: #C25A08; }\n'
      '    .num { font-variant-numeric: tabular-nums; }\n'
      + anim +
      '  </style>\n</helmet>\n')

FOOT = ('</x-dc>\n<script data-dc-script data-props=\'{"$preview":{"width":393,"height":852},'
  '"accent":{"editor":"color","default":"#1B3B6F","options":["#1B3B6F","#0E5A46","#5B3A7E","#8A4B1F"],"section":"Theme"}}\'>\n'
  'class Component extends DCLogic {\n'
  '  renderVals() {\n'
  '    return { accent: this.props.accent ?? \'#1B3B6F\' };\n'
  '  }\n'
  '}\n</script>\n</body>\n</html>\n')

def screen(inner):
    return ('<div style="position: relative; width: 393px; height: 852px; background: ' + BG
            + '; color: ' + INK + '; overflow: hidden">\n' + inner + '\n</div>\n')

def _near(v, scale):
    return min(scale, key=lambda x: (abs(x - v), x))

def snap(html):
    """Pull every size, gap and radius onto its scale. Nothing drifts."""
    html = re.sub(r"font-size: ([0-9.]+)px",
                  lambda m: "font-size: %dpx" % _near(float(m.group(1)), TYPE), html)
    html = re.sub(r"font-weight: (\d+)",
                  lambda m: "font-weight: %d" % WEIGHT.get(int(m.group(1)), 500), html)
    html = re.sub(r"\b(gap|row-gap|column-gap): ([0-9.]+)px",
                  lambda m: "%s: %dpx" % (m.group(1), _near(float(m.group(2)), SPACE)), html)

    def _rad(m):
        v = float(m.group(1))
        if v >= 100 or v < 8:          # a pill, or too small to belong to the scale
            return m.group(0)
        return "border-radius: %dpx" % _near(v, RADII)
    html = re.sub(r"border-radius: ([0-9.]+)px", _rad, html)

    def _pad(m):
        out = []
        for p in m.group(1).split():
            if p.endswith("px"):
                v = float(p[:-2])
                out.append("0" if v == 0 else "%dpx" % _near(v, SPACE))
            else:
                out.append(p)
        return "padding: " + " ".join(out)
    html = re.sub(r"padding: ([^;\"]+)", _pad, html)
    return html

NAIRA = "&#8358;"
EMIT = (__name__ == "__main__")
SCREENS = {}

def hook(go="", act=""):
    """data-go navigates, data-act runs an action. Artboards ignore both."""
    out = ""
    if go:
        out += ' data-go="' + go + '"'
    if act:
        out += ' data-act="' + act + '"'
    return out

def write(name, inner, anim="", italic=False):
    inner = snap(inner)
    inner = inner.replace(NAIRA, '<span style="margin: 0 0.09em 0 0.05em">' + NAIRA + '</span>')
    SCREENS[name] = inner
    if EMIT:
        open(os.path.join(OUT, name + ".dc.html"), "w").write(head(anim, italic) + screen(inner) + FOOT)

# ---------- shared pieces ----------

def mark(size=20, color=ACC, extra=""):
    """The model's badge: a filled squircle with a soft ring inside."""
    s = str(size)
    glyph = ACC_HEX if color.startswith("#FFF") else "#FFFFFF"
    return ('<svg width="' + s + '" height="' + s + '" viewBox="0 0 24 24" fill="none" style="flex-shrink: 0' + extra + '">'
      '<rect width="24" height="24" rx="8.6" fill="' + color + '"/>'
      '<circle cx="12" cy="12" r="6.1" stroke="' + glyph + '" stroke-width="1.7" opacity="0.5"/>'
      '<circle cx="12" cy="12" r="2.9" fill="' + glyph + '"/></svg>')

ICONS = {
 "airtime": '<rect x="7" y="3.2" width="10" height="17.6" rx="2.4"/><path d="M10.4 17.8h3.2"/>',
 "data": '<path d="M4.4 9.6a10.6 10.6 0 0 1 15.2 0"/><path d="M7.6 13a6.4 6.4 0 0 1 8.8 0"/><path d="M11.2 16.6h1.6"/>',
 "power": '<path d="M13 3 6 13.2h5.2L11 21l7-10.2h-5.2z"/>',
 "tv": '<rect x="3" y="6.6" width="18" height="11.4" rx="2.2"/><path d="M8.6 21h6.8M9.4 3.4 12 6.6l2.6-3.2"/>',
 "send": '<path d="M7.4 16.6 16.6 7.4M9.6 7.4h7v7"/>',
 "more": '<circle cx="8" cy="8" r="1.5" fill="currentColor" stroke="none"/><circle cx="16" cy="8" r="1.5" fill="currentColor" stroke="none"/><circle cx="8" cy="16" r="1.5" fill="currentColor" stroke="none"/><circle cx="16" cy="16" r="1.5" fill="currentColor" stroke="none"/>',
 "card": '<rect x="2.6" y="5.4" width="18.8" height="13.2" rx="2.6"/><path d="M2.6 10.2h18.8"/>',
 "loan": '<ellipse cx="12" cy="6.6" rx="7" ry="2.8"/><path d="M5 6.6v4.8c0 1.5 3.1 2.8 7 2.8s7-1.3 7-2.8V6.6"/><path d="M5 11.4v5c0 1.5 3.1 2.8 7 2.8s7-1.3 7-2.8v-5"/>',
 "pot": '<path d="M5 10.4h14V17a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3z"/><path d="M9 10.4V7.4a3 3 0 0 1 6 0v3"/>',
 "bet": '<rect x="3.6" y="3.6" width="16.8" height="16.8" rx="3.8"/><circle cx="8.4" cy="8.4" r="1.35" fill="currentColor" stroke="none"/><circle cx="12" cy="12" r="1.35" fill="currentColor" stroke="none"/><circle cx="15.6" cy="15.6" r="1.35" fill="currentColor" stroke="none"/>',
 "request": '<path d="M16.6 7.4 7.4 16.6M14.4 16.6h-7v-7"/>',
 "school": '<path d="M12 4.6 2.8 9 12 13.4 21.2 9z"/><path d="M6.6 11v4.6c0 1.4 2.4 2.6 5.4 2.6s5.4-1.2 5.4-2.6V11"/>',
 "water": '<path d="M12 3.6s5.8 6.2 5.8 9.8a5.8 5.8 0 0 1-11.6 0c0-3.6 5.8-9.8 5.8-9.8z"/>',
 "globe": '<circle cx="12" cy="12" r="8.6"/><path d="M3.4 12h17.2"/><path d="M12 3.4c2.4 2.6 2.4 14.6 0 17.2M12 3.4c-2.4 2.6-2.4 14.6 0 17.2"/>',
 "shield": '<path d="M12 3.4 19 6.2v5.4c0 4.2-2.9 7.3-7 9.1-4.1-1.8-7-4.9-7-9.1V6.2z"/>',
 "search": '<circle cx="10.6" cy="10.6" r="6.4"/><path d="M15.4 15.4 20 20"/>',
 "copy": '<rect x="8.4" y="8.4" width="11.6" height="11.6" rx="2.2"/><path d="M15.6 8.4V6.2a2.2 2.2 0 0 0-2.2-2.2H6.2A2.2 2.2 0 0 0 4 6.2v7.2a2.2 2.2 0 0 0 2.2 2.2h2.2"/>',
 "check": '<path d="M5.4 12.6 10 17.4 18.8 6.8"/>',
 "freeze": '<path d="M12 3.4v17.2M4.6 7.7l14.8 8.6M19.4 7.7 4.6 16.3"/>',
 "plus": '<path d="M12 5.2v13.6M5.2 12h13.6"/>',
 "minus": '<path d="M5.2 12h13.6"/>',
 "lock": '<rect x="4.6" y="10.2" width="14.8" height="9.4" rx="2.4"/><path d="M8 10.2V7.6a4 4 0 0 1 8 0v2.6"/>',
 "waste": '<path d="M4.6 7h14.8M9.4 7V4.8h5.2V7M6.8 7l.9 12.2a1.6 1.6 0 0 0 1.6 1.5h5.4a1.6 1.6 0 0 0 1.6-1.5L17.2 7"/>',
 "list": '<path d="M4 6.6h16M4 12h16M4 17.4h9.6"/>',
 "clock": '<circle cx="12" cy="12" r="8.6"/><path d="M12 6.8V12l3.4 2"/>',
 "receipt": '<path d="M5.4 3.6h13.2v17.2l-2.6-1.6-2.2 1.6-2.2-1.6-2.2 1.6-2.2-1.6-1.8 1.6z"/><path d="M8.6 8.6h6.8M8.6 12.8h6.8"/>',
 "bell": '<path d="M18 9.6a6 6 0 1 0-12 0c0 5.4-2.2 6.6-2.2 6.6h16.4S18 15 18 9.6z"/><path d="M13.7 19.6a2 2 0 0 1-3.4 0"/>',
 "mic": '<rect x="9.4" y="3" width="5.2" height="9.6" rx="2.6"/><path d="M5.6 11.2a6.4 6.4 0 0 0 12.8 0M12 17.6V21"/>',
}

def icon(name, size=22, color=INK2, sw=1.7, extra=""):
    s = str(size)
    return ('<svg width="' + s + '" height="' + s + '" viewBox="0 0 24 24" fill="none" stroke="' + color
            + '" stroke-width="' + str(sw) + '" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink: 0; color: ' + color
            + extra + '">' + ICONS[name] + '</svg>')

def avatar(t, size=38, bg=FILL, fg=INK2, act="", eid=""):
    s = str(size)
    return ('<div' + hook("", act) + (' id="' + eid + '"' if eid else '') + ' style="width: ' + s + 'px; height: ' + s
      + 'px; border-radius: ' + str(size // 2) + 'px; background: ' + bg
      + '; display: flex; align-items: center; justify-content: center; font-size: ' + str(round(size * 0.36, 1))
      + 'px; font-weight: 700; color: ' + fg + '; flex-shrink: 0">' + t + '</div>')

def chevbtn(size=24):
    return ('<div style="width: ' + str(size) + 'px; height: ' + str(size) + 'px; border-radius: ' + PILL
      + '; background: ' + FILL + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
      + chev(11, INK3, 2.2) + '</div>')

def badge(ic, t=None, size=44, radius=R_ICON, isz=None, dark=False):
    """A circle behind an icon. Grey by default, black when it is a main action."""
    bg = BTN if dark else FILL
    fg = "#FFFFFF" if dark else INK
    isz = isz or int(round(size * 0.46))
    return ('<div style="width: ' + str(size) + 'px; height: ' + str(size) + 'px; border-radius: ' + PILL
      + '; background: ' + bg + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
      + icon(ic, isz, fg, 1.8) + '</div>')

def chev(size=14, color=INK3, sw=2):
    s = str(size)
    return ('<svg width="' + s + '" height="' + s + '" viewBox="0 0 14 14" fill="none" style="flex-shrink: 0">'
            '<path d="M5 3l4 4-4 4" stroke="' + color + '" stroke-width="' + str(sw) + '" stroke-linecap="round" stroke-linejoin="round"/></svg>')

def back():
    return ('<div' + hook("back") + ' style="width: 40px; height: 40px; border-radius: ' + PILL + '; background: ' + FILL
            + '; display: flex; align-items: center; justify-content: center; margin-left: -2px; flex-shrink: 0">'
            '<svg width="19" height="19" viewBox="0 0 20 20" fill="none"><path d="M12 4.5 6.5 10l5.5 5.5" stroke="' + INK
            + '" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></div>')

def topbar(title="", right=""):
    t = ''
    if title:
        t = '<span style="flex-grow: 1; text-align: center; font-size: 17px; font-weight: 700; letter-spacing: -0.015em">' + title + '</span>'
    r = right if right else '<div style="width: 40px; flex-shrink: 0"></div>'
    return ('<div style="display: flex; align-items: center; height: 44px; gap: 8px">' + back() + t + r + '</div>')

def askbar(placeholder, height=106, tabbar=False):
    inner = ('<div' + hook("ask") + ' style="flex-grow: 1; height: 58px; border-radius: ' + pill(58)
        + '; background: ' + SURF + '; ' + SH_RAISE + '; display: flex; align-items: center; gap: 11px; padding: 0 18px 0 10px">'
        + mark(38) + '<span style="flex-grow: 1; font-size: 15.5px; font-weight: 500; color: ' + INK3 + '">' + placeholder + '</span>'
        + icon("mic", 19, INK3, 1.8) + '</div>')
    return ('<div class="dock" style="position: absolute; left: 0; right: 0; bottom: 0; z-index: 3; height: ' + str(height)
        + 'px; background: linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.86) 38%, ' + BG
        + ' 68%); display: flex; align-items: flex-end; padding: 0 18px 26px 18px"><div style="display: flex; width: 100%; gap: 10px; align-items: center">'
        + inner + '</div></div>')

def cardstyle(pad="18px", radius=R_CARD, bg=SURF, extra=""):
    return ('background: ' + bg + '; ' + CARD_EDGE + '; border-radius: ' + radius
            + '; padding: ' + pad + '; ' + SHADOW + extra)

def tinted(inner, note, pad="14px 16px"):
    """A field the model filled in. It speaks from its own soft panel."""
    return ('<div style="border-radius: ' + R_INNER + '; background: ' + ACC_SOFT
        + '; padding: ' + pad + '; display: flex; flex-direction: column; gap: 7px">' + inner
        + '<span style="font-size: 11.5px; font-weight: 700; letter-spacing: 0.01em; color: '
        + ACC_INK + '">' + note + '</span></div>')

def slide(label, go="", lid=""):
    return ('<div class="slide"' + hook(go) + ' style="position: relative; height: 60px; border-radius: ' + pill(60)
        + '; background: ' + BTN + '; ' + SH_BTN + '; display: flex; align-items: center; padding: 5px">'
        '<div class="knob" style="width: 50px; height: 50px; border-radius: ' + PILL + '; background: #FFFFFF'
        '; display: flex; align-items: center; justify-content: center; flex-shrink: 0; z-index: 2">'
        '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M4 10h11M11 6l4 4-4 4" stroke="' + BTN
        + '" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"/></svg></div>'
        '<span' + (' id="' + lid + '"' if lid else '') + ' class="num slideLabel" style="flex-grow: 1; text-align: center; font-size: 15.5px; font-weight: 600; color: rgba(255,255,255,0.9)'
        '; margin-right: 50px">' + label + '</span></div>')

def panel(text, size="15.5px", aid=""):
    return ('<div' + (' id="' + aid + '"' if aid else '') + ' style="flex-grow: 1; border-radius: ' + R_INNER
        + '; background: ' + ACC_SOFT + '; padding: 13px 15px; font-size: ' + size
        + '; line-height: 1.45; font-weight: 500; color: ' + INK + '; text-wrap: pretty">' + text + '</div>')

def aline(text, size="16.5px", aid=""):
    """The model speaking, beside its badge. Always from its own soft panel."""
    return ('<div style="display: flex; gap: 11px; align-items: flex-start">' + mark(34)
        + panel(text, size, aid) + '</div>')

def aicard(text, head="", size="15.5px", aid=""):
    """The model speaking with its panel run full width, badge on the row above."""
    h = ('<div style="display: flex; align-items: center; gap: 9px; padding: 1px 1px 0 1px">' + mark(30)
         + '<span style="font-size: 14.5px; font-weight: 700; letter-spacing: -0.01em; color: ' + INK + '">' + head + '</span></div>')
    return h + panel(text, size, aid)

def label(t, color=INK):
    """A section heading. Sentence case, because a shouted label is noise."""
    txt = t if t[:1].islower() else t[:1].upper() + t[1:].lower()
    return ('<div style="font-size: 17px; font-weight: 700; letter-spacing: -0.02em; color: ' + color + '">' + txt + '</div>')

def caption(t, color=INK3):
    """A quiet line above something, e.g. what you said."""
    return ('<div style="font-size: 13px; font-weight: 500; color: ' + color + '">' + t + '</div>')

def money(whole, dec, size=50, dsize=24, color=INK, dcolor=None):
    return ('<div style="display: flex; align-items: baseline; gap: 1px">'
        '<span class="num" style="font-size: ' + str(size) + 'px; font-weight: 800; letter-spacing: -0.04em; line-height: 1; color: '
        + color + '">' + whole + '</span><span class="num" style="font-size: ' + str(dsize)
        + 'px; font-weight: 700; letter-spacing: -0.025em; color: ' + (dcolor or INK3) + '">' + dec + '</span></div>')

def navbar(title):
    """Holds the back button. Its own title and background only appear once
    you have scrolled the big title away."""
    return ('<div class="nav" style="position: absolute; left: 0; right: 0; top: 0; z-index: 4; height: 98px; '
      'padding: 54px 20px 0 20px; display: flex; align-items: center; gap: 10px">'
      '<div class="navbg" style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; background: ' + SURF
      + '; border-bottom: 1px solid ' + LINE + '; opacity: 0"></div>'
      + '<div style="position: relative">' + back() + '</div>'
      + '<span class="navtitle" style="position: relative; flex-grow: 1; text-align: center; font-size: 17px; '
        'font-weight: 700; letter-spacing: -0.02em; color: ' + INK + '; opacity: 0">' + title + '</span>'
      '<div style="width: 40px; flex-shrink: 0"></div></div>')

def pagehead(title, sub=""):
    p = ''
    if sub:
        p = ('<div style="font-size: 15px; font-weight: 500; line-height: 1.45; color: ' + INK3
             + '; text-wrap: pretty">' + sub + '</div>')
    return ('<div class="phead" style="display: flex; flex-direction: column; gap: 6px">'
      '<div style="font-size: 30px; font-weight: 700; letter-spacing: -0.035em; line-height: 1.12; color: '
      + INK + '; text-wrap: balance">' + title + '</div>' + p + '</div>')

def T(title, sub=""):
    """Marks a screen's title. page() turns it into the bar and the big head."""
    return "\x00T\x01" + title + "\x01" + sub + "\x02"

_TMARK = re.compile("\x00T\x01(.*?)\x01(.*?)\x02", re.S)

def page(inner, gap=14, top=54, center=False, wash_h=0):
    nav = ""
    m = _TMARK.search(inner)
    if m:
        nav = navbar(m.group(1))
        inner = inner[:m.start()] + pagehead(m.group(1), m.group(2)) + inner[m.end():]
        top = 98
        gap = max(gap, 20)
    w = ''
    if wash_h:
        w = ('<div style="position: absolute; left: 0; right: 0; top: 0; height: ' + str(wash_h)
             + 'px; background: ' + WASH + '; pointer-events: none; z-index: 0"></div>')
    return (nav + '<div class="pg" style="position: relative; ' + ('justify-content: center; ' if center else '')
            + 'padding: ' + str(top) + 'px 20px 0 20px; display: flex; flex-direction: column; gap: '
            + str(gap) + 'px">\n' + w + '<div class="pgin" style="position: relative; display: flex; flex-direction: column; gap: '
            + str(gap) + 'px">' + inner + '</div>\n</div>')

# ================= HOME =================
def svc_tile(name, ic, go=""):
    return ('<div' + hook(go) + ' style="flex-grow: 1; flex-basis: 0; display: flex; flex-direction: column; align-items: center; gap: 8px">'
      + badge(ic, None, 48, R_TILE, 21, True)
      + '<span style="font-size: 11.5px; font-weight: 600; color: ' + INK2 + '">' + name + '</span></div>')

home = page(
  '<div style="display: flex; align-items: center; gap: 12px; height: 48px">'
    + avatar("IW", 44)
    + '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 2px">'
      + '<span style="font-size: 13px; font-weight: 500; color: ' + INK3 + '">Good morning</span>'
      + '<span style="font-size: 17px; font-weight: 700; letter-spacing: -0.02em; color: ' + INK + '">Ibrahim Weng</span></div>'
    + '<div style="width: 44px; height: 44px; border-radius: ' + PILL + '; background: ' + SURF + '; ' + SHADOW
      + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">' + icon("bell", 20, INK, 1.8) + '</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 8px; padding-top: 4px">'
    + caption("Total balance")
    + '<div id="mBal">' + money("&#8358;248,320", ".75", 44, 22, INK, INK3) + '</div>'
    + '<div style="display: flex; gap: 20px; align-items: center; padding-top: 4px">'
      '<div style="display: flex; align-items: center; gap: 6px">'
        '<svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M7 2.5v9M3.6 8.1 7 11.5l3.4-3.4" stroke="' + IN + '" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
        '<span class="num" style="font-size: 14px; font-weight: 600; color: ' + INK2 + '">&#8358;640,000 in</span></div>'
      '<div style="display: flex; align-items: center; gap: 6px">'
        '<svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M7 11.5v-9M3.6 5.9 7 2.5l3.4 3.4" stroke="' + INK3 + '" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
        '<span class="num" style="font-size: 14px; font-weight: 600; color: ' + INK2 + '">&#8358;391,680 out</span></div></div></div>'
  + '<div style="' + cardstyle("16px 8px") + '; display: flex; gap: 4px">'
      + svc_tile("Airtime","airtime","Airtime") + svc_tile("Data","data","Airtime")
      + svc_tile("Power","power","PowerPay") + svc_tile("Send","send","Pay") + svc_tile("More","more","Services") + '</div>'
  + label("Three things this morning")
  + '<div style="display: flex; flex-direction: column; gap: 12px; margin-top: -4px">'

    + '<div id="mBill" style="' + cardstyle("16px") + '; display: flex; flex-direction: column; gap: 12px">'
      + aicard("Your Ikeja Electric bill lands on Thursday. Last month it was &#8358;7,500.", "Due on Thursday")
      + '<div style="display: flex; gap: 8px; align-items: center">'
        '<div' + hook("PowerPay") + ' style="flex-grow: 1; height: 52px; border-radius: ' + PILL + '; background: ' + BTN + '; ' + SH_BTN
        + '; color: ' + BTN_INK + '; display: flex; align-items: center; justify-content: center; font-size: 15px; font-weight: 700">Pay &#8358;8,000 now</div>'
        '<div' + hook("", "dismiss") + ' style="width: 52px; height: 52px; border-radius: ' + PILL + '; background: ' + FILL + '; display: flex; align-items: center; justify-content: center">'
        '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M4.5 4.5l7 7M11.5 4.5l-7 7" stroke="' + INK2 + '" stroke-width="2" stroke-linecap="round"/></svg></div></div></div>'

    + '<div style="' + cardstyle("16px") + '; display: flex; flex-direction: column; gap: 12px">'
      + aicard("Your data usually runs out about now. The same 5GB is &#8358;2,500.", "Your data is nearly gone")
      + '<div style="display: flex; align-items: center; gap: 12px; height: 64px; border-radius: ' + R_INNER + '; background: ' + FILL + '; padding: 0 12px">'
        + badge("data", None, 40, R_ICON, 20)
        + '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 2px">'
          '<span style="font-size: 15px; font-weight: 600">5GB for 30 days</span>'
          '<span style="font-size: 13px; font-weight: 500; color: ' + INK3 + '">MTN &#183; your line</span></div>'
        '<span class="num" style="font-size: 15px; font-weight: 700">&#8358;2,500</span></div>'
      '<div' + hook("Airtime") + ' style="height: 48px; border-radius: ' + PILL + '; background: ' + FILL
      + '; display: flex; align-items: center; justify-content: center; gap: 6px">'
        '<span style="font-size: 15px; font-weight: 600; color: ' + INK + '">Buy it again</span>' + chev(12, INK, 2.2) + '</div></div>'

    + '<div' + hook("Answer") + ' style="' + cardstyle("16px") + '; display: flex; flex-direction: column; gap: 12px">'
      + aicard("You spent &#8358;18,900 on airtime and data last month. That is your highest month this year.", "Where your money went") + '</div>'
  + '</div>', 16) + askbar("Ask, or just say what you need", 112)
write("Main", home)

# ================= ALL SERVICES =================
def grid_tile(name, ic, go="", act=""):
    return ('<div' + hook(go, act) + ' style="flex-grow: 1; flex-basis: 0; display: flex; flex-direction: column; align-items: center; gap: 10px">'
      + badge(ic, None, 62, R_TILE, 27)
      + '<span style="font-size: 11.5px; font-weight: 600; color: ' + INK2 + '; text-align: center">' + name + '</span></div>')

def listrow(name, ic, sub="", last=False, go="", act="soon"):
    border = "" if last else "border-bottom: 1px solid " + LINE + "; "
    sb = ''
    if sub:
        sb = '<span style="font-size: 12px; font-weight: 500; color: ' + INK3 + '">' + sub + '</span>'
    return ('<div' + hook(go, "" if go else act) + ' style="' + border + 'display: flex; align-items: center; gap: 13px; height: 62px; padding: 0 14px">'
      + badge(ic, None, 40, R_ICON, 20)
      + '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 2px">'
      '<span style="font-size: 15px; font-weight: 700; letter-spacing: -0.01em">' + name + '</span>' + sb + '</div>'
      + chevbtn() + '</div>')

services = page(
  T("All services", "Everything you can pay for from here")
  + '<div' + hook("ask") + ' style="height: 52px; border-radius: 26px; background: ' + FILL + '; ' + SHADOW
    + '; display: flex; align-items: center; gap: 11px; padding: 0 17px">' + icon("search", 19, INK3, 1.6)
    + '<span style="flex-grow: 1; font-size: 15.5px; font-weight: 500; color: ' + INK3 + '">Search, or say what you need</span>'
    + icon("mic", 18, INK3, 1.5) + '</div>'
  + '<div style="display: flex; flex-direction: column; gap: 12px">' + label("YOU USE THESE MOST")
    + '<div style="display: flex; gap: 10px">' + grid_tile("Airtime","airtime","Airtime") + grid_tile("Data","data","Airtime") + grid_tile("Power","power","PowerPay") + grid_tile("Send","send","Pay") + '</div>'
    + '<div style="display: flex; gap: 10px">' + grid_tile("Cable TV","tv","","soon") + grid_tile("Betting","bet","","soon") + grid_tile("Loan","loan","Loan") + grid_tile("Cards","card","Card") + '</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 11px">' + label("BILLS")
    + '<div style="background: ' + SURF + '; ' + CARD_EDGE + '; border-radius: ' + R_PANEL + '; ' + SHADOW + '; overflow: hidden">'
      + listrow("Internet", "globe", "Spectranet, Smile, Starlink")
      + listrow("Water", "water", "State water boards")
      + listrow("Waste", "waste", "LAWMA and others")
      + listrow("School fees", "school", "WAEC, JAMB, tuition", True) + '</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 11px">' + label("SAVE AND BORROW")
    + '<div style="background: ' + SURF + '; ' + CARD_EDGE + '; border-radius: ' + R_PANEL + '; ' + SHADOW + '; overflow: hidden">'
      + listrow("Savings pot", "pot", "Put money aside")
      + listrow("Fixed savings", "clock", "Lock it for a set time", True) + '</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 11px">' + label("MONEY")
    + '<div style="background: ' + SURF + '; ' + CARD_EDGE + '; border-radius: ' + R_PANEL + '; ' + SHADOW + '; overflow: hidden">'
      + listrow("Request money", "request", "Ask someone to pay you")
      + listrow("Send abroad", "globe", "Pounds, dollars and euros", True) + '</div></div>', 15)
services += ('<div style="position: absolute; left: 0; right: 0; bottom: 0; height: 90px; background: linear-gradient(180deg, rgba(244,245,247,0) 0%, '
  + BG + ' 72%)"></div>')
write("Services", services)

def offer(text, action, go=""):
    return ('<div style="' + cardstyle("14px") + '; display: flex; flex-direction: column; gap: 12px">'
      + aline(text, "15.5px")
      + '<div' + hook(go, "" if go else "soon") + ' style="height: 46px; border-radius: ' + pill(46)
      + '; background: ' + FILL + '; display: flex; align-items: center; justify-content: center; gap: 7px">'
      '<span style="font-size: 14.5px; font-weight: 700; color: ' + INK + '">' + action + '</span>'
      + chev(12, INK, 2.2) + '</div></div>')

def quote(t):
    return ('<div style="display: flex; flex-direction: column; gap: 6px">' + caption("You said")
      + '<span style="font-size: 17px; font-style: italic; font-weight: 500; color: ' + INK2 + '">' + t + '</span></div>')

def plainrow(k, v, last=False, vcolor=INK, chevron=False, vid=""):
    border = "" if last else "border-bottom: 1px solid " + LINE + "; "
    c = chevbtn(22) if chevron else ""
    return ('<div style="' + border + 'display: flex; align-items: center; height: 54px; padding: 0 16px; gap: 10px">'
      '<span style="flex-grow: 1; font-size: 14px; font-weight: 500; color: ' + INK2 + '">' + k + '</span>'
      '<span' + (' id="' + vid + '"' if vid else '') + ' class="num" style="font-size: 15px; font-weight: 700; color: '
      + vcolor + '">' + v + '</span>' + c + '</div>')

def bundle(size, price, act=""):
    return ('<div' + hook("", act) + ' class="bchip" style="flex-grow: 1; flex-basis: 0; height: 62px; border-radius: ' + R_BUNDLE
      + '; background: ' + FILL + '; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 3px">'
      '<span style="font-size: 14px; font-weight: 700">' + size + '</span>'
      '<span class="num" style="font-size: 12.5px; font-weight: 500; color: ' + INK2 + '">' + price + '</span></div>')

# ================= BUY AIRTIME / DATA =================
airtime = page(
  T("Buy data", "Check the parts I filled in before it goes")
  + quote("2k data for mum")
  + aline("5GB for 30 days, on Mum&#8217;s MTN line.", "17.5px", "aLine")
  + '<div style="' + cardstyle("14px") + '; display: flex; flex-direction: column; gap: 10px">'
    + tinted('<div style="display: flex; align-items: center; gap: 12px">' + avatar("M", 38, FILL, INK2, "", "bAv")
        + '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 2px">'
          '<span id="bWho" style="font-size: 15px; font-weight: 600">Mum</span>'
          '<span class="num" style="font-size: 12.5px; color: ' + INK2 + '">0803 214 4471 &#183; MTN</span></div>' + chev() + '</div>',
        "The number you top up most")
    + tinted('<div style="display: flex; align-items: center; gap: 12px">' + icon("data", 21, INK2, 1.6)
        + '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 2px">'
          '<span id="bSize" style="font-size: 15px; font-weight: 600">5GB for 30 days</span>'
          '<span style="font-size: 12.5px; color: ' + INK2 + '">It will not renew on its own</span></div>'
        '<span id="bPrice" class="num" style="font-size: 16px; font-weight: 600">&#8358;2,500</span></div>',
        "The bundle you bought last month")
    + '<div style="background: ' + FILL + '; border-radius: ' + R_FIELD + '; overflow: hidden">'
      + plainrow("From", "Everyday &#183; 0102 4457 88", False, INK, True)
      + plainrow("You get back", "&#8358;25", True, IN, False, "bBack") + '</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 11px">' + label("OTHER BUNDLES")
    + '<div style="display: flex; gap: 8px">' + bundle("1GB", "&#8358;800", "gb|1GB for 7 days|800") + bundle("2GB", "&#8358;2,000", "gb|2GB for 30 days|2,000") + bundle("10GB", "&#8358;4,000", "gb|10GB for 30 days|4,000") + '</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 11px">' + label("YOU ALSO TOP UP")
    + '<div style="display: flex; gap: 14px; align-items: center">'
      + avatar("D", 46, act="who|Dad") + avatar("K", 46, act="who|Kemi") + avatar("B", 46, act="who|Bro") + avatar("T", 46, act="who|Tunde")
      + '<div style="width: 46px; height: 46px; border-radius: 23px; border: 1px dashed ' + LINE2
      + '; display: flex; align-items: center; justify-content: center">' + icon("plus", 18, INK3, 1.7) + '</div></div></div>', 15)
airtime += ('<div style="position: absolute; left: 0; right: 0; bottom: 0; padding: 30px 20px 30px 20px; background: linear-gradient(180deg, rgba(244,245,247,0) 0%, '
  + BG + ' 40%)">' + slide("Slide to buy &#8358;2,500", "done|Airtime", "aSlide") + '</div>')
write("Airtime", airtime, "", True)

# ================= ELECTRICITY, PAID =================
power = page(
  T("Bill paid", "Ikeja Electric, a moment ago")
  + '<div style="display: flex; flex-direction: column; gap: 14px; align-items: flex-start">'
    '<div style="width: 52px; height: 52px; border-radius: ' + PILL + '; background: color-mix(in srgb, ' + ACC
      + ' 10%, ' + SURF + '); border: 1px solid color-mix(in srgb, ' + ACC + ' 26%, transparent); display: flex; align-items: center; justify-content: center">'
      + icon("check", 24, ACC, 2.0) + '</div>'
    '<div style="display: flex; flex-direction: column; gap: 5px">' + money("&#8358;8,000", "", 38, 20)
      + '<span style="font-size: 14px; color: ' + INK2 + '">Paid to Ikeja Electric</span></div></div>'
  + aline("Type this into your meter. I have sent it to your messages as well.", "16.5px")
  + '<div style="' + cardstyle("16px") + '; display: flex; flex-direction: column; gap: 12px">'
    + label("METER TOKEN")
    + '<span class="num" style="font-size: 21px; font-weight: 600; letter-spacing: 0.02em; color: ' + INK + '">4471 8823 0195 6640 3277</span>'
    + '<div' + hook("", "copy") + ' style="display: flex; align-items: center; justify-content: center; gap: 8px; height: 46px; border-radius: 23px; background: ' + FILL + '">'
      + icon("copy", 17, INK, 1.8) + '<span style="font-size: 14px; font-weight: 600; color: ' + INK + '">Copy the token</span></div></div>'
  + '<div style="background: ' + SURF + '; ' + CARD_EDGE + '; border-radius: ' + R_PANEL + '; ' + SHADOW + '; overflow: hidden">'
    + plainrow("Meter", "0102 4457 8891")
    + plainrow("Units", "38.4 kWh")
    + plainrow("Reference", "IKJ-90441-2286", True) + '</div>'
  + offer("Want me to pay this every month?", "Set it up", "Rules"), 15)
power += ('<div style="position: absolute; left: 0; right: 0; bottom: 0; padding: 30px 20px 30px 20px; display: flex; gap: 10px; background: linear-gradient(180deg, rgba(244,245,247,0) 0%, '
  + BG + ' 40%)">'
  '<div' + hook("", "soon") + ' style="flex-grow: 1; height: 52px; border-radius: ' + pill(52) + '; background: ' + FILL
  + '; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 15px; font-weight: 700; color: ' + INK + '">Share receipt</div>'
  '<div' + hook("Main") + ' style="flex-grow: 1; height: 52px; border-radius: ' + pill(52) + '; background: ' + BTN + '; ' + SH_BTN
  + '; display: flex; align-items: center; justify-content: center; font-size: 15px; font-weight: 700; color: ' + BTN_INK + '">Done</div></div>')
write("Power", power)

# ================= BILLS =================
def chip(t, color=INK3):
    """A status, said in the subtitle rather than shouted in a pill."""
    txt = t if t[:1].islower() else t[:1].upper() + t[1:].lower()
    return ('<span style="font-size: 13px; font-weight: 600; color: ' + color + '; white-space: nowrap">&#183; ' + txt + '</span>')

def bill(name, ic, sub, amount, chp, last=False, dim=False, go="", act="soon"):
    border = "" if last else "border-bottom: 1px solid " + LINE + "; "
    nc = INK3 if dim else INK
    return ('<div' + hook(go, "" if go else act) + ' style="' + border + 'display: flex; align-items: center; gap: 12px; height: 64px; padding: 0 14px">'
      + badge(ic, None, 40, R_ICON, 20)
      + '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 4px">'
      '<span style="font-size: 15px; font-weight: 700; letter-spacing: -0.01em; color: ' + nc + '">' + name + '</span>'
      '<div style="display: flex; align-items: center; gap: 4px">'
      '<span style="font-size: 13px; font-weight: 500; color: ' + INK3 + '; white-space: nowrap">' + sub + '</span>' + chp + '</div></div>'
      '<span class="num" style="font-size: 15px; font-weight: 700; color: ' + nc + '">' + amount + '</span></div>')

bills = page(
  T("Bills", "Everything that repeats each month")
  + '<div style="' + cardstyle("14px") + '">' + aline("&#8358;34,500 of bills this month. Two of them are not covered.", "16px") + '</div>'
  + '<div style="display: flex; flex-direction: column; gap: 11px">' + label("THIS MONTH")
    + '<div style="background: ' + SURF + '; ' + CARD_EDGE + '; border-radius: ' + R_PANEL + '; ' + SHADOW + '; overflow: hidden">'
      + bill("Ikeja Electric", "power", "Due Thursday", "&#8358;8,000", chip("I pay it", ACC_TEXT), False, False, "PowerPay")
      + bill("DStv Compact", "tv", "Due 24 August", "&#8358;12,500", chip("Not covered", WARN))
      + bill("Spectranet", "globe", "Due 27 August", "&#8358;15,000", chip("Not covered", WARN))
      + bill("LAWMA waste", "waste", "Paid 2 August", "&#8358;2,000", '', False, True)
      + bill("MTN 5GB", "data", "Paid 4 August", "&#8358;2,500", '', True, True) + '</div></div>'
  + '<div style="height: 50px; border-radius: 25px; background: ' + FILL
    + '; display: flex; align-items: center; justify-content: center; gap: 9px">' + icon("plus", 17, INK, 2)
    + '<span style="font-size: 14.5px; font-weight: 600; color: ' + INK + '">Add a bill</span></div>'
  + offer("DStv and Spectranet are not covered. Shall I pay them?", "Set both up", "Rules"), 14) + askbar("Ask about your bills", 106)
write("Bills", bills)

# ================= LOAN =================
def rowline(k, v, last=False, strong=False, vcolor=INK, vid="", kid=""):
    border = "" if last else "border-bottom: 1px solid " + LINE + "; "
    kw = "700" if strong else "500"
    ks = "14.5px" if strong else "14px"
    vs = "18px" if strong else "15px"
    kc = INK if strong else INK2
    return ('<div style="' + border + 'display: flex; align-items: center; height: 46px; padding: 0 16px; gap: 10px">'
      '<span' + (' id="' + kid + '"' if kid else '') + ' style="flex-grow: 1; font-size: ' + ks + '; font-weight: ' + kw + '; color: ' + kc + '">' + k + '</span>'
      '<span' + (' id="' + vid + '"' if vid else '') + ' class="num" style="font-size: ' + vs + '; font-weight: 700; color: ' + vcolor + '">' + v + '</span></div>')

def dchip(t, on, act=""):
    if on:
        return ('<div' + hook("", act) + ' class="dchip on" style="flex-grow: 1; flex-basis: 0; height: 46px; border-radius: ' + pill(46)
          + '; background: ' + BTN + '; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700; color: '
          + BTN_INK + '">' + t + '</div>')
    return ('<div' + hook("", act) + ' class="dchip" style="flex-grow: 1; flex-basis: 0; height: 46px; border-radius: ' + pill(46)
      + '; background: ' + FILL + '; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 600; color: '
      + INK2 + '">' + t + '</div>')

loan = page(
  T("Borrow", "The whole cost, before you decide")
  + aline("You asked what you could borrow. Here is the whole cost.", "16px")
  + '<div style="' + cardstyle("16px") + '; display: flex; flex-direction: column; gap: 14px">'
    + label("HOW MUCH YOU WANT")
    + '<div style="display: flex; align-items: center; gap: 14px">'
      '<div' + hook("", "loan|-") + ' style="width: 42px; height: 42px; border-radius: 21px'
      + '; display: flex; align-items: center; justify-content: center">' + icon("minus", 17, INK2, 1.8) + '</div>'
      '<div id="lnAmt" style="flex-grow: 1; display: flex; justify-content: center">' + money("&#8358;150,000", "", 32, 18) + '</div>'
      '<div' + hook("", "loan|+") + ' style="width: 42px; height: 42px; border-radius: 21px'
      + '; display: flex; align-items: center; justify-content: center">' + icon("plus", 17, INK2, 1.8) + '</div></div>'
    + '<div style="display: flex; flex-direction: column; gap: 7px">'
      '<div style="height: 6px; border-radius: 3px; background: ' + FILL + '; overflow: hidden"><div id="lnBar" style="width: 60%; height: 6px; border-radius: 3px; background: ' + ACC + '"></div></div>'
      '<div style="display: flex; justify-content: space-between"><span class="num" style="font-size: 12.5px; color: ' + INK3 + '">&#8358;10,000</span>'
      '<span class="num" style="font-size: 12.5px; color: ' + INK3 + '">&#8358;250,000 is your limit</span></div></div>'
    + '<div style="display: flex; gap: 9px">' + dchip("30 days", False, "term|1") + dchip("60 days", False, "term|2") + dchip("90 days", True, "term|3") + '</div></div>'
  + '<div style="background: ' + SURF + '; ' + CARD_EDGE + '; border-radius: ' + R_PANEL + '; ' + SHADOW + '; overflow: hidden">'
    + rowline("You get today", "&#8358;150,000", False, False, INK, "lnGet")
    + rowline("Interest, 4% a month", "&#8358;18,000", False, False, INK, "lnInt")
    + rowline("One off fee", "&#8358;1,500")
    + rowline("You pay back in all", "&#8358;169,500", False, True, INK, "lnTot")
    + rowline("Three payments of", "&#8358;56,500", False, False, INK, "lnPer", "lnPerK")
    + rowline("First payment", "19 September", True, False, INK, "lnDate") + '</div>'
  + '<div style="display: flex; gap: 9px; align-items: flex-start">' + icon("lock", 16, INK3, 1.6, "; margin-top: 2px")
    + '<span style="font-size: 14.5px; font-weight: 500; line-height: 1.45; color: ' + INK2
    + '; text-wrap: pretty">Pay late and it costs &#8358;2,000 a day. Late loans are reported to the credit bureau.</span></div>', 14)
loan += ('<div style="position: absolute; left: 0; right: 0; bottom: 0; padding: 30px 20px 30px 20px; background: linear-gradient(180deg, rgba(244,245,247,0) 0%, '
  + BG + ' 40%)">' + slide("Slide to take &#8358;150,000", "done|Loan", "lnSlide") + '</div>')
write("Loan", loan)

# ================= VIRTUAL CARD =================
def act(name, ic, go="", action="soon"):
    return ('<div' + hook(go, "" if go else action) + ' style="flex-grow: 1; flex-basis: 0; display: flex; flex-direction: column; align-items: center; gap: 9px">'
      + badge(ic, None, 52, R_ACT, 23)
      + '<span style="font-size: 11.5px; font-weight: 600; color: ' + INK2 + '">' + name + '</span></div>')

vcard = page(
  T("Virtual card", "Made for one merchant, with its own limit")
  + '<div id="cdFace" style="height: 194px; border-radius: ' + R_CARDLG + '; background: ' + CARD_FACE + '; ' + SH_RAISE + '; padding: 20px; display: flex; flex-direction: column; justify-content: space-between; '
    + SHADOW + '">'
    '<div style="display: flex; align-items: flex-start; justify-content: space-between">'
      + mark(24, "#FFFFFF") + '<span style="font-size: 10px; font-weight: 700; letter-spacing: 0.16em; color: rgba(255,255,255,0.7)">NETFLIX ONLY</span></div>'
    '<div style="width: 34px; height: 25px; border-radius: 5px; background: rgba(255,255,255,0.22); border: 1px solid rgba(255,255,255,0.28); display: flex; flex-direction: column; justify-content: center; gap: 3px; padding: 0 5px">'
      '<div style="height: 1.5px; background: rgba(255,255,255,0.45)"></div>'
      '<div style="height: 1.5px; background: rgba(255,255,255,0.45)"></div></div>'
    '<div style="display: flex; flex-direction: column; gap: 16px">'
      '<span id="cdNum" class="num" style="font-size: 20px; font-weight: 500; letter-spacing: 0.12em; color: #FFFFFF">5399 &#8226;&#8226;&#8226;&#8226; &#8226;&#8226;&#8226;&#8226; 4471</span>'
      '<div style="display: flex; align-items: flex-end; justify-content: space-between">'
        '<div style="display: flex; flex-direction: column; gap: 4px">'
          '<span style="font-size: 9px; font-weight: 600; letter-spacing: 0.14em; color: rgba(255,255,255,0.55)">CARD HOLDER</span>'
          '<span style="font-size: 13px; font-weight: 500; letter-spacing: 0.06em; color: #FFFFFF">IBRAHIM WENG</span></div>'
        '<div style="display: flex; flex-direction: column; gap: 4px">'
          '<span style="font-size: 9px; font-weight: 600; letter-spacing: 0.14em; color: rgba(255,255,255,0.55)">EXPIRES</span>'
          '<span class="num" style="font-size: 13px; font-weight: 500; color: #FFFFFF">09/28</span></div>'
        '</div></div></div>'
  + '<div style="display: flex; gap: 10px">' + act("Reveal","search","","reveal") + act("Freeze","freeze","","freeze") + act("Fund","plus") + act("Rules","list","Rules") + '</div>'
  + '<div style="' + cardstyle("14px") + '">' + aline("This card has paid Netflix four times, &#8358;21,000 in all.", "15.5px") + '</div>'
  + '<div style="' + cardstyle("15px") + '; display: flex; flex-direction: column; gap: 11px">'
    + '<div style="display: flex; align-items: baseline; justify-content: space-between">'
      '<span style="font-size: 13.5px; color: ' + INK2 + '">Spent this month</span>'
      '<span class="num" style="font-size: 15px; font-weight: 600">&#8358;21,000 of &#8358;50,000</span></div>'
    + '<div style="height: 7px; border-radius: 4px; background: ' + FILL + '; overflow: hidden"><div style="width: 42%; height: 7px; border-radius: 4px; background: ' + ACC + '"></div></div>'
    + '<span class="num" style="font-size: 12.5px; color: ' + INK3 + '">&#8358;29,000 left before it stops working</span></div>'
  + '<div style="height: 50px; border-radius: 25px; background: ' + FILL
    + '; display: flex; align-items: center; justify-content: center; gap: 9px">' + icon("plus", 17, INK, 2)
    + '<span style="font-size: 14.5px; font-weight: 600; color: ' + INK + '">Make another card</span></div>', 14) + askbar("Ask about this card", 106)
write("Card", vcard)

# ================= ASKING BY VOICE =================
ANIM = ('    @keyframes sweep { 0% { transform: translateX(-22%); } 100% { transform: translateX(22%); } }\n'
        '    .sweep { animation: sweep 2.6s ease-in-out infinite alternate; }\n')

def wave():
    hs = [10,18,30,14,38,24,44,20,32,12,26,40,16,28,10,22,34,14,8,18,10,6]
    ops = [0.3,0.5,0.7,0.5,1,0.8,1,0.7,0.85,0.4,0.7,1,0.5,0.75,0.3,0.6,0.85,0.35,0.25,0.4,0.22,0.18]
    out = '<div style="display: flex; align-items: center; gap: 3px; height: 44px">'
    for h, o in zip(hs, ops):
        out += ('<div class="wv" style="width: 3px; height: ' + str(h) + 'px; border-radius: 2px; background: ' + ACC
                + '; opacity: ' + str(o) + '; transform-origin: center"></div>')
    return out + '</div>'

def sugg(t, go=""):
    return ('<div' + hook(go) + ' style="height: 48px; border-radius: ' + pill(48) + '; background: ' + FILL
      + '; display: flex; align-items: center; padding: 0 18px; font-size: 14.5px; font-weight: 600; color: ' + INK + '">' + t + '</div>')

ask = ('<div' + hook("back") + ' class="fauxbg" style="padding: 54px 20px 0 20px; display: flex; flex-direction: column; gap: 15px; opacity: 0.42">'
  '<div style="display: flex; align-items: center; justify-content: space-between; height: 44px">'
    '<div style="display: flex; flex-direction: column; gap: 4px">' + label("EVERYDAY ACCOUNT")
    + '<span class="num" style="font-size: 12px; color: ' + INK3 + '; letter-spacing: 0.07em">0102 4457 88</span></div>'
    '<div style="width: 38px; height: 38px; border-radius: ' + PILL + '; background: ' + FILL + '"></div></div>'
  + money("&#8358;248,320", ".75", 48, 23)
  + '<div style="display: flex; gap: 10px">' + svc_tile("Airtime","airtime") + svc_tile("Data","data")
    + svc_tile("Power","power") + svc_tile("Send","send") + svc_tile("More","more") + '</div></div>')
ask += ('<div style="position: absolute; left: 0; right: 0; top: 318px; bottom: 0; background: ' + SURF
  + '; border-top-left-radius: 28px; border-top-right-radius: 28px; box-shadow: 0 -10px 30px rgba(15,21,33,0.09); overflow: hidden; display: flex; flex-direction: column">'
  '<div style="height: 2px; width: 100%; overflow: hidden; flex-shrink: 0"><div class="sweep" style="height: 2px; width: 100%; background: linear-gradient(90deg, rgba(0,0,0,0) 0%, '
  + ACC + ' 50%, rgba(0,0,0,0) 100%)"></div></div>'
  '<div style="display: flex; justify-content: center; padding: 12px 0 0 0"><div style="width: 38px; height: 4px; border-radius: 2px; background: ' + LINE2 + '"></div></div>'
  '<div style="padding: 24px 20px 16px 20px; display: flex; flex-direction: column; gap: 22px; flex-grow: 1">'
    '<div style="display: flex; align-items: center; gap: 9px">' + mark(20) + label("LISTENING", ACC_TEXT) + '</div>'
    '<div style="font-size: 28px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.26; color: ' + INK + '; text-wrap: pretty">2k data for<span style="color: ' + INK3 + '"> mum</span></div>'
    + wave()
    + '<div style="display: flex; flex-direction: column; gap: 12px">' + label("OR TRY ONE OF THESE")
      + '<div style="display: flex; flex-direction: column; gap: 8px">'
      + sugg("Pay my light bill", "PowerPay") + sugg("How much did I spend on data?", "Answer") + sugg("What can I borrow?", "Loan") + '</div></div></div>'
  '<div style="padding: 0 20px 30px 20px; display: flex; gap: 10px; align-items: center">'
    '<div' + hook("Airtime") + ' style="flex-grow: 1; height: 56px; border-radius: 28px; background: color-mix(in srgb, ' + ACC + ' 8%, ' + SURF
    + '); border: 1px solid ' + ACC + '; display: flex; align-items: center; justify-content: center">'
    '<span style="font-size: 15px; font-weight: 600; color: ' + ACC + '">Release to send</span></div>'
    '<div' + hook("back") + ' style="width: 56px; height: 56px; border-radius: 28px; background: ' + FILL + ''
    + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
    '<div style="width: 14px; height: 14px; border-radius: 3px; background: ' + INK3 + '"></div></div></div></div>')
write("Ask", ask, ANIM)

# ================= ANSWER =================
def bar(h, accent=False):
    c = ACC if accent else FILL2
    lc = INK2 if accent else INK3
    return ('<div style="flex-grow: 1; display: flex; flex-direction: column; justify-content: flex-end; gap: 10px; align-items: center">'
      '<div style="width: 62%; height: ' + str(h) + 'px; border-radius: ' + R_BAR + '; background: ' + c + '"></div>'
      '<span style="font-size: 10.5px; font-weight: 600; color: ' + lc + '">MONTH</span></div>')

def barm(h, m, accent=False):
    return bar(h, accent).replace("MONTH", m)

def mrow(name, ic, count, amount, last=False):
    return ('<div style="display: flex; align-items: center; gap: 13px">' + badge(ic, None, 40, R_ICON, 20)
      + '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 2px">'
      '<span style="font-size: 15px; font-weight: 700; letter-spacing: -0.01em">' + name + '</span>'
      '<span class="num" style="font-size: 12.5px; font-weight: 500; color: ' + INK3 + '">' + count + '</span></div>'
      '<span class="num" style="font-size: 15px; font-weight: 700">' + amount + '</span></div>')

def qchip(t):
    return ('<div' + hook("", "soon") + ' style="height: 42px; border-radius: ' + pill(42) + '; background: ' + FILL
      + '; display: flex; align-items: center; gap: 7px; padding: 0 15px">'
      '<span style="font-size: 13.5px; font-weight: 600; color: ' + INK + '">' + t + '</span>'
      '<svg width="11" height="11" viewBox="0 0 12 12" fill="none"><path d="M3 4.5 6 7.5l3-3" stroke="' + INK3
      + '" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></div>')

answer = page(
  T("Airtime and data", "You asked how much you spend on staying connected")
  + aline("&#8358;18,900 on airtime and data last month. That is your highest month this year.")
  + '<div style="' + cardstyle("18px 16px 8px 16px") + '; display: flex; flex-direction: column; gap: 18px">'
    + '<div style="display: flex; align-items: flex-end; justify-content: space-between">' + money("&#8358;18,900", "", 40, 20)
      + '<div style="display: flex; align-items: center; gap: 5px; height: 28px; padding: 0 11px; border-radius: 14px; background: rgba(176,69,58,0.10); margin-bottom: 4px">'
      '<svg width="11" height="11" viewBox="0 0 12 12" fill="none"><path d="M6 9.5v-7M3 5.5 6 2.5l3 3" stroke="' + WARN + '" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
      '<span class="num" style="font-size: 12.5px; font-weight: 600; color: ' + WARN + '">&#8358;4,200</span></div></div>'
    + '<div style="display: flex; gap: 8px; height: 76px; align-items: stretch">'
      + barm(38,"Feb") + barm(50,"Mar") + barm(41,"Apr") + barm(56,"May") + barm(47,"Jun") + barm(68,"Jul", True) + '</div>'
    + '<div style="display: flex; flex-wrap: wrap; gap: 7px">' + qchip("Airtime and data") + qchip("Last month") + '</div>'
    + '<div' + hook("", "soon") + ' style="border-top: 1px solid ' + LINE + '; display: flex; align-items: center; gap: 9px; height: 48px">'
      + icon("list", 15, INK3, 1.5)
      + '<span class="num" style="flex-grow: 1; font-size: 12.5px; color: ' + INK3 + '">Added up from 14 top ups, 1 to 31 July</span>' + chev() + '</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 13px">' + label("WHERE IT WENT")
    + '<div style="display: flex; flex-direction: column; gap: 15px">'
    + mrow("MTN data", "data", "5 top ups", "&#8358;12,500")
    + mrow("MTN airtime", "airtime", "7 top ups", "&#8358;4,400")
    + mrow("Glo airtime", "airtime", "2 top ups", "&#8358;2,000") + '</div></div>'
  + '<div style="' + cardstyle("14px") + '">' + aline("A 10GB monthly plan is &#8358;4,000 and would save about &#8358;1,800.", "15.5px") + '</div>', 13) + askbar("Ask about this", 106)
write("Answer", answer)

# ================= SEND MONEY =================
pay = page(
  T("Send money", "To Sarah Adeyemi")
  + quote("send Sarah 50k for the flat deposit")
  + aline("Here it is, ready to go. Check the three parts I filled in.")
  + '<div style="' + cardstyle("14px") + '; display: flex; flex-direction: column; gap: 10px">'
    + tinted(money("&#8358;50,000", "", 36, 19), "I took this from your message", "14px 15px 12px 15px")
    + tinted('<div style="display: flex; align-items: center; gap: 12px">' + avatar("SA")
        + '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 2px">'
          '<span style="font-size: 15px; font-weight: 600">Sarah Adeyemi</span>'
          '<span class="num" style="font-size: 12.5px; color: ' + INK2 + '">GTBank &#183; 0123 4457 8842</span></div>' + chev() + '</div>',
        "The only Sarah you have paid before")
    + tinted('<div style="display: flex; align-items: center; height: 22px">'
        '<span style="flex-grow: 1; font-size: 13.5px; color: ' + INK2 + '">Reference</span>'
        '<span style="font-size: 15px; font-weight: 500">Flat deposit</span></div>',
        "I took this from your message")
    + '<div style="background: ' + FILL + '; border-radius: ' + R_FIELD + '; overflow: hidden">'
      + plainrow("From", "Everyday &#183; 0102 4457 88", False, INK, True)
      + plainrow("Arrives", "In a few seconds", False, INK, True)
      + plainrow("Fee", "Free", True, IN) + '</div></div>'
  + '<div style="display: flex; gap: 9px; align-items: flex-start">' + icon("lock", 16, INK3, 1.6, "; margin-top: 2px")
    + '<span style="font-size: 14.5px; font-weight: 500; line-height: 1.45; color: ' + INK2
    + '; text-wrap: pretty">Nothing moves until you slide.</span></div>', 15)
pay += ('<div style="position: absolute; left: 0; right: 0; bottom: 0; padding: 30px 20px 30px 20px; background: linear-gradient(180deg, rgba(244,245,247,0) 0%, '
  + BG + ' 40%)">' + slide("Slide to send &#8358;50,000", "done|Pay") + '</div>')
write("Pay", pay, "", True)

# ================= STANDING INSTRUCTIONS =================
def switch(on, act="toggle"):
    knob = '<div style="width: 26px; height: 26px; border-radius: ' + PILL + '; background: #FFFFFF"></div>'
    if on:
        return ('<div' + hook("", act) + ' class="sw on" style="width: 52px; height: 32px; border-radius: ' + PILL + '; background: ' + ACC
          + '; padding: 3px; display: flex; justify-content: flex-end; flex-shrink: 0; margin-top: 2px">' + knob + '</div>')
    return ('<div' + hook("", act) + ' class="sw" style="width: 52px; height: 32px; border-radius: ' + PILL + '; background: #E4E4E8'
      '; padding: 3px; display: flex; justify-content: flex-start; flex-shrink: 0; margin-top: 2px">' + knob + '</div>')

def rule(title, desc, log, link, on, act="toggle"):
    tc = INK if on else INK3
    dc = INK2 if on else INK3
    foot = ''
    if log:
        foot = ('<div style="display: flex; align-items: center; height: 32px; border-top: 1px solid ' + LINE + '; padding-top: 6px">'
          '<span class="num" style="flex-grow: 1; font-size: 12.5px; font-weight: 500; color: ' + INK3 + '">' + log + '</span>'
          '<span' + hook("", "soon") + ' style="font-size: 13.5px; font-weight: 700; color: ' + ACC_TEXT + '">' + link + '</span></div>')
    return ('<div style="' + cardstyle("16px") + '; display: flex; flex-direction: column; gap: 12px">'
      '<div style="display: flex; align-items: flex-start; gap: 14px">'
      '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 6px">'
      '<span style="font-size: 16px; font-weight: 700; letter-spacing: -0.015em; color: ' + tc + '">' + title + '</span>'
      '<span style="font-size: 14px; font-weight: 500; line-height: 1.45; color: ' + dc + '; text-wrap: pretty">' + desc + '</span></div>'
      + switch(on, act) + '</div>' + foot + '</div>')

def never(t):
    return ('<div style="display: flex; align-items: center; gap: 12px">' + badge("lock", "neutral", 32, "11px", 16)
      + '<span style="font-size: 14.5px; font-weight: 500; color: ' + INK2 + '">' + t + '</span></div>')

rules = page(
  T("Standing instructions", "What I can do without asking you first")
  + '<div style="display: flex; flex-direction: column; gap: 10px">'
    + rule("Pay the Ikeja Electric bill", "When it lands, up to &#8358;10,000.", "Paid 3 times &#183; &#8358;22,400", "See log", True)
    + rule("Buy 5GB when my data runs out", "Once a month at most.", "Bought twice &#183; &#8358;5,000", "See log", True)
    + rule("Cover a bill from Savings", "Tops you up when a bill would bounce. It tells you every time.", "", "", False) + '</div>'
  + '<div style="display: flex; flex-direction: column; gap: 11px">' + label("I WILL ALWAYS ASK FIRST")
    + never("Paying anyone you have not paid before")
    + never("Anything over &#8358;20,000")
    + never("Taking a loan on your behalf") + '</div>'
  + '<div style="height: 50px; border-radius: 25px; background: ' + FILL
    + '; display: flex; align-items: center; justify-content: center; gap: 9px">' + icon("plus", 17, INK, 2)
    + '<span style="font-size: 14.5px; font-weight: 600; color: ' + INK + '">Add an instruction</span></div>', 14)
rules += askbar("Ask me to set one up", 106)
write("Rules", rules)

# ================= ELECTRICITY, BEFORE PAYING =================
powerpay = page(
  T("Pay a bill", "Ikeja Electric, on your saved meter")
  + quote("pay my light bill")
  + aline("Ikeja Electric, the meter you always use.")
  + '<div style="' + cardstyle("14px") + '; display: flex; flex-direction: column; gap: 10px">'
    + tinted('<div style="display: flex; align-items: center; gap: 12px">' + icon("power", 21, INK2, 1.6)
        + '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 2px">'
          '<span style="font-size: 15px; font-weight: 600">Ikeja Electric</span>'
          '<span class="num" style="font-size: 12.5px; color: ' + INK2 + '">Prepaid &#183; 0102 4457 8891</span></div>' + chev() + '</div>',
        "The meter you paid last month")
    + tinted('<div style="display: flex; align-items: baseline; gap: 1px">'
        '<span id="pwAmt" class="num" style="font-size: 36px; font-weight: 600; letter-spacing: -0.035em; line-height: 1; color: ' + INK + '">&#8358;8,000</span></div>',
        "About what you used last month", "14px 15px 12px 15px")
    + '<div style="background: ' + FILL + '; border-radius: ' + R_FIELD + '; overflow: hidden">'
      + plainrow("From", "Everyday &#183; 0102 4457 88", False, INK, True)
      + plainrow("Token arrives", "In a few seconds", True) + '</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 11px">' + label("OR PICK AN AMOUNT")
    + '<div style="display: flex; gap: 8px">' + bundle("&#8358;3,000", "About 14 kWh", "pw|3,000") + bundle("&#8358;8,000", "About 38 kWh", "pw|8,000") + bundle("&#8358;15,000", "About 72 kWh", "pw|15,000") + '</div></div>'
  + '<div style="display: flex; gap: 9px; align-items: flex-start">' + icon("lock", 16, INK3, 1.6, "; margin-top: 2px")
    + '<span style="font-size: 14.5px; font-weight: 500; line-height: 1.45; color: ' + INK2
    + '; text-wrap: pretty">The token appears here and in your messages.</span></div>', 15)
powerpay += ('<div class="dock" style="position: absolute; left: 0; right: 0; bottom: 0; z-index: 3; padding: 30px 20px 30px 20px; background: linear-gradient(180deg, rgba(244,245,247,0) 0%, '
  + BG + ' 40%)">' + slide("Slide to pay &#8358;8,000", "Power", "pwSlide") + '</div>')
write("PowerPay", powerpay, "", True)

# ================= DONE =================
done = page(
  T("All done", "Your receipt is below, and in your messages")
  + '<div style="display: flex; flex-direction: column; gap: 16px; align-items: flex-start">'
    '<div style="width: 56px; height: 56px; border-radius: ' + PILL + '; background: color-mix(in srgb, ' + ACC
      + ' 10%, ' + SURF + '); border: 1px solid color-mix(in srgb, ' + ACC + ' 26%, transparent); display: flex; align-items: center; justify-content: center">'
      + icon("check", 26, ACC, 2.0) + '</div>'
    '<div style="display: flex; flex-direction: column; gap: 6px">'
      '<div id="dnAmt">' + money("&#8358;2,500", "", 40, 20) + '</div>'
      '<span id="dnWhat" style="font-size: 15px; color: ' + INK2 + '">5GB sent to Mum</span></div></div>'
  + '<div id="dnCard" style="background: ' + SURF + '; ' + CARD_EDGE + '; border-radius: ' + R_PANEL + '; ' + SHADOW + '; overflow: hidden">'
    + plainrow("From", "Everyday &#183; 0102 4457 88")
    + plainrow("Reference", "MTN-88231-4471", True) + '</div>'
  + '<div id="dnOffer">' + offer("Want me to do this every month without asking?", "Set it up", "Rules") + '</div>', 16)
done += ('<div class="dock" style="position: absolute; left: 0; right: 0; bottom: 0; z-index: 3; padding: 30px 20px 30px 20px; display: flex; gap: 10px; background: linear-gradient(180deg, rgba(244,245,247,0) 0%, '
  + BG + ' 40%)">'
  '<div' + hook("", "soon") + ' style="flex-grow: 1; height: 52px; border-radius: 26px; background: ' + FILL
  + '; display: flex; align-items: center; justify-content: center; font-size: 14.5px; font-weight: 600; color: ' + INK2 + '">Share receipt</div>'
  '<div' + hook("Main") + ' style="flex-grow: 1; height: 52px; border-radius: ' + pill(52) + '; background: ' + BTN + '; ' + SH_BTN
  + '; display: flex; align-items: center; justify-content: center; font-size: 15px; font-weight: 700; color: ' + BTN_INK + '">Done</div></div>')
write("Done", done)

if EMIT:
    print("built:", ", ".join(sorted(f for f in os.listdir(OUT) if f.endswith(".dc.html"))))
