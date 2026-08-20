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
      '    a { color: ' + ACC_HEX + '; } a:hover { color: #1B4FC4; }\n'
      '    .num { font-variant-numeric: tabular-nums; }\n'
      + anim +
      '  </style>\n</helmet>\n')

FOOT = ('</x-dc>\n<script data-dc-script data-props=\'{"$preview":{"width":393,"height":852},'
  '"accent":{"editor":"color","default":"#2A6AF5","options":["#2A6AF5","#0A84FF","#5B3A7E","#0E7C7A"],"section":"Theme"}}\'>\n'
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
                  lambda m: "font-weight: %d" % WEIGHT.get(int(m.group(1)), 400), html)
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
    """The model's badge. A rounded square like every other icon here, so it
    belongs to the set, with a ring glyph so you know which one it is."""
    s = str(size)
    glyph = ACC_HEX if color.startswith("#FFF") else "#FFFFFF"
    return ('<svg width="' + s + '" height="' + s + '" viewBox="0 0 24 24" fill="none" style="flex-shrink: 0' + extra + '">'
      '<rect width="24" height="24" rx="7.2" fill="' + color + '"/>'
      '<circle cx="12" cy="12" r="6.1" stroke="' + glyph + '" stroke-width="1.8" opacity="0.55"/>'
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
 "gear": '<circle cx="12" cy="12" r="3.2"/><path d="M19.1 14.6a1.6 1.6 0 0 0 .32 1.76l.06.06a1.9 1.9 0 1 1-2.7 2.7l-.06-.06a1.6 1.6 0 0 0-1.76-.32 1.6 1.6 0 0 0-.97 1.47V20.5a1.9 1.9 0 1 1-3.8 0v-.1a1.6 1.6 0 0 0-1.05-1.47 1.6 1.6 0 0 0-1.76.32l-.06.06a1.9 1.9 0 1 1-2.7-2.7l.06-.06a1.6 1.6 0 0 0 .32-1.76 1.6 1.6 0 0 0-1.47-.97H3.5a1.9 1.9 0 1 1 0-3.8h.1a1.6 1.6 0 0 0 1.47-1.05 1.6 1.6 0 0 0-.32-1.76l-.06-.06a1.9 1.9 0 1 1 2.7-2.7l.06.06a1.6 1.6 0 0 0 1.76.32h.08a1.6 1.6 0 0 0 .97-1.47V3.5a1.9 1.9 0 1 1 3.8 0v.1a1.6 1.6 0 0 0 .97 1.47 1.6 1.6 0 0 0 1.76-.32l.06-.06a1.9 1.9 0 1 1 2.7 2.7l-.06.06a1.6 1.6 0 0 0-.32 1.76v.08a1.6 1.6 0 0 0 1.47.97h.14a1.9 1.9 0 1 1 0 3.8h-.1a1.6 1.6 0 0 0-1.47.97z"/>',
 "key": '<circle cx="8" cy="15.4" r="3.6"/><path d="M10.6 12.8 19 4.4M16.2 7.2l2.2 2.2M14 9.4l2.2 2.2"/>',
 "chat": '<path d="M20.4 11.6a7.6 7.6 0 0 1-8.2 7.6 8.6 8.6 0 0 1-2.6-.5L4 20.4l1.7-5.4a8 8 0 0 1-.6-3 7.6 7.6 0 0 1 7.6-8.2 7.6 7.6 0 0 1 7.7 7.8z"/>',
 "star": '<path d="m12 3.6 2.6 5.3 5.8.85-4.2 4.1 1 5.8-5.2-2.75-5.2 2.75 1-5.8-4.2-4.1 5.8-.85z"/>',
 "swap": '<path d="M4.6 8.4h13M14 4.8l3.6 3.6L14 12M19.4 15.6h-13M10 12l-3.6 3.6L10 19.2"/>',
 "person": '<circle cx="12" cy="8" r="3.8"/><path d="M4.8 20.4a7.4 7.4 0 0 1 14.4 0"/>',
 "gift": '<rect x="3.4" y="8.2" width="17.2" height="4.4" rx="1.4"/><path d="M5 12.6v6.4a1.6 1.6 0 0 0 1.6 1.6h10.8a1.6 1.6 0 0 0 1.6-1.6v-6.4M12 8.2v12.4"/><path d="M12 8.2S10.4 3.6 8 3.6a2.3 2.3 0 0 0 0 4.6zM12 8.2s1.6-4.6 4-4.6a2.3 2.3 0 0 1 0 4.6z"/>',
 "bank": '<path d="M3.4 9.4 12 4.6l8.6 4.8M5.6 9.4v8.4M10 9.4v8.4M14 9.4v8.4M18.4 9.4v8.4M3.4 20.4h17.2"/>',
 "down": '<path d="M12 4.8v14.4M6.2 13.4 12 19.2l5.8-5.8"/>',
 "up": '<path d="M12 19.2V4.8M6.2 10.6 12 4.8l5.8 5.8"/>',
}

def icon(name, size=22, color=INK2, sw=1.7, extra=""):
    s = str(size)
    return ('<svg width="' + s + '" height="' + s + '" viewBox="0 0 24 24" fill="none" stroke="' + color
            + '" stroke-width="' + str(sw) + '" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink: 0; color: ' + color
            + extra + '">' + ICONS[name] + '</svg>')

def avatar(t, size=38, bg=FILL, fg=INK, act="", eid=""):
    s = str(size)
    return ('<div' + hook("", act) + (' id="' + eid + '"' if eid else '') + ' style="width: ' + s + 'px; height: ' + s
      + 'px; border-radius: ' + PILL + '; background: ' + bg
      + '; display: flex; align-items: center; justify-content: center; font-size: 15px'
      + '; font-weight: 700; color: ' + fg + '; flex-shrink: 0">' + t + '</div>')

def chev(size=15, color=INK4, sw=2.1):
    s = str(size)
    return ('<svg width="' + s + '" height="' + s + '" viewBox="0 0 14 14" fill="none" style="flex-shrink: 0">'
            '<path d="M5 3l4 4-4 4" stroke="' + color + '" stroke-width="' + str(sw) + '" stroke-linecap="round" stroke-linejoin="round"/></svg>')

def chevbtn(size=24):
    """A row's chevron. Bare and pale, the way the reference draws it."""
    return chev(15, INK4, 2.1)

def chevdark(size=34):
    """The filled circle chevron the reference puts on a promotion row."""
    s = str(size)
    return ('<div style="width: ' + s + 'px; height: ' + s + 'px; border-radius: ' + PILL + '; background: ' + BTN
      + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">' + chev(13, "#FFFFFF", 2.3) + '</div>')

def badge(ic, t=None, size=44, radius=None, isz=None, dark=False, color=None):
    """An icon in its own colour, inside a rounded square. This is the single
    most repeated shape in the reference, so it is the one to get right."""
    r = radius or (R_TILE if size >= 46 else R_ICON)
    bg = IC["black"] if dark else (color or paint(ic))
    isz = isz or int(round(size * 0.5))
    return ('<div style="width: ' + str(size) + 'px; height: ' + str(size) + 'px; border-radius: ' + r
      + '; background: ' + bg + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
      + icon(ic, isz, "#FFFFFF", 2.0) + '</div>')

def circicon(ic, ring="#FFFFFF", glyph=BTN, size=26, isz=None):
    """The small filled circle that rides inside a pill button."""
    isz = isz or int(round(size * 0.62))
    return ('<div style="width: ' + str(size) + 'px; height: ' + str(size) + 'px; border-radius: ' + PILL
      + '; background: ' + ring + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
      + icon(ic, isz, glyph, 2.2) + '</div>')

def back():
    """The reference keeps back at the bottom left, as a bare chevron."""
    return ('<div' + hook("back") + ' class="backBtn" style="width: 40px; height: 40px; display: flex; align-items: center; '
      'justify-content: center; flex-shrink: 0">'
      '<svg width="22" height="22" viewBox="0 0 22 22" fill="none">'
      '<path d="M13.4 4.6 6.8 11l6.6 6.4" stroke="' + INK + '" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg></div>')

def topbar(title="", right=""):
    t = ''
    if title:
        t = '<span style="flex-grow: 1; text-align: center; font-size: 17px; font-weight: 700; letter-spacing: -0.015em">' + title + '</span>'
    r = right if right else '<div style="width: 40px; flex-shrink: 0"></div>'
    return ('<div style="display: flex; align-items: center; height: 44px; gap: 8px">' + back() + t + r + '</div>')

# ---------- buttons ----------

def pillbtn(text, go="", act="", ic="", kind="black", full=True, height=56, bid=""):
    """Every button here is a pill. Black is the action you are meant to take,
    blue is the one that belongs to the thing you are looking at."""
    bg = {"black": BTN, "blue": ACC, "grey": FILL}[kind]
    fg = INK if kind == "grey" else "#FFFFFF"
    lead = ''
    if ic:
        lead = circicon(ic, "#FFFFFF" if kind != "grey" else BTN,
                        (BTN if kind == "black" else ACC_HEX) if kind != "grey" else "#FFFFFF",
                        height - 26) + ''
    width = ('width: 100%; ' if full else '')
    pad = ('0 24px' if not ic else ('0 24px 0 ' + str((height - 26) // 2 + 3) + 'px'))
    sh = ('; ' + SH_BTN) if kind != "grey" else ''
    return ('<div' + hook(go, act) + (' id="' + bid + '"' if bid else '') + ' class="pbtn" style="' + width + 'height: ' + str(height)
      + 'px; border-radius: ' + PILL + '; background: ' + bg + sh + '; display: flex; align-items: center; justify-content: center; gap: 10px; padding: '
      + pad + '">' + lead + '<span style="font-size: 17px; font-weight: 700; letter-spacing: -0.01em; color: ' + fg + '">' + text + '</span></div>')

def ctabtn(text, go="", act="", ic="", kind="black", height=56, bid=""):
    """The same pill, hugging its own text and centred. The reference uses
    exactly one of these on a screen and never two."""
    return ('<div style="display: flex; justify-content: center">'
            + pillbtn(text, go, act, ic, kind, False, height, bid) + '</div>')

def segment(items, sel=0, act=""):
    """A light track with a white pill riding in it."""
    cells = ''
    for i, it in enumerate(items):
        on = (i == sel)
        cells += ('<div' + hook("", act) + ' class="segcell" data-seg="' + str(i) + '" style="height: 40px; padding: 0 26px; border-radius: ' + PILL
          + '; background: ' + (SURF if on else 'transparent') + (('; ' + SH_RAISE) if on else '')
          + '; display: flex; align-items: center; justify-content: center; gap: 8px">'
          '<span style="font-size: 15px; font-weight: 700; color: ' + (INK if on else INK2) + '">' + it + '</span></div>')
    return ('<div style="display: flex; gap: 4px; padding: 4px; border-radius: ' + PILL + '; background: ' + FILL
            + '; align-self: center">' + cells + '</div>')

# ---------- surfaces ----------

def cardstyle(pad="20px", radius=R_CARD, bg=FILL, extra=""):
    """The normal card. A flat grey fill on a white page, no border, no shadow."""
    return 'background: ' + bg + '; border-radius: ' + radius + '; padding: ' + pad + ';' + extra

def bordered(pad="20px", radius=R_CARD, bg=SURF, extra=""):
    """A white card held by a hairline. The reference saves this for a promotion."""
    return 'background: ' + bg + '; ' + CARD_EDGE + '; border-radius: ' + radius + '; padding: ' + pad + ';' + extra

def dashedcard(pad="18px", radius=R_CARD, bg=SURF, extra=""):
    """A dashed outline, which is how the reference draws somewhere to go next."""
    return 'background: ' + bg + '; ' + DASH + '; border-radius: ' + radius + '; padding: ' + pad + ';' + extra

def dashtile(name, sub, ic, go="", act="", height=128):
    """The home grid. Icon at the top, the words held down at the bottom."""
    return ('<div' + hook(go, act) + ' class="dtile" style="flex-grow: 1; flex-basis: 0; ' + dashedcard("18px", "24px")
      + ' height: ' + str(height) + 'px; display: flex; flex-direction: column">'
      + badge(ic, None, 48, R_TILE, 24)
      + '<div style="flex-grow: 1"></div>'
      + '<span style="font-size: 17px; font-weight: 700; letter-spacing: -0.02em; color: ' + INK + '">' + name + '</span>'
      + '<span style="font-size: 17px; font-weight: 400; color: ' + INK3 + '; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">' + sub + '</span></div>')

def promorow(title, sub, ic, go="", act="", dark=True):
    """The bordered white row with a filled chevron on the right."""
    return ('<div' + hook(go, act) + ' style="' + bordered("14px 16px", "20px")
      + ' display: flex; align-items: center; gap: 14px">' + badge(ic, None, 44, R_ICON, 22, dark)
      + '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 2px">'
      '<span style="font-size: 17px; font-weight: 700; letter-spacing: -0.015em; color: ' + INK + '">' + title + '</span>'
      '<span style="font-size: 15px; font-weight: 400; color: ' + INK3 + '">' + sub + '</span></div>'
      + chevdark() + '</div>')

def featcard(title, sub, lead, rows, foot="", footic="lock"):
    """The reference's tall explainer card. A header, a dashed rule, a short
    list of what you get, and a strip along the bottom for what it costs."""
    rs = ''
    for ic, txt in rows:
        rs += ('<div style="display: flex; align-items: flex-start; gap: 14px">' + badge(ic, None, 40, R_ICON, 20)
          + '<span style="flex-grow: 1; font-size: 17px; font-weight: 400; line-height: 1.4; color: ' + INK3
          + '; padding-top: 8px; text-wrap: pretty">' + txt + '</span></div>')
    f = ''
    if foot:
        f = ('<div style="margin-top: 20px; background: ' + FILL2 + '; border-radius: 0 0 ' + R_CARDLG + ' ' + R_CARDLG
          + '; height: 56px; display: flex; align-items: center; justify-content: center; gap: 8px">'
          + icon(footic, 17, INK, 2.0)
          + '<span style="font-size: 17px; font-weight: 700; color: ' + INK + '">' + foot + '</span></div>')
    return ('<div style="background: ' + FILL + '; border-radius: ' + R_CARDLG + '; overflow: hidden">'
      '<div style="padding: 20px 20px 0 20px; display: flex; flex-direction: column; gap: 16px">'
      + lead
      + '<div style="display: flex; flex-direction: column; gap: 2px">'
        '<span style="font-size: 19px; font-weight: 700; letter-spacing: -0.02em; color: ' + INK + '">' + title + '</span>'
        '<span style="font-size: 17px; font-weight: 400; color: ' + INK3 + '">' + sub + '</span></div>'
      '<div style="height: 0; border-top: 1.5px dashed ' + LINE2 + '"></div>'
      '<div style="display: flex; flex-direction: column; gap: 16px; padding-bottom: 4px">' + rs + '</div></div>' + f + '</div>')

def ghost(head, sub, btn, go="", act="", kind="blue", ic="down", height=250):
    """An empty state. The reference blurs a ghost of what would be here rather
    than drawing an empty box, so the screen still reads as the same screen."""
    shapes = ('<div style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; filter: blur(16px); opacity: 0.55; '
      'pointer-events: none">'
      '<div style="position: absolute; left: 22px; top: 30px; width: 76px; height: 76px; border-radius: ' + PILL + '; background: ' + ACC + '; opacity: 0.5"></div>'
      '<div style="position: absolute; left: 22px; top: 124px; width: 104px; height: 18px; border-radius: 9px; background: ' + FILL2 + '"></div>'
      '<div style="position: absolute; left: 22px; top: 186px; width: 46px; height: 46px; border-radius: 14px; background: ' + ACC + '; opacity: 0.35"></div>'
      '<div style="position: absolute; left: 82px; top: 198px; width: 150px; height: 20px; border-radius: 10px; background: ' + FILL2 + '"></div>'
      '<div style="position: absolute; right: 24px; top: 122px; width: 88px; height: 30px; border-radius: 15px; background: ' + FILL2 + '"></div>'
      '<div style="position: absolute; right: 24px; top: 196px; width: 116px; height: 22px; border-radius: 11px; background: ' + FILL2 + '"></div></div>')
    return ('<div style="position: relative; height: ' + str(height) + 'px; display: flex; flex-direction: column; '
      'align-items: center; justify-content: center; gap: 8px">' + shapes
      + '<span style="position: relative; font-size: 19px; font-weight: 700; letter-spacing: -0.02em; color: ' + INK + '; text-align: center">' + head + '</span>'
      + '<span style="position: relative; font-size: 17px; font-weight: 400; color: ' + INK3 + '; text-align: center; margin-bottom: 12px">' + sub + '</span>'
      + '<div style="position: relative">' + pillbtn(btn, go, act, ic, kind, False, 52) + '</div></div>')

def tinted(inner, note, pad="14px 16px"):
    """A field the model filled in. It speaks from its own soft panel."""
    return ('<div style="border-radius: ' + R_INNER + '; background: ' + ACC_SOFT
        + '; padding: ' + pad + '; display: flex; flex-direction: column; gap: 7px">' + inner
        + '<span style="font-size: 13px; font-weight: 700; color: '
        + ACC_INK + '">' + note + '</span></div>')

def slide(label, go="", lid=""):
    return ('<div class="slide"' + hook(go) + ' style="position: relative; height: 60px; border-radius: ' + PILL
        + '; background: ' + BTN + '; ' + SH_BTN + '; display: flex; align-items: center; padding: 5px">'
        '<div class="knob" style="width: 50px; height: 50px; border-radius: ' + PILL + '; background: #FFFFFF'
        '; display: flex; align-items: center; justify-content: center; flex-shrink: 0; z-index: 2">'
        '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M4 10h11M11 6l4 4-4 4" stroke="' + BTN
        + '" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"/></svg></div>'
        '<span' + (' id="' + lid + '"' if lid else '') + ' class="num slideLabel" style="flex-grow: 1; text-align: center; font-size: 17px; font-weight: 700; color: rgba(255,255,255,0.92)'
        '; margin-right: 50px">' + label + '</span></div>')

def panel(text, size="17px", aid=""):
    return ('<div' + (' id="' + aid + '"' if aid else '') + ' style="flex-grow: 1; border-radius: ' + R_INNER
        + '; background: ' + ACC_SOFT + '; padding: 14px 16px; font-size: ' + size
        + '; line-height: 1.45; font-weight: 400; color: ' + INK + '; text-wrap: pretty">' + text + '</div>')

def aline(text, size="17px", aid=""):
    """The model speaking, beside its badge. Always from its own soft panel."""
    return ('<div style="display: flex; gap: 12px; align-items: flex-start">' + mark(34)
        + panel(text, size, aid) + '</div>')

def aicard(text, head="", size="17px", aid=""):
    """The model speaking with its panel run full width, badge on the row above."""
    h = ('<div style="display: flex; align-items: center; gap: 9px; padding: 1px 1px 0 1px">' + mark(28)
         + '<span style="font-size: 15px; font-weight: 700; letter-spacing: -0.01em; color: ' + INK + '">' + head + '</span></div>')
    return h + panel(text, size, aid)

def label(t, color=INK):
    """A heading over a group, in the black the reference uses for its own."""
    txt = t if t[:1].islower() else t[:1].upper() + t[1:].lower()
    return ('<div style="font-size: 22px; font-weight: 700; letter-spacing: -0.03em; color: ' + color + '">' + txt + '</div>')

def sectionhead(t):
    """The quieter grey heading the reference puts over a settings group."""
    return ('<div style="font-size: 17px; font-weight: 400; color: ' + INK2 + '; padding-left: 2px">' + t + '</div>')

def caption(t, color=INK2):
    """The grey line that sits above a figure."""
    return ('<div style="font-size: 17px; font-weight: 400; color: ' + color + '">' + t + '</div>')

def money(whole, dec="", size=60, color=INK, dcolor=None):
    """The reference's signature. The whole number in black and heavy, the
    decimal two thirds the size and pale, so the figure reads at a glance."""
    d = ''
    if dec:
        d = ('<span class="num" style="font-size: ' + str(int(round(size * 0.66))) + 'px; font-weight: 800; '
             'letter-spacing: -0.03em; color: ' + (dcolor or INK4) + '">' + dec + '</span>')
    return ('<div style="display: flex; align-items: baseline; gap: 0px">'
        '<span class="num" style="font-size: ' + str(size) + 'px; font-weight: 800; letter-spacing: -0.04em; line-height: 1.05; color: '
        + color + '">' + whole + '</span>' + d + '</div>')

def statpill(t):
    """The small grey chip the reference sets beside a balance label."""
    return ('<div style="display: flex; align-items: center; gap: 6px; height: 24px; padding: 0 10px; border-radius: ' + PILL
      + '; background: ' + FILL + '"><span class="num" style="font-size: 13px; font-weight: 700; color: ' + INK2 + '">' + t + '</span></div>')

def pagehead(title, sub="", ic=""):
    """A detail page names itself with a small icon and the title on one line."""
    lead = (badge(ic, None, 40, R_ICON, 21) + '') if ic else ''
    p = ''
    if sub:
        p = ('<div style="font-size: 17px; font-weight: 400; line-height: 1.4; color: ' + INK3
             + '; text-wrap: pretty">' + sub + '</div>')
    return ('<div class="phead" style="display: flex; flex-direction: column; gap: 8px">'
      '<div style="display: flex; align-items: center; gap: 12px">' + lead
      + '<div style="font-size: 28px; font-weight: 700; letter-spacing: -0.035em; line-height: 1.1; color: '
      + INK + '">' + title + '</div></div>' + p + '</div>')

def ring(pct, size=180, stroke=14):
    r = (size - stroke) / 2.0
    circ = 2 * 3.141592653589793 * r
    off = circ * (1 - pct / 100.0)
    half = size / 2.0
    def n(v):
        return ("%g" % v)
    return ('<div style="position: relative; width: ' + str(size) + 'px; height: ' + str(size) + 'px; flex-shrink: 0">'
      '<svg width="' + str(size) + '" height="' + str(size) + '" viewBox="0 0 ' + str(size) + ' ' + str(size)
      + '" style="transform: rotate(-90deg)">'
      '<circle cx="' + n(half) + '" cy="' + n(half) + '" r="' + n(r) + '" fill="none" stroke="' + FILL3
      + '" stroke-width="' + str(stroke) + '"/>'
      '<circle class="ring" cx="' + n(half) + '" cy="' + n(half) + '" r="' + n(r) + '" fill="none" stroke="' + ACC
      + '" stroke-width="' + str(stroke) + '" stroke-linecap="round" stroke-dasharray="' + n(circ)
      + '" stroke-dashoffset="' + n(off) + '"/></svg>'
      '<div style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; display: flex; flex-direction: column; '
      'align-items: center; justify-content: center; gap: 2px">'
      '<span id="glPct" class="num" style="font-size: 40px; font-weight: 800; letter-spacing: -0.04em; color: ' + INK + '">'
      + str(pct) + '%</span>'
      '<span style="font-size: 15px; font-weight: 400; color: ' + INK3 + '">of the way</span></div></div>')

def meter(done, total):
    """Coverage, shown as segments rather than a number you can farm."""
    segs = ''
    for i in range(total):
        segs += ('<div style="flex-grow: 1; height: 6px; border-radius: ' + R_TRACK + '; background: '
                 + (ACC if i < done else FILL2) + '"></div>')
    return '<div style="display: flex; gap: 4px">' + segs + '</div>'

# ---------- the bottom bar, and what its black circle opens ----------

def dock(placeholder, back_btn=False, height=104):
    """The reference floats its bar on white with no bar behind it, and puts a
    black circle at the right. Ours holds the model instead of tab icons, so
    the ask bar takes the width and the circle keeps the corner."""
    left = back() if back_btn else ('<div' + hook("Settings") + ' style="width: 40px; height: 40px; display: flex; '
      'align-items: center; justify-content: center; flex-shrink: 0">' + icon("gear", 24, INK, 1.7) + '</div>')
    ask = ('<div' + hook("ask") + ' class="askpill" style="flex-grow: 1; min-width: 0; height: 48px; border-radius: ' + PILL
      + '; background: ' + FILL + '; display: flex; align-items: center; gap: 9px; padding: 0 14px 0 8px">'
      + mark(32) + '<span style="flex-grow: 1; font-size: 15px; font-weight: 400; color: ' + INK2
      + '; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">' + placeholder + '</span>'
      + icon("mic", 18, INK2, 1.8) + '</div>')
    fab = ('<div class="fab"' + hook("", "actions") + ' style="width: 56px; height: 56px; border-radius: ' + PILL
      + '; background: ' + BTN + '; ' + SH_FAB + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
      '<svg class="fabx" width="24" height="24" viewBox="0 0 24 24" fill="none">'
      '<path d="M12 5.4v13.2M5.4 12h13.2" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round"/></svg></div>')
    return ('<div class="dock" style="position: absolute; left: 0; right: 0; bottom: 0; z-index: 3; height: ' + str(height)
      + 'px; background: linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.9) 34%, ' + BG
      + ' 62%); display: flex; align-items: flex-end; padding: 0 18px 26px 18px">'
      '<div style="display: flex; width: 100%; gap: 10px; align-items: center">' + left + ask + fab + '</div></div>')

def askbar(placeholder, height=104, tabbar=False):
    """Home shows the settings icon at the left of the bar."""
    return dock(placeholder, False, height)

def dockback(placeholder, height=104):
    """Every other screen shows back in the same spot, at the bottom left."""
    return dock(placeholder, True, height)

def confirmbar(inner):
    """A screen that is a task earns one action and nothing else. Back keeps
    the bottom left corner it has everywhere."""
    return ('<div class="dock" style="position: absolute; left: 0; right: 0; bottom: 0; z-index: 3; '
      'padding: 34px 20px 26px 20px; background: linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.9) 34%, '
      + BG + ' 62%); display: flex; gap: 10px; align-items: center">' + back()
      + '<div style="flex-grow: 1; min-width: 0">' + inner + '</div></div>')

def tickmark(eid="", size=56, color=None):
    """A payment that worked. A filled circle, not a tinted one, because the
    reference never draws a pale shape where a solid one will do."""
    c = color or IC["green"]
    return ('<div' + (' id="' + eid + '"' if eid else '') + ' style="width: ' + str(size) + 'px; height: ' + str(size)
      + 'px; border-radius: ' + PILL + '; background: ' + c + '; display: flex; align-items: center; justify-content: center">'
      + icon("check", int(size * 0.46), "#FFFFFF", 2.4) + '</div>')

ACTIONS_LIST = [("Send money", "send", "blue", "Pay"),
                ("Receive", "down", "green", "receive"),
                ("Activity", "clock", "purple", "Activity"),
                ("Pay a bill", "receipt", "amber", "Bills")]

def fabsheet():
    """What the black circle opens. Four things you do most, stacked above the
    circle over a blurred page, the way the reference dims behind a sheet."""
    rows = ''
    for i, (name, ic, col, go) in enumerate(ACTIONS_LIST):
        rows += ('<div class="fabrow" data-i="' + str(i) + '"' + hook(go if go != "receive" else "", "" if go != "receive" else "receive")
          + ' style="display: flex; align-items: center; justify-content: flex-end; gap: 12px">'
          '<span style="height: 40px; padding: 0 16px; border-radius: ' + PILL + '; background: ' + SURF + '; ' + SH_RAISE
          + '; display: flex; align-items: center; font-size: 17px; font-weight: 700; letter-spacing: -0.015em; color: ' + INK + '">' + name + '</span>'
          + badge(ic, None, 52, PILL, 24, False, IC[col]) + '</div>')
    return ('<div class="fabwrap" style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; z-index: 6">'
      '<div class="fabscrim"' + hook("", "actions") + ' style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; background: '
      + SCRIM + '; ' + BLUR + '"></div>'
      '<div style="position: absolute; right: 18px; bottom: 96px; display: flex; flex-direction: column; align-items: flex-end; gap: 14px">'
      + rows + '</div>'
      '<div class="fab fabclose"' + hook("", "actions") + ' style="position: absolute; right: 18px; bottom: 26px; width: 56px; height: 56px; '
      'border-radius: ' + PILL + '; background: ' + BTN + '; ' + SH_FAB + '; display: flex; align-items: center; justify-content: center">'
      '<svg width="22" height="22" viewBox="0 0 24 24" fill="none">'
      '<path d="M6.4 6.4l11.2 11.2M17.6 6.4 6.4 17.6" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round"/></svg></div></div>')

def sheet(inner, pad="26px 20px 28px 20px"):
    """A sheet rises over a page that is dimmed and blurred, and it floats
    clear of all four edges rather than sitting on the bottom."""
    return ('<div class="fauxbg" style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; background: ' + SCRIM
      + '; ' + BLUR + '; z-index: 5"></div>'
      '<div class="sheet" style="position: absolute; left: 10px; right: 10px; bottom: 10px; z-index: 6; background: ' + SURF
      + '; border-radius: ' + R_SHEET + '; ' + SH_SHEET + '; padding: ' + pad + '">' + inner + '</div>')

def sheetx():
    return ('<div' + hook("back") + ' style="position: absolute; right: 18px; top: 18px; width: 32px; height: 32px; '
      'display: flex; align-items: center; justify-content: center">'
      '<svg width="20" height="20" viewBox="0 0 20 20" fill="none">'
      '<path d="M5.4 5.4l9.2 9.2M14.6 5.4l-9.2 9.2" stroke="' + INK2 + '" stroke-width="2.2" stroke-linecap="round"/></svg></div>')

def T(title, sub="", ic=""):
    """Marks a screen's title. page() turns it into the head."""
    return "\x00T\x01" + title + "\x01" + sub + "\x01" + ic + "\x02"

_TMARK = re.compile("\x00T\x01(.*?)\x01(.*?)\x01(.*?)\x02", re.S)

def page(inner, gap=16, top=72, center=False, wash_h=0):
    m = _TMARK.search(inner)
    if m:
        inner = inner[:m.start()] + pagehead(m.group(1), m.group(2), m.group(3)) + inner[m.end():]
    return ('<div class="pg" style="position: relative; ' + ('justify-content: center; ' if center else '')
            + 'padding: ' + str(top) + 'px 20px 0 20px; display: flex; flex-direction: column; gap: '
            + str(gap) + 'px">\n<div class="pgin" style="position: relative; display: flex; flex-direction: column; gap: '
            + str(gap) + 'px">' + inner + '</div>\n</div>')
# ================= HOME =================
def svc_tile(name, ic, go=""):
    return ('<div' + hook(go) + ' style="flex-grow: 1; flex-basis: 0; display: flex; flex-direction: column; align-items: center; gap: 8px">'
      + badge(ic, None, 48, R_TILE, 24)
      + '<span style="font-size: 13px; font-weight: 700; color: ' + INK + '">' + name + '</span></div>')

def aisay(head, text, tail="", eid=""):
    """Something the model prepared. It gets a white card with a hairline, so
    it never reads as one of the flat grey cards the app itself fills in."""
    return ('<div' + (' id="' + eid + '"' if eid else '') + ' style="' + bordered("16px", "24px")
      + ' display: flex; flex-direction: column; gap: 14px">' + aicard(text, head) + tail + '</div>')

LEAD = (aisay("Due on Thursday", "Ikeja Electric, and last month it was &#8358;7,500.",
      '<div style="display: flex; gap: 8px; align-items: center">'
      '<div' + hook("PowerPay") + ' style="flex-grow: 1; height: 52px; border-radius: ' + PILL + '; background: ' + BTN + '; ' + SH_BTN
      + '; color: ' + BTN_INK + '; display: flex; align-items: center; justify-content: center; font-size: 17px; font-weight: 700">Pay &#8358;8,000 now</div>'
      '<div' + hook("", "dismiss") + ' style="width: 52px; height: 52px; border-radius: ' + PILL + '; background: ' + FILL + '; display: flex; align-items: center; justify-content: center">'
      '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M4.5 4.5l7 7M11.5 4.5l-7 7" stroke="' + INK2 + '" stroke-width="2" stroke-linecap="round"/></svg></div></div>', "mBill"))

home_inner = (
  '<div style="font-size: 28px; font-weight: 700; letter-spacing: -0.035em; color: ' + INK + '">Wallet</div>'
  + '<div style="display: flex; flex-direction: column; gap: 6px; padding-top: 24px">'
    + '<div style="display: flex; align-items: center; gap: 10px">' + caption("Total balance") + statpill("+9% this month") + '</div>'
    + '<div id="mBal">' + money("&#8358;248,320", ".75", 60) + '</div></div>'
  + '<div style="padding: 6px 0 12px 0">' + ctabtn("Add money", "", "receive", "down", "black", 56) + '</div>'
  + LEAD
  + '<div style="display: flex; gap: 12px">'
      + dashtile("Airtime", "Top up any line", "airtime", "Airtime")
      + dashtile("Bills", "Power, TV, water", "power", "Bills") + '</div>'
  + '<div style="display: flex; gap: 12px">'
      + dashtile("Savings", "33% of the way", "pot", "Goal")
      + dashtile("Services", "Forty more", "more", "Services") + '</div>'
  + promorow("Your card is ready", "Spend online anywhere", "card", "Card")
  + '<div style="padding-top: 12px">' + label("More this morning") + '</div>'
  + '<div style="display: flex; flex-direction: column; gap: 12px; margin-top: -4px">'

    + aisay("Your data is nearly gone", "Your data usually runs out about now. The same 5GB is &#8358;2,500.",
      '<div style="display: flex; align-items: center; gap: 12px; height: 68px; border-radius: ' + R_INNER + '; background: ' + FILL + '; padding: 0 14px">'
      + badge("data", None, 40, R_ICON, 20)
      + '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 1px">'
        '<span style="font-size: 17px; font-weight: 700; letter-spacing: -0.015em">5GB for 30 days</span>'
        '<span style="font-size: 15px; font-weight: 400; color: ' + INK3 + '">MTN &#183; your line</span></div>'
      '<span class="num" style="font-size: 17px; font-weight: 700">&#8358;2,500</span></div>'
      '<div' + hook("Airtime") + ' style="height: 48px; border-radius: ' + PILL + '; background: ' + FILL
      + '; display: flex; align-items: center; justify-content: center; gap: 6px">'
        '<span style="font-size: 17px; font-weight: 700; color: ' + INK + '">Buy it again</span>' + chev(13, INK, 2.2) + '</div>')

    + '<div' + hook("Answer") + ' style="' + bordered("16px", "24px") + ' display: flex; flex-direction: column; gap: 12px">'
      + aicard("You spent &#8358;18,900 on airtime and data last month. That is your highest month this year.", "Where your money went") + '</div>'
  + '</div>')

home = page(home_inner, 16) + askbar("Ask, or just say what you need")
write("Main", home)

# The same screen with the black circle opened. Kept as its own board so the
# four things it holds can be looked at without running the prototype.
FAB_SHEET = fabsheet()
write("Actions", page(home_inner, 16) + askbar("Ask, or just say what you need") + FAB_SHEET)

# ================= ALL SERVICES =================
def grid_tile(name, ic, go="", act=""):
    return ('<div' + hook(go, act) + ' style="flex-grow: 1; flex-basis: 0; display: flex; flex-direction: column; align-items: center; gap: 10px">'
      + badge(ic, None, 62, "16px", 28)
      + '<span style="font-size: 15px; font-weight: 700; color: ' + INK + '; text-align: center">' + name + '</span></div>')

def listrow(name, ic, sub="", last=False, go="", act="soon"):
    sb = ''
    if sub:
        sb = '<span style="font-size: 15px; font-weight: 400; color: ' + INK3 + '">' + sub + '</span>'
    return ('<div' + hook(go, "" if go else act) + ' style="display: flex; align-items: center; gap: 14px; height: 68px">'
      + badge(ic, None, 40, R_ICON, 20)
      + '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 2px">'
      '<span style="font-size: 19px; font-weight: 700; letter-spacing: -0.02em">' + name + '</span>' + sb + '</div>'
      + chevbtn() + '</div>')

services = page(
  T("All services", "Everything you can pay for from here")
  + '<div style="display: flex; flex-direction: column; gap: 12px">' + sectionhead("You use these most")
    + '<div style="display: flex; gap: 10px">' + grid_tile("Airtime","airtime","Airtime") + grid_tile("Data","data","Airtime") + grid_tile("Power","power","PowerPay") + grid_tile("Send","send","Pay") + '</div>'
    + '<div style="display: flex; gap: 10px">' + grid_tile("Cable TV","tv","","soon") + grid_tile("Betting","bet","","soon") + grid_tile("Loan","loan","Loan") + grid_tile("Cards","card","Card") + '</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 11px">' + sectionhead("Bills")
    + '<div style="display: flex; flex-direction: column">'
      + listrow("Internet", "globe", "Spectranet, Smile, Starlink")
      + listrow("Water", "water", "State water boards")
      + listrow("Waste", "waste", "LAWMA and others")
      + listrow("School fees", "school", "WAEC, JAMB, tuition", True) + '</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 11px">' + sectionhead("Save and borrow")
    + '<div style="display: flex; flex-direction: column">'
      + listrow("Savings pot", "pot", "Put money aside", False, "Goal")
      + listrow("Fixed savings", "clock", "Lock it for a set time", True) + '</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 11px">' + sectionhead("Money")
    + '<div style="display: flex; flex-direction: column">'
      + listrow("Request money", "request", "Ask someone to pay you")
      + listrow("Send abroad", "globe", "Pounds, dollars and euros", True) + '</div></div>', 15)
services += dockback("Search, or say what you need")
write("Services", services)

def offer(text, action, go=""):
    return ('<div style="' + bordered("16px", "24px") + ' display: flex; flex-direction: column; gap: 12px">'
      + aline(text, "17px")
      + '<div' + hook(go, "" if go else "soon") + ' style="height: 46px; border-radius: ' + pill(46)
      + '; background: ' + FILL + '; display: flex; align-items: center; justify-content: center; gap: 7px">'
      '<span style="font-size: 14.5px; font-weight: 700; color: ' + INK + '">' + action + '</span>'
      + chev(12, INK, 2.2) + '</div></div>')

def quote(t):
    return ('<div style="display: flex; flex-direction: column; gap: 6px">' + caption("You said")
      + '<span style="font-size: 17px; font-style: italic; font-weight: 500; color: ' + INK2 + '">' + t + '</span></div>')

def plainrow(k, v, last=False, vcolor=INK, chevron=False, vid=""):
    c = chevbtn(22) if chevron else ""
    return ('<div style="display: flex; align-items: center; height: 56px; gap: 10px">'
      '<span style="flex-grow: 1; font-size: 17px; font-weight: 400; color: ' + INK3 + '">' + k + '</span>'
      '<span' + (' id="' + vid + '"' if vid else '') + ' class="num" style="font-size: 17px; font-weight: 700; color: '
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
    + '<div style="background: ' + SURF + '; border-radius: ' + R_FIELD + '; overflow: hidden; padding: 0 16px">'
      + plainrow("From", "Everyday &#183; 0102 4457 88", False, INK, True)
      + plainrow("Goes to your Holiday goal", "&#8358;25", True, ACC_TEXT, False, "bBack") + '</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 11px">' + sectionhead("Other bundles")
    + '<div style="display: flex; gap: 8px">' + bundle("1GB", "&#8358;800", "gb|1GB for 7 days|800") + bundle("2GB", "&#8358;2,000", "gb|2GB for 30 days|2,000") + bundle("10GB", "&#8358;4,000", "gb|10GB for 30 days|4,000") + '</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 11px">' + sectionhead("You also top up")
    + '<div style="display: flex; gap: 14px; align-items: center">'
      + avatar("D", 46, act="who|Dad") + avatar("K", 46, act="who|Kemi") + avatar("B", 46, act="who|Bro") + avatar("T", 46, act="who|Tunde")
      + '<div style="width: 46px; height: 46px; border-radius: 23px; border: 1px dashed ' + LINE2
      + '; display: flex; align-items: center; justify-content: center">' + icon("plus", 18, INK3, 1.7) + '</div></div></div>', 15)
airtime += confirmbar(slide("Slide to buy &#8358;2,500", "done|Airtime", "aSlide"))
write("Airtime", airtime, "", True)

# ================= ELECTRICITY, PAID =================
power = page(
  T("Bill paid", "Ikeja Electric, a moment ago")
  + '<div style="display: flex; flex-direction: column; gap: 14px; align-items: flex-start">'
    + tickmark("", 56)
    + '<div style="display: flex; flex-direction: column; gap: 5px">' + money("&#8358;8,000", "", 40)
      + '<span style="font-size: 14px; color: ' + INK2 + '">Paid to Ikeja Electric</span></div></div>'
  + aline("Type this into your meter. I have sent it to your messages as well.", "16.5px")
  + '<div style="' + cardstyle("16px") + '; display: flex; flex-direction: column; gap: 12px">'
    + sectionhead("Meter token")
    + '<span class="num" style="font-size: 21px; font-weight: 600; letter-spacing: 0.02em; color: ' + INK + '">4471 8823 0195 6640 3277</span>'
    + '<div' + hook("", "copy") + ' style="display: flex; align-items: center; justify-content: center; gap: 8px; height: 48px; border-radius: ' + PILL + '; background: ' + SURF + '">'
      + icon("copy", 18, INK, 1.8) + '<span style="font-size: 17px; font-weight: 700; color: ' + INK + '">Copy the token</span></div></div>'
  + '<div style="display: flex; flex-direction: column">'
    + plainrow("Meter", "0102 4457 8891")
    + plainrow("Units", "38.4 kWh")
    + plainrow("Reference", "IKJ-90441-2286", True) + '</div>'
  + offer("Want me to pay this every month?", "Set it up", "Rules"), 15)
power += dockback("Ask about this payment")
write("Power", power)

# ================= BILLS =================
def chip(t, color=INK3):
    """A status, said in the subtitle rather than shouted in a pill."""
    txt = t if t[:1].islower() else t[:1].upper() + t[1:].lower()
    return ('<span style="font-size: 13px; font-weight: 600; color: ' + color + '; white-space: nowrap">&#183; ' + txt + '</span>')

def bill(name, ic, sub, amount, chp, last=False, dim=False, go="", act="soon"):
    nc = INK3 if dim else INK
    return ('<div' + hook(go, "" if go else act) + ' style="display: flex; align-items: center; gap: 14px; height: 70px">'
      + badge(ic, None, 40, R_ICON, 20)
      + '<div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px">'
      '<span style="font-size: 19px; font-weight: 700; letter-spacing: -0.02em; color: ' + nc + '">' + name + '</span>'
      '<div style="display: flex; align-items: center; gap: 4px">'
      '<span style="font-size: 15px; font-weight: 400; color: ' + INK3 + '; white-space: nowrap">' + sub + '</span>' + chp + '</div></div>'
      '<span class="num" style="font-size: 17px; font-weight: 700; color: ' + nc + '">' + amount + '</span></div>')

bills = page(
  T("Bills", "Everything that repeats each month")
  + '<div style="' + bordered("16px", "24px") + ' display: flex; flex-direction: column; gap: 14px">'
    + aline("&#8358;34,500 of bills this month. Three of the five are covered.", "17px")
    + '<div style="display: flex; flex-direction: column; gap: 8px">' + meter(3, 5)
      + '<div style="display: flex; justify-content: space-between">'
        '<span style="font-size: 13px; font-weight: 700; color: ' + ACC_TEXT + '">3 of 5 covered</span>'
        '<span style="font-size: 13px; font-weight: 500; color: ' + INK3 + '">2 still to sort</span></div></div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 11px">' + sectionhead("This month")
    + '<div style="display: flex; flex-direction: column">'
      + bill("Ikeja Electric", "power", "Due Thursday", "&#8358;8,000", chip("I pay it", ACC_TEXT), False, False, "PowerPay")
      + bill("DStv Compact", "tv", "Due 24 August", "&#8358;12,500", chip("Not covered", WARN_TEXT))
      + bill("Spectranet", "globe", "Due 27 August", "&#8358;15,000", chip("Not covered", WARN_TEXT))
      + bill("LAWMA waste", "waste", "Paid 2 August", "&#8358;2,000", '', False, True)
      + bill("MTN 5GB", "data", "Paid 4 August", "&#8358;2,500", '', True, True) + '</div></div>'
  + '<div style="height: 50px; border-radius: 25px; background: ' + FILL
    + '; display: flex; align-items: center; justify-content: center; gap: 9px">' + icon("plus", 17, INK, 2)
    + '<span style="font-size: 14.5px; font-weight: 600; color: ' + INK + '">Add a bill</span></div>'
  + offer("DStv and Spectranet are not covered. Shall I pay them?", "Set both up", "Rules"), 14) + dockback("Ask about your bills")
write("Bills", bills)

# ================= LOAN =================
def rowline(k, v, last=False, strong=False, vcolor=INK, vid="", kid=""):
    border = "" if strong else ""
    kw = "700" if strong else "400"
    ks = "17px"
    vs = "22px" if strong else "17px"
    kc = INK if strong else INK3
    return ('<div style="display: flex; align-items: center; height: 54px; gap: 10px">'
      '<span' + (' id="' + kid + '"' if kid else '') + ' style="flex-grow: 1; font-size: ' + ks + '; font-weight: ' + kw + '; color: ' + kc + '">' + k + '</span>'
      '<span' + (' id="' + vid + '"' if vid else '') + ' class="num" style="font-size: ' + vs + '; font-weight: 700; color: ' + vcolor + '">' + v + '</span></div>')

def dchip(t, on, act=""):
    if on:
        return ('<div' + hook("", act) + ' class="dchip on" style="flex-grow: 1; flex-basis: 0; height: 46px; border-radius: ' + pill(46)
          + '; background: ' + BTN + '; display: flex; align-items: center; justify-content: center; font-size: 17px; font-weight: 700; color: '
          + BTN_INK + '">' + t + '</div>')
    return ('<div' + hook("", act) + ' class="dchip" style="flex-grow: 1; flex-basis: 0; height: 46px; border-radius: ' + pill(46)
      + '; background: ' + SURF + '; display: flex; align-items: center; justify-content: center; font-size: 17px; font-weight: 700; color: '
      + INK2 + '">' + t + '</div>')

loan = page(
  T("Borrow", "The whole cost, before you decide")
  + aline("You asked what you could borrow. Here is the whole cost.", "16px")
  + '<div style="' + cardstyle("16px") + '; display: flex; flex-direction: column; gap: 14px">'
    + sectionhead("How much you want")
    + '<div style="display: flex; align-items: center; gap: 14px">'
      '<div' + hook("", "loan|-") + ' style="width: 44px; height: 44px; border-radius: ' + PILL + '; background: ' + SURF
      + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">' + icon("minus", 19, INK, 2.2) + '</div>'
      '<div id="lnAmt" style="flex-grow: 1; display: flex; justify-content: center">' + money("&#8358;150,000", "", 40) + '</div>'
      '<div' + hook("", "loan|+") + ' style="width: 44px; height: 44px; border-radius: ' + PILL + '; background: ' + SURF
      + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">' + icon("plus", 19, INK, 2.2) + '</div></div>'
    + '<div style="display: flex; flex-direction: column; gap: 7px">'
      '<div style="height: 6px; border-radius: 3px; background: ' + FILL3 + '; overflow: hidden"><div id="lnBar" style="width: 60%; height: 6px; border-radius: 3px; background: ' + ACC + '"></div></div>'
      '<div style="display: flex; justify-content: space-between"><span class="num" style="font-size: 12.5px; color: ' + INK3 + '">&#8358;10,000</span>'
      '<span class="num" style="font-size: 12.5px; color: ' + INK3 + '">&#8358;250,000 is your limit</span></div></div>'
    + '<div style="display: flex; gap: 9px">' + dchip("30 days", False, "term|1") + dchip("60 days", False, "term|2") + dchip("90 days", True, "term|3") + '</div></div>'
  + '<div style="display: flex; flex-direction: column">'
    + rowline("You get today", "&#8358;150,000", False, False, INK, "lnGet")
    + rowline("Interest, 4% a month", "&#8358;18,000", False, False, INK, "lnInt")
    + rowline("One off fee", "&#8358;1,500")
    + rowline("You pay back in all", "&#8358;169,500", False, True, INK, "lnTot")
    + rowline("Three payments of", "&#8358;56,500", False, False, INK, "lnPer", "lnPerK")
    + rowline("First payment", "19 September", True, False, INK, "lnDate") + '</div>'
  + '<div style="display: flex; gap: 9px; align-items: flex-start">' + icon("lock", 16, INK3, 1.6, "; margin-top: 2px")
    + '<span style="font-size: 14.5px; font-weight: 500; line-height: 1.45; color: ' + INK2
    + '; text-wrap: pretty">Pay late and it costs &#8358;2,000 a day. Late loans are reported to the credit bureau.</span></div>', 14)
loan += confirmbar(slide("Slide to take &#8358;150,000", "done|Loan", "lnSlide"))
write("Loan", loan)

# ================= VIRTUAL CARD =================
def act(name, ic, go="", action="soon", col=None):
    return ('<div' + hook(go, "" if go else action) + ' style="flex-grow: 1; flex-basis: 0; display: flex; flex-direction: column; align-items: center; gap: 9px">'
      + badge(ic, None, 52, R_TILE, 25, False, col)
      + '<span style="font-size: 15px; font-weight: 700; color: ' + INK + '">' + name + '</span></div>')

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
  + '<div style="display: flex; gap: 10px">' + act("Reveal","search","","reveal") + act("Freeze","freeze","","freeze", IC["cyan"]) + act("Fund","plus","","soon", IC["green"]) + act("Rules","list","Rules", IC["purple"]) + '</div>'
  + '<div style="' + bordered("16px", "24px") + '">' + aline("This card has paid Netflix four times, &#8358;21,000 in all.", "17px") + '</div>'
  + '<div style="' + cardstyle("15px") + '; display: flex; flex-direction: column; gap: 11px">'
    + '<div style="display: flex; align-items: baseline; justify-content: space-between">'
      '<span style="font-size: 13.5px; color: ' + INK2 + '">Spent this month</span>'
      '<span class="num" style="font-size: 15px; font-weight: 600">&#8358;21,000 of &#8358;50,000</span></div>'
    + '<div style="height: 7px; border-radius: 4px; background: ' + FILL3 + '; overflow: hidden"><div style="width: 42%; height: 7px; border-radius: 4px; background: ' + ACC + '"></div></div>'
    + '<span class="num" style="font-size: 12.5px; color: ' + INK3 + '">&#8358;29,000 left before it stops working</span></div>'
  + '<div style="height: 50px; border-radius: 25px; background: ' + FILL
    + '; display: flex; align-items: center; justify-content: center; gap: 9px">' + icon("plus", 17, INK, 2)
    + '<span style="font-size: 14.5px; font-weight: 600; color: ' + INK + '">Make another card</span></div>', 14) + dockback("Ask about this card")
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

ask = ('<div class="behind">' + page(home_inner, 16) + askbar("Ask, or just say what you need") + '</div>'
  + '<div class="fauxbg" style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; background: ' + SCRIM
  + '; ' + BLUR + '; z-index: 5"></div>'
  + '<div class="sheet" style="position: absolute; left: 10px; right: 10px; bottom: 10px; max-height: 76%; z-index: 6; background: ' + SURF
  + '; border-radius: ' + R_SHEET + '; ' + SH_SHEET + '; overflow: hidden; display: flex; flex-direction: column">'
  '<div style="height: 3px; width: 100%; overflow: hidden; flex-shrink: 0"><div class="sweep" style="height: 3px; width: 100%; background: linear-gradient(90deg, rgba(0,0,0,0) 0%, '
  + ACC + ' 50%, rgba(0,0,0,0) 100%)"></div></div>'
  '<div style="display: flex; justify-content: center; padding: 12px 0 0 0"><div style="width: 38px; height: 4px; border-radius: 2px; background: ' + LINE2 + '"></div></div>'
  '<div style="padding: 20px 20px 20px 20px; display: flex; flex-direction: column; gap: 20px">'
    '<div style="display: flex; align-items: center; gap: 9px">' + mark(24)
    + '<span style="font-size: 17px; font-weight: 700; color: ' + ACC_TEXT + '">Listening</span></div>'
    '<div style="font-size: 28px; font-weight: 700; letter-spacing: -0.03em; line-height: 1.24; color: ' + INK + '; text-wrap: pretty">2k data for<span style="color: ' + INK3 + '"> mum</span></div>'
    + wave()
    + '<div style="display: flex; flex-direction: column; gap: 10px">' + sectionhead("Or try one of these")
      + '<div style="display: flex; flex-direction: column; gap: 8px">'
      + sugg("Pay my light bill", "PowerPay") + sugg("How much did I spend on data?", "Answer") + sugg("What can I borrow?", "Loan") + '</div></div></div>'
  '<div style="padding: 0 20px 24px 20px; display: flex; gap: 10px; align-items: center">'
    '<div' + hook("Airtime") + ' style="flex-grow: 1; height: 56px; border-radius: ' + PILL + '; background: ' + ACC + '; ' + SH_BTN
    + '; display: flex; align-items: center; justify-content: center">'
    '<span style="font-size: 17px; font-weight: 700; color: #FFFFFF">Release to send</span></div>'
    '<div' + hook("back") + ' style="width: 56px; height: 56px; border-radius: ' + PILL + '; background: ' + FILL
    + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
    '<div style="width: 15px; height: 15px; border-radius: 3px; background: ' + INK2 + '"></div></div></div></div>')
write("Ask", ask, ANIM)

# ================= ANSWER =================
def bar(h, accent=False):
    c = ACC if accent else FILL3
    lc = INK2 if accent else INK3
    return ('<div style="flex-grow: 1; display: flex; flex-direction: column; justify-content: flex-end; gap: 10px; align-items: center">'
      '<div style="width: 62%; height: ' + str(h) + 'px; border-radius: ' + R_BAR + '; background: ' + c + '"></div>'
      '<span style="font-size: 10.5px; font-weight: 600; color: ' + lc + '">MONTH</span></div>')

def barm(h, m, accent=False):
    return bar(h, accent).replace("MONTH", m)

def mrow(name, ic, count, amount, last=False):
    return ('<div style="display: flex; align-items: center; gap: 14px; height: 62px">' + badge(ic, None, 40, R_ICON, 20)
      + '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 2px">'
      '<span style="font-size: 19px; font-weight: 700; letter-spacing: -0.02em">' + name + '</span>'
      '<span class="num" style="font-size: 15px; font-weight: 400; color: ' + INK3 + '">' + count + '</span></div>'
      '<span class="num" style="font-size: 17px; font-weight: 700">' + amount + '</span></div>')

def qchip(t):
    return ('<div' + hook("", "soon") + ' style="height: 42px; border-radius: ' + pill(42) + '; background: ' + SURF
      + '; display: flex; align-items: center; gap: 7px; padding: 0 15px">'
      '<span style="font-size: 13.5px; font-weight: 600; color: ' + INK + '">' + t + '</span>'
      '<svg width="11" height="11" viewBox="0 0 12 12" fill="none"><path d="M3 4.5 6 7.5l3-3" stroke="' + INK3
      + '" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></div>')

answer = page(
  T("Airtime and data", "You asked how much you spend on staying connected")
  + aline("&#8358;18,900 on airtime and data last month. That is your highest month this year.")
  + '<div style="' + cardstyle("18px 16px 8px 16px") + '; display: flex; flex-direction: column; gap: 18px">'
    + '<div style="display: flex; align-items: flex-end; justify-content: space-between">' + money("&#8358;18,900", "", 40)
      + '<div style="display: flex; align-items: center; gap: 5px; height: 28px; padding: 0 11px; border-radius: 14px; background: rgba(176,69,58,0.10); margin-bottom: 4px">'
      '<svg width="11" height="11" viewBox="0 0 12 12" fill="none"><path d="M6 9.5v-7M3 5.5 6 2.5l3 3" stroke="' + WARN_TEXT + '" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
      '<span class="num" style="font-size: 13px; font-weight: 700; color: ' + WARN_TEXT + '">&#8358;4,200</span></div></div>'
    + '<div style="display: flex; gap: 8px; height: 76px; align-items: stretch">'
      + barm(38,"Feb") + barm(50,"Mar") + barm(41,"Apr") + barm(56,"May") + barm(47,"Jun") + barm(68,"Jul", True) + '</div>'
    + '<div style="display: flex; flex-wrap: wrap; gap: 7px">' + qchip("Airtime and data") + qchip("Last month") + '</div>'
    + '<div' + hook("", "soon") + ' style="border-top: 1px solid ' + LINE + '; display: flex; align-items: center; gap: 9px; height: 48px">'
      + icon("list", 15, INK3, 1.5)
      + '<span class="num" style="flex-grow: 1; font-size: 12.5px; color: ' + INK3 + '">Added up from 14 top ups, 1 to 31 July</span>' + chev() + '</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 13px">' + sectionhead("Where it went")
    + '<div style="display: flex; flex-direction: column; gap: 15px">'
    + mrow("MTN data", "data", "5 top ups", "&#8358;12,500")
    + mrow("MTN airtime", "airtime", "7 top ups", "&#8358;4,400")
    + mrow("Glo airtime", "airtime", "2 top ups", "&#8358;2,000") + '</div></div>'
  + '<div style="' + bordered("16px", "24px") + '">' + aline("A 10GB monthly plan is &#8358;4,000 and would save about &#8358;1,800.", "17px") + '</div>', 13) + dockback("Ask about this")
write("Answer", answer)

# ================= SEND MONEY =================
pay = page(
  T("Send money", "To Sarah Adeyemi")
  + quote("send Sarah 50k for the flat deposit")
  + aline("Here it is, ready to go. Check the three parts I filled in.")
  + '<div style="' + cardstyle("14px") + '; display: flex; flex-direction: column; gap: 10px">'
    + tinted(money("&#8358;50,000", "", 40), "I took this from your message", "14px 15px 12px 15px")
    + tinted('<div style="display: flex; align-items: center; gap: 12px">' + avatar("SA")
        + '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 2px">'
          '<span style="font-size: 15px; font-weight: 600">Sarah Adeyemi</span>'
          '<span class="num" style="font-size: 12.5px; color: ' + INK2 + '">GTBank &#183; 0123 4457 8842</span></div>' + chev() + '</div>',
        "The only Sarah you have paid before")
    + tinted('<div style="display: flex; align-items: center; height: 22px">'
        '<span style="flex-grow: 1; font-size: 13.5px; color: ' + INK2 + '">Reference</span>'
        '<span style="font-size: 15px; font-weight: 500">Flat deposit</span></div>',
        "I took this from your message")
    + '<div style="background: ' + SURF + '; border-radius: ' + R_FIELD + '; overflow: hidden; padding: 0 16px">'
      + plainrow("From", "Everyday &#183; 0102 4457 88", False, INK, True)
      + plainrow("Arrives", "In a few seconds", False, INK, True)
      + plainrow("Fee", "Free", True, IN_TEXT) + '</div></div>'
  + '<div style="display: flex; gap: 9px; align-items: flex-start">' + icon("lock", 16, INK3, 1.6, "; margin-top: 2px")
    + '<span style="font-size: 14.5px; font-weight: 500; line-height: 1.45; color: ' + INK2
    + '; text-wrap: pretty">Nothing moves until you slide.</span></div>', 15)
pay += confirmbar(slide("Slide to send &#8358;50,000", "done|Pay"))
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
    + rule("Move &#8358;20,000 to Holiday on payday", "The day your salary lands.", "Moved 4 times &#183; &#8358;80,000 put aside", "See log", True)
    + rule("Pay the Ikeja Electric bill", "When it lands, up to &#8358;10,000.", "Paid 3 times &#183; &#8358;22,400", "See log", True)
    + rule("Buy 5GB when my data runs out", "Once a month at most.", "Bought twice &#183; &#8358;5,000", "See log", True) + '</div>'
  + '<div style="display: flex; flex-direction: column; gap: 11px">' + sectionhead("I will always ask first")
    + never("Paying anyone you have not paid before")
    + never("Anything over &#8358;20,000")
    + never("Taking a loan on your behalf") + '</div>'
  + '<div style="height: 50px; border-radius: 25px; background: ' + FILL
    + '; display: flex; align-items: center; justify-content: center; gap: 9px">' + icon("plus", 17, INK, 2)
    + '<span style="font-size: 14.5px; font-weight: 600; color: ' + INK + '">Add an instruction</span></div>', 14)
rules += dockback("Ask me to set one up")
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
    + '<div style="background: ' + SURF + '; border-radius: ' + R_FIELD + '; overflow: hidden; padding: 0 16px">'
      + plainrow("From", "Everyday &#183; 0102 4457 88", False, INK, True)
      + plainrow("Token arrives", "In a few seconds", True) + '</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 11px">' + sectionhead("Or pick an amount")
    + '<div style="display: flex; gap: 8px">' + bundle("&#8358;3,000", "About 14 kWh", "pw|3,000") + bundle("&#8358;8,000", "About 38 kWh", "pw|8,000") + bundle("&#8358;15,000", "About 72 kWh", "pw|15,000") + '</div></div>'
  + '<div style="display: flex; gap: 9px; align-items: flex-start">' + icon("lock", 16, INK3, 1.6, "; margin-top: 2px")
    + '<span style="font-size: 14.5px; font-weight: 500; line-height: 1.45; color: ' + INK2
    + '; text-wrap: pretty">The token appears here and in your messages.</span></div>', 15)
powerpay += confirmbar(slide("Slide to pay &#8358;8,000", "Power", "pwSlide"))
write("PowerPay", powerpay, "", True)

# ================= DONE =================
done = page(
  T("All done", "Your receipt is below, and in your messages")
  + '<div style="display: flex; flex-direction: column; gap: 16px; align-items: flex-start">'
    + tickmark("dnMark", 56)
    + '<div style="display: flex; flex-direction: column; gap: 6px">'
      '<div id="dnAmt">' + money("&#8358;2,500", "", 40) + '</div>'
      '<span id="dnWhat" style="font-size: 15px; color: ' + INK2 + '">5GB sent to Mum</span></div></div>'
  + '<div id="dnCard" style="display: flex; flex-direction: column">'
    + plainrow("From", "Everyday &#183; 0102 4457 88")
    + plainrow("Reference", "MTN-88231-4471", True) + '</div>'
  + '<div id="dnOffer">' + offer("Want me to do this every month without asking?", "Set it up", "Rules") + '</div>', 16)
done += dockback("Ask about this")
write("Done", done)

# ================= A GOAL =================
def feeder(name, ic, sub, amount, last=False):
    return ('<div style="display: flex; align-items: center; gap: 14px; height: 68px">'
      + badge(ic, None, 40, R_ICON, 20)
      + '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 2px">'
      '<span style="font-size: 19px; font-weight: 700; letter-spacing: -0.02em">' + name + '</span>'
      '<span style="font-size: 15px; font-weight: 400; color: ' + INK3 + '">' + sub + '</span></div>'
      '<span class="num" style="font-size: 17px; font-weight: 700; color: ' + ACC_TEXT + '">' + amount + '</span></div>')

goal = page(
  T("Holiday", "&#8358;250,000 by 12 March")
  + '<div style="' + cardstyle("20px") + '; display: flex; flex-direction: column; align-items: center; gap: 16px">'
    + ring(33)
    + '<div style="display: flex; flex-direction: column; align-items: center; gap: 4px">'
      + '<div style="display: flex; align-items: baseline; gap: 1px">'
        '<span id="glAmt" class="num" style="font-size: 30px; font-weight: 700; letter-spacing: -0.04em; color: ' + INK + '">&#8358;82,400</span></div>'
      + '<span class="num" style="font-size: 15px; font-weight: 500; color: ' + INK3 + '">of &#8358;250,000 put aside</span></div></div>'
  + aline("You are a fortnight ahead. Keep this up and you will get there on 26 February.", "16px")
  + '<div style="display: flex; flex-direction: column; gap: 12px">' + label("What is feeding it")
    + '<div style="display: flex; flex-direction: column">'
      + feeder("Payday transfer", "pot", "&#8358;20,000 every month", "&#8358;80,000")
      + feeder("Round ups", "swap", "The change from card payments", "&#8358;2,280")
      + feeder("Money back on top ups", "airtime", "Instead of cash back", "&#8358;120", True) + '</div></div>'
  + '<div style="display: flex; gap: 10px">'
    '<div' + hook("", "soon") + ' style="flex-grow: 1; height: 52px; border-radius: ' + PILL + '; background: ' + BTN + '; ' + SH_BTN
    + '; display: flex; align-items: center; justify-content: center; font-size: 15px; font-weight: 700; color: ' + BTN_INK + '">Add money</div>'
    '<div' + hook("Rules") + ' style="flex-grow: 1; height: 52px; border-radius: ' + PILL + '; background: ' + FILL
    + '; display: flex; align-items: center; justify-content: center; font-size: 15px; font-weight: 700; color: ' + INK + '">Change the plan</div></div>'
  + '<div style="display: flex; gap: 10px; align-items: flex-start">' + icon("lock", 16, INK3, 1.8, "; margin-top: 2px")
    + '<span style="font-size: 14px; font-weight: 500; line-height: 1.45; color: ' + INK3
    + '; text-wrap: pretty">Nothing here is locked. Take it back whenever you need it.</span></div>', 20)
goal += dockback("Ask about this goal")
write("Goal", goal)


# ================= SETTINGS =================
def setrow(name, ic, go="", act="soon", color=None, last=False):
    return ('<div' + hook(go, "" if go else act) + ' style="display: flex; align-items: center; gap: 14px; height: 64px">'
      + badge(ic, None, 36, "11px", 19, False, color)
      + '<span style="flex-grow: 1; font-size: 19px; font-weight: 700; letter-spacing: -0.02em; color: ' + INK + '">' + name + '</span>'
      + chevbtn() + '</div>')

def setgroup(title, rows):
    return ('<div style="display: flex; flex-direction: column; gap: 4px">' + sectionhead(title)
      + '<div style="display: flex; flex-direction: column">' + rows + '</div></div>')

settings = page(
  '<div style="font-size: 28px; font-weight: 700; letter-spacing: -0.035em; color: ' + INK + '">Settings</div>'
  + '<div style="padding-top: 16px">'
  + promorow("Get Leorio Plus", "Higher limits and no fees", "star", "", "soon") + '</div>'
  + setgroup("Security", setrow("Keys and recovery", "key") + setrow("Spending limits", "shield")
             + setrow("Standing instructions", "list", "Rules"))
  + setgroup("General", setrow("Your details", "person") + setrow("Notifications", "bell")
             + setrow("Saved people", "gift") + setrow("Cards", "card", "Card"))
  + setgroup("About", setrow("Contact support", "chat") + setrow("Give feedback", "star")
             + '<div' + hook("", "soon") + ' style="display: flex; align-items: center; gap: 14px; height: 64px">'
             + badge("lock", None, 36, "11px", 19, False, IC["red"])
             + '<span style="flex-grow: 1; font-size: 19px; font-weight: 700; letter-spacing: -0.02em; color: ' + WARN_TEXT + '">Sign out</span></div>')
  + '<div style="padding-top: 8px; text-align: center">'
    '<span style="font-size: 15px; font-weight: 400; color: ' + INK3 + '">Version 1.0.4</span></div>', 20)
settings += dockback("Ask me to change something")
write("Settings", settings)

# ================= ACTIVITY =================
def tx(name, ic, sub, amount, incoming=False, last=False):
    col = IN_TEXT if incoming else INK
    sign = "+" if incoming else "&#8722;"
    return ('<div' + hook("", "soon") + ' style="display: flex; align-items: center; gap: 14px; height: 70px">'
      + badge(ic, None, 40, R_ICON, 20)
      + '<div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px">'
      '<span style="font-size: 19px; font-weight: 700; letter-spacing: -0.02em">' + name + '</span>'
      '<span style="font-size: 15px; font-weight: 400; color: ' + INK3 + '">' + sub + '</span></div>'
      '<span class="num" style="font-size: 17px; font-weight: 700; color: ' + col + '">' + sign + amount + '</span></div>')

activity = page(
  T("Activity", "Everything that moved, newest first", "clock")
  + segment(["All", "In", "Out"], 0, "seg")
  + '<div style="display: flex; flex-direction: column; gap: 4px">' + sectionhead("Today")
    + '<div style="display: flex; flex-direction: column">'
    + tx("Sarah Adeyemi", "send", "Flat deposit &#183; 09:14", "&#8358;50,000")
    + tx("MTN", "data", "5GB for Mum &#183; 08:02", "&#8358;2,500")
    + tx("Holiday goal", "pot", "Round ups &#183; 07:30", "&#8358;280") + '</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 4px">' + sectionhead("Yesterday")
    + '<div style="display: flex; flex-direction: column">'
    + tx("Pagrin Limited", "bank", "August salary &#183; 16:40", "&#8358;640,000", True)
    + tx("Ikeja Electric", "power", "Meter 4457 8891 &#183; 11:22", "&#8358;8,000")
    + tx("Netflix", "card", "Virtual card &#183; 09:00", "&#8358;5,200") + '</div></div>'
  + '<div style="' + bordered("16px", "24px") + '">'
    + aline("Your spending is &#8358;41,000 below this point last month.", "17px") + '</div>', 18)
activity += dockback("Ask about any of these")
write("Activity", activity)

# ================= ADD MONEY, AS A SHEET =================
def sheetrow(name, ic, sub, last=False):
    return ('<div' + hook("", "soon") + ' style="display: flex; align-items: center; gap: 14px; height: 72px">'
      + badge(ic, None, 44, R_ICON, 22)
      + '<div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px">'
      '<span style="font-size: 19px; font-weight: 700; letter-spacing: -0.02em">' + name + '</span>'
      '<span style="font-size: 15px; font-weight: 400; color: ' + INK3 + '">' + sub + '</span></div>'
      + chevbtn() + '</div>')

receive_inner = (sheetx()
  + '<div style="display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 4px 0 20px 0">'
  + badge("down", None, 64, "20px", 30, False, IC["blue"])
  + '<span style="font-size: 22px; font-weight: 700; letter-spacing: -0.025em; color: ' + INK + '; margin-top: 8px">Add money</span>'
  + '<span style="font-size: 17px; font-weight: 400; color: ' + INK3 + '; text-align: center; text-wrap: pretty">'
    'Pick how you want the money to reach you</span></div>'
  + '<div style="display: flex; flex-direction: column">'
  + sheetrow("Bank transfer", "bank", "Your number, 0102 4457 88")
  + sheetrow("From a card", "card", "Any Nigerian debit card")
  + sheetrow("Ask someone", "request", "Send a request they can pay", True) + '</div>')

RECEIVE_SHEET = sheet(receive_inner)
write("Receive", page(home_inner, 16) + askbar("Ask, or just say what you need") + RECEIVE_SHEET)

if EMIT:
    print("built:", ", ".join(sorted(f for f in os.listdir(OUT) if f.endswith(".dc.html"))))
