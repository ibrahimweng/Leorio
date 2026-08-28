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

def _ramp(fs, fw, num=False):
    """Answer the question 'which of the nine styles was this?'. A size that
    does not exist goes to its neighbour, then a weight that does not exist at
    that size goes to its own. The one judgement call is small and bold: there
    is no bold at twelve, and a short bold thing at that size is a tag, so it
    becomes one."""
    fs = _near(fs, TYPE)
    fw = WEIGHT.get(fw, 400)
    if num and fs < MONEY_MIN_PX:      # money never renders at the bottom
        fs = MONEY_MIN_PX
    if fw not in WEIGHTS_AT[fs]:
        if fs == 12 and fw >= 700:
            fs, fw = 10, 700
        elif fs == 10 and fw < 700:
            fs, fw = 12, 400
        else:
            fw = min(WEIGHTS_AT[fs], key=lambda w: (abs(w - fw), -w))
    return fs, fw

def _sized(css, num=False):
    """Rewrite one inline style so its type is a style off the ramp and not a
    set of numbers that happen to be nearby."""
    m = re.search(r"font-size: ([0-9.]+)px", css)
    if not m:
        return css
    wm = re.search(r"font-weight: (\d+)", css)
    fs, fw = _ramp(float(m.group(1)), int(wm.group(1)) if wm else 400, num)
    _, lh, tr = STYLE[(fs, fw)]
    css = re.sub(r"font-size: [0-9.]+px", "font-size: %dpx" % fs, css, count=1)
    css = (re.sub(r"font-weight: \d+", "font-weight: %d" % fw, css, count=1) if wm
           else css.replace("font-size: %dpx" % fs, "font-size: %dpx; font-weight: %d" % (fs, fw), 1))
    # The style owns the line and the tracking. Whatever the call site asked
    # for is replaced, because a style that only half applies is not a style.
    ls = "letter-spacing: %sem" % ("0" if tr == 0 else ("%.4f" % (tr / 100.0)).rstrip("0"))
    css = (re.sub(r"letter-spacing: -?[0-9.]+em", ls, css, count=1)
           if "letter-spacing:" in css else css + "; " + ls)
    css = (re.sub(r"line-height: [0-9.]+(px)?", "line-height: " + lh, css, count=1)
           if "line-height:" in css else css + "; line-height: " + lh)
    return css

_ELEM = re.compile(r'<[^>]+>')

def _type_pass(html):
    """Every element that sets a size gets its style. Two surfaces opt out:
    the on-screen keyboard and the payment card are objects the phone and the
    bank draw, not text this product writes, and neither belongs to the ramp."""
    def one(m):
        tag = m.group(0)
        cls = re.search(r'class="([^"]*)"', tag)
        names = cls.group(1).split() if cls else []
        if "chrome" in names:
            return tag
        sm = re.search(r'style="([^"]*)"', tag)
        if not sm:
            return tag
        css = _sized(sm.group(1), num="num" in names)
        return tag[:sm.start(1)] + css + tag[sm.end(1):]
    return _ELEM.sub(one, html)

def snap(html):
    """Pull every size, gap and radius onto its scale. Nothing drifts."""
    html = _type_pass(html)
    html = re.sub(r"\b(gap|row-gap|column-gap): ([0-9.]+)px",
                  lambda m: "%s: %dpx" % (m.group(1), _near(float(m.group(2)), SPACE)), html)

    def _one(p):
        v = float(p[:-2])
        if v >= 100 or v < 8:          # a pill, or too small to belong to the scale
            return p
        return "%dpx" % _near(v, RADII)

    def _rad(m):
        # A radius can name one corner or all four. Reading only the first
        # number rounded one corner of an oval and left the other three, which
        # is how the face oval came out lopsided.
        return "border-radius: " + " ".join(_one(p) for p in m.group(1).split())
    html = re.sub(r"border-radius: ((?:[0-9.]+px)(?:\s+[0-9.]+px){0,3})", _rad, html)

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
 "share": '<path d="M12 3.6v11.2M8.3 7.3 12 3.6l3.7 3.7"/><path d="M7.2 11.2H5.6A1.6 1.6 0 0 0 4 12.8v6.2a1.6 1.6 0 0 0 1.6 1.6h12.8a1.6 1.6 0 0 0 1.6-1.6v-6.2a1.6 1.6 0 0 0-1.6-1.6h-1.6"/>',
 "more": '<circle cx="8" cy="8" r="1.5" fill="currentColor" stroke="none"/><circle cx="16" cy="8" r="1.5" fill="currentColor" stroke="none"/><circle cx="8" cy="16" r="1.5" fill="currentColor" stroke="none"/><circle cx="16" cy="16" r="1.5" fill="currentColor" stroke="none"/>',
 "grid": '<rect x="3.4" y="3.4" width="7.4" height="7.4" rx="2.2"/><rect x="13.2" y="3.4" width="7.4" height="7.4" rx="2.2"/><rect x="3.4" y="13.2" width="7.4" height="7.4" rx="2.2"/><rect x="13.2" y="13.2" width="7.4" height="7.4" rx="2.2"/>',
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
 "sort": '<path d="M7.4 19.2V4.8M4 8.2l3.4-3.4 3.4 3.4"/><path d="M16.6 4.8v14.4M13.2 15.8l3.4 3.4 3.4-3.4"/>',
 "faceid": '<path d="M3.6 8.8V6.2a2.6 2.6 0 0 1 2.6-2.6h2.6"/><path d="M15.2 3.6h2.6a2.6 2.6 0 0 1 2.6 2.6v2.6"/>'
           '<path d="M20.4 15.2v2.6a2.6 2.6 0 0 1-2.6 2.6h-2.6"/><path d="M8.8 20.4H6.2a2.6 2.6 0 0 1-2.6-2.6v-2.6"/>'
           '<path d="M8.6 9.4v2.4M15.4 9.4v2.4"/><path d="M12 9.4v4.4h-1.8"/><path d="M8.6 16.4a5 5 0 0 0 6.8 0"/>',
 "del": '<path d="M20.2 5.6H9.8a2 2 0 0 0-1.5.7l-4.6 5.1a.9.9 0 0 0 0 1.2l4.6 5.1a2 2 0 0 0 1.5.7h10.4a1.6 1.6 0 0 0 1.6-1.6V7.2a1.6 1.6 0 0 0-1.6-1.6z"/>'
        '<path d="M12.4 9.8 17 14.2M17 9.8l-4.6 4.4"/>',
 "camera": '<path d="M3.4 8.8a2.4 2.4 0 0 1 2.4-2.4h1.9l1.3-2.2h6l1.3 2.2h1.9a2.4 2.4 0 0 1 2.4 2.4v8.4a2.4 2.4 0 0 1-2.4 2.4H5.8a2.4 2.4 0 0 1-2.4-2.4z"/>'
           '<circle cx="12" cy="12.8" r="3.6"/>',
 "alert": '<path d="M12 3.8 21.2 19.8H2.8z"/><path d="M12 9.8v4.2M12 16.8h.02"/>',
 "close": '<path d="M6.4 6.4 17.6 17.6M17.6 6.4 6.4 17.6"/>',
 "laptop": '<rect x="3.4" y="4.6" width="17.2" height="11.4" rx="2.1"/><path d="M2 19.4h20"/>',
 "eye": '<path d="M2.3 12s3.5-6.3 9.7-6.3S21.7 12 21.7 12s-3.5 6.3-9.7 6.3S2.3 12 2.3 12z"/><circle cx="12" cy="12" r="2.9"/>',
 "chart": '<path d="M4.6 19.6V13.2M9.5 19.6V8.1M14.4 19.6v-4.3M19.4 19.6V4.5"/>',
    "dollar": '<path d="M12 3.2v17.6"/>'
              '<path d="M16.4 7.6a3.8 3.8 0 0 0-3.7-2.6h-1.5a3.5 3.5 0 0 0 0 7h1.6a3.5 3.5 0 0 1 0 7h-1.6a3.8 3.8 0 0 1-3.7-2.6"/>',
 "id": '<rect x="2.6" y="4.8" width="18.8" height="14.4" rx="2.8"/><circle cx="8.6" cy="11.2" r="2.2"/>'
       '<path d="M5.2 16.6a3.9 3.9 0 0 1 6.8 0M14.8 10.2h3.6M14.8 13.8h3.6"/>',
 "qr": '<rect x="3.4" y="3.4" width="7" height="7" rx="1.8"/><rect x="13.6" y="3.4" width="7" height="7" rx="1.8"/>'
       '<rect x="3.4" y="13.6" width="7" height="7" rx="1.8"/><path d="M13.6 13.6h3.2v3.2h-3.2zM17.4 17.4h3.2v3.2h-3.2z"/>',
}

def _attr(color):
    """A colour on its way into an SVG attribute. The browser computes a
    color-mix in a style; in an attribute it is a string, and Figma reads the
    string. So the mix is resolved here instead of being passed on."""
    return ACC_TEXT_HEX if "color-mix" in str(color) else color

def icon(name, size=22, color=INK2, sw=1.7, extra=""):
    color = _attr(color)
    s = str(size)
    return ('<svg width="' + s + '" height="' + s + '" viewBox="0 0 24 24" fill="none" stroke="' + color
            + '" stroke-width="' + str(sw) + '" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink: 0; color: ' + color
            + extra + '">' + ICONS[name] + '</svg>')

# The action menu sits on a blurred white page, so its glyphs carry their own
# colour and stand on nothing. A circle behind each one is a second shape doing
# the first one's job. Filled, not drawn, so a small mark still reads as itself.
FILLED = {
 "home": '<path d="M11.1 2.9a1.4 1.4 0 0 1 1.8 0l8.1 6.75a1.4 1.4 0 0 1 .5 1.07V19.4a2.1 2.1 0 0 1-2.1 2.1H4.6a2.1 2.1 0 0 1-2.1-2.1v-8.68a1.4 1.4 0 0 1 .5-1.07z" fill="CUR"/>'
         '<path d="M9.6 21.5v-5.1a2.4 2.4 0 0 1 4.8 0v5.1z" fill="#FFFFFF"/>',
 "phone": '<rect x="5.4" y="1.8" width="13.2" height="20.4" rx="3.4" fill="CUR"/>'
          '<path d="M10.3 5.1h3.4" stroke="#FFFFFF" stroke-width="1.7" stroke-linecap="round" fill="none"/>'
          '<circle cx="12" cy="18.5" r="1.3" fill="#FFFFFF"/>',
 "id": '<rect x="2.1" y="4.5" width="19.8" height="15" rx="3.4" fill="CUR"/>'
       '<circle cx="8.5" cy="10.7" r="2.3" fill="#FFFFFF"/>'
       '<path d="M5.1 16.2c.5-1.7 1.85-2.6 3.4-2.6s2.9.9 3.4 2.6" stroke="#FFFFFF" stroke-width="1.7" stroke-linecap="round" fill="none"/>'
       '<path d="M14.8 9.9h4.2M14.8 13.5h2.8" stroke="#FFFFFF" stroke-width="1.7" stroke-linecap="round" fill="none"/>',
 "voice": '<g fill="CUR"><rect x="1.4" y="9.6" width="2.9" height="4.8" rx="1.45"/>'
          '<rect x="6" y="5.2" width="2.9" height="13.6" rx="1.45"/>'
          '<rect x="10.6" y="1.6" width="2.9" height="20.8" rx="1.45"/>'
          '<rect x="15.2" y="7" width="2.9" height="10" rx="1.45"/>'
          '<rect x="19.8" y="10.4" width="2.9" height="3.2" rx="1.45"/></g>',
 "send": '<path d="M21.5 2.9 3 10.1c-.93.36-.88 1.7.07 1.99l7.28 2.2 2.2 7.28c.29.95 1.63 1 1.99.07z" fill="CUR"/>'
         '<path d="M21.5 2.9 10.35 14.29l2.2 7.28c.29.95 1.63 1 1.99.07z" fill="CUR" opacity="0.55"/>',
 "receive": '<path d="M12 2.4a2 2 0 0 1 2 2v9.35l3.3-3.3a2 2 0 1 1 2.83 2.83l-6.71 6.72a2 2 0 0 1-2.83 0L3.87 13.3A2 2 0 0 1 6.7 10.45l3.3 3.3V4.4a2 2 0 0 1 2-2z" fill="CUR"/>',
 "history": '<circle cx="12" cy="12" r="9.5" fill="CUR"/>'
            '<path d="M12 6.5v5.75l3.6 2.1" stroke="#FFFFFF" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round" fill="none"/>',
 "settings": '<path d="M5.1 3.3h13.8v18l-2.76-1.72-2.34 1.72-2.34-1.72-2.34 1.72-2.34-1.72L5.1 21.3z" fill="CUR"/>'
             '<path d="M8.5 8.7h7M8.5 12.9h4.9" stroke="#FFFFFF" stroke-width="1.9" stroke-linecap="round" fill="none"/>',
 "warn": '<path d="M12 2.9a2.1 2.1 0 0 1 1.83 1.06l8.5 14.9A2.1 2.1 0 0 1 20.5 22h-17a2.1 2.1 0 0 1-1.83-3.14l8.5-14.9A2.1 2.1 0 0 1 12 2.9z" fill="CUR"/>'
         '<path d="M12 9v4.6M12 17.4h.02" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" fill="none"/>',
 "wait": '<circle cx="12" cy="12" r="8.7" stroke="CUR" stroke-width="3" opacity="0.26" fill="none"/>'
         '<path d="M12 3.3a8.7 8.7 0 0 1 8.7 8.7" stroke="CUR" stroke-width="3" stroke-linecap="round" fill="none"/>',
 # ---- the settings set, drawn as shapes so a row reads without a tile ----
 # Anything knocked out of a glyph is knocked out in white and recoloured by
 # fglyph, so the same drawing works on the page and on a grey card.
 "faceid": '<rect x="2.4" y="2.4" width="19.2" height="19.2" rx="5.4" fill="CUR"/>'
           '<path d="M9 9.3v2.3M15 9.3v2.3" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" fill="none"/>'
           '<path d="M9.1 15.4a4.6 4.6 0 0 0 5.8 0" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" fill="none"/>',
 "shield": '<path d="M11.6 2.5a1 1 0 0 1 .8 0l7 2.8a1 1 0 0 1 .6.93v5.37c0 4.63-3.17 8.05-7.6 9.95a1 1 0 0 1-.8 0C7.17 19.65 4 16.23 4 11.6V6.23a1 1 0 0 1 .6-.93z" fill="CUR"/>'
           '<path d="M8.7 11.9 11 14.3l4.3-4.5" stroke="#FFFFFF" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round" fill="none"/>',
 "list": '<g fill="CUR"><rect x="3.2" y="5" width="17.6" height="2.9" rx="1.45"/>'
         '<rect x="3.2" y="10.55" width="17.6" height="2.9" rx="1.45"/>'
         '<rect x="3.2" y="16.1" width="10.6" height="2.9" rx="1.45"/></g>',
 "laptop": '<rect x="2.8" y="4.2" width="18.4" height="12.2" rx="2.6" fill="CUR"/>'
           '<rect x="5.5" y="6.9" width="13" height="6.8" rx="1.2" fill="#FFFFFF"/>'
           '<rect x="1.1" y="17.9" width="21.8" height="2.7" rx="1.35" fill="CUR"/>',
 "key": '<circle cx="8.3" cy="15.5" r="4.9" fill="CUR"/><circle cx="8.3" cy="15.5" r="1.75" fill="#FFFFFF"/>'
        '<path d="M11.3 12 19.1 4.2a1.7 1.7 0 0 1 2.4 2.4l-.85.85-1.5-1.5-1.75 1.75 1.5 1.5-1.7 1.7-1.5-1.5-1.75 1.75 1.5 1.5-2 2z" fill="CUR"/>',
 "person": '<g fill="CUR"><circle cx="12" cy="7.9" r="4.3"/>'
           '<path d="M12 13.7c4.4 0 8 3 8 6.6a.9.9 0 0 1-.9.9H4.9a.9.9 0 0 1-.9-.9c0-3.6 3.6-6.6 8-6.6z"/></g>',
 "bell": '<g fill="CUR"><path d="M12 2.4a6.8 6.8 0 0 1 6.8 6.8c0 4.6 1.6 5.8 2.1 6.3a.95.95 0 0 1-.66 1.63H3.76a.95.95 0 0 1-.66-1.63c.5-.5 2.1-1.7 2.1-6.3A6.8 6.8 0 0 1 12 2.4z"/>'
         '<path d="M9.5 18.8h5a2.5 2.5 0 0 1-5 0z"/></g>',
 "gift": '<g fill="CUR"><rect x="2.6" y="7.5" width="18.8" height="5.1" rx="1.7"/>'
         '<path d="M4.5 13.5h15v5.7a1.8 1.8 0 0 1-1.8 1.8H6.3a1.8 1.8 0 0 1-1.8-1.8z"/>'
         '<path d="M12 7.5S10.3 2.9 7.9 2.9a2.3 2.3 0 0 0 0 4.6zM12 7.5s1.7-4.6 4.1-4.6a2.3 2.3 0 0 1 0 4.6z"/></g>'
         '<path d="M12 8.1v12.5" stroke="#FFFFFF" stroke-width="2.1" fill="none"/>',
 "card": '<rect x="2.3" y="4.9" width="19.4" height="14.2" rx="3.1" fill="CUR"/>'
         '<path d="M2.3 10.1h19.4" stroke="#FFFFFF" stroke-width="2.3" fill="none"/>'
         '<path d="M5.6 15.4h3.6" stroke="#FFFFFF" stroke-width="1.9" stroke-linecap="round" fill="none"/>',
 "chat": '<path d="M12.5 3.4a8.3 8.3 0 0 1 8.3 8.3 8.3 8.3 0 0 1-8.7 8.3 9.1 9.1 0 0 1-2.6-.44l-4.83 1.22a.82.82 0 0 1-1-1.02l1.34-4.5a8.6 8.6 0 0 1-.67-3.13A8.3 8.3 0 0 1 12.5 3.4z" fill="CUR"/>',
 "star": '<path d="m12 2.8 2.87 5.82 6.42.94a1 1 0 0 1 .56 1.7l-4.65 4.53 1.1 6.4a1 1 0 0 1-1.46 1.05L12 20.22l-5.74 3.02a1 1 0 0 1-1.46-1.05l1.1-6.4-4.65-4.53a1 1 0 0 1 .56-1.7l6.42-.94z" fill="CUR"/>',
 "clock": '<circle cx="12" cy="12" r="9.4" fill="CUR"/>'
          '<path d="M12 6.4v5.85l3.7 2.15" stroke="#FFFFFF" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round" fill="none"/>',
 "eye": '<path d="M12 4.8c6.7 0 10.4 6.5 10.4 7.2s-3.7 7.2-10.4 7.2S1.6 12.7 1.6 12 5.3 4.8 12 4.8z" fill="CUR"/>'
        '<circle cx="12" cy="12" r="3.2" fill="#FFFFFF"/>',
 "camera": '<path d="M8.5 3.3h7a1.4 1.4 0 0 1 1.21.69l1.03 1.75h2.06a2.9 2.9 0 0 1 2.9 2.9v8.56a2.9 2.9 0 0 1-2.9 2.9H4.2a2.9 2.9 0 0 1-2.9-2.9V8.64a2.9 2.9 0 0 1 2.9-2.9h2.06L7.29 4a1.4 1.4 0 0 1 1.21-.7z" fill="CUR"/>'
           '<circle cx="12" cy="12.8" r="3.6" fill="#FFFFFF"/>',
 "lock": '<path d="M12 2a5 5 0 0 1 5 5v2.8h-2.7V7a2.3 2.3 0 0 0-4.6 0v2.8H7V7a5 5 0 0 1 5-5z" fill="CUR"/>'
         '<rect x="4.1" y="9.7" width="15.8" height="11.5" rx="2.9" fill="CUR"/>'
         '<circle cx="12" cy="15.4" r="1.65" fill="#FFFFFF"/>',
 "undo": '<path d="M12 4.6a9.4 9.4 0 1 1-8.9 12.5 1.9 1.9 0 0 1 3.6-1.24A5.6 5.6 0 1 0 12 8.4H9.9l1.5-1.5A1.9 1.9 0 0 0 8.7 4.2L3.9 9a1.9 1.9 0 0 0 0 2.7l4.8 4.8a1.9 1.9 0 0 0 2.7-2.7l-1.5-1.5H12z" fill="CUR"/>',
}

def fglyph(name, size=34, color=INK, hole="#FFFFFF"):
    """A glyph that is a shape, not a line. Colour and the colour of anything
    knocked out of it both come in by substitution, so a white glyph on a
    coloured panel does not lose its own detail to the panel."""
    return ('<svg width="' + str(size) + '" height="' + str(size) + '" viewBox="0 0 24 24" fill="none" '
            'style="flex-shrink: 0">' + FILLED[name].replace("CUR", color).replace("#FFFFFF", hole) + '</svg>')

def avatar(t, size=38, bg=FILL, fg=INK, act="", eid=""):
    s = str(size)
    return ('<div' + hook("", act) + (' id="' + eid + '"' if eid else '') + ' style="width: ' + s + 'px; height: ' + s
      + 'px; border-radius: ' + PILL + '; background: ' + bg
      + '; display: flex; align-items: center; justify-content: center; font-size: 15px'
      + '; font-weight: 700; color: ' + fg + '; flex-shrink: 0">' + t + '</div>')

def chev(size=15, color=INK4, sw=2.1):
    color = _attr(color)
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

def badge(ic, t=None, size=44, radius=None, isz=None, dark=False, color=None, on=BG):
    """An icon in a quiet square. The square used to carry the service's own
    colour, so you found electricity before you read the word. On a page with
    eighteen of them that was not finding, it was the page shouting, and a
    thing that shouts everywhere cannot point at anything. So the square is
    grey and the glyph is black, and the colour is saved for the one item on a
    screen that is actually worth a look.

    `color` now paints the glyph and not the square, so a red padlock or a blue
    suggestion still reads without the square joining in. `on` is the surface
    underneath: a badge standing on a grey card takes a white square, because
    grey on grey is not a square at all."""
    r = radius or (R_TILE if size >= 46 else R_ICON)
    box = IC["black"] if dark else (SURF if on == FILL else FILL)
    glyph = "#FFFFFF" if dark else (color or INK)
    isz = isz or int(round(size * 0.5))
    return ('<div style="width: ' + str(size) + 'px; height: ' + str(size) + 'px; border-radius: ' + r
      + '; background: ' + box + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
      + icon(ic, isz, glyph, 1.8) + '</div>')

def circicon(ic, ring="#FFFFFF", glyph=BTN, size=26, isz=None):
    """The small filled circle that rides inside a pill button."""
    isz = isz or int(round(size * 0.62))
    return ('<div style="width: ' + str(size) + 'px; height: ' + str(size) + 'px; border-radius: ' + PILL
      + '; background: ' + ring + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
      + icon(ic, isz, glyph, 2.2) + '</div>')

def back():
    """The reference keeps back at the bottom left, as a bare chevron."""
    return ('<div' + hook("back") + ' class="backBtn" style="width: 44px; height: 44px; display: flex; align-items: center; '
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
    bg = {"black": BTN, "blue": ACC, "grey": FILL, "white": SURF}[kind]
    quiet = kind in ("grey", "white")
    fg = INK if quiet else "#FFFFFF"
    lead = ''
    if ic:
        _c = int(round(height * 0.58))
        lead = circicon(ic, "#FFFFFF" if not quiet else BTN,
                        (BTN if kind == "black" else ACC_HEX) if not quiet else "#FFFFFF",
                        _c) + ''
    width = ('width: 100%; ' if full else '')
    pad = ('0 24px' if not ic else ('0 20px 0 ' + str(int(round((height - int(round(height * 0.58))) / 2)) + 2) + 'px'))
    sh = ('; ' + SH_BTN) if not quiet else (('; ' + SH_RAISE) if kind == "white" else '')
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

# ---------- two tone glyphs ----------
# The founder's reference draws an action as a filled silhouette in two flat
# tones of one colour, with no outline and no gradient. The darker tone is
# always the part that would fold under or fall into shadow, which is what
# gives a flat shape its depth. This is the whole trick and it is worth stating
# plainly, because doing it with a gradient instead looks cheap immediately.
#
# It is used in one place: the four shortcuts on home. They are the only icons
# in the product meant to be picked out at a glance rather than read in order,
# so they are the only ones that earn colour.

def _hsl(hexcol):
    h = hexcol.lstrip("#")
    r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    mx, mn = max(r, g, b), min(r, g, b)
    l = (mx + mn) / 2
    if mx == mn:
        return 0.0, 0.0, l
    d = mx - mn
    s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
    if mx == r:   hh = ((g - b) / d) % 6
    elif mx == g: hh = (b - r) / d + 2
    else:         hh = (r - g) / d + 4
    return hh * 60, s, l

def _rgb(hh, s, l):
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs(((hh / 60) % 2) - 1))
    m = l - c / 2
    r, g, b = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)][int(hh // 60) % 6]
    return "#%02X%02X%02X" % tuple(round((v + m) * 255) for v in (r, g, b))

def _deep(hexcol, l=0.58, s=1.18):
    """The second tone. Darker, but not muddier: the lightness comes down and
    the saturation goes up a little, so the fold stays as vivid as the face.
    Multiplying the channels toward black instead is what turns an orange into
    a brown, and that is the difference between this and a cheap looking icon."""
    hh, ss, ll = _hsl(hexcol)
    return _rgb(hh, min(1.0, ss * s), max(0.0, ll * l))

def _vivid(hexcol, s=1.20, l=1.06):
    """The face, pushed a little brighter than the flat token. These four are
    the only icons carrying colour, so they carry it properly."""
    hh, ss, ll = _hsl(hexcol)
    return _rgb(hh, min(1.0, ss * s), min(0.92, ll * l))

def _pale(hexcol, s=0.60, l=1.58):
    """The lit face: the same hue washed nearly to white. It is what makes a
    screen read as glass and a keyhole read as a hole rather than a dent."""
    hh, ss, ll = _hsl(hexcol)
    return _rgb(hh, min(1.0, ss * s), min(0.93, ll * l))

def _rgba(hexcol, a):
    h = hexcol.lstrip("#")
    return "rgba(%d, %d, %d, %s)" % (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)

# Every corner is round. A filled path has no way to round its own joins, so
# the shape is drawn a little small and then stroked in its own paint with a
# round join, which fattens it back out with every point turned soft. This is
# the whole reason these read as drawn rather than as clip art.
_R = ' stroke-width="2.1" stroke-linejoin="round" stroke-linecap="round"'

# GRD is the light falling down the glyph, PAL the lit face, DIM the part
# turned away. Every glyph is lit from the same place, which is what makes four
# different objects look like one set.
TWOTONE = {
 # A phone. Without a screen it is only a rectangle, so the screen is the pale
 # tone and the body around it takes the light.
 "airtime": '<rect x="5.2" y="1.6" width="13.6" height="20.8" rx="4.4" fill="GRD"/>'
            '<rect x="7.7" y="4.7" width="8.6" height="12.2" rx="2.6" fill="PAL"/>'
            '<rect x="10.2" y="18.6" width="3.6" height="1.8" rx="0.9" fill="PAL"/>',
 # A bolt. One shape, so the light does all of the shading.
 "power":   '<path d="M14.4 3.2 6.9 13.1h4.1l-0.9 7.7 7.5-9.9h-4.1z" fill="GRD" stroke="GRD"' + _R + '/>',
 # Money shut away. The shackle sits behind the body, which is what makes it a
 # lock rather than a bag, and being behind is why it takes the darker tone.
 "pot":     '<path d="M8.9 11.2V7.6a3.1 3.1 0 0 1 6.2 0v3.6" fill="none" stroke="DIM" stroke-width="3" stroke-linecap="round"/>'
            '<rect x="4.2" y="9.4" width="15.6" height="12.4" rx="4.4" fill="GRD"/>'
            '<path d="M12 13.9a1.7 1.7 0 0 0-0.92 3.13l-0.34 1.67a0.6 0.6 0 0 0 0.59 0.72h1.34a0.6 0.6 0 0 0 0.59-0.72'
            'l-0.34-1.67A1.7 1.7 0 0 0 12 13.9z" fill="PAL"/>',
 # All of them. Four squares on one gradient read as one object lit from above;
 # four squares each lit on their own read as four objects.
 "grid":    '<rect x="3.9" y="3.9" width="7" height="7" rx="2.6" fill="GRD"/>'
            '<rect x="13.1" y="3.9" width="7" height="7" rx="2.6" fill="GRD"/>'
            '<rect x="3.9" y="13.1" width="7" height="7" rx="2.6" fill="GRD"/>'
            '<rect x="13.1" y="13.1" width="7" height="7" rx="2.6" fill="GRD"/>',
}

def ttglyph(name, size=22, hue=ACC_HEX):
    """A glyph lit from above, with a glow of its own colour under it. The glow
    is the third thing the reference does, after the light and the round
    corners, and it is what lifts the icon off the card instead of printing it
    on. The gradient is named after the colour and not after the glyph, so two
    icons of the same hue share one definition and the file stays small."""
    face, fold, pale = _vivid(hue), _deep(hue), _pale(hue)
    gid = "lg" + hue.lstrip("#")
    grad = ('<defs><linearGradient id="' + gid + '" x1="0" y1="2" x2="0" y2="22" '
            'gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="' + face + '"/>'
            '<stop offset="1" stop-color="' + fold + '"/></linearGradient></defs>')
    body = (TWOTONE[name].replace("GRD", "url(#" + gid + ")")
            .replace("CUR", face).replace("DIM", fold).replace("PAL", pale))
    return ('<svg width="' + str(size) + '" height="' + str(size) + '" viewBox="0 0 24 24" fill="none" '
            'style="flex-shrink: 0; filter: drop-shadow(0 3px 7px ' + _rgba(face, "0.45") + ')">'
            + grad + body + '</svg>')

def quickrow(items, card=True):
    """A row of shortcuts. No tile behind the glyph, which is the rule the
    reference follows: the square is kept for a thing that exists, like a bill
    or a service in the catalogue.

    A fourth value on an item is a colour, and it makes the glyph two tone
    rather than a black line. These four are the only icons in the product that
    are meant to be picked out at a glance, so they are the only ones with it."""
    cells = ''
    for it in items:
        name, ic, go = it[0], it[1], it[2]
        hue = it[3] if len(it) > 3 else None
        glyph = ttglyph(ic, 22, hue) if hue else icon(ic, 22, INK, 1.9)
        cells += ('<div' + hook(go) + ' class="qcell" style="flex-grow: 1; flex-basis: 0; min-width: 0; display: flex; '
          'flex-direction: column; align-items: center; gap: 10px; padding: 2px 0">' + glyph
          + '<span style="font-size: 12px; font-weight: 400; color: ' + INK + '; white-space: nowrap; '
            'overflow: hidden; text-overflow: ellipsis; max-width: 100%">' + name + '</span></div>')
    inner = '<div style="display: flex; gap: 4px">' + cells + '</div>'
    if not card:
        return inner
    return '<div style="' + cardstyle("14px 8px", "20px") + '">' + inner + '</div>'

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

def tinted(inner, note, pad="14px 16px", on=BG):
    """A field the model filled in. On a white page it speaks from its own soft
    blue panel, which is the one place that wash belongs. Stood inside a grey
    card it takes a white panel instead: a seven per cent blue over grey is
    neither white nor blue, it is a smudge, and three of them stacked up is the
    card looking dirty rather than the model looking careful. The note under it
    goes grey there too, so the only blue left inside the card is the one
    figure worth reading twice."""
    grey = (on == FILL)
    return ('<div style="border-radius: ' + R_INNER + '; background: ' + (SURF if grey else ACC_SOFT)
        + '; padding: ' + pad + '; display: flex; flex-direction: column; gap: 7px">' + inner
        + '<span style="font-size: 12px; font-weight: 400; color: '
        + (INK3 if grey else ACC_INK) + '">' + note + '</span></div>')

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

def caption(t, color=INK2, size=12):
    """The grey line that sits above a figure."""
    return ('<div style="font-size: ' + str(size) + 'px; font-weight: 400; color: ' + color + '">' + t + '</div>')

def money(whole, dec="", size=36, color=INK, dcolor=None):
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
        p = ('<div style="font-size: 16px; font-weight: 400; color: ' + INK3
             + '; text-wrap: pretty">' + sub + '</div>')
    # Heading 2. The home screen sets "Activities" at this size, and a page
    # title is the same rank as that, so it is the same style.
    return ('<div class="phead" style="display: flex; flex-direction: column; gap: 8px">'
      '<div style="display: flex; align-items: center; gap: 12px">' + lead
      + '<div style="font-size: 22px; font-weight: 700; color: '
      + INK + '">' + title + '</div></div>' + p + '</div>')

def arcpath(cx, cy, r, pct):
    """The visible part of a ring, as a path. A dashed circle says the same
    thing in a browser and nothing at all once the dashes are dropped, and the
    one place that happens is the one place the ring has to be right."""
    import math
    pct = max(0.0, min(100.0, float(pct)))
    a = math.radians(-90 + 3.6 * pct)
    x, y = cx + r * math.cos(a), cy + r * math.sin(a)
    return ("M %g %g A %g %g 0 %d 1 %g %g"
            % (cx, cy - r, r, r, 1 if pct > 50 else 0, x, y))

def ring(pct, size=180, stroke=14, suffix="%", foot="of the way", eid="glPct"):
    r = (size - stroke) / 2.0
    circ = 2 * 3.141592653589793 * r
    off = circ * (1 - pct / 100.0)
    half = size / 2.0
    def n(v):
        return ("%g" % v)
    return ('<div style="position: relative; width: ' + str(size) + 'px; height: ' + str(size) + 'px; flex-shrink: 0">'
      '<svg width="' + str(size) + '" height="' + str(size) + '" viewBox="0 0 ' + str(size) + ' ' + str(size)
      + '">'
      '<circle cx="' + n(half) + '" cy="' + n(half) + '" r="' + n(r) + '" fill="none" stroke="' + FILL3
      + '" stroke-width="' + str(stroke) + '"/>'
      + ('<circle class="ring" cx="' + n(half) + '" cy="' + n(half) + '" r="' + n(r) + '" fill="none" stroke="' + ACC
         + '" stroke-width="' + str(stroke) + '"/>' if pct >= 100 else
         '<path class="ring" d="' + arcpath(half, half, r, pct) + '" fill="none" stroke="' + ACC
         + '" stroke-width="' + str(stroke) + '" stroke-linecap="round"/>') + '</svg>'
      '<div style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; display: flex; flex-direction: column; '
      'align-items: center; justify-content: center; gap: 2px">'
      '<span' + (' id="' + eid + '"' if eid else '') + ' class="num" style="font-size: 40px; font-weight: 800; letter-spacing: -0.04em; color: ' + INK + '">'
      + str(pct) + suffix + '</span>'
      '<span style="font-size: 15px; font-weight: 400; color: ' + INK3 + '">' + foot + '</span></div></div>')

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
    left = back() if back_btn else ('<div' + hook("Settings") + ' style="width: 44px; height: 44px; border-radius: ' + PILL
      + '; background: ' + FILL + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
      + icon("gear", 22, INK, 1.8) + '</div>')
    ask = ('<div' + hook("ask") + ' class="askpill" style="flex-grow: 1; min-width: 0; height: 48px; border-radius: ' + PILL
      + '; background: ' + FILL + '; display: flex; align-items: center; gap: 9px; padding: 0 14px 0 8px">'
      + mark(32) + '<span style="flex-grow: 1; min-width: 0; font-size: 15px; font-weight: 400; color: ' + INK2
      + '; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">' + placeholder + '</span>'
      # Type, talk, or show. An account number photographed off a wall is the
      # same prompt as one spoken, so the camera belongs in the bar the other
      # two live in, not in a button on one screen.
      + '<div' + hook("Scan") + ' class="camtap" style="width: 22px; height: 22px; display: flex; align-items: center; '
        'justify-content: center; flex-shrink: 0">' + icon("camera", 18, INK2, 1.8) + '</div>'
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

# Five things, in the order they are reached for. Voice first, because saying
# it is the shortest way to do anything here.
ACTIONS_LIST = [("Voice",      "voice",    "black",  "",         "ask"),
                ("Send money", "send",     "blue",   "Pay",      ""),
                ("Receive",    "receive",  "green",  "",         "receive"),
                ("History",    "history",  "purple", "History",  ""),
                ("Settings",   "settings", "amber",  "Settings", "")]

# The page behind the menu goes to milk, not to grey: white at three quarters
# over a hard blur, so the feed is plainly still there and plainly not the
# thing to read. Grey would say the page is disabled. This says it is behind.
MILK = "rgba(255,255,255,0.76)"
BLUR_HARD = "backdrop-filter: blur(26px); -webkit-backdrop-filter: blur(26px)"

def fabsheet():
    """What the black circle opens. A word and a glyph on each line, right
    aligned above the circle, with nothing drawn behind either of them."""
    rows = ''
    for i, (name, ic, col, go, act) in enumerate(ACTIONS_LIST):
        rows += ('<div class="fabrow" data-i="' + str(i) + '"' + hook(go, act)
          + ' style="display: flex; align-items: center; justify-content: flex-end; gap: 20px">'
          '<span style="font-size: 22px; font-weight: 700; letter-spacing: -0.03em; color: ' + INK + '">' + name + '</span>'
          '<div style="width: 52px; height: 52px; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
          + fglyph(ic, 38, IC[col]) + '</div></div>')
    return ('<div class="fabwrap" style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; z-index: 6">'
      '<div class="fabscrim"' + hook("", "actions") + ' style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; background: '
      + MILK + '; ' + BLUR_HARD + '"></div>'
      '<div style="position: absolute; right: 20px; bottom: 100px; display: flex; flex-direction: column; align-items: flex-end; gap: 18px">'
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

def grabber():
    """A sheet that came up from the bottom can go back down the same way, so
    it carries the bar you throw it by. Nothing else on the screen has one."""
    return ('<div style="display: flex; justify-content: center; padding: 2px 0 12px 0">'
      '<div style="width: 44px; height: 5px; border-radius: ' + PILL + '; background: ' + LINE2 + '"></div></div>')

def sheetup(inner, done="Done", go="back", pad="12px 20px 20px 20px"):
    """A screen that came from one place and goes back to it is not a page. It
    is a sheet: a handle at the top to throw it down, and a word at the bottom
    middle to close it. No back arrow, because there is nothing behind it but
    the thing it rose from."""
    tail = ('<div style="display: flex; justify-content: center; padding-top: 18px">'
      '<div' + hook(go) + ' style="height: 50px; padding: 0 40px; border-radius: ' + PILL + '; background: ' + FILL
      + '; display: flex; align-items: center; justify-content: center">'
      '<span style="font-size: 17px; font-weight: 700; letter-spacing: -0.01em; color: ' + INK + '">' + done + '</span></div></div>')
    return sheet(grabber() + inner + tail, pad)

def dial(n, size=48, stroke=5, fs=17, color=None):
    """The score at the size of an icon. The same ring the savings goal uses,
    small enough to ride in a row, because the number belongs where the money is."""
    c = color or ACC
    r = (size - stroke) / 2.0
    circ = 2 * 3.141592653589793 * r
    off = circ * (1 - n / 100.0)
    h = "%g" % (size / 2.0)
    return ('<div style="position: relative; width: ' + str(size) + 'px; height: ' + str(size)
      + 'px; flex-shrink: 0"><svg width="' + str(size) + '" height="' + str(size) + '" viewBox="0 0 ' + str(size)
      + ' ' + str(size) + '">'
      '<circle cx="' + h + '" cy="' + h + '" r="' + ("%g" % r) + '" fill="none" stroke="' + FILL3
      + '" stroke-width="' + str(stroke) + '"/>'
      + '<path d="' + arcpath(size / 2.0, size / 2.0, r, n) + '" fill="none" stroke="' + c
      + '" stroke-width="' + str(stroke) + '" stroke-linecap="round"/></svg>'
      '<div style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; display: flex; align-items: center; justify-content: center">'
      '<span class="num" style="font-size: ' + str(fs) + 'px; font-weight: 800; letter-spacing: -0.03em; color: ' + INK + '">'
      + str(n) + '</span></div></div>')

def healthstrip(n=72, moved="Up 4 since July"):
    """The one figure this product asks you to watch, on home and nowhere else.
    It says nothing in a quiet week. It speaks when it has moved, says by how
    much, and stops."""
    return ('<div' + hook("Health") + ' style="' + cardstyle("14px 16px") + '; display: flex; align-items: center; gap: 14px">'
      + dial(n)
      + '<div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px">'
        '<span style="font-size: 17px; font-weight: 700; letter-spacing: -0.02em; color: ' + INK + '">Money health</span>'
        '<span style="font-size: 14px; font-weight: 400; color: ' + IN_TEXT + '">' + moved + '</span></div>'
      + chevbtn() + '</div>')

def dollarstrip(usd="$412.60", ngn="&#8358;640,300 today"):
    """The second pocket, on home, as one row and nothing more. Naira keeps the
    big figure at the top because that is what nearly every day is spent in.
    Dollars are a thing you hold rather than a thing you spend, so they sit
    where a thing you hold belongs, and a person who never touches them reads
    one extra line for the rest of their life."""
    return ('<div' + hook("Dollars") + ' style="' + cardstyle("14px 16px") + '; display: flex; align-items: center; gap: 14px">'
      '<div style="width: 48px; height: 48px; border-radius: ' + PILL + '; background: ' + BTN
      + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
      '<span class="num" style="font-size: 22px; font-weight: 700; letter-spacing: -0.02em; color: #FFFFFF">$</span></div>'
      + '<div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px">'
        '<span style="font-size: 17px; font-weight: 700; letter-spacing: -0.02em; color: ' + INK + '">Dollars</span>'
        '<span class="num" style="font-size: 14px; font-weight: 400; color: ' + INK3 + '">' + ngn + '</span></div>'
      + '<span class="num" style="font-size: 17px; font-weight: 700; color: ' + INK + '">' + usd + '</span>'
      + chevbtn() + '</div>')

def track(pct, color=None, h=10, bed=None):
    """One filled track. The savings ring is for a thing you are building; this
    is for a thing you are spending, which only runs the one way."""
    return ('<div style="height: ' + str(h) + 'px; border-radius: ' + R_TRACK + '; background: '
      + (bed or FILL3) + '; overflow: hidden">'
      '<div style="width: ' + str(pct) + '%; height: 100%; border-radius: ' + R_TRACK + '; background: '
      + (color or ACC) + '"></div></div>')

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
def tx(name, ic, sub, amount, incoming=False, last=False):
    col = IN_TEXT if incoming else INK
    sign = "+" if incoming else "&#8722;"
    return ('<div' + hook("", "soon") + ' style="display: flex; align-items: center; gap: 14px; height: 70px">'
      + badge(ic, None, 40, R_ICON, 20)
      + '<div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px">'
      '<span style="font-size: 19px; font-weight: 700; letter-spacing: -0.02em">' + name + '</span>'
      '<span style="font-size: 15px; font-weight: 400; color: ' + INK3 + '">' + sub + '</span></div>'
      '<span class="num" style="font-size: 17px; font-weight: 700; color: ' + col + '">' + sign + amount + '</span></div>')

def txgroup(rows):
    """Consecutive money rows sit flush, the way a statement reads."""
    return '<div style="display: flex; flex-direction: column">' + rows + '</div>'

def fchip(t, on=False):
    """A small tap chip. The feed is filtered by these, not by a hidden menu."""
    return ('<div' + hook("", "soon") + ' class="fchip' + (' on' if on else '') + '" style="height: 34px; padding: 0 12px; border-radius: '
      + PILL + '; background: ' + (BTN if on else FILL) + '; display: flex; align-items: center; justify-content: center">'
      '<span style="font-size: 14px; font-weight: 700; color: ' + (BTN_INK if on else INK2) + '; white-space: nowrap">' + t + '</span></div>')

def sortbtn():
    """Sort lives at the right end of the filter row, where a control belongs
    that changes the order rather than the contents."""
    return ('<div' + hook("", "soon") + ' class="sortbtn" style="width: 36px; height: 36px; border-radius: ' + PILL
      + '; background: ' + FILL + '; display: flex; align-items: center; justify-content: center">'
      + icon("sort", 18, INK2, 1.9) + '</div>')

def seeall(go=""):
    """The call to action, on the title line where the eye already is."""
    return ('<div' + hook(go) + ' class="seeall" style="display: flex; align-items: center; gap: 4px">'
      '<span style="font-size: 14px; font-weight: 700; color: ' + ACC_TEXT + '">See all</span>'
      + chev(12, ACC_TEXT_HEX, 2.2) + '</div>')

def daygroup(title, inner):
    """A day of the feed. The grey date, then whatever happened under it."""
    return ('<div style="display: flex; flex-direction: column; gap: 8px">' + sectionhead(title)
      + '<div style="display: flex; flex-direction: column; gap: 12px">' + inner + '</div></div>')

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

# NOT THE HOME SCREEN. The home screen is the founder's, it lives in Figma at
# 193:1566, and every Home screen on the Flows page is an instance of it. This
# is what the walkable prototype starts from, and it is never sent to Figma.
#
# So a row added here appears in the prototype and nowhere anybody looks. When
# something belongs on home it goes into their component too, with
# figma/rowgraft.mjs. The money health row and the dollars row were both added
# here first and reached the real home screen only afterwards.
home_inner = (
  # The whole top block is compact on purpose. The balance was eating the fold
  # and pushing the model's first card off the screen.
  '<div style="font-size: 14px; font-weight: 700; letter-spacing: -0.03em; color: ' + INK + '">Wallet</div>'
  + '<div style="display: flex; flex-direction: column; gap: 4px; padding-top: 16px">'
    + '<div style="display: flex; align-items: center; gap: 8px">' + caption("Total balance") + statpill("+9% this month") + '</div>'
    + '<div id="mBal">' + money("&#8358;248,320", ".75", 36) + '</div></div>'
  + '<div style="padding: 4px 0 8px 0">' + ctabtn("Receive", "", "receive", "down", "black", 44) + '</div>'
  + quickrow([("Airtime", "airtime", "Airtime", IC["blue"]), ("Bills", "power", "Bills", IC["amber"]),
              ("Savings", "pot", "Goal", IC["green"]), ("Services", "grid", "Services", IC["purple"])])
  # One number for how the money is being handled, sitting between what you
  # have and what you did with it. This is the only place it appears and the
  # only place the model volunteers anything, because advice you did not ask
  # for is only tolerable somewhere you can walk past it.
  + dollarstrip()
  + healthstrip(72, "Up 4 since July")
  # The section names itself, says in one line what it holds, and offers the
  # way out. Then the filter and the sort, then the feed itself: what the model
  # noticed and what the money did, in one column, newest first.
  + '<div style="padding-top: 8px; display: flex; flex-direction: column; gap: 6px">'
    + '<div style="display: flex; align-items: center; justify-content: space-between; gap: 8px">'
      + label("Activities") + seeall("History") + '</div>'
    + '<span style="font-size: 14px; font-weight: 400; color: ' + INK3 + '">What I noticed, and every naira that moved.</span>'
  + '</div>'
  + '<div style="display: flex; align-items: center; justify-content: space-between; gap: 8px">'
    + '<div style="display: flex; align-items: center; gap: 6px">'
      + fchip("All", True) + fchip("Insights") + fchip("In") + fchip("Out") + '</div>'
    + sortbtn() + '</div>'
  + '<div style="display: flex; flex-direction: column; gap: 20px">'
    + daygroup("Today",
        LEAD
        + txgroup(tx("Sarah Adeyemi", "send", "Flat deposit &#183; 09:14", "&#8358;50,000")
                + tx("MTN", "data", "5GB for Mum &#183; 08:02", "&#8358;2,500"))
        + aisay("Your data is nearly gone", "Your data usually runs out about now. The same 5GB is &#8358;2,500.",
      '<div style="display: flex; align-items: center; gap: 12px; height: 64px; border-radius: ' + R_INNER + '; background: ' + FILL + '; padding: 0 14px">'
      + badge("data", None, 38, R_ICON, 19, on=FILL)
      + '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 1px">'
        '<span style="font-size: 16px; font-weight: 700; letter-spacing: -0.015em">5GB for 30 days</span>'
        '<span style="font-size: 12px; font-weight: 400; color: ' + INK3 + '">MTN &#183; your line</span></div>'
      '<span class="num" style="font-size: 16px; font-weight: 700">&#8358;2,500</span></div>'
      '<div' + hook("Airtime") + ' style="height: 44px; border-radius: ' + PILL + '; background: ' + FILL
      + '; display: flex; align-items: center; justify-content: center; gap: 6px">'
        '<span style="font-size: 16px; font-weight: 700; color: ' + INK + '">Buy it again</span>' + chev(12, INK, 2.2) + '</div>')
        + tx("Holiday goal", "pot", "Round ups &#183; 07:30", "&#8358;280")
        + aisay("Three changes you made", "They save you &#8358;1,800 every month. The data plan, the DStv package, and the transfer you moved off your card.",
            '<div' + hook("", "soon") + ' style="height: 44px; border-radius: ' + PILL + '; background: ' + FILL
            + '; display: flex; align-items: center; justify-content: center; gap: 6px">'
              '<span style="font-size: 16px; font-weight: 700; color: ' + INK + '">See the three</span>' + chev(12, INK, 2.2) + '</div>'))
    + daygroup("Yesterday",
        promorow("Your card is ready", "Spend online anywhere", "card", "Card")
        + txgroup(tx("Pagrin Limited", "bank", "August salary &#183; 16:40", "&#8358;640,000", True)
                + tx("Ikeja Electric", "power", "Meter 4457 8891 &#183; 11:22", "&#8358;8,000"))
        + aisay("Where your money went", "You spent &#8358;18,900 on airtime and data last month. That is your highest month this year.",
            '<div' + hook("Answer") + ' style="height: 44px; border-radius: ' + PILL + '; background: ' + FILL
            + '; display: flex; align-items: center; justify-content: center; gap: 6px">'
              '<span style="font-size: 16px; font-weight: 700; color: ' + INK + '">Show me what would help</span>' + chev(12, INK, 2.2) + '</div>')
        + tx("Netflix", "card", "Virtual card &#183; 09:00", "&#8358;5,200"))
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
      + listrow("Dollars", "dollar", "$412.60, holding steady", False, "Dollars")
      + listrow("Request money", "request", "Ask someone to pay you")
      + listrow("Send abroad", "globe", "Pounds, dollars and euros", True) + '</div></div>', 15)
services += dockback("Search, or say what you need")
write("Services", services)

def txstate(name, sub, amount, ic, col, go):
    """A row in the list for money that is not simply gone. It wears its state
    where a normal row wears its service, so the list can be read at a glance
    for the ones that still need something from you."""
    return ('<div' + hook(go) + ' style="display: flex; align-items: center; gap: 14px; height: 64px">'
      '<div style="width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
      + fglyph(ic, 26, IC[col]) + '</div>'
      '<div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 1px">'
      '<span style="font-size: 16px; font-weight: 700; letter-spacing: -0.015em; color: ' + INK + '">' + name + '</span>'
      '<span style="font-size: 12px; font-weight: 400; color: ' + INK3 + '">' + sub + '</span></div>'
      '<span class="num" style="font-size: 16px; font-weight: 700; color: ' + INK2 + '">' + amount + '</span>'
      + chevbtn() + '</div>')

def wrongrow(t="Something wrong with this?"):
    """Every receipt needs a door out of it. Without one, the only route a
    person has when a payment reached the wrong place is the call centre."""
    return ('<div' + hook("Wrong") + ' style="display: flex; align-items: center; justify-content: center; gap: 7px; height: 44px">'
      '<span style="font-size: 14px; font-weight: 700; color: ' + ACC_TEXT + '">' + t + '</span>'
      + chev(11, ACC_TEXT_HEX, 2.2) + '</div>')

def offer(text, action, go=""):
    return ('<div style="' + bordered("16px", "24px") + ' display: flex; flex-direction: column; gap: 12px">'
      + aline(text, "17px")
      + '<div' + hook(go, "" if go else "soon") + ' style="height: 46px; border-radius: ' + pill(46)
      + '; background: ' + FILL + '; display: flex; align-items: center; justify-content: center; gap: 7px">'
      '<span style="font-size: 14.5px; font-weight: 700; color: ' + INK + '">' + action + '</span>'
      + chev(12, INK, 2.2) + '</div></div>')

# ---------- a receipt ----------
# A receipt is not a screen that says a payment worked. It is the record a
# person keeps, sends to a landlord, and reads out to a bank when something has
# gone wrong. So it carries what those three uses need and nothing else: who,
# what it cost, what is left, and the number the bank will ask for.
#
# It is laid out as fields, not as rows. A label on the left with its figure
# pushed to the right makes the eye cross a gap for every line it reads; a
# label with its figure directly under it lets the eye go straight down, and
# two or three of those side by side use the width the phone actually has.

def rfield(label, value, sub="", strong=False):
    """One field: a small grey word, and the thing it names underneath."""
    s2 = ('<span style="font-size: 12px; font-weight: 400; color: ' + INK3
          + '; text-wrap: pretty">' + sub + '</span>') if sub else ''
    return ('<div style="flex-grow: 1; flex-basis: 0; min-width: 0; display: flex; flex-direction: column; gap: 4px">'
      '<span style="font-size: 12px; font-weight: 500; color: ' + INK2 + '">' + label + '</span>'
      '<span class="num" style="font-size: 16px; font-weight: ' + ('800' if strong else '700')
      + '; letter-spacing: -0.02em; color: ' + INK + '">' + value + '</span>' + s2 + '</div>')

def rline(*fields):
    """Fields side by side, sharing the width evenly."""
    return ('<div style="display: flex; gap: 16px; align-items: flex-start">' + "".join(fields) + '</div>')

def rnote(t):
    return ('<span style="font-size: 12px; font-weight: 400; color: ' + INK3 + '; text-wrap: pretty">' + t + '</span>')

def rcut():
    """The tear in the paper. It separates who the money went to from what it
    cost, and it is the one place this card is allowed a dashed line."""
    return '<div style="height: 0; border-top: 1px dashed ' + LINE2 + '"></div>'

def rid(k, v):
    """The number the bank asks for when something has gone wrong. It takes a
    line of its own and a way to copy it, which is the only thing anybody has
    ever done with one."""
    return ('<div' + hook("", "copy|" + k) + ' style="display: flex; align-items: center; gap: 16px">'
      '<div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 4px">'
      '<span style="font-size: 12px; font-weight: 500; color: ' + INK2 + '">' + k + '</span>'
      '<span class="num" style="font-size: 14px; font-weight: 700; letter-spacing: -0.01em; color: ' + INK
      + '">' + v + '</span></div>'
      '<div style="width: 32px; height: 32px; border-radius: 999px; background: ' + FILL
      + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
      + icon("copy", 16, INK2, 1.9) + '</div></div>')

def rhero(amount, line, status="Successful"):
    """The figure and the tick on one row, with the word beside them. The word
    matters as much as the tick: a green circle is what an app thinks happened,
    and Successful is what a person can read out."""
    pill = ('<div style="display: flex; align-items: center; gap: 6px; height: 30px; padding: 0 12px; '
      'border-radius: 999px; background: ' + FILL + '; flex-shrink: 0">'
      '<div style="width: 7px; height: 7px; border-radius: 999px; background: ' + IC["green"] + '"></div>'
      '<span style="font-size: 13px; font-weight: 700; color: ' + IN_TEXT + '">' + status + '</span></div>')
    return ('<div style="display: flex; align-items: center; gap: 16px">' + tickmark("", 52)
      + '<div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 4px">'
      + money(amount, "", 38)
      + '<span style="font-size: 15px; font-weight: 500; color: ' + INK2 + '">' + line + '</span></div>'
      + pill + '</div>')

def receipt(blocks):
    """White, held by a hairline, so the record reads as a document laid on the
    page rather than another grey card in the stack. The gap between blocks is
    what does the grouping; the dashed lines only mark the two big joins."""
    return ('<div style="' + bordered("20px", "24px") + ' display: flex; flex-direction: column; gap: 24px">'
      + "".join(blocks) + '</div>')

def offerrow(text, action, go=""):
    """The assistant offering the next thing, on one row. The card version
    costs a hundred pixels, and two stacked blocks that both speak in its voice
    are one block too many."""
    return ('<div style="' + bordered("16px", "20px") + ' display: flex; align-items: center; gap: 12px">'
      + mark(28)
      + '<span style="flex-grow: 1; min-width: 0; font-size: 15px; font-weight: 500; color: ' + INK
      + '; text-wrap: pretty">' + text + '</span>'
      + '<div' + hook(go, "" if go else "soon") + ' style="height: 38px; padding: 0 16px; border-radius: 999px; background: '
      + FILL + '; display: flex; align-items: center; gap: 6px; flex-shrink: 0">'
      '<span style="font-size: 14px; font-weight: 700; color: ' + INK + '">' + action + '</span>'
      + chev(11, INK, 2.2) + '</div></div>')

def sharebtn(go):
    return pillbtn("Share receipt", go, "", "share", "black", True, 56)

def quote(t):
    return ('<div style="display: flex; flex-direction: column; gap: 6px">' + caption("You said")
      + '<span style="font-size: 17px; font-style: italic; font-weight: 500; color: ' + INK2 + '">' + t + '</span></div>')

def plainrow(k, v, last=False, vcolor=INK, chevron=False, vid="", go=""):
    c = chevbtn(22) if chevron else ""
    return ('<div' + (hook(go) if go else '') + ' style="display: flex; align-items: center; height: 56px; gap: 10px">'
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
        "The number you top up most", on=FILL)
    + tinted('<div style="display: flex; align-items: center; gap: 12px">' + icon("data", 21, INK2, 1.6)
        + '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 2px">'
          '<span id="bSize" style="font-size: 15px; font-weight: 600">5GB for 30 days</span>'
          '<span style="font-size: 12.5px; color: ' + INK2 + '">It will not renew on its own</span></div>'
        '<span id="bPrice" class="num" style="font-size: 16px; font-weight: 600">&#8358;2,500</span></div>',
        "The bundle you bought last month", on=FILL)
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
    + '<span class="num chrome" style="font-size: 21px; font-weight: 600; letter-spacing: 0.02em; color: ' + INK + '">4471 8823 0195 6640 3277</span>'
    + '<div' + hook("", "copy") + ' style="display: flex; align-items: center; justify-content: center; gap: 8px; height: 48px; border-radius: ' + PILL + '; background: ' + SURF + '">'
      + icon("copy", 18, INK, 1.8) + '<span style="font-size: 17px; font-weight: 700; color: ' + INK + '">Copy the token</span></div></div>'
  + '<div style="display: flex; flex-direction: column">'
    + plainrow("Meter", "0102 4457 8891", True) + '</div>'
  + offer("Want me to pay this every month?", "Set it up", "Rule")
  + wrongrow("The token did not work?"), 15)
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
  + offer("DStv and Spectranet are not covered. Shall I pay them?", "Set both up", "Rule"), 14) + dockback("Ask about your bills")
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
    """An action on a detail screen. Same rule as quickrow, so no tile."""
    return ('<div' + hook(go, "" if go else action) + ' style="flex-grow: 1; flex-basis: 0; display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 2px 0">'
      + icon(ic, 22, col or INK, 1.9)
      + '<span style="font-size: 12px; font-weight: 400; color: ' + INK + '">' + name + '</span></div>')

vcard = page(
  T("Virtual card", "Made for one merchant, with its own limit")
  + '<div id="cdFace" style="height: 194px; border-radius: ' + R_CARDLG + '; background: ' + CARD_FACE + '; ' + SH_RAISE + '; padding: 20px; display: flex; flex-direction: column; justify-content: space-between; '
    + SHADOW + '">'
    '<div style="display: flex; align-items: flex-start; justify-content: space-between">'
      + mark(24, "#FFFFFF") + '<span class="chrome" style="font-size: 10px; font-weight: 700; letter-spacing: 0.16em; color: rgba(255,255,255,0.7)">NETFLIX ONLY</span></div>'
    '<div style="width: 34px; height: 25px; border-radius: 5px; background: rgba(255,255,255,0.22); border: 1px solid rgba(255,255,255,0.28); display: flex; flex-direction: column; justify-content: center; gap: 3px; padding: 0 5px">'
      '<div style="height: 1.5px; background: rgba(255,255,255,0.45)"></div>'
      '<div style="height: 1.5px; background: rgba(255,255,255,0.45)"></div></div>'
    '<div style="display: flex; flex-direction: column; gap: 16px">'
      '<span id="cdNum" class="num chrome" style="font-size: 20px; font-weight: 500; letter-spacing: 0.12em; color: #FFFFFF">5399 &#8226;&#8226;&#8226;&#8226; &#8226;&#8226;&#8226;&#8226; 4471</span>'
      '<div style="display: flex; align-items: flex-end; justify-content: space-between">'
        '<div style="display: flex; flex-direction: column; gap: 4px">'
          '<span class="chrome" style="font-size: 9px; font-weight: 600; letter-spacing: 0.14em; color: rgba(255,255,255,0.55)">CARD HOLDER</span>'
          '<span class="chrome" style="font-size: 13px; font-weight: 500; letter-spacing: 0.06em; color: #FFFFFF">IBRAHIM WENG</span></div>'
        '<div style="display: flex; flex-direction: column; gap: 4px">'
          '<span class="chrome" style="font-size: 9px; font-weight: 600; letter-spacing: 0.14em; color: rgba(255,255,255,0.55)">EXPIRES</span>'
          '<span class="num" style="font-size: 13px; font-weight: 500; color: #FFFFFF">09/28</span></div>'
        '</div></div></div>'
  + '<div style="' + cardstyle("14px 8px", "20px") + ' display: flex; gap: 4px">' + act("Reveal","search","","reveal") + act("Freeze","freeze","","freeze", IC["cyan"]) + act("Fund","plus","","soon", IC["green"]) + act("Rules","list","Rules", IC["purple"]) + '</div>'
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
    '<div style="font-size: 28px; font-weight: 700; letter-spacing: -0.03em; line-height: 1.24; color: ' + INK + '; text-wrap: pretty">Send 20k to<span style="color: ' + INK3 + '"> Sarah</span></div>'
    + wave()
    + '<div style="display: flex; flex-direction: column; gap: 10px">' + sectionhead("Or try one of these")
      + '<div style="display: flex; flex-direction: column; gap: 8px">'
      + sugg("Pay my light bill", "PowerPay") + sugg("How much did I spend on data?", "Answer") + sugg("What can I borrow?", "Loan") + '</div></div></div>'
  '<div style="padding: 0 20px 24px 20px; display: flex; flex-direction: column; gap: 12px">'
    '<div' + hook("Amend") + ' style="display: flex; justify-content: center">'
      '<span style="font-size: 14px; font-weight: 700; color: ' + ACC_TEXT + '">Not what I said</span></div>'
    '<div style="display: flex; gap: 10px; align-items: center">'
    '<div' + hook("Chat") + ' style="flex-grow: 1; height: 56px; border-radius: ' + PILL + '; background: ' + ACC + '; ' + SH_BTN
    + '; display: flex; align-items: center; justify-content: center">'
    '<span style="font-size: 17px; font-weight: 700; color: #FFFFFF">Release to send</span></div>'
    '<div' + hook("back") + ' style="width: 56px; height: 56px; border-radius: ' + PILL + '; background: ' + FILL
    + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
    '<div style="width: 15px; height: 15px; border-radius: 3px; background: ' + INK2 + '"></div></div></div></div></div>')
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
# The same send, twice. Sarah is paid in naira whichever pocket it leaves from,
# so the screen is the same screen: only the grey block at the bottom changes,
# because that block is the answer to "what is this actually going to do".
#
# From dollars it has to say the rate and it has to say what leaves, on the
# screen before the slide, not after it. A person who finds out the rate on the
# receipt has been told, not asked.

def paypage(fx=False):
    frm = plainrow("From", "Dollars &#183; $412.60" if fx else "Everyday &#183; &#8358;640,300",
                   False, INK, True, "", "PayFrom")
    # What it costs in dollars belongs on the amount, not in a row of its own.
    # The eye is already on the big number, and a rate the person reads there is
    # a rate they were asked about rather than told about afterwards.
    note = ("About $32.07 from your dollars, at &#8358;1,559 to $1"
            if fx else "I took this from your message")
    foot = ("The rate is held for sixty seconds once you slide, and nothing moves until then."
            if fx else "Nothing moves until you slide.")
    return page(
      T("Send money", "To Sarah Adeyemi")
      + quote("send Sarah 50k for the flat deposit")
      + aline("Here it is, ready to go. Check the three parts I filled in.")
      + '<div style="' + cardstyle("14px") + '; display: flex; flex-direction: column; gap: 10px">'
        + tinted(money("&#8358;50,000", "", 40), note, "14px 15px 12px 15px", FILL)
        + tinted('<div style="display: flex; align-items: center; gap: 12px">' + avatar("SA")
            + '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 2px">'
              '<span style="font-size: 15px; font-weight: 600">Sarah Adeyemi</span>'
              '<span class="num" style="font-size: 12.5px; color: ' + INK2 + '">GTBank &#183; 0123 4457 8842</span></div>' + chev() + '</div>',
            "The only Sarah you have paid before", on=FILL)
        + tinted('<div style="display: flex; align-items: center; height: 22px">'
            '<span style="flex-grow: 1; font-size: 13.5px; color: ' + INK2 + '">Reference</span>'
            '<span style="font-size: 15px; font-weight: 500">Flat deposit</span></div>',
            "I took this from your message", on=FILL)
        + '<div style="background: ' + SURF + '; border-radius: ' + R_FIELD + '; overflow: hidden; padding: 0 16px">'
          + frm
          + plainrow("Arrives", "In a few seconds", False, INK, True)
          + plainrow("Fee", "Free", True, IN_TEXT) + '</div></div>'
      + '<div style="display: flex; gap: 9px; align-items: flex-start">' + icon("lock", 16, INK3, 1.6, "; margin-top: 2px")
        + '<span style="font-size: 14.5px; font-weight: 500; line-height: 1.45; color: ' + INK2
        + '; text-wrap: pretty">' + foot + '</span></div>', 15)

pay = paypage()
pay += confirmbar(slide("Slide to send &#8358;50,000", "done|Pay"))
write("Pay", pay, "", True)

paydollars = paypage(True)
paydollars += confirmbar(slide("Slide to send &#8358;50,000", "done|PayDollars"))
write("PayDollars", paydollars, "", True)

# ================= THE SAME SEND, ASKED FOR IN CHAT =================
# The voice sheet hands over to a conversation. What the model is doing is not
# described in a paragraph, it is drawn: a panel belonging to the transfers
# tool fills itself in a line at a time, inside the chat, where it can be
# watched and stopped. It carries its own name and its own edge, because it is
# not the app talking.

def bubble(t, voice=True):
    """What the person said. If it came off the voice sheet it keeps the
    microphone beside it rather than pretending it was typed."""
    lead = ('<div style="opacity: 0.6; display: flex">' + icon("mic", 16, "#FFFFFF", 1.9) + '</div>') if voice else ''
    return ('<div style="display: flex; justify-content: flex-end">'
      '<div style="max-width: 74%; border-radius: 20px; background: ' + BTN
      + '; padding: 12px 16px; display: flex; align-items: center; gap: 8px">' + lead
      + '<span style="font-size: 16px; font-weight: 700; letter-spacing: -0.01em; color: #FFFFFF">' + t + '</span></div></div>')

def stepdot(state):
    """Where a step has got to. Done, running, or not started yet. Drawn with
    plain hexes, because an SVG paints through an attribute and a color-mix()
    never reaches the renderer there."""
    if state == "done":
        return ('<svg width="18" height="18" viewBox="0 0 18 18" fill="none" style="flex-shrink: 0">'
          '<circle cx="9" cy="9" r="9" fill="' + IN + '"/>'
          '<path d="M5.3 9.2 7.9 11.8l4.8-5.2" stroke="#FFFFFF" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    if state == "work":
        return ('<svg width="18" height="18" viewBox="0 0 18 18" fill="none" style="flex-shrink: 0">'
          '<circle cx="9" cy="9" r="7.4" stroke="' + FILL3 + '" stroke-width="2.2"/>'
          '<path d="M9 1.6a7.4 7.4 0 0 1 7.4 7.4" stroke="' + ACC_TEXT_HEX + '" stroke-width="2.2" stroke-linecap="round"/></svg>')
    return ('<svg width="18" height="18" viewBox="0 0 18 18" fill="none" style="flex-shrink: 0">'
      '<circle cx="9" cy="9" r="7.4" stroke="' + FILL3 + '" stroke-width="2.2"/></svg>')

def toolrow(state, k, v, vcolor=INK, first=False, num=False, go=""):
    """A field the model filled in. Give it a `go` and the value becomes the
    way to change it, because a number that was misheard is corrected with a
    keypad and not by arguing with a chat."""
    edge = '' if first else 'border-top: 1px solid ' + LINE + '; '
    cls = ' class="num"' if num else ''
    tail = ('<div' + hook(go) + ' style="flex-grow: 1; display: flex; align-items: center; justify-content: flex-end; gap: 5px">'
            + '<span' + cls + ' style="font-size: 14px; font-weight: 700; color: ' + vcolor + '">' + v + '</span>'
            + chev(11, INK3, 2.2) + '</div>') if go else (
            '<span' + cls + ' style="flex-grow: 1; text-align: right; font-size: 14px; font-weight: 700; color: ' + vcolor + '">' + v + '</span>')
    return ('<div style="' + edge + 'display: flex; align-items: center; gap: 12px; height: 44px">' + stepdot(state)
      + '<span style="font-size: 14px; font-weight: 400; color: ' + INK2 + '">' + k + '</span>' + tail + '</div>')

def toolpanel(name, status, rows, cta="", go=""):
    """The tool's own surface, running inside the chat."""
    head = ('<div style="height: 48px; background: ' + FILL + '; border-bottom: 1px solid ' + LINE
      + '; display: flex; align-items: center; gap: 10px; padding: 0 14px">' + badge("send", None, 26, "10px", 15, on=FILL)
      + '<span style="flex-grow: 1; font-size: 14px; font-weight: 700; letter-spacing: -0.01em; color: ' + INK + '">' + name + '</span>'
      '<div style="display: flex; align-items: center; gap: 6px; height: 24px; padding: 0 10px; border-radius: ' + PILL
      + '; background: ' + SURF + '">'
      '<div style="width: 6px; height: 6px; border-radius: ' + PILL + '; background: ' + ACC + '"></div>'
      '<span style="font-size: 12px; font-weight: 700; color: ' + INK2 + '">' + status + '</span></div></div>')
    body = '<div style="padding: 4px 14px 12px 14px; display: flex; flex-direction: column">' + rows + '</div>'
    foot = ('<div style="padding: 0 14px 14px 14px">' + pillbtn(cta, go, "", "", "black", True, 52) + '</div>') if cta else ''
    return ('<div class="mcp" style="background: ' + SURF + '; ' + CARD_EDGE + '; border-radius: ' + R_CARD
      + '; overflow: hidden">' + head + body + foot + '</div>')

def chathead(title="Leorio"):
    """Back goes to the top here. A conversation has no page title to centre,
    so the model's own badge names the screen instead."""
    return ('<div style="display: flex; align-items: center; gap: 10px; height: 44px">' + back()
      + '<div style="flex-grow: 1; display: flex; align-items: center; justify-content: center; gap: 8px">' + mark(24)
      + '<span style="font-size: 16px; font-weight: 700; letter-spacing: -0.015em; color: ' + INK + '">' + title + '</span></div>'
      '<div style="width: 44px; flex-shrink: 0"></div></div>')

def chatbar(placeholder="Reply, or just keep talking", height=104):
    """The composer. The same bar as everywhere else, minus the left button,
    because back has moved to the top."""
    ask = ('<div' + hook("", "soon") + ' class="askpill" style="flex-grow: 1; min-width: 0; height: 48px; border-radius: ' + PILL
      + '; background: ' + FILL + '; display: flex; align-items: center; gap: 9px; padding: 0 14px 0 8px">' + mark(32)
      + '<span style="flex-grow: 1; min-width: 0; font-size: 15px; font-weight: 400; color: ' + INK2
      + '; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">' + placeholder + '</span>'
      + '<div' + hook("Scan") + ' class="camtap" style="width: 22px; height: 22px; display: flex; align-items: center; '
        'justify-content: center; flex-shrink: 0">' + icon("camera", 18, INK2, 1.8) + '</div>'
      + icon("mic", 18, INK2, 1.8) + '</div>')
    send = ('<div' + hook("", "soon") + ' class="fab" style="width: 56px; height: 56px; border-radius: ' + PILL
      + '; background: ' + BTN + '; ' + SH_FAB + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
      + icon("up", 24, "#FFFFFF", 2.4) + '</div>')
    return ('<div class="dock" style="position: absolute; left: 0; right: 0; bottom: 0; z-index: 3; height: ' + str(height)
      + 'px; background: linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.9) 34%, ' + BG
      + ' 62%); display: flex; align-items: flex-end; padding: 0 18px 26px 18px">'
      '<div style="display: flex; width: 100%; gap: 10px; align-items: center">' + ask + send + '</div></div>')

def chatscreen(said, reply, panel, foot, footic="lock", voice=True):
    """A conversation that is doing something. The tool runs in the middle of
    it, and the line the person sent sits above. `voice` is what decides
    whether that line keeps its microphone: the same chat is reached by
    speaking and by typing, and only one of those is true at a time."""
    c = page(chathead("Leorio") + bubble(said, voice) + aline(reply, "16px") + panel
      + '<div style="display: flex; gap: 9px; align-items: flex-start">' + icon(footic, 16, INK3, 1.6, "; margin-top: 2px")
        + '<span style="font-size: 14px; font-weight: 400; line-height: 1.45; color: ' + INK2
        + '; text-wrap: pretty">' + foot + '</span></div>', 16)
    return c + chatbar("Reply, or just keep talking")

def transferchat(voice=True):
    return chatscreen("Send 20k to Sarah",
      "Sarah Adeyemi at GTBank, the same account the flat deposit went to. I am putting it together now.",
      toolpanel("Leorio Transfers", "Running",
        toolrow("done", "Recipient", "Sarah Adeyemi", INK, True)
        + toolrow("done", "Bank", "GTBank &#183; 0123 4457 8842", INK, False, True)
        + toolrow("done", "Amount", "&#8358;20,000", INK, False, True, "Amend")
        + toolrow("done", "Fee", "Free", IN_TEXT)
        + toolrow("work", "Arrives", "Checking with GTBank", INK3),
        "Confirm &#8358;20,000", "Confirm"),
      "Face ID first. Nothing leaves your account until then.", "lock", voice)

write("Chat", transferchat(True))
write("ChatTyped", transferchat(False))

# ================= CONFIRMING IT, FACE FIRST =================
# Face ID is tried the moment this opens. The keypad is what you see when it
# does not catch you, which is why the face keeps the corner of the pad it has
# on a phone rather than becoming a screen of its own.

def pindots(filled=2, total=4):
    ds = ''
    for i in range(total):
        on = i < filled
        ds += ('<div class="pindot" data-on="' + ("1" if on else "0") + '" style="width: 14px; height: 14px; border-radius: '
          + PILL + '; background: ' + (INK if on else "transparent")
          + ('' if on else '; border: 1.5px solid ' + LINE2) + '"></div>')
    return '<div style="display: flex; justify-content: center; gap: 20px">' + ds + '</div>'

def pinkey(t="", glyph="", act=""):
    """One key. A digit sits in a filled circle and the two helpers do not,
    the way a phone draws them."""
    if glyph:
        return ('<div' + hook("", act) + ' class="pinkey" style="width: 76px; height: 76px; border-radius: ' + PILL
          + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">' + glyph + '</div>')
    return ('<div' + hook("", "pin|" + t) + ' class="pinkey" style="width: 76px; height: 76px; border-radius: ' + PILL
      + '; background: ' + FILL + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
      '<span class="num" style="font-size: 26px; font-weight: 700; letter-spacing: -0.02em; color: ' + INK + '">' + t + '</span></div>')

def pinpad():
    out = ''
    for r in (["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]):
        out += '<div style="display: flex; gap: 24px; justify-content: center">' + "".join(pinkey(k) for k in r) + '</div>'
    out += ('<div style="display: flex; gap: 24px; justify-content: center">'
      + pinkey("", icon("faceid", 34, ACC_TEXT_HEX, 1.7), "faceid") + pinkey("0")
      + pinkey("", icon("del", 28, INK2, 1.8), "pin|del") + '</div>')
    return '<div style="display: flex; flex-direction: column; gap: 16px">' + out + '</div>'

def confirmscreen(amount, initials, name, sub, tone=None, foot="Nothing moves until the fourth number lands.",
                  missed=False):
    """One gate for every naira that leaves. A slide says you meant it; a face
    says it is you, and only one of those is worth anything if the phone is not
    yours.

    The passcode is the gate and Face ID is the shortcut, so the keypad is what
    the screen rests on and the face keeps the corner it has on a phone. It used
    to say Face ID had not caught you, which put an error in front of four
    flows that were going perfectly well. `missed` is that state now, and it
    lives on one screen of its own."""
    lead = (avatar(initials, 40) if len(initials) <= 2
            else badge(initials, None, 40, R_ICON, 20))
    return page(
      topbar("Confirm")
      + '<div style="display: flex; flex-direction: column; align-items: center; gap: 12px">'
        + money(amount, "", 36)
        + '<div style="display: flex; align-items: center; gap: 12px">' + lead
          + '<div style="display: flex; flex-direction: column; gap: 2px">'
          '<span style="font-size: 16px; font-weight: 700; letter-spacing: -0.02em; color: ' + INK + '">' + name + '</span>'
          '<span class="num" style="font-size: 12px; font-weight: 400; color: ' + INK3 + '">' + sub + '</span>'
          '</div></div></div>'
      + '<div style="display: flex; flex-direction: column; align-items: center; gap: 6px">'
        '<span style="font-size: 22px; font-weight: 700; letter-spacing: -0.03em; color: ' + INK + '">Enter your passcode</span>'
        + ('<span style="font-size: 14px; font-weight: 400; color: ' + WARN_TEXT
           + '">Face ID did not catch you. Tap the face to try again.</span>' if missed else
           '<span style="font-size: 14px; font-weight: 400; color: ' + INK3
           + '">Or tap the face to use Face ID.</span>') + '</div>'
      + pindots(2)
      + pinpad()
      + '<div style="display: flex; gap: 9px; align-items: center; justify-content: center">' + icon("lock", 16, INK3, 1.6)
        + '<span style="font-size: 14px; font-weight: 400; color: ' + INK2 + '">' + foot + '</span></div>', 24)

write("Confirm", confirmscreen("&#8358;20,000", "SA", "Sarah Adeyemi", "GTBank &#183; 0123 4457 8842"))
write("NoFace", confirmscreen("&#8358;20,000", "SA", "Sarah Adeyemi", "GTBank &#183; 0123 4457 8842", None,
  "Three wrong tries locks the passcode for an hour.", True))

# ================= SENDING FROM A PICTURE =================
# An account number does not usually arrive as something you type. It arrives
# as a screenshot somebody sent you, a slip photographed off a counter, or a
# flyer with three banks on it. So the model is shown the picture and reads it
# back before anything moves, marking what it read and what it could not.

def shotline(t, size=12):
    return '<span style="font-size: ' + str(size) + 'px; font-weight: 400; color: ' + INK2 + '">' + t + '</span>'

def readline(t, ok=True, num=False, tag=""):
    """A run of words lifted out of the picture, boxed where it sits. A solid
    blue edge is what the model read. A broken red one is what it could not,
    and that difference is the whole safety of this flow."""
    cls = ' class="num"' if num else ''
    t8 = ('<span style="font-size: 12px; font-weight: 400; color: ' + (ACC_TEXT if ok else WARN_TEXT)
          + '; margin-left: 8px">' + tag + '</span>') if tag else ''
    return ('<div style="align-self: flex-start; display: flex; align-items: center; border-radius: 10px; '
      'padding: 2px 8px; border: 1.5px ' + ('solid ' + ACC_EDGE if ok else 'dashed ' + WARN_EDGE)
      + '; background: ' + (ACC_SOFT if ok else WARN_SOFT) + '">'
      '<span' + cls + ' style="font-size: 12px; font-weight: 700; color: ' + INK + '">' + t + '</span>' + t8 + '</div>')

def swatch(ok, t):
    return ('<div style="display: flex; align-items: center; gap: 6px">'
      '<div style="width: 14px; height: 14px; border-radius: 4px; border: 1.5px '
      + ('solid ' + ACC_EDGE if ok else 'dashed ' + WARN_EDGE) + '; background: '
      + (ACC_SOFT if ok else WARN_SOFT) + '"></div>'
      '<span style="font-size: 12px; font-weight: 400; color: ' + INK2 + '">' + t + '</span></div>')

def legend(unsure=True):
    """Only claim an uncertainty when there is one. A key that lists a state
    the picture does not contain teaches the wrong thing."""
    return ('<div style="display: flex; gap: 20px; padding-left: 2px">' + swatch(True, "What I read")
      + (swatch(False, "What I am unsure of") if unsure else '') + '</div>')

def sender(initials, name, when, color):
    return ('<div style="display: flex; align-items: center; gap: 8px">'
      '<div style="width: 24px; height: 24px; border-radius: ' + PILL + '; background: ' + color
      + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
      '<span style="font-size: 12px; font-weight: 700; color: #FFFFFF">' + initials + '</span></div>'
      '<span style="flex-grow: 1; font-size: 12px; font-weight: 700; color: ' + INK + '">' + name + '</span>'
      '<span style="font-size: 12px; font-weight: 400; color: ' + INK3 + '">' + when + '</span></div>')

def photo(kind="one", legend_in=True):
    """A stand in for the picture itself, kept in the design so the read back
    can be checked against the thing it was read from."""
    if kind == "one":
        body = (shotline("Good afternoon sir. Rent part payment:")
          + readline("&#8358;20,000", True, True)
          + readline("GTBank", True)
          + readline("0123 4457 8842", True, True)
          + readline("Sarah A.", False, False, "not sure"))
        head = sender("MA", "Musa &#183; Agent", "2:14 PM", IC["green"])
    else:
        body = (shotline("ACME PROPERTIES &#183; Rent 2026")
          + readline("1 &#183; GTBank 0123 4457 8842", True, True)
          + readline("2 &#183; Zenith 2087 6612 04", True, True)
          + readline("3 &#183; Access 0691 3345 71", True, True)
          + shotline("Part payment due &#8358;20,000"))
        head = sender("AP", "Invoice photo", "2:14 PM", IC["orange"])
    if kind == "meter":
        body = (shotline("IKEJA ELECTRIC &#183; Prepaid")
          + readline("Meter 4457 8891", True, True)
          + readline("&#8358;8,000", True, True)
          + readline("14 Bode Thomas", True)
          + shotline("Keep this slip for your records"))
        head = sender("IE", "Bill photo", "4:02 PM", IC["amber"])
    lg = ('<div style="padding-top: 4px">' + legend(kind == "one") + '</div>') if legend_in else ''
    # nothing on a bill is guessed at, so its key does not claim otherwise
    return ('<div style="' + cardstyle("12px", "20px", FILL) + ' display: flex; flex-direction: column; gap: 8px">'
      + head + '<div style="' + cardstyle("12px", "14px", SURF)
      + ' display: flex; flex-direction: column; gap: 6px; align-items: flex-start">' + body + '</div>' + lg + '</div>')

# ---------- the viewfinder ----------
SCAN_BG = "linear-gradient(180deg, #16161A 0%, #0C0C0E 44%, #08080A 100%)"
GLASS   = "rgba(255,255,255,0.14)"

def roundbtn(ic, go="", act="", size=44, isz=20):
    return ('<div' + hook(go, act) + ' style="width: ' + str(size) + 'px; height: ' + str(size) + 'px; border-radius: '
      + PILL + '; background: ' + GLASS + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
      + icon(ic, isz, "#FFFFFF", 1.9) + '</div>')

scan = ('<div style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; background: ' + SCAN_BG
  + '; display: flex; flex-direction: column; gap: 20px; padding: 60px 20px 32px 20px">'
  '<div style="display: flex; align-items: center; height: 44px">'
    + roundbtn("close", "back") + '<div style="flex-grow: 1"></div>' + roundbtn("power", "", "soon") + '</div>'
  '<div style="display: flex; flex-direction: column; align-items: center; gap: 6px">'
    '<span style="font-size: 16px; font-weight: 700; color: #FFFFFF">Point at an account number</span>'
    '<span style="font-size: 14px; font-weight: 400; color: rgba(255,255,255,0.62)">A QR code works too. So does a screenshot.</span></div>'
  '<div style="flex-grow: 1; display: flex; flex-direction: column; justify-content: flex-start; gap: 16px; padding-top: 8px">'
    '<div style="border: 2px solid rgba(255,255,255,0.34); border-radius: 24px; padding: 14px">'
      + photo("one", False) + '</div>'
    '<div style="align-self: center; display: flex; align-items: center; gap: 8px; height: 36px; padding: 0 14px; '
      'border-radius: ' + PILL + '; background: ' + GLASS + '">' + stepdot("done")
      + '<span class="num" style="font-size: 14px; font-weight: 700; color: #FFFFFF">0123 4457 8842</span></div></div>'
  '<div style="display: flex; align-items: center; height: 72px">'
    # The last screenshot in the roll, because the commonest case is not a
    # thing in front of you, it is a thing somebody already sent you.
    + '<div' + hook("Found") + ' style="width: 52px; height: 52px; border-radius: 14px; overflow: hidden; background: '
      + SURF + '; display: flex; flex-direction: column; gap: 4px; padding: 8px; flex-shrink: 0">'
      '<div style="display: flex; align-items: center; gap: 4px">'
        '<div style="width: 10px; height: 10px; border-radius: ' + PILL + '; background: ' + IC["green"] + '"></div>'
        '<div style="flex-grow: 1; height: 4px; border-radius: 4px; background: ' + LINE2 + '"></div></div>'
      '<div style="height: 4px; border-radius: 4px; background: ' + INK4 + '"></div>'
      '<div style="height: 4px; border-radius: 4px; background: ' + INK4 + '"></div>'
      '<div style="height: 4px; width: 62%; border-radius: 4px; background: ' + LINE2 + '"></div></div>'
    + '<div style="flex-grow: 1; display: flex; justify-content: center">'
      '<div' + hook("Found") + ' style="width: 72px; height: 72px; border-radius: ' + PILL
      + '; border: 4px solid #FFFFFF; display: flex; align-items: center; justify-content: center">'
      '<div style="width: 56px; height: 56px; border-radius: ' + PILL + '; background: #FFFFFF"></div></div></div>'
    + roundbtn("qr", "Pick", "", 52, 22) + '</div>'
  '<span style="text-align: center; font-size: 12px; font-weight: 400; color: rgba(255,255,255,0.5)">'
    'Or send a screenshot straight to Leorio from WhatsApp.</span></div>')
write("Scan", scan)

# ---------- three accounts on one piece of paper ----------
def acctrow(bank, num, who, color=None, last=False):
    """Three accounts a photograph turned up. They were told apart by three
    colours; they are told apart by the number, which is the thing being
    checked, and the colours were only ever decorating the check."""
    return ('<div' + hook("Found") + ' style="display: flex; align-items: center; gap: 14px; height: 72px'
      + ('' if last else '; border-bottom: 1px solid ' + LINE) + '">' + badge("bank", None, 44, R_ICON, 22)
      + '<div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px">'
      '<span class="num" style="font-size: 16px; font-weight: 700; letter-spacing: -0.02em; color: ' + INK + '">' + num + '</span>'
      '<span style="font-size: 14px; font-weight: 400; color: ' + INK3 + '">' + bank + ' &#183; ' + who + '</span></div>'
      + chevbtn() + '</div>')

pick = page(
  T("Three accounts here", "I read them all and asked each bank who it belongs to")
  + photo("many")
  + '<div style="' + cardstyle("0 16px", R_CARD) + '">'
    + acctrow("GTBank", "0123 4457 8842", "SARAH ADEYEMI", IC["orange"])
    + acctrow("Zenith", "2087 6612 04", "ACME PROPERTIES LTD", IC["red"])
    + acctrow("Access", "0691 3345 71", "M. IBRAHIM", IC["blue"], True) + '</div>'
  + aline("The invoice is from Acme, so the middle one is most likely who you owe. Tap whichever you meant.", "16px"), 16)
pick += dockback("Ask about this photo")
write("Pick", pick)

# ---------- what the model read, and the one question it must ask ----------
def nrow(k, v, warn=False):
    return ('<div style="display: flex; align-items: center; gap: 12px; height: 28px">'
      '<span style="font-size: 14px; font-weight: 400; color: ' + INK2 + '">' + k + '</span>'
      '<span style="flex-grow: 1; text-align: right; font-size: 14px; font-weight: 700; color: '
      + (WARN_TEXT if warn else INK) + '">' + v + '</span></div>')

def namecheck():
    """The only place this flow stops you. Two names that are not the same is
    the one thing a photograph cannot settle, so it is put to the person
    rather than decided for them."""
    return ('<div style="' + bordered("16px", "24px") + ' display: flex; flex-direction: column; gap: 12px">'
      '<div style="display: flex; align-items: center; gap: 8px">' + icon("alert", 18, WARN_TEXT, 2.0)
      + '<span style="font-size: 16px; font-weight: 700; letter-spacing: -0.02em; color: ' + INK
      + '">Is this the person you mean?</span></div>'
      + '<div style="' + cardstyle("8px 14px", "16px") + ' display: flex; flex-direction: column">'
        + nrow("On the photo", "Sarah A.", True) + nrow("At GTBank", "SARAH ADEYEMI") + '</div>'
      '<div style="display: flex; gap: 8px">'
        '<div' + hook("", "sure") + ' class="pbtn" style="flex-grow: 1; height: 48px; border-radius: ' + PILL
        + '; background: ' + BTN + '; ' + SH_BTN + '; display: flex; align-items: center; justify-content: center">'
        '<span style="font-size: 16px; font-weight: 700; color: #FFFFFF">Yes, that is them</span></div>'
        '<div' + hook("back") + ' class="pbtn" style="height: 48px; padding: 0 20px; border-radius: ' + PILL
        + '; background: ' + FILL + '; display: flex; align-items: center; justify-content: center">'
        '<span style="font-size: 16px; font-weight: 700; color: ' + INK + '">No</span></div></div></div>')

def foundrow(k, v, num=False, last=False, tag=""):
    t8 = ('<span style="font-size: 12px; font-weight: 400; color: ' + INK3 + '; margin-left: 8px">' + tag + '</span>') if tag else ''
    return ('<div style="display: flex; align-items: center; gap: 12px; height: 48px'
      + ('' if last else '; border-bottom: 1px solid ' + LINE) + '">' + stepdot("done")
      + '<span style="font-size: 14px; font-weight: 400; color: ' + INK2 + '">' + k + '</span>'
      + '<div style="flex-grow: 1; display: flex; align-items: center; justify-content: flex-end">'
      '<span' + (' class="num"' if num else '') + ' style="font-size: 16px; font-weight: 700; color: ' + INK + '">' + v + '</span>'
      + t8 + '</div></div>')

found = page(
  T("What I found", "Read from your photo, 2:14 PM")
  + photo("one")
  + namecheck()
  # The amount leads, because it is the number that costs you if it is wrong.
  + '<div style="' + cardstyle("0 16px", R_CARD) + '">'
    + foundrow("Amount", "&#8358;20,000", True, False, "from the photo")
    + foundrow("Account", "0123 4457 8842", True)
    + foundrow("Bank", "GTBank", False, True) + '</div>', 12)
found += confirmbar(pillbtn("Continue", "", "fnwait", "", "grey", True, 56, "fnGo"))
write("Found", found)

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

TIGHT = ('<div style="' + bordered("16px", "24px") + ' display: flex; flex-direction: column; gap: 12px">'
  '<div style="display: flex; align-items: flex-start; gap: 14px">'
  '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 6px">'
  '<span style="font-size: 16px; font-weight: 700; letter-spacing: -0.015em; color: ' + INK + '">Money is tight this month</span>'
  '<span style="font-size: 14px; font-weight: 400; line-height: 1.45; color: ' + INK2 + '; text-wrap: pretty">'
  'Turn this on and I stop moving money into savings, and I stop asking you to. '
  'Your goals wait where they are. Nothing is lost and nothing is charged.</span></div>'
  + switch(False, "tight") + '</div>'
  '<div style="display: flex; align-items: center; height: 32px; border-top: 1px solid ' + LINE + '; padding-top: 6px">'
  '<span style="flex-grow: 1; font-size: 12px; font-weight: 400; color: ' + INK3 + '">'
  'You can also just tell me, any time.</span></div></div>')

rules = page(
  T("Standing instructions", "What I can do without asking you first")
  + TIGHT
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
        "The meter you paid last month", on=FILL)
    + tinted('<div style="display: flex; align-items: baseline; gap: 1px">'
        '<span id="pwAmt" class="num" style="font-size: 36px; font-weight: 600; letter-spacing: -0.035em; line-height: 1; color: ' + INK + '">&#8358;8,000</span></div>',
        "About what you used last month", "14px 15px 12px 15px", FILL)
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

# ================= DONE, THE RECEIPT FOR A PURCHASE =================
done = page(
  T("All done", "28 August 2026 at 2:19 PM")
  + rhero("&#8358;2,500", "5GB sent to Mum")
  + '<div id="dnCard">' + receipt([
      rline(rfield("To", "Mum", "0803 214 4471 &#183; MTN"),
            rfield("From", "Everyday", "0102 4457 88")),
      rline(rfield("What", "5GB for 30 days", "Valid until 27 September")),
      rcut(),
      rline(rfield("Amount", "&#8358;2,500.00"), rfield("Fee", "Free")),
      rline(rfield("Total charged", "&#8358;2,500.00", "", True),
            rfield("Balance after", "&#8358;637,800.00")),
      rcut(),
      rid("MTN reference", "MTN 88231 4471 0392")]) + '</div>'
  + sharebtn("ShareBuy")
  + '<div id="dnOffer">' + offerrow("Mum has it. Every month, without asking?", "Set it up", "Rule") + '</div>'
  + wrongrow(), 20)
done += dockback("Ask about this")
write("Done", done)

# ================= A GOAL =================
def feeder(name, ic, sub, amount, last=False, off=False):
    """A thing putting money into the goal. When the month is tight it is drawn
    stopped rather than removed, because the person has not given it up."""
    return ('<div style="display: flex; align-items: center; gap: 14px; height: 68px' + ('; opacity: 0.5' if off else '') + '">'
      + badge(ic, None, 40, R_ICON, 20)
      + '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 2px">'
      '<span style="font-size: 19px; font-weight: 700; letter-spacing: -0.02em">' + name + '</span>'
      '<span style="font-size: 15px; font-weight: 400; color: ' + INK3 + '">' + sub + '</span></div>'
      '<span class="num" style="font-size: 17px; font-weight: 700; color: ' + (INK3 if off else ACC_TEXT) + '">' + amount + '</span></div>')

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
    '<div' + hook("SaveRule") + ' style="flex-grow: 1; height: 52px; border-radius: ' + PILL + '; background: ' + FILL
    + '; display: flex; align-items: center; justify-content: center; font-size: 15px; font-weight: 700; color: ' + INK + '">Feed it more</div></div>'
  + '<div style="display: flex; gap: 10px; align-items: flex-start">' + icon("lock", 16, INK3, 1.8, "; margin-top: 2px")
    + '<span style="font-size: 14px; font-weight: 500; line-height: 1.45; color: ' + INK3
    + '; text-wrap: pretty">Nothing here is locked. Take it back whenever you need it.</span></div>'
  # The question everybody actually has about a savings plan, answered on the
  # screen where it occurs to them rather than buried in a help page.
  + '<div' + hook("Paused") + ' style="display: flex; align-items: center; justify-content: center; gap: 6px; height: 40px">'
    '<span style="font-size: 14px; font-weight: 700; color: ' + ACC_TEXT + '">What happens if money gets tight?</span>'
    + chev(11, ACC_TEXT_HEX, 2.2) + '</div>', 20)
goal += dockback("Ask about this goal")
write("Goal", goal)

# ================= THE SAME GOAL, WITH THE MONTH DECLARED TIGHT =================
# The one place the product shows the model behaving differently for one person
# than for another. Nothing is deleted, nothing is charged, and the cost of the
# pause is stated plainly instead of being hidden or scolded about.
paused = page(
  T("Holiday", "Paused while things are tight")
  + '<div style="' + cardstyle("20px") + '; display: flex; flex-direction: column; align-items: center; gap: 16px">'
    + ring(33)
    + '<div style="display: flex; flex-direction: column; align-items: center; gap: 4px">'
      + '<div style="display: flex; align-items: baseline; gap: 1px">'
        '<span class="num" style="font-size: 30px; font-weight: 700; letter-spacing: -0.04em; color: ' + INK + '">&#8358;82,400</span></div>'
      + '<span class="num" style="font-size: 15px; font-weight: 500; color: ' + INK3 + '">of &#8358;250,000, holding steady</span></div></div>'
  + aline("You told me money is tight, so I have stopped moving it. Your date moves from 12 March to 9 April. "
          "Nothing has been taken and nothing has been charged.", "16px")
  + '<div style="display: flex; flex-direction: column; gap: 12px">' + label("Waiting for you")
    + '<div style="display: flex; flex-direction: column">'
      + feeder("Payday transfer", "pot", "Paused since 3 August", "Paused", False, True)
      + feeder("Round ups", "swap", "Paused since 3 August", "Paused", False, True)
      + feeder("Money back on top ups", "airtime", "Still going in", "&#8358;120", True) + '</div></div>'
  + '<div style="display: flex; gap: 10px">'
    '<div' + hook("", "soon") + ' style="flex-grow: 1; height: 52px; border-radius: ' + PILL + '; background: ' + FILL
    + '; display: flex; align-items: center; justify-content: center; font-size: 15px; font-weight: 700; color: ' + INK + '">Add money anyway</div>'
    '<div' + hook("Goal") + ' style="flex-grow: 1; height: 52px; border-radius: ' + PILL + '; background: ' + BTN + '; ' + SH_BTN
    + '; display: flex; align-items: center; justify-content: center; font-size: 15px; font-weight: 700; color: ' + BTN_INK + '">Start again</div></div>'
  + '<div style="display: flex; gap: 10px; align-items: flex-start">' + icon("lock", 16, INK3, 1.8, "; margin-top: 2px")
    + '<span style="font-size: 14px; font-weight: 500; line-height: 1.45; color: ' + INK3
    + '; text-wrap: pretty">I will not ask you about this again until you tell me to.</span></div>', 20)
paused += dockback("Ask about this goal")
write("Paused", paused)


# ================= SETTINGS =================
# A settings list where every row looks the same is a list nobody reads, so
# each row says where it stands without being opened, and the five that decide
# whether the money stays yours are the ones at the top.
# The action menu draws its five as shapes standing on nothing, each in its
# own colour, and settings follows it. This is the one list in the product
# where colour is doing work rather than decorating: a settings list is read
# by hunting, not by reading top to bottom, and a colour is found faster than
# a word. Everywhere else a list is read in order, which is why everywhere
# else the glyph is black.
SET_TONE = {"faceid": "blue", "shield": "green", "list": "purple", "laptop": "amber",
            "key": "cyan", "person": "blue", "bell": "amber", "gift": "pink",
            "card": "purple", "chat": "green", "star": "amber", "clock": "cyan",
            "eye": "blue", "camera": "purple", "lock": "red"}

def rowglyph(ic, color=None, on=BG, size=26, cell=36):
    """A settings row's mark. A shape, not a line drawing, and standing on
    nothing rather than inside a tile. Anything knocked out of it is knocked
    out in the colour of the ground it is on, so the same drawing works on the
    page and on a grey card."""
    c = color or IC[SET_TONE.get(ic, "black")]
    return ('<div style="width: ' + str(cell) + 'px; height: ' + str(cell) + 'px; display: flex; '
      'align-items: center; justify-content: center; flex-shrink: 0">'
      + fglyph(ic, size, c, FILL if on == FILL else SURF) + '</div>')

def setrow(name, ic, go="", act="soon", color=None, last=False, val="", tail=None, on=BG):
    right = tail if tail is not None else (
      ('<span class="num" style="font-size: 15px; font-weight: 500; color: ' + INK3 + '">' + val + '</span>' if val else '')
      + chevbtn())
    return ('<div' + hook(go, "" if go else act) + ' style="display: flex; align-items: center; gap: 12px; height: 64px">'
      + rowglyph(ic, color, on)
      + '<span style="flex-grow: 1; min-width: 0; font-size: 19px; font-weight: 700; letter-spacing: -0.02em; color: ' + INK + '">' + name + '</span>'
      + right + '</div>')

def setgroup(title, rows):
    return ('<div style="display: flex; flex-direction: column; gap: 4px">' + sectionhead(title)
      + '<div style="display: flex; flex-direction: column">' + rows + '</div></div>')

settings = page(
  '<div style="font-size: 28px; font-weight: 700; letter-spacing: -0.035em; color: ' + INK + '">Settings</div>'
  + '<div style="padding-top: 16px">'
  + promorow("Get Leorio Plus", "No transfer fees and instant settlement", "star", "", "soon") + '</div>'
  # The five that matter, named for what they do rather than for what they are.
  + setgroup("What keeps the money yours",
             setrow("Lock and privacy", "faceid", "Lock", "", None, False, "Face ID")
             + setrow("Spending limits", "shield", "Limits", "", None, False, "&#8358;100,000 a day")
             + setrow("Standing instructions", "list", "Rules", "", None, False, "3 running")
             + setrow("Devices", "laptop", "Devices", "", None, False, "3 signed in")
             + setrow("Keys and recovery", "key", "", "soon", None, False, "Set up"))
  + setgroup("Your account", setrow("Your details", "person") + setrow("Notifications", "bell")
             + setrow("Saved people", "gift") + setrow("Cards", "card", "Card", "", None, False, "1 virtual"))
  + setgroup("About", setrow("Contact support", "chat") + setrow("Give feedback", "star")
             + '<div' + hook("", "soon") + ' style="display: flex; align-items: center; gap: 12px; height: 64px">'
             + rowglyph("lock", IC["red"])
             + '<span style="flex-grow: 1; font-size: 19px; font-weight: 700; letter-spacing: -0.02em; color: ' + WARN_TEXT + '">Sign out</span></div>')
  + '<div style="padding-top: 8px; text-align: center">'
    '<span style="font-size: 15px; font-weight: 400; color: ' + INK3 + '">Version 1.0.4</span></div>', 20)
settings += dockback("Ask me to change something")
write("Settings", settings)

# ---------- what it takes to open this, and what shows once it is open ----------
# Hiding a balance is not vanity. A figure on a screen in a danfo is a reason
# for somebody to follow you home, and the product that knows that is the one
# people trust with the figure in the first place.
lock = page(
  T("Lock and privacy", "What it takes to open this, and what shows once it is open")
  + '<div style="' + cardstyle("2px 16px") + '; display: flex; flex-direction: column">'
    + setrow("Face ID", "faceid", "", "", None, False, "", switch(True), FILL)
    + setrow("Passcode", "key", "", "soon", None, False, "6 digits", None, FILL)
    + setrow("Ask again after", "clock", "", "soon", None, False, "2 minutes", None, FILL) + '</div>'
  + '<div style="display: flex; flex-direction: column; gap: 12px">' + label("What other people can see")
    + '<div style="' + cardstyle("2px 16px") + '; display: flex; flex-direction: column">'
      + setrow("Hide my balance", "eye", "", "", None, False, "", switch(True), FILL)
      + setrow("Hide it in screenshots", "camera", "", "", None, False, "", switch(True), FILL)
      + setrow("Amounts in notifications", "bell", "", "", None, False, "", switch(False), FILL) + '</div></div>'
  + '<div style="display: flex; gap: 10px; align-items: flex-start">' + icon("eye", 16, INK3, 1.8, "; margin-top: 2px")
    + '<span style="font-size: 14px; font-weight: 500; line-height: 1.45; color: ' + INK3
    + '; text-wrap: pretty">With this on, your balance is dots until you look at the phone. '
      'Nobody standing behind you in a queue reads it over your shoulder.</span></div>'
  + tinted('<span style="font-size: 16px; font-weight: 700; color: ' + ACC_INK + '">Your passcode is not on our servers</span>',
           "It opens this phone and nothing else. If you lose it, recovery gives you a new one. Nobody, here or anywhere, can read the old one."), 18)
lock += dockback("Ask me to lock something down")
write("Lock", lock)

# ================= ACTIVITY =================
activity = page(
  T("History", "Everything that moved, newest first", "clock")
  + segment(["All", "In", "Out"], 0, "seg")
  + '<div style="display: flex; flex-direction: column; gap: 4px">' + sectionhead("Today")
    + '<div style="display: flex; flex-direction: column">'
    # Money that has not landed is money you go looking for, so it sits at the
    # top of the list it is missing from rather than buried in it.
    + txstate("Sarah Adeyemi", "Still on its way &#183; 14:22", "&#8358;20,000", "wait", "blue", "Pending")
    + txstate("Sarah Adeyemi", "Did not go &#183; 14:22", "&#8358;20,000", "warn", "red", "Failed")
    + txstate("Musa Danjuma", "Came back &#183; 16:22", "&#8358;20,000", "undo", "green", "Reversed")
    + tx("Sarah Adeyemi", "send", "Flat deposit &#183; 09:14", "&#8358;50,000")
    + tx("MTN", "data", "5GB for Mum &#183; 08:02", "&#8358;2,500") + '</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 4px">' + sectionhead("Yesterday")
    + '<div style="display: flex; flex-direction: column">'
    + tx("Pagrin Limited", "bank", "August salary &#183; 16:40", "&#8358;640,000", True)
    + tx("Ikeja Electric", "power", "Meter 4457 8891 &#183; 11:22", "&#8358;8,000")
    + tx("Netflix", "card", "Virtual card &#183; 09:00", "&#8358;5,200") + '</div></div>'
  + '<div style="' + bordered("16px", "24px") + '">'
    + aline("Your spending is &#8358;41,000 below this point last month.", "17px") + '</div>', 18)
activity += dockback("Ask about any of these")
write("History", activity)

# ================= ADD MONEY, AS A SHEET =================
def sheetrow(name, ic, sub, last=False, go=""):
    return ('<div' + hook(go, "" if go else "soon") + ' style="display: flex; align-items: center; gap: 14px; height: 72px">'
      + badge(ic, None, 44, R_ICON, 22)
      + '<div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px">'
      '<span style="font-size: 19px; font-weight: 700; letter-spacing: -0.02em">' + name + '</span>'
      '<span style="font-size: 15px; font-weight: 400; color: ' + INK3 + '">' + sub + '</span></div>'
      + chevbtn() + '</div>')

# Nothing here is a page. It came up from home, it goes back to home, and it
# can be thrown back down by the handle. A back arrow would be a second way to
# do what the handle and the word at the bottom already do.
receive_inner = ('<div style="display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 4px 0 20px 0">'
  + badge("down", None, 64, "20px", 30)
  + '<span style="font-size: 22px; font-weight: 700; letter-spacing: -0.025em; color: ' + INK + '; margin-top: 8px">Receive</span>'
  + '<span style="font-size: 17px; font-weight: 400; color: ' + INK3 + '; text-align: center; text-wrap: pretty">'
    'Pick how you want the money to reach you</span></div>'
  + '<div style="display: flex; flex-direction: column">'
  + sheetrow("Bank transfer", "bank", "Your number, 0102 4457 88", False, "Ways")
  + sheetrow("From a card", "card", "Any Nigerian debit card")
  + sheetrow("Ask someone", "request", "Send a request they can pay")
  # Dollars are not a place of their own any more. You reach them where you
  # reach every other way money gets to you, because that is what they are.
  + sheetrow("In dollars", "dollar", "Hold it steady, or turn naira across", True, "Dollars") + '</div>')

RECEIVE_SHEET = sheetup(receive_inner)
write("Receive", page(home_inner, 16) + askbar("Ask, or just say what you need") + RECEIVE_SHEET)


# ================= THE NINE FLOWS =================
# The same three jobs, reached three ways. Money out always ends at a face and
# a passcode, because a slide only says you meant it and a face says it is you.
# Money in never asks for anything, because nothing can leave an account by
# being paid into, and a gate people learn to tap past is worse than no gate.

# ---------- a line typed rather than spoken ----------
KEYS = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]

def keyboard():
    """The system keyboard, drawn rather than implied, so a screen about typing
    looks like typing."""
    rows = ''
    for i, r in enumerate(KEYS):
        pad = {0: 0, 1: 20, 2: 0}[i]
        cells = ''
        if i == 2:
            cells += ('<div style="width: 42px; height: 42px; border-radius: 6px; background: ' + FILL2
              + '; display: flex; align-items: center; justify-content: center">' + icon("up", 18, INK, 2.0) + '</div>')
        for ch in r:
            cells += ('<div style="width: 33px; height: 42px; border-radius: 6px; background: ' + SURF + '; ' + SH_RAISE
              + '; display: flex; align-items: center; justify-content: center">'
              '<span class="chrome" style="font-size: 22px; font-weight: 400; color: ' + INK + '">' + ch + '</span></div>')
        if i == 2:
            cells += ('<div style="width: 42px; height: 42px; border-radius: 6px; background: ' + FILL2
              + '; display: flex; align-items: center; justify-content: center">' + icon("del", 20, INK, 1.8) + '</div>')
        rows += ('<div style="display: flex; gap: 6px; justify-content: center; padding: 0 ' + str(pad) + 'px">' + cells + '</div>')
    rows += ('<div style="display: flex; gap: 6px; justify-content: center">'
      '<div style="width: 42px; height: 42px; border-radius: 6px; background: ' + FILL2
      + '; display: flex; align-items: center; justify-content: center">'
      '<span style="font-size: 14px; font-weight: 400; color: ' + INK + '">123</span></div>'
      '<div style="flex-grow: 1; height: 42px; border-radius: 6px; background: ' + SURF + '; ' + SH_RAISE + '"></div>'
      '<div style="width: 76px; height: 42px; border-radius: 6px; background: ' + ACC
      + '; display: flex; align-items: center; justify-content: center">'
      '<span style="font-size: 14px; font-weight: 700; color: #FFFFFF">send</span></div></div>')
    return ('<div style="position: absolute; left: 0; right: 0; bottom: 0; z-index: 4; background: ' + FILL
      + '; padding: 10px 4px 28px 4px; display: flex; flex-direction: column; gap: 11px">' + rows + '</div>')

def typedbar(text, go=""):
    """The ask bar with something in it. Black words instead of grey ones, and
    the microphone gives way to the button that sends."""
    return ('<div style="position: absolute; left: 0; right: 0; bottom: 262px; z-index: 4; padding: 0 18px 12px 18px; '
      'background: linear-gradient(180deg, rgba(255,255,255,0) 0%, ' + BG + ' 40%); display: flex; gap: 10px; align-items: center">'
      '<div class="askpill" style="flex-grow: 1; min-width: 0; height: 48px; border-radius: ' + PILL
      + '; background: ' + FILL + '; display: flex; align-items: center; gap: 9px; padding: 0 14px 0 8px">' + mark(32)
      + '<span style="flex-grow: 1; min-width: 0; font-size: 15px; font-weight: 400; color: ' + INK
      + '; white-space: nowrap; overflow: hidden">' + text + '</span>'
      '<div style="width: 2px; height: 20px; background: ' + ACC + '"></div></div>'
      + '<div' + hook(go) + ' style="width: 48px; height: 48px; border-radius: ' + PILL + '; background: ' + BTN + '; ' + SH_BTN
      + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
      + icon("up", 22, "#FFFFFF", 2.4) + '</div></div>')

def typedscreen(text, go):
    # No dimming. A phone does not grey out the page when the keyboard is up.
    return ('<div class="behind">' + page(home_inner, 16) + '</div>'
      + typedbar(text, go) + keyboard())

write("Typed", typedscreen("send sarah 20k", "Draft"))
write("TypedAsk", typedscreen("ask musa for 20k", "Request"))
write("TypedBuy", typedscreen("2k data for mum", "Buy"))

# ---------- what a voice sheet says, when it says something else ----------
def voicesheet(lead, tail, go, sugs):
    s = ''.join(sugg(t, g) for t, g in sugs)
    return ('<div class="behind">' + page(home_inner, 16) + askbar("Ask, or just say what you need") + '</div>'
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
        '<div style="font-size: 28px; font-weight: 700; letter-spacing: -0.03em; line-height: 1.24; color: ' + INK
        + '; text-wrap: pretty">' + lead + '<span style="color: ' + INK3 + '"> ' + tail + '</span></div>'
        + wave()
        + '<div style="display: flex; flex-direction: column; gap: 10px">' + sectionhead("Or try one of these")
          + '<div style="display: flex; flex-direction: column; gap: 8px">' + s + '</div></div></div>'
      '<div style="padding: 0 20px 24px 20px; display: flex; flex-direction: column; gap: 12px">'
        '<div' + hook("Amend") + ' style="display: flex; justify-content: center">'
          '<span style="font-size: 14px; font-weight: 700; color: ' + ACC_TEXT + '">Not what I said</span></div>'
        '<div style="display: flex; gap: 10px; align-items: center">'
        '<div' + hook(go) + ' style="flex-grow: 1; height: 56px; border-radius: ' + PILL + '; background: ' + ACC + '; ' + SH_BTN
        + '; display: flex; align-items: center; justify-content: center">'
        '<span style="font-size: 17px; font-weight: 700; color: #FFFFFF">Release to send</span></div>'
        '<div' + hook("back") + ' style="width: 56px; height: 56px; border-radius: ' + PILL + '; background: ' + FILL
        + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
        '<div style="width: 15px; height: 15px; border-radius: 3px; background: ' + INK2 + '"></div></div></div></div></div>')

write("AskReq", voicesheet("Ask Musa for", "20k", "Request",
  [("Who owes me money?", "History"), ("Show my code", "MyCode"), ("Remind Musa again", "soon")]), ANIM)
write("AskSvc", voicesheet("2k data for", "mum", "Buy",
  [("Pay my light bill", "Meter"), ("How much did I spend on data?", "Answer"), ("Top up my own line", "Airtime")]), ANIM)

# ---------- asking somebody to pay you ----------

def requestchat(voice=True):
    return chatscreen("Ask Musa for 20k",
      "Musa Danjuma, the line ending 4471. He is the only Musa who has ever paid you.",
      toolpanel("Leorio Requests", "Running",
        toolrow("done", "Person", "Musa Danjuma", INK, True)
        + toolrow("done", "Reaches him", "WhatsApp and SMS", INK, False)
        + toolrow("done", "Amount", "&#8358;20,000", INK, False, True, "Amend")
        + toolrow("done", "For", "Rent balance", INK)
        + toolrow("work", "Expires", "Picking a date", INK3),
        "Send the request", "Sent"),
      "Asking cannot move money. Nothing can leave your account because somebody was asked to pay into it.",
      "lock", voice)

write("Request", requestchat(True))
write("RequestTyped", requestchat(False))

sent = page(
  T("Request sent", "Musa has it on WhatsApp and in a text")
  + '<div style="display: flex; flex-direction: column; gap: 16px; align-items: flex-start">'
    + tickmark("", 56, IC["blue"])
    + '<div style="display: flex; flex-direction: column; gap: 6px">' + money("&#8358;20,000", "", 40)
      + '<span style="font-size: 15px; color: ' + INK2 + '">Asked Musa Danjuma</span></div></div>'
  + '<div style="display: flex; flex-direction: column">'
    + plainrow("For", "Rent balance")
    + plainrow("Expires", "In 7 days")
    + plainrow("Reference", "REQ-40112-8873", True) + '</div>'
  + aline("I will tell you the moment it lands. You do not have to watch for it.", "16px")
  + offer("Want me to remind him if nothing comes by Friday?", "Set that up", "Rule"), 16)
sent += dockback("Ask about this request")
write("Sent", sent)

# ---------- the code somebody points a camera at ----------
def qrsvg(size=190):
    """A stand in for the code. The right shape and density, and it rides as a
    single node rather than four hundred little squares."""
    n = 21
    c = size / float(n)
    out = ['<svg width="' + str(size) + '" height="' + str(size) + '" viewBox="0 0 ' + str(size) + ' ' + str(size) + '" fill="none">']
    def rect(x, y, w, h, r, fill):
        out.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="%.2f" fill="%s"/>' % (x, y, w, h, r, fill))
    def finder(cx, cy):
        rect(cx * c, cy * c, c * 7, c * 7, c, "#000000")
        rect((cx + 1) * c, (cy + 1) * c, c * 5, c * 5, c * 0.7, "#FFFFFF")
        rect((cx + 2) * c, (cy + 2) * c, c * 3, c * 3, c * 0.5, "#000000")
    seed = 20240823
    for y in range(n):
        for x in range(n):
            corner = (x < 8 and y < 8) or (x > n - 9 and y < 8) or (x < 8 and y > n - 9)
            if corner:
                continue
            seed = (seed * 1103515245 + 12345) % 2147483648
            if (seed >> 16) % 100 < 46:
                rect(x * c + c * 0.1, y * c + c * 0.1, c * 0.8, c * 0.8, c * 0.22, "#000000")
    finder(0, 0); finder(n - 7, 0); finder(0, n - 7)
    out.append('</svg>')
    return "".join(out)

mycode = page(
  T("Your code", "Point their camera at this and the money reaches you")
  + '<div style="' + cardstyle("24px", R_CARDLG, SURF, " " + CARD_EDGE + ";")
    + ' display: flex; flex-direction: column; align-items: center; gap: 20px">'
    + qrsvg(190)
    + '<div style="display: flex; align-items: center; gap: 12px">' + avatar("IM", 44, IC["blue"], "#FFFFFF")
      + '<div style="display: flex; flex-direction: column; gap: 2px">'
      '<span style="font-size: 16px; font-weight: 700; letter-spacing: -0.02em; color: ' + INK + '">Ibrahim Musa</span>'
      '<span class="num" style="font-size: 14px; font-weight: 400; color: ' + INK3 + '">Leorio &#183; 0102 4457 88</span></div></div></div>'
  + '<div style="display: flex; gap: 10px">'
    + '<div' + hook("", "soon") + ' class="pbtn" style="flex-grow: 1; height: 52px; border-radius: ' + PILL + '; background: ' + BTN + '; ' + SH_BTN
    + '; display: flex; align-items: center; justify-content: center; gap: 8px">' + icon("send", 18, "#FFFFFF", 2.0)
    + '<span style="font-size: 16px; font-weight: 700; color: #FFFFFF">Share it</span></div>'
    + '<div' + hook("", "soon") + ' class="pbtn" style="flex-grow: 1; height: 52px; border-radius: ' + PILL + '; background: ' + FILL
    + '; display: flex; align-items: center; justify-content: center; gap: 8px">' + icon("down", 18, INK, 2.0)
    + '<span style="font-size: 16px; font-weight: 700; color: ' + INK + '">Save it</span></div></div>'
  + '<div style="display: flex; gap: 9px; align-items: flex-start">' + icon("lock", 16, INK3, 1.6, "; margin-top: 2px")
    + '<span style="font-size: 14px; font-weight: 400; line-height: 1.45; color: ' + INK2
    + '; text-wrap: pretty">Anyone can pay you with this. Nobody can take anything with it, and it does not carry your balance.</span></div>', 16)
mycode += dockback("Ask about your code")
write("MyCode", mycode)

# ---------- buying something, in the chat ----------
def buychat(voice=True):
    return chatscreen("2k data for mum",
      "Mum&#8217;s MTN line, the one ending 881. She ran dry eleven days early last month, so I have priced the bigger bundle too.",
      toolpanel("Leorio Airtime", "Running",
        toolrow("done", "Line", "MTN &#183; 0803 4457 881", INK, True, True)
        + toolrow("done", "Whose", "Mum", INK)
        + toolrow("done", "Plan", "5GB for 30 days", INK)
        + toolrow("done", "Price", "&#8358;2,500", INK, False, True)
        + toolrow("work", "Cheaper?", "Checking MTN plans", INK3),
        "Confirm &#8358;2,500", "ConfirmBuy"),
      "Face ID first. Nothing leaves your account until then.", "lock", voice)

write("Buy", buychat(True))
write("BuyTyped", buychat(False))

write("ConfirmBuy", confirmscreen("&#8358;2,500", "data", "MTN &#183; 5GB", "Mum &#183; 0803 4457 881", IC["purple"]))

# ---------- a meter number, read off a bill ----------
meter = page(
  T("What I found", "Read from your photo, 4:02 PM")
  + photo("meter")
  + '<div style="' + bordered("16px", "24px") + ' display: flex; flex-direction: column; gap: 12px">'
    '<div style="display: flex; align-items: center; gap: 8px">' + icon("alert", 18, WARN_TEXT, 2.0)
    + '<span style="font-size: 16px; font-weight: 700; letter-spacing: -0.02em; color: ' + INK
    + '">Is this your meter?</span></div>'
    + '<div style="' + cardstyle("8px 14px", "16px") + ' display: flex; flex-direction: column">'
      + nrow("On the bill", "Meter 4457 8891")
      + nrow("Ikeja Electric says", "14 Bode Thomas") + '</div>'
    '<div style="display: flex; gap: 8px">'
      '<div' + hook("", "sure") + ' class="pbtn" style="flex-grow: 1; height: 48px; border-radius: ' + PILL
      + '; background: ' + BTN + '; ' + SH_BTN + '; display: flex; align-items: center; justify-content: center">'
      '<span style="font-size: 16px; font-weight: 700; color: #FFFFFF">Yes, that is mine</span></div>'
      '<div' + hook("back") + ' class="pbtn" style="height: 48px; padding: 0 20px; border-radius: ' + PILL
      + '; background: ' + FILL + '; display: flex; align-items: center; justify-content: center">'
      '<span style="font-size: 16px; font-weight: 700; color: ' + INK + '">No</span></div></div></div>'
  + '<div style="' + cardstyle("0 16px", R_CARD) + '">'
    + foundrow("Amount", "&#8358;8,000", True, False, "from the photo")
    + foundrow("Meter", "0102 4457 8891", True)
    + foundrow("Disco", "Ikeja Electric", False, True) + '</div>', 12)
meter += confirmbar(pillbtn("Continue", "", "fnwait", "", "grey", True, 56, "mtGo"))
write("Meter", meter)

write("ConfirmMeter", confirmscreen("&#8358;8,000", "power", "Ikeja Electric", "Meter 0102 4457 8891", IC["amber"]))

# ---------- the receipt for money that left ----------
# The fee is shown even when there is none, because a row that only appears on
# the receipts where you were charged is a row people learn to dread.
donesend = page(
  T("All done", "28 August 2026 at 2:22 PM")
  + rhero("&#8358;20,000", "Sent to Sarah Adeyemi")
  + receipt([
      rline(rfield("To", "Sarah Adeyemi", "GTBank &#183; 0123 4457 8842"),
            rfield("From", "Everyday", "0102 4457 88")),
      rline(rfield("Narration", "Rent part payment")),
      rcut(),
      '<div style="display: flex; flex-direction: column; gap: 6px">'
      + rline(rfield("Amount", "&#8358;20,000.00"), rfield("Fee", "&#8358;26.88"))
      + rnote("Transfers under &#8358;10,000 carry none") + '</div>',
      rline(rfield("Total charged", "&#8358;20,026.88", "", True),
            rfield("Balance after", "&#8358;620,273.12")),
      rcut(),
      rid("Session ID", "000016 260828 142204 471803 926104")])
  + sharebtn("Share")
  + offerrow("She has it. Rent again next month?", "Set it up", "Rule")
  + wrongrow(), 20)
donesend += dockback("Ask about this transfer")
write("DoneSend", donesend)

# ---------- sending the receipt on ----------
# A receipt nobody can send is not a receipt here. It goes to a landlord, to
# the person who asked for the money, or into a folder for an office, and the
# balance is left off every copy that leaves the phone.
def share_inner(line):
    return ('<div style="display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 4px 0 20px 0">'
      + badge("share", None, 64, "20px", 28)
      + '<span style="font-size: 22px; font-weight: 700; letter-spacing: -0.025em; color: ' + INK
        + '; margin-top: 8px">Share this receipt</span>'
      + '<span style="font-size: 17px; font-weight: 400; color: ' + INK3
        + '; text-align: center; text-wrap: pretty">' + line + '</span></div>'
    + '<div style="display: flex; flex-direction: column">'
      + sheetrow("WhatsApp", "chat", "The picture, ready to send")
      + sheetrow("Save to photos", "camera", "It stays on this phone")
      + sheetrow("Save as PDF", "receipt", "The full record, for an office")
      + sheetrow("Somewhere else", "grid", "Messages, mail, anywhere you share")
      + '</div>'
    + '<div style="display: flex; gap: 8px; align-items: flex-start; padding: 12px 4px 0 4px">'
      + icon("eye", 16, INK3, 1.7, "; margin-top: 2px")
      + '<span style="font-size: 14.5px; font-weight: 500; line-height: 1.45; color: ' + INK2
      + '; text-wrap: pretty">Your balance is left off every copy that leaves the phone.</span></div>')

write("Share", donesend + sheetup(share_inner("&#8358;20,000 to Sarah Adeyemi, 2:22 PM")))
write("ShareBuy", done + sheetup(share_inner("&#8358;2,500 of data for Mum, 2:19 PM")))


# ================= WHEN IT DOES NOT GO =================
# Nine flows of everything working is a brochure. These are the four ways a
# transfer really ends when it ends badly, and the two ways a person asks for
# money back afterwards.
#
# The whole point of these screens is one distinction: money that is late is
# not money that is lost. A person who cannot tell those apart sends the twenty
# thousand a second time, and then they are out forty. So every screen here
# says which of the two it is, in the first line, before anything else.

def limitrow(ic, col, t):
    """What the model did, and what it cannot do, told apart by their marks.
    The same padlock on all three would say it failed at all three."""
    return ('<div style="display: flex; align-items: flex-start; gap: 12px">'
      + badge(ic, None, 30, "10px", 16)
      + '<span style="flex-grow: 1; font-size: 14px; font-weight: 400; line-height: 1.45; color: '
      + INK2 + '; text-wrap: pretty">' + t + '</span></div>')

def statehead(ic, colour, amount, line):
    """A glyph, the figure, and one sentence. Every state screen opens the same
    way, so what happened is read before it is explained."""
    return ('<div style="display: flex; flex-direction: column; gap: 16px; align-items: flex-start">'
      '<div style="width: 56px; height: 56px; display: flex; align-items: center; justify-content: center">'
      + fglyph(ic, 52, colour) + '</div>'
      '<div style="display: flex; flex-direction: column; gap: 5px">' + money(amount, "", 40)
      + '<span style="font-size: 15px; color: ' + INK2 + '">' + line + '</span></div></div>')

def loudnote(text, colour):
    """The one sentence on the screen that has to survive being skimmed."""
    return ('<div style="border-radius: ' + R_INNER + '; background: ' + colour
      + '; padding: 16px 18px; display: flex; align-items: center; gap: 12px">'
      + fglyph("warn", 24, "#FFFFFF", colour)
      + '<span style="flex-grow: 1; font-size: 16px; font-weight: 700; letter-spacing: -0.015em; '
        'color: #FFFFFF; text-wrap: pretty">' + text + '</span></div>')

def waylist(items):
    """A short list of ways out of a hole, each one a row you can take."""
    out = ''
    for i, (name, sub, ic, col, go) in enumerate(items):
        out += ('<div' + hook(go, "" if go else "soon") + ' style="display: flex; align-items: center; gap: 14px; height: 72px'
          + ('' if i == 0 else '; border-top: 1px solid ' + LINE) + '">'
          + badge(ic, None, 44, R_ICON, 22, on=FILL)
          + '<div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px">'
          '<span style="font-size: 17px; font-weight: 700; letter-spacing: -0.02em">' + name + '</span>'
          '<span style="font-size: 14px; font-weight: 400; color: ' + INK3 + '">' + sub + '</span></div>'
          + chevbtn() + '</div>')
    return '<div style="' + cardstyle("4px 16px") + '; display: flex; flex-direction: column">' + out + '</div>'

# ---------- not enough money, before anything is tried ----------
short = page(
  T("Not enough in Everyday", "Nothing has been sent")
  + statehead("warn", IC["amber"], "&#8358;7,520", "short of the &#8358;20,000 you asked for")
  + '<div style="display: flex; flex-direction: column">'
    + plainrow("You asked for", "&#8358;20,000")
    + plainrow("In Everyday", "&#8358;12,480")
    + plainrow("Short by", "&#8358;7,520", True, IC["amber"]) + '</div>'
  + aline("Three ways to close it. None of them costs you anything.", "16px")
  + waylist([
      ("Move it from Holiday", "&#8358;48,000 is sitting there", "pot", "green", ""),
      ("Send &#8358;12,480 now", "The rest when your salary lands", "send", "blue", "Confirm"),
      ("Ask Musa for &#8358;7,520", "He owes you from the rent", "request", "purple", "Request")])
  + tinted('<span style="font-size: 16px; font-weight: 700; color: ' + ACC_INK + '">Nothing has left your account</span>',
           "No fee and no attempt. This is a sum I did before trying."), 13)
short += dockback("Ask me about this")
write("Short", short)

# ---------- sent, and the bank is slow ----------
pending = page(
  T("Still on its way", "Sent at 14:22, not confirmed yet")
  + statehead("wait", ACC, "&#8358;20,000", "to Sarah Adeyemi &#183; GTBank")
  + loudnote("Do not send it again. This one is still live.", IC["amber"])
  + '<div style="' + cardstyle("16px") + '; display: flex; flex-direction: column; gap: 2px">'
    + toolrow("done", "Left your account", "14:22", INK, True)
    + toolrow("done", "GTBank has it", "14:22")
    + toolrow("run", "Reaching Sarah", "Waiting", INK3) + '</div>'
  + aline("Slow, not lost. If GTBank has not confirmed by 16:22 it comes back on its own, "
          "and I will tell you either way.", "16px")
  + offer("Want a message the moment it lands?", "Yes, tell me", "Rule"), 15)
pending += dockback("Ask about this transfer")
write("Pending", pending)

# ---------- the bank turned it down ----------
failed = page(
  T("It did not go", "GTBank turned it down at 14:22")
  + statehead("warn", IC["red"], "&#8358;20,000", "still in your account")
  + loudnote("Your balance is exactly what it was.", IC["green"])
  + aline("Nothing was taken and nothing was charged. GTBank has been failing since 13:40, "
          "so this is their afternoon, not your account.", "16px")
  + waylist([
      ("Try again now", "It may have cleared already", "send", "blue", "Chat"),
      ("Send it another way", "Through your Zenith account", "bank", "purple", "")])
  + offer("Keep trying until GTBank is back?", "Do that", "Rule"), 13)
failed += dockback("Ask why this failed")
write("Failed", failed)

# ---------- it went, and it came back ----------
reversal = page(
  T("It came back", "Returned at 16:22")
  + statehead("undo", IC["green"], "&#8358;20,000", "back in Everyday")
  + '<div style="display: flex; flex-direction: column">'
    + plainrow("Left", "14:22")
    + plainrow("Came back", "16:22")
    + plainrow("Why", "Account could not be credited", False, INK2)
    + plainrow("Reference", "REV-40118-2290", True) + '</div>'
  + aline("Sarah never got it, so GTBank sent it back and I put it where it came from. "
          "Nothing was charged, and your balance is whole.", "16px")
  + waylist([
      ("Check the account number", "One digit is usually all it is", "search", "amber", "Found"),
      ("Try Sarah again", "Same amount, same account", "send", "blue", "Chat")]), 15)
reversal += dockback("Ask about this")
write("Reversed", reversal)

# ---------- something was wrong with a payment that worked ----------
wrong = page(
  T("What went wrong?", "Tell me which and I start it now")
  + waylist([
      ("It went to the wrong person", "I ask their bank to send it back", "person", "amber", "Recall"),
      ("They say it never arrived", "I make GTBank trace it", "search", "blue", "Pending"),
      ("I did not make this payment", "I freeze the account first, then we look", "shield", "red", "Paused")])
  + aline("Some of this I can do in minutes. Some of it only a bank can do, and that takes days. "
          "I will tell you which one you are in before you start, not after.", "16px")
  + '<div style="' + bordered("16px", "24px") + ' display: flex; flex-direction: column; gap: 12px">'
    + sectionhead("The payment")
    + plainrow("Amount", "&#8358;20,000")
    + plainrow("To", "Sarah Adeyemi &#183; GTBank")
    + plainrow("Sent", "Today, 14:22", True) + '</div>', 15)
wrong += dockback("Tell me what happened")
write("Wrong", wrong)

# ---------- asking for it back, and what that really means ----------
recall = page(
  T("Asking GTBank to send it back", "&#8358;20,000, sent at 14:22")
  + toolpanel("Leorio Recall", "Running",
      toolrow("done", "You reported it", "16:24", INK, True)
      + toolrow("done", "Sent to GTBank", "16:24")
      + toolrow("done", "Sarah asked to approve", "16:25")
      + toolrow("run", "Her answer", "Up to 5 working days", INK3))
  # The honest part. A product that implies it can claw money back out of
  # somebody else's account is lying, and the person finds out on the worst
  # day they have had this year.
  + '<div style="' + bordered("16px", "24px") + ' display: flex; flex-direction: column; gap: 14px">'
    + sectionhead("What this is and is not")
    + '<div style="display: flex; flex-direction: column; gap: 10px">'
      + limitrow("check", "green", "I have asked GTBank. That part is done.")
      + limitrow("lock", "amber", "I cannot take it back. It is her money until she agrees.")
      + limitrow("lock", "amber", "If she says no, no bank can force her.") + '</div>'
    + '<span style="font-size: 14px; font-weight: 400; color: ' + INK2 + '; text-wrap: pretty">'
      'After that it is a formal dispute, then a police report. I walk you through either.</span></div>'
  + waylist([
      ("Message Sarah", "Most of these end here, in an hour", "chat", "green", ""),
      ("Open a dispute", "If she has not answered by Friday", "list", "amber", "")]), 15)
recall += dockback("Ask what happens next")
write("Recall", recall)

# ================= WHAT A STANDING INSTRUCTION IS =================
# Set it up appears at the end of five flows. Until now it made a promise
# nobody could read and nobody could cancel. This is the thing it makes.
ruleconfirm = page(
  T("Set this up?", "Nothing is saved until you say yes")
  + '<div style="' + cardstyle("6px 16px") + '; display: flex; flex-direction: column">'
    + plainrow("What", "Pay Ikeja Electric")
    + plainrow("Meter", "0102 4457 8891")
    + plainrow("When", "The day the bill lands")
    + plainrow("Up to", "&#8358;10,000")
    + plainrow("Stops if", "Everyday is under &#8358;15,000", True, INK2) + '</div>'
  + aline("Over &#8358;10,000 and I stop and ask you, every time. I never raise this on my own.", "16px")
  + tinted('<span style="font-size: 16px; font-weight: 700; color: ' + ACC_INK + '">You can stop it any time</span>',
           "It sits in Standing instructions with a switch beside it. Or just tell me to stop and it stops.")
  + ctabtn("Set it up", "Rule")
  + '<div' + hook("back") + ' style="display: flex; justify-content: center; height: 44px; align-items: center">'
    '<span style="font-size: 16px; font-weight: 700; color: ' + INK2 + '">Not now</span></div>', 15)
write("Rule", ruleconfirm)

# ================= CHANGING THE NUMBER =================
# A model that mishears twenty thousand as two hundred thousand and offers you
# only conversation to fix it has put the burden in the wrong place. A number
# is corrected with a keypad.
def numkey(k, act="amend"):
    return ('<div class="pinkey"' + hook("", act) + ' style="width: 74px; height: 74px; border-radius: ' + PILL
      + '; background: ' + FILL + '; display: flex; align-items: center; justify-content: center">'
      '<span class="num" style="font-size: 26px; font-weight: 400; color: ' + INK + '">' + k + '</span></div>')

def numpad():
    out = ''
    for r in (["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]):
        out += '<div style="display: flex; gap: 22px; justify-content: center">' + "".join(numkey(k) for k in r) + '</div>'
    out += ('<div style="display: flex; gap: 22px; justify-content: center">'
      + numkey("000") + numkey("0")
      + '<div class="pinkey"' + hook("", "amend") + ' style="width: 74px; height: 74px; display: flex; align-items: center; justify-content: center">'
      + icon("del", 30, INK2, 1.8) + '</div></div>')
    return ('<div style="display: flex; flex-direction: column; gap: 18px; align-items: center">' + out + '</div>')

amend = page(
  T("Change the amount", "Nothing has been sent")
  + '<div style="display: flex; flex-direction: column; gap: 8px; align-items: center">'
    + caption("I heard")
    + '<span class="num" style="font-size: 16px; font-weight: 400; color: ' + INK3
    + '; text-decoration: line-through">&#8358;200,000</span>'
    + '<div id="amAmt">' + money("&#8358;20,000", "", 36) + '</div></div>'
  + numpad()
  + aline("Change it as many times as you like. It moves after your face and your passcode, not before.", "16px")
  + ctabtn("Use &#8358;20,000", "Confirm")
  + '<div' + hook("Short") + ' style="display: flex; justify-content: center; height: 40px; align-items: center">'
    '<span style="font-size: 14px; font-weight: 700; color: ' + ACC_TEXT + '">What if it is more than I have?</span></div>', 14)
write("Amend", amend)

# ================= HOW MONEY REACHES YOU =================
# Receiving is not something the model does. It is two facts about you, and it
# can hand you both. Asking somebody to pay is a different job with a different
# name, and it is on this screen as a third thing, not as the first one.
def waycard(head, big, sub, action, ic, col, go="", act="soon"):
    return ('<div style="' + cardstyle("16px") + '; display: flex; flex-direction: column; gap: 14px">'
      '<div style="display: flex; align-items: center; gap: 12px">'
      + badge(ic, None, 40, R_ICON, 20, on=FILL)
      + '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 1px">'
        '<span style="font-size: 16px; font-weight: 700; letter-spacing: -0.015em; color: ' + INK + '">' + head + '</span>'
        '<span style="font-size: 12px; font-weight: 400; color: ' + INK3 + '">' + sub + '</span></div></div>'
      '<span class="num" style="font-size: 16px; font-weight: 700; color: ' + INK + '">' + big + '</span>'
      '<div' + hook(go, "" if go else act) + ' style="height: 44px; border-radius: ' + PILL + '; background: ' + SURF
      + '; display: flex; align-items: center; justify-content: center; gap: 7px">'
      '<span style="font-size: 16px; font-weight: 700; color: ' + INK + '">' + action + '</span>' + chev(12, INK, 2.2) + '</div></div>')

ways = page(
  T("Three ways to be paid", "All of them safe to hand out")
  + aline("You cannot receive by talking. What I can do is hand you the two things money "
          "reaches you by, and write the message that asks.", "16px")
  + waycard("Your account number", "0102 4457 88", "Leorio &#183; Ibrahim Musa", "Copy it", "bank", "blue", "", "copy")
  + waycard("Your code", "Point a camera at it", "Works with any bank app", "Show it", "qr", "green", "MyCode")
  + waycard("Ask somebody", "On WhatsApp and SMS", "I write it, you check it", "Ask for money", "request", "purple", "Request")
  + tinted('<span style="font-size: 16px; font-weight: 700; color: ' + ACC_INK + '">None of these can take anything</span>',
           "A number and a code can only be paid into. Neither carries your balance."), 13)
ways += dockback("Ask about getting paid")
write("Ways", ways)


# ================= THE CAMERA, POINTED AT A BILL =================
# Section eight opened on a screen that says point at an account number and
# shows somebody's transfer message, and then read an electricity bill on the
# next screen. The camera has two jobs and they want two prompts.
def camera(title, sub, shot, chip, foot, go):
    return ('<div style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; background: ' + SCAN_BG
      + '; display: flex; flex-direction: column; gap: 20px; padding: 60px 20px 32px 20px">'
      '<div style="display: flex; align-items: center; height: 44px">'
        + roundbtn("close", "back") + '<div style="flex-grow: 1"></div>' + roundbtn("power", "", "soon") + '</div>'
      '<div style="display: flex; flex-direction: column; align-items: center; gap: 6px">'
        '<span style="font-size: 16px; font-weight: 700; color: #FFFFFF">' + title + '</span>'
        '<span style="font-size: 14px; font-weight: 400; color: rgba(255,255,255,0.62)">' + sub + '</span></div>'
      '<div style="flex-grow: 1; display: flex; flex-direction: column; justify-content: flex-start; gap: 16px; padding-top: 8px">'
        '<div style="border: 2px solid rgba(255,255,255,0.34); border-radius: 24px; padding: 14px">'
        + photo(shot, False) + '</div>'
        '<div style="align-self: center; display: flex; align-items: center; gap: 8px; height: 36px; padding: 0 14px; '
        'border-radius: ' + PILL + '; background: ' + GLASS + '">' + stepdot("done")
        + '<span class="num" style="font-size: 14px; font-weight: 700; color: #FFFFFF">' + chip + '</span></div></div>'
      '<div style="display: flex; align-items: center; height: 72px">'
        + '<div' + hook(go) + ' style="width: 52px; height: 52px; border-radius: 14px; overflow: hidden; background: '
          + SURF + '; display: flex; flex-direction: column; gap: 4px; padding: 8px; flex-shrink: 0">'
          '<div style="display: flex; align-items: center; gap: 4px">'
            '<div style="width: 10px; height: 10px; border-radius: ' + PILL + '; background: ' + IC["green"] + '"></div>'
            '<div style="flex-grow: 1; height: 4px; border-radius: 4px; background: ' + LINE2 + '"></div></div>'
          '<div style="height: 4px; border-radius: 4px; background: ' + INK4 + '"></div>'
          '<div style="height: 4px; border-radius: 4px; background: ' + INK4 + '"></div>'
          '<div style="height: 4px; width: 62%; border-radius: 4px; background: ' + LINE2 + '"></div></div>'
        + '<div style="flex-grow: 1; display: flex; justify-content: center">'
          '<div' + hook(go) + ' style="width: 72px; height: 72px; border-radius: ' + PILL
          + '; border: 4px solid #FFFFFF; display: flex; align-items: center; justify-content: center">'
          '<div style="width: 56px; height: 56px; border-radius: ' + PILL + '; background: #FFFFFF"></div></div></div>'
        + roundbtn("qr", "Pick", "", 52, 22) + '</div>'
      '<span style="text-align: center; font-size: 12px; font-weight: 400; color: rgba(255,255,255,0.5)">'
      + foot + '</span></div>')

write("ScanBill", camera("Point at a bill or a meter",
  "The number on the card works too.", "meter", "4457 8891",
  "Or the meter number, typed, if the light is bad.", "Meter"))

# ================= A LINE YOU CAN STILL CHANGE =================
# Speaking and typing were the same screen after step two, which made six of
# the nine flows three. This is the thing typing can do that speaking cannot:
# hold the sentence still while you read it, and let you take it apart.
def chip(t, strong=False):
    return ('<div' + hook("Amend") + ' style="height: 34px; padding: 0 13px; border-radius: ' + PILL
      + '; background: ' + (ACC_SOFT if strong else FILL) + '; display: flex; align-items: center; gap: 5px; flex-shrink: 0">'
      '<span style="font-size: 14px; font-weight: 700; color: ' + (ACC_INK if strong else INK) + '">' + t + '</span>'
      + chev(10, ACC_INK if strong else INK3, 2.2) + '</div>')

def draftbar(text):
    """The ask bar holding a sentence that has not gone anywhere yet, with the
    parts of it that can still be argued with sitting above it."""
    return ('<div style="position: absolute; left: 0; right: 0; bottom: 262px; z-index: 4; padding: 0 18px 12px 18px; '
      'background: linear-gradient(180deg, rgba(255,255,255,0) 0%, ' + BG + ' 30%); '
      'display: flex; flex-direction: column; gap: 10px">'
      '<div style="display: flex; gap: 7px; align-items: center">'
      + chip("&#8358;20,000", True) + chip("Sarah Adeyemi") + chip("Everyday") + '</div>'
      '<div style="display: flex; gap: 10px; align-items: center">'
      '<div class="askpill" style="flex-grow: 1; min-width: 0; height: 48px; border-radius: ' + PILL
      + '; background: ' + FILL + '; display: flex; align-items: center; gap: 9px; padding: 0 14px 0 8px">' + mark(32)
      + '<span style="flex-grow: 1; min-width: 0; font-size: 15px; font-weight: 400; color: ' + INK
      + '; white-space: nowrap; overflow: hidden">' + text + '</span>'
      '<div style="width: 2px; height: 20px; background: ' + ACC + '"></div></div>'
      + '<div' + hook("Chat") + ' style="width: 48px; height: 48px; border-radius: ' + PILL + '; background: ' + BTN + '; ' + SH_BTN
      + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
      + icon("up", 22, "#FFFFFF", 2.4) + '</div></div></div>')

write("Draft", '<div class="behind">' + page(home_inner, 16) + '</div>' + draftbar("send sarah 20k") + keyboard())


# ================= WHAT YOU SET, AND WHAT HAPPENS AT THE LINE =================
# A limit that a tap can clear is not a limit. The point of this one is that
# passing it costs deliberate work: the passcode you know, plus three words
# typed out in full. Nobody does that by accident, and nobody does it on the
# phone in a stranger's hand.
def caprow(name, val, sub, first=False):
    return ('<div' + hook("", "soon") + ' style="' + ('' if first else 'border-top: 1px solid ' + LINE + '; ')
      + 'display: flex; align-items: center; gap: 12px; height: 66px">'
      '<div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px">'
      '<span style="font-size: 17px; font-weight: 700; letter-spacing: -0.02em; color: ' + INK + '">' + name + '</span>'
      '<span style="font-size: 13px; font-weight: 400; color: ' + INK3 + '">' + sub + '</span></div>'
      '<span class="num" style="font-size: 17px; font-weight: 700; white-space: nowrap; flex-shrink: 0; color: '
      + INK + '">' + val + '</span>' + chevbtn() + '</div>')

def gatestep(n, title, done=False, body="", first=False):
    """A step in the gate, numbered rather than described, so how much is left
    is countable at a glance."""
    dot = ('<div style="width: 28px; height: 28px; border-radius: ' + PILL + '; background: '
      + (IC["green"] if done else FILL3) + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
      + (icon("check", 16, "#FFFFFF", 2.6) if done
         else '<span class="num" style="font-size: 15px; font-weight: 700; color: ' + INK2 + '">' + str(n) + '</span>')
      + '</div>')
    return ('<div style="' + ('' if first else 'border-top: 1px solid ' + LINE + '; padding-top: 16px; ')
      + 'display: flex; flex-direction: column; gap: 12px">'
      '<div style="display: flex; align-items: center; gap: 12px">' + dot
      + '<span style="flex-grow: 1; font-size: 16px; font-weight: 700; letter-spacing: -0.015em; color: '
      + (INK3 if done else INK) + '">' + title + '</span>'
      + ('<span style="font-size: 13px; font-weight: 700; color: ' + IN_TEXT + '">Done</span>' if done else '')
      + '</div>' + (('<div style="padding-left: 40px; padding-bottom: 4px">' + body + '</div>') if body else '') + '</div>')

def typefield(typed, ghost):
    """The words, half written. What you have typed is black, what is left is
    grey, and the caret sits between the two, so the screen shows the work
    instead of describing it."""
    return ('<div style="' + bordered("15px 16px", R_FIELD) + ' display: flex; align-items: center">'
      '<span style="font-size: 17px; font-weight: 700; letter-spacing: -0.01em; color: ' + INK + '">' + typed + '</span>'
      '<div class="caret" style="width: 2px; height: 20px; background: ' + ACC + '; margin: 0 1px"></div>'
      '<span style="font-size: 17px; font-weight: 700; letter-spacing: -0.01em; color: ' + INK4 + '">' + ghost + '</span></div>')

limits = page(
  T("Spending limits", "What you set, and where today stands")
  + '<div style="' + cardstyle("18px") + '; display: flex; flex-direction: column; gap: 12px">'
    + '<div style="display: flex; align-items: baseline; justify-content: space-between; gap: 10px">'
      + caption("Out today", INK2, 14)
      + '<span class="num" style="font-size: 14px; font-weight: 500; color: ' + INK3 + '">of &#8358;100,000</span></div>'
    + money("&#8358;64,000", "", 34)
    + track(64)
    + '<span style="font-size: 15px; font-weight: 500; color: ' + INK2
    + '">&#8358;36,000 left before I stop and ask you twice.</span></div>'
  + '<div style="display: flex; flex-direction: column; gap: 12px">' + label("Your caps")
    + '<div style="' + cardstyle("2px 16px") + '; display: flex; flex-direction: column">'
      + caprow("One transfer", "&#8358;50,000", "The most that can leave in a single go", True)
      + caprow("One day", "&#8358;100,000", "Midnight to midnight")
      + caprow("One month", "&#8358;900,000", "Resets on the first") + '</div></div>'
  + '<div style="' + bordered("18px", "24px") + ' display: flex; flex-direction: column; gap: 14px">'
    + sectionhead("What happens at the line")
    + '<div style="display: flex; flex-direction: column; gap: 12px">'
      + limitrow("key", "purple", "Your passcode. Not your face, because a face can be held up to a phone.")
      + limitrow("list", "amber", "Then you type <b>Confirm this transaction</b> in full. Three words, spelled out.") + '</div>'
    + '<span style="font-size: 14px; font-weight: 400; color: ' + INK2 + '; text-wrap: pretty">'
      'Two deliberate things, so a bad minute cannot carry you past a line you drew on a good one.</span>'
    + '<div' + hook("LimitStop") + ' style="height: 46px; border-radius: ' + PILL + '; background: ' + FILL
    + '; display: flex; align-items: center; justify-content: center; gap: 7px">'
      '<span style="font-size: 14.5px; font-weight: 700; color: ' + INK + '">Show me what that looks like</span>'
      + chev(12, INK, 2.2) + '</div></div>'
  + '<div style="display: flex; gap: 10px; align-items: flex-start">' + icon("clock", 16, INK3, 1.8, "; margin-top: 2px")
    + '<span style="font-size: 14px; font-weight: 500; line-height: 1.45; color: ' + INK3
    + '; text-wrap: pretty">Raising a cap takes a day to come into force. Lowering one is immediate. '
      'That way nobody talks you into a bigger number in the moment.</span></div>', 18)
limits += dockback("Ask me to change a limit")
write("Limits", limits)

# ---------- the gate itself, caught halfway through ----------
limitstop = page(
  T("Past your own limit", "Nothing has been sent")
  + statehead("warn", IC["amber"], "&#8358;120,000",
              "&#8358;20,000 over the &#8358;100,000 you set for one transfer")
  + loudnote("This is your limit, not the bank&#8217;s. Two things and it goes.", IC["amber"])
  + '<div style="' + cardstyle("18px") + '; display: flex; flex-direction: column; gap: 16px">'
    + gatestep(1, "Your passcode", True, "", True)
    + gatestep(2, "Now type the words in full", False,
               typefield("Confirm this transa", "ction")
               + '<div style="padding-top: 8px"><span style="font-size: 13px; font-weight: 400; color: ' + INK3
               + '">Five letters to go. Exactly those three words, nothing shorter.</span></div>') + '</div>'
  + '<div' + hook("Confirm") + ' style="display: flex; align-items: center; gap: 12px; height: 62px; '
    'border-radius: ' + R_INNER + '; background: ' + FILL + '; padding: 0 16px">'
    + badge("send", None, 34, "11px", 18, color=ACC_TEXT_HEX, on=FILL)
    + '<div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 1px">'
      '<span style="font-size: 15px; font-weight: 700; letter-spacing: -0.015em; color: ' + INK + '">Send &#8358;100,000 instead</span>'
      '<span style="font-size: 13px; font-weight: 400; color: ' + INK3 + '">The rest tomorrow, no typing</span></div>'
    + chevbtn() + '</div>', 15)
# The button is grey and it stays grey. A screen that shows the action already
# lit is a screen that has not understood its own point.
limitstop += confirmbar(
  '<div style="height: 56px; border-radius: ' + PILL + '; background: ' + FILL
  + '; display: flex; align-items: center; justify-content: center">'
  '<span style="font-size: 17px; font-weight: 700; letter-spacing: -0.01em; color: ' + INK3 + '">Send &#8358;120,000</span></div>')
write("LimitStop", limitstop)

# ================= WHERE YOU ARE SIGNED IN =================
def devrow(name, where, ic, col, tag="", tcol=None, first=False):
    t = ''
    if tag:
        t = ('<div style="height: 24px; padding: 0 10px; border-radius: ' + PILL + '; background: '
          + (tcol or FILL3) + '; display: flex; align-items: center; flex-shrink: 0">'
          '<span style="font-size: 12px; font-weight: 700; color: '
          + ("#FFFFFF" if tcol else INK2) + '">' + tag + '</span></div>')
    return ('<div' + hook("", "soon") + ' style="' + ('' if first else 'border-top: 1px solid ' + LINE + '; ')
      + 'display: flex; align-items: center; gap: 13px; height: 74px">'
      + badge(ic, None, 42, R_ICON, 21, on=FILL)
      + '<div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px">'
      '<span style="font-size: 17px; font-weight: 700; letter-spacing: -0.02em; color: ' + INK + '">' + name + '</span>'
      '<span style="font-size: 13px; font-weight: 400; color: ' + INK3 + '">' + where + '</span></div>' + t + '</div>')

devices = page(
  T("Devices", "Everywhere this account is open")
  + '<div style="' + cardstyle("2px 16px") + '; display: flex; flex-direction: column">'
    + devrow("iPhone 13", "Lagos &#183; open now", "airtime", "green", "This one", None, True)
    + devrow("Tecno Spark 10", "Lagos &#183; 3 days ago", "airtime", "blue")
    + devrow("Chrome on Windows", "Abuja &#183; 12 August", "laptop", "amber", "Odd one", IC["amber"]) + '</div>'
  + aline("The Windows one signed in from Abuja on 12 August and has not been back. If that was not you, "
          "sign it out and change your passcode. I will not do either without you.", "16px")
  + ctabtn("Sign out everywhere else", "", "soon")
  + '<div style="display: flex; gap: 10px; align-items: flex-start">' + icon("lock", 16, INK3, 1.8, "; margin-top: 2px")
    + '<span style="font-size: 14px; font-weight: 500; line-height: 1.45; color: ' + INK3
    + '; text-wrap: pretty">Signing a device out never touches your money. It only means that device '
      'has to ask for your passcode again.</span></div>', 18)
devices += dockback("Ask about a device")
write("Devices", devices)


# ================= ONE NUMBER FOR HOW THE MONEY IS BEING HANDLED =================
# Five habits, one figure. Points instead of one score would turn this into a
# game people farm; five separate meters would turn it into homework. A single
# number moves slowly, which is the only honest speed for a habit.
#
# It is deliberately not a credit score and the screen says so, because in this
# market a number a bank keeps about you is assumed to be a number held against
# you, and a product that does not answer that suspicion never earns the habit.
def habitrow(name, note, val, ic, col, first=False):
    return ('<div' + hook("", "soon") + ' style="' + ('' if first else 'border-top: 1px solid ' + LINE + '; ')
      + 'display: flex; align-items: center; gap: 13px; height: 72px">'
      + badge(ic, None, 38, R_ICON, 20, on=FILL)
      + '<div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px">'
      '<span style="font-size: 16px; font-weight: 700; letter-spacing: -0.02em; color: ' + INK + '">' + name + '</span>'
      '<span style="font-size: 13px; font-weight: 400; color: ' + INK3 + '">' + note + '</span></div>'
      '<span class="num" style="font-size: 14px; font-weight: 700; white-space: nowrap; flex-shrink: 0; color: '
      + (INK2 if col != "amber" else IC["amber"]) + '">' + val + '</span></div>')

health = page(
  T("Money health", "One number for how you are handling it")
  + '<div style="' + cardstyle("20px") + '; display: flex; flex-direction: column; align-items: center; gap: 14px">'
    + ring(72, 180, 14, "", "out of 100", "")
    + '<div style="display: flex; align-items: center; gap: 6px">' + icon("up", 15, IN_TEXT, 2.6)
      + '<span style="font-size: 15px; font-weight: 700; color: ' + IN_TEXT + '">Up 4 since July</span></div></div>'
  + aline("Steadier than you were. The one thing holding it down is spending, which is up 18% on last month. "
          "Everything else is going the right way.", "16px")
  + '<div style="display: flex; flex-direction: column; gap: 12px">' + label("What moves it")
    + '<div style="' + cardstyle("2px 16px") + '; display: flex; flex-direction: column">'
      + habitrow("You check before you send", "Every transfer read before it left", "9 of 9", "check", "green", True)
      + habitrow("You save on payday", "Before it can go anywhere else", "3 months", "pot", "green")
      + habitrow("Your balance stays covered", "Dots in public, figures at home", "On", "eye", "green")
      + habitrow("Only you can open this", "Face ID, a passcode, and a limit", "On", "faceid", "green")
      + habitrow("You watch where it goes", "Against what you planned to spend", "18% over", "chart", "amber") + '</div></div>'
  + offer("Holding &#8358;5,000 back on payday would take this to 76 by October. Want me to set it up?",
          "Set it up", "SaveRule")
  + tinted('<span style="font-size: 16px; font-weight: 700; color: ' + ACC_INK + '">This is not a credit score</span>',
           "It never leaves this phone. No lender sees it, no bank is sent it, and it changes nothing about "
           "what you can borrow. It is here so you can watch your own habits, and for no other reason."), 18)
health += dockback("Ask me how to move it")
write("Health", health)

# ================= FEEDING A GOAL, AS A SHEET OVER THE GOAL =================
# It came up from the goal and it goes back to the goal, so it has a handle at
# the top and a word at the bottom middle. A back arrow would be a third way of
# doing what those two already do.
def saverow(name, sub, gain, ic, col, on=True, first=False, action=""):
    right = (switch(on) if not action else
      ('<div style="height: 32px; padding: 0 14px; border-radius: ' + PILL + '; background: ' + FILL
       + '; display: flex; align-items: center; flex-shrink: 0">'
       '<span style="font-size: 13px; font-weight: 700; color: ' + INK + '">' + action + '</span></div>'))
    return ('<div' + hook("", "soon") + ' style="' + ('' if first else 'border-top: 1px solid ' + LINE + '; ')
      + 'display: flex; align-items: center; gap: 13px; height: 76px">'
      + badge(ic, None, 40, R_ICON, 20)
      + '<div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px">'
      '<span style="font-size: 16px; font-weight: 700; letter-spacing: -0.02em; color: ' + INK + '">' + name + '</span>'
      '<span style="font-size: 13px; font-weight: 400; color: ' + INK3 + '">' + sub + '</span>'
      '<span class="num" style="font-size: 13px; font-weight: 700; color: '
      + (INK3 if action else IN_TEXT) + '">' + gain + '</span></div>'
      + right + '</div>')

saverule_inner = (
  '<div style="display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 2px 0 18px 0">'
  + badge("pot", None, 60, "19px", 29)
  + '<span style="font-size: 22px; font-weight: 700; letter-spacing: -0.025em; color: ' + INK + '; margin-top: 8px">Feed the Holiday goal</span>'
  + '<span style="font-size: 16px; font-weight: 400; color: ' + INK3 + '; text-align: center; text-wrap: pretty">'
    'Pick something that runs without you thinking about it</span></div>'
  + '<div style="display: flex; flex-direction: column">'
  + saverow("A slice of payday", "10% the day your salary lands", "&#8358;20,000 a month", "pot", "green", True, True)
  + saverow("Round ups", "The change from every card payment", "&#8358;2,280 a month", "swap", "blue", True)
  + saverow("Money back on top ups", "Cash back comes here instead of out", "&#8358;120 a month", "airtime", "purple", True)
  + saverow("A fixed amount", "You pick the day and the sum", "You choose", "plus", "black", False, False, "Set it") + '</div>'
  + '<div style="padding-top: 16px">'
  + tinted('<span style="font-size: 15px; font-weight: 700; color: ' + ACC_INK + '">None of this is locked away</span>',
           "Take any of it back the same day. No fee, no notice, and no question from me about why.") + '</div>')

write("SaveRule", goal + sheetup(saverule_inner))

# ================= THE SECOND POCKET =================
# A Nigerian who wants a stablecoin wants dollars that hold their value. So the
# product says Dollars. It does not say crypto, or USDT, or blockchain, or
# network, or gas, because none of those words is the thing being bought. The
# balance is held by a partner licensed for it; this app never holds a key, and
# says so on the screen rather than in a help centre.
#
# The naira-pegged coin is plumbing, not a pocket. It settles transfers at two
# in the morning and on a public holiday, which is a thing the user feels and
# never has to be told the name of. A third balance would be a third thing to
# understand in exchange for nothing.

def bigmoney(big, small, note=""):
    """A figure and what it is worth in the other currency, which is the only
    way a dollar balance means anything to somebody who is paid in naira."""
    return ('<div style="display: flex; flex-direction: column; gap: 6px">'
      + money(big, "", 40)
      + '<span class="num" style="font-size: 17px; font-weight: 400; color: ' + INK3 + '">' + small + '</span>'
      + (('<span style="font-size: 14px; font-weight: 400; color: ' + INK3 + '">' + note + '</span>') if note else '')
      + '</div>')

def raterow(rate, moved, up=True):
    """Today's rate, and which way it went. A number with no direction on it is
    the same number every day."""
    c = IN_TEXT if up else WARN_TEXT
    return ('<div style="' + cardstyle("14px 16px") + '; display: flex; align-items: center; gap: 12px">'
      + icon("chart", 20, INK2, 1.8)
      + '<span style="flex-grow: 1; font-size: 15px; font-weight: 400; color: ' + INK2 + '">' + rate + '</span>'
      + '<span class="num" style="font-size: 14px; font-weight: 700; white-space: nowrap; flex-shrink: 0; color: '
      + c + '">' + moved + '</span></div>')

def twoup(a, b):
    """Two pills on one line. Each takes half, because a pill told to fill its
    parent and given no basis takes all of it and sits on its neighbour."""
    return ('<div style="display: flex; gap: 10px">'
      '<div style="flex-grow: 1; flex-basis: 0; min-width: 0">' + a + '</div>'
      '<div style="flex-grow: 1; flex-basis: 0; min-width: 0">' + b + '</div></div>')

dollars = page(
  T("Dollars", "Steady when the naira is not, and yours to turn back any day")
  + '<div style="' + cardstyle("18px") + '; display: flex; flex-direction: column; gap: 16px">'
    + bigmoney("$412.60", "&#8358;640,300 at today&#8217;s rate")
    + twoup(pillbtn("Convert", "Convert", "", "swap", "black", True, 50),
            pillbtn("Send", "Pay", "", "send", "white", True, 50)) + '</div>'
  + raterow("&#8358;1,552 to the dollar today", "Up &#8358;18")
  + aline("You put these away in March at &#8358;1,410. Held in naira that same money would "
          "be worth &#8358;58,200 less than it is now.", "16px")
  + '<div style="display: flex; flex-direction: column; gap: 11px">' + label("Where they came from")
    + '<div style="display: flex; flex-direction: column">'
      + tx("Converted from naira", "swap", "12 August &#183; at &#8358;1,534", "$180.00", True)
      + tx("From Musa Danjuma", "down", "28 July &#183; for the generator", "$120.00", True)
      + tx("Converted from naira", "swap", "3 March &#183; at &#8358;1,410", "$112.60", True) + '</div></div>'
  + tinted('<span style="font-size: 16px; font-weight: 700; color: ' + ACC_INK + '">Nobody here holds a key</span>',
           "Your dollars sit with a custodian licensed by the SEC to hold them. Leorio moves them "
           "when you say so and cannot move them when you do not.")
  + '<div style="display: flex; gap: 9px; align-items: flex-start">' + icon("lock", 16, INK3, 1.6, "; margin-top: 2px")
    + '<span style="font-size: 14.5px; font-weight: 500; line-height: 1.45; color: ' + INK2
    + '; text-wrap: pretty">Turn any of it back to naira the same day. There is no notice and no lock.</span></div>', 15)
dollars += dockback("Ask me about your dollars")
write("Dollars", dollars)

# ---------- naira in, dollars out ----------
def pocketrow(name, sub, amount, last=False):
    return ('<div style="display: flex; align-items: center; gap: 12px; height: 62px'
      + ('' if last else '; border-bottom: 1px solid ' + LINE) + '">'
      + '<div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 1px">'
        '<span style="font-size: 13px; font-weight: 400; color: ' + INK3 + '">' + name + '</span>'
        '<span style="font-size: 16px; font-weight: 700; letter-spacing: -0.015em; color: ' + INK + '">' + sub + '</span></div>'
      + '<span class="num" style="font-size: 15px; font-weight: 500; white-space: nowrap; flex-shrink: 0; color: '
      + INK3 + '">' + amount + '</span></div>')

convert = page(
  T("Convert", "Naira into dollars, at the rate on this screen")
  + '<div style="position: relative; ' + cardstyle("2px 16px") + '">'
    + pocketrow("From", "Everyday", "&#8358;640,300 there")
    + pocketrow("To", "Dollars", "$412.60 there", True)
    + '<div style="position: absolute; right: 16px; top: 50%; margin-top: -18px; width: 36px; height: 36px; '
      'border-radius: ' + PILL + '; background: ' + SURF + '; ' + SH_RAISE + '; display: flex; align-items: center; '
      'justify-content: center">' + icon("swap", 18, INK, 1.9) + '</div></div>'
  + '<div style="' + cardstyle("18px") + '; display: flex; flex-direction: column; gap: 8px">'
    + caption("You are converting", INK2, 14)
    + '<div style="display: flex; align-items: baseline; gap: 1px">'
      '<span id="cvAmt" class="num" style="font-size: 40px; font-weight: 600; letter-spacing: -0.035em; line-height: 1; color: '
      + INK + '">&#8358;155,200</span>'
      '<div class="caret" style="width: 2px; height: 34px; background: ' + ACC + '; margin-left: 3px"></div></div>'
    + '<span class="num" style="font-size: 17px; font-weight: 400; color: ' + INK3 + '">You get about $100.00</span></div>'
  + '<div style="background: ' + SURF + '; border-radius: ' + R_FIELD + '; overflow: hidden; padding: 0 16px">'
    + plainrow("Rate", "&#8358;1,552 to $1", False, INK, False)
    + plainrow("Our fee", "Free under $500", False, IN_TEXT, False)
    + plainrow("You get", "$100.00", True, INK, False) + '</div>'
  + aline("The rate moved &#8358;18 your way this week. If you were waiting for a better day, this is one of them.", "16px")
  + '<div style="display: flex; gap: 9px; align-items: flex-start">' + icon("lock", 16, INK3, 1.6, "; margin-top: 2px")
    + '<span style="font-size: 14.5px; font-weight: 500; line-height: 1.45; color: ' + INK2
    + '; text-wrap: pretty">The rate is held for sixty seconds once you slide.</span></div>', 15)
convert += confirmbar(slide("Slide to convert", "Converted", "cvSlide"))
write("Convert", convert, "", True)

converted = page(
  T("Converted", "It is in your dollars already")
  + '<div style="display: flex; flex-direction: column; gap: 16px; align-items: flex-start">'
    + tickmark("", 56)
    + '<div style="display: flex; flex-direction: column; gap: 6px">' + money("$100.00", "", 40)
      + '<span style="font-size: 15px; color: ' + INK2 + '">From &#8358;155,200 in Everyday</span></div></div>'
  + '<div style="display: flex; flex-direction: column">'
    + plainrow("Rate you got", "&#8358;1,552 to $1")
    + plainrow("Fee", "Free", False, IN_TEXT)
    + plainrow("Dollars now", "$512.60", True) + '</div>'
  + offer("Dollars sitting still do nothing. Move &#8358;20,000 across on payday and you never have to think about it again.",
          "Set it up", "SaveRule")
  + '<div' + hook("Dollars") + ' style="display: flex; align-items: center; justify-content: center; gap: 6px; height: 44px">'
    '<span style="font-size: 14px; font-weight: 700; color: ' + ACC_TEXT + '">See your dollars</span>'
    + chev(11, ACC_TEXT_HEX, 2.2) + '</div>'
  + wrongrow("Something wrong with this?"), 16)
converted += dockback("Ask me about this")
write("Converted", converted)

# ================= OPENING AN ACCOUNT =================
# This is not six screens. It is one screen, six times.
#
# Every question the account needs is a row in one list, and that list is on
# screen from the first moment to the last. The question you are on is the only
# one that opens: its glyph takes its colour, its name grows, and the way to
# answer it appears underneath. The rest stay small and grey, above if they are
# answered and below if they are not, so at any moment you can see what you
# gave and what is still coming. That is the whole of the navigation. There is
# no progress bar, no step counter and no back arrow, because the list already
# says everything those would say and it says it in words.
#
# No question is ever ticked. One that is done simply goes quiet. The only tick
# on a question is the green one on the last row, and it means what it means
# because it is the only one in the run.
#
# Each question owns a colour, and the colour goes into the room rather than
# onto anything: a wash fills the top of the screen and is gone before it
# reaches the first word, so no text and no control ever sits on top of it. The
# six run cool to warm, and the last two screens have no wash at all. The flow
# starts strange and ends calm.
#
# Nigeria requires a BVN or a NIN on every account, so that question is not
# optional. The typing is: eleven digits come back with a name and a date of
# birth attached, and the person confirms rather than fills a form. Everything
# else the regulations want in the end can be handed over later, from a row on
# the Ready screen, which is the difference between ninety seconds and ten
# minutes at the one moment a person is deciding whether to bother.

# name, glyph, colour, the line under it when it is the one you are on
STEPS = [
  ("Your number", "phone",  "#22B8E8", "I will text you six digits to check the number is yours."),
  ("Who you are", "id",     "#8B5CF6", "Eleven digits from your NIN or your BVN, whichever you know. Your name comes back with them."),
  ("Your face",   "faceid", "#FF3B8E", "One photo, checked against the same record, so that only you can open this again."),
  ("A passcode",  "lock",   "#F5A524", "Six digits. These are what send your money, so pick something nobody watching could guess."),
]
LAST = ("Your account", "wait")

def _rgba(h, a):
    h = h.lstrip("#")
    return ('rgba(' + str(int(h[0:2], 16)) + ', ' + str(int(h[2:4], 16)) + ', '
            + str(int(h[4:6], 16)) + ', ' + str(a) + ')')

def steplight(hex):
    """The colour of the question you are on. It is light in the room: not a
    panel and not a card, so it has no edge to notice.

    It is given the space the list does not use rather than a height of its own,
    and it fades out inside that space. So it can never reach a word, and it
    retreats on its own as answered questions pile up. By the last question
    there is little left of it, and the two screens after that are white."""
    if not hex:
        return '<div style="flex-grow: 1; min-height: 0"></div>'
    return ('<div style="flex-grow: 1; min-height: 0; margin: 0 -20px; '
      'background: radial-gradient(126% 92% at 50% -6%, ' + _rgba(hex, 1) + ' 0%, ' + _rgba(hex, 0.95) + ' 30%, '
      + _rgba(hex, 0.5) + ' 58%, ' + _rgba(hex, 0.12) + ' 78%, ' + _rgba(hex, 0) + ' 92%)"></div>')

def qrow(name, ic, done=False):
    """A question you are not on. The glyph goes grey and the word goes grey,
    and an answered one looks the same as one not asked yet, because neither of
    them is what you are doing now. Nothing here is ticked."""
    return ('<div style="display: flex; align-items: center; gap: 14px; height: 40px">'
      '<div style="width: 26px; height: 26px; display: flex; align-items: center; justify-content: center; '
      'flex-shrink: 0">' + fglyph(ic, 23, INK4, BG) + '</div>'
      '<span style="font-size: 17px; font-weight: 400; color: ' + INK3 + '">' + name + '</span></div>')

def qopen(name, sub, ic, color):
    """The one you are on. The glyph is the only saturated thing at reading
    size on the screen, and the name is the only large one."""
    return ('<div style="display: flex; flex-direction: column; gap: 7px; padding: 2px 0">'
      + fglyph(ic, 30, color, BG)
      + '<span style="font-size: 30px; font-weight: 800; letter-spacing: -0.035em; line-height: 1.08; color: '
      + INK + '">' + name + '</span>'
      + '<span style="font-size: 15px; font-weight: 400; line-height: 1.42; color: ' + INK3
      + '; text-wrap: pretty">' + sub + '</span></div>')

def qdone(name, sub):
    """The end of it. One tick, green, and the only one in the flow."""
    return ('<div style="display: flex; gap: 14px; padding: 2px 0">' + tickmark("", 26)
      + '<div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 4px">'
      '<span style="font-size: 19px; font-weight: 700; letter-spacing: -0.02em; color: ' + INK + '">' + name + '</span>'
      '<span style="font-size: 15px; font-weight: 400; line-height: 1.42; color: ' + INK3
      + '; text-wrap: pretty">' + sub + '</span></div></div>')

def account(at, control="", tail="", sub=None, foot=120, steps=None, ahead=False, done=None, below=""):
    """One screen of a run of questions: the same list every time, with a
    different one of them open. `at` is which, counting from zero, and -1 and -2
    are the two screens that come after the questions run out.

    `ahead` says whether the questions not reached yet are drawn. Opening an
    account does not draw them, because a keypad is up and there is no room.
    Finishing setting up does, because it is optional and a person deciding
    whether to bother needs to see the whole of what they are agreeing to."""
    steps = steps or STEPS
    rows = ''
    for i, (name, ic, color, dsub) in enumerate(steps):
        if i > at >= 0 and not ahead:
            continue
        if i == at:
            rows += qopen(name, sub or dsub, ic, color)
            if control:
                rows += '<div style="padding-top: 14px">' + control + '</div>'
            if tail:
                rows += tail
        else:
            rows += qrow(name, ic)
    if at == -1:
        rows += ('<div style="display: flex; align-items: center; gap: 14px; height: 44px">'
          '<div style="width: 26px; height: 26px; display: flex; align-items: center; justify-content: center; '
          'flex-shrink: 0">' + fglyph("wait", 24, ACC_TEXT_HEX, BG) + '</div>'
          '<span style="font-size: 17px; font-weight: 700; letter-spacing: -0.02em; color: ' + INK
          + '">Opening your account</span></div>'
          '<span style="font-size: 15px; font-weight: 400; color: ' + INK3
          + '; padding-left: 40px">Hold on. This takes a few seconds.</span>')
    elif at == -2:
        d = done or ("Your account is ready", "Your number is 0102 4457 88, and money can reach it now.")
        rows += qdone(d[0], d[1])
        rows += tail
    rows += below                     # after the whole list, not inside it
    wash = steplight(steps[at][2] if 0 <= at < len(steps) else '')
    return ('<div class="pg" style="position: relative; height: 852px; padding: 0 20px; '
      'display: flex; flex-direction: column">' + wash
      + '<div class="pgin" style="position: relative; z-index: 1; flex-shrink: 0; padding-top: 24px; '
        'display: flex; flex-direction: column">' + rows + '</div>'
      + '<div style="height: ' + str(foot) + 'px; flex-shrink: 0"></div></div>')

def obfoot(text, go="", act="", back_btn=True, kind="black"):
    """Onboarding's bottom bar. Back keeps the corner it has everywhere else,
    and there is one thing to press."""
    return ('<div class="dock" style="position: absolute; left: 0; right: 0; bottom: 0; z-index: 3; '
      'padding: 30px 20px 26px 20px; background: linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.9) 34%, '
      + BG + ' 62%); display: flex; gap: 10px; align-items: center">'
      + (back() if back_btn else '<div style="width: 6px; flex-shrink: 0"></div>')
      + '<div style="flex-grow: 1; min-width: 0">' + pillbtn(text, go, act, "", kind, True, 56) + '</div></div>')

def bigfield(value, caret=True):
    """The answer, drawn as the biggest thing under the question, because it is
    the only thing under it."""
    return ('<div style="display: flex; align-items: baseline; gap: 1px; height: 46px">'
      '<span class="num" style="font-size: 30px; font-weight: 600; letter-spacing: -0.02em; color: ' + INK + '">' + value + '</span>'
      + ('<div class="caret" style="width: 2px; height: 28px; background: ' + ACC + '; margin-left: 3px"></div>' if caret else '')
      + '</div>')

NUMPAD_H = 336

def obkey(t="", glyph="", act=""):
    """A key. Smaller than the one the passcode gate uses, because that screen
    has a name and an amount above it and this one has six questions."""
    body = (glyph if glyph else '<span class="num" style="font-size: 24px; font-weight: 700; '
            'letter-spacing: -0.02em; color: ' + INK + '">' + t + '</span>')
    return ('<div' + hook("", act or ("pin|" + t)) + ' class="pinkey" style="width: 68px; height: 68px; border-radius: '
      + PILL + (('; background: ' + FILL) if not glyph else '')
      + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">' + body + '</div>')

def numpad():
    """The same keys the passcode uses. A phone number and an eleven digit NIN
    are both numbers, so neither of them deserves a different keyboard."""
    out = ''
    for r in (["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]):
        out += '<div style="display: flex; gap: 18px; justify-content: center">' + "".join(obkey(k) for k in r) + '</div>'
    out += ('<div style="display: flex; gap: 18px; justify-content: center">'
      '<div style="width: 68px; height: 68px; flex-shrink: 0"></div>' + obkey("0")
      + obkey("", icon("del", 26, INK2, 1.8), "pin|del") + '</div>')
    return ('<div class="dock" style="position: absolute; left: 0; right: 0; bottom: 0; z-index: 3; height: '
      + str(NUMPAD_H) + 'px; padding: 16px 20px 20px 20px; background: ' + BG
      + '; display: flex; flex-direction: column; gap: 8px">' + out + '</div>')

# ---------- the door ----------
# The same grammar as the flow it opens: one word lit, the rest ghosted. A
# person meets the pattern before they are asked to read it.
def wheelword(t, ic=None, color=None):
    on = ic is not None
    return ('<div style="display: flex; align-items: center; gap: 10px; height: 42px">'
      + (fglyph(ic, 26, color, BG) if on else '<div style="width: 26px; height: 26px"></div>')
      + '<span style="font-size: 30px; font-weight: 800; letter-spacing: -0.035em; color: '
      + (INK if on else FILL3) + '">' + t + '</span></div>')

start = ('<div class="pg" style="position: relative; height: 852px; padding: 0 20px; '
  'display: flex; flex-direction: column">'
  + steplight("#2A6AF5")
  + '<div class="pgin" style="position: relative; z-index: 1; flex-shrink: 0; '
    'display: flex; flex-direction: column; gap: 22px">'
  + '<div style="display: flex; flex-direction: column">'
    + wheelword("Save") + wheelword("Send", "send", "#2A6AF5") + wheelword("Spend")
    + wheelword("Ask") + '</div>'
  + '<div style="display: flex; flex-direction: column; gap: 10px">' + mark(40)
    + '<span style="font-size: 22px; font-weight: 700; letter-spacing: -0.025em; color: ' + INK + '">Leorio</span>'
    + '<span style="font-size: 16px; font-weight: 400; color: ' + INK3 + '; text-wrap: pretty">'
      'A bank that answers when you ask it something. Opening one takes about a minute, '
      'and all it needs is your number and your NIN.</span></div></div>'
  + '<div style="height: 164px; flex-shrink: 0"></div></div>')
start += ('<div class="dock" style="position: absolute; left: 0; right: 0; bottom: 0; z-index: 3; '
  'padding: 30px 20px 26px 20px; display: flex; flex-direction: column; gap: 6px; align-items: center">'
  + '<div style="width: 100%">' + pillbtn("Open an account", "Number", "", "", "black", True, 56) + '</div>'
  + '<div' + hook("Signin") + ' style="display: flex; align-items: center; justify-content: center; gap: 6px; height: 44px">'
    '<span style="font-size: 15px; font-weight: 400; color: ' + INK3 + '">Already have one?</span>'
    '<span style="font-size: 15px; font-weight: 700; color: ' + ACC_TEXT + '">Sign in</span></div></div>')
write("Start", start)

# ---------- one ----------
number = account(0, bigfield("0803 214 4471"), foot=NUMPAD_H) + numpad()
write("Number", number, "", True)

# ---------- two ----------
code = account(0, '<div style="display: flex; justify-content: flex-start">' + pindots(4, 6) + '</div>',
  sub="Six digits, sent to 0803 214 4471 a moment ago.", foot=NUMPAD_H, tail=
  '<div' + hook("", "soon") + ' style="display: flex; align-items: center; gap: 6px; height: 38px">'
  '<span style="font-size: 14px; font-weight: 700; color: ' + ACC_TEXT + '">I did not get it</span>'
  + chev(11, ACC_TEXT_HEX, 2.2) + '</div>') + numpad()
write("Code", code, "", True)

# ---------- three ----------
nin = account(1, bigfield("1234 5678 90"), foot=NUMPAD_H) + numpad()
write("Nin", nin, "", True)

# ---------- four: the model reads it back ----------
who = account(1,
  '<div style="' + cardstyle("16px") + '; display: flex; flex-direction: column; gap: 12px">'
  + '<div style="display: flex; align-items: center; gap: 14px">' + avatar("IM", 48, FILL3, INK2)
    + '<div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px">'
      '<span style="font-size: 19px; font-weight: 700; letter-spacing: -0.02em; color: ' + INK + '">Ibrahim Musa</span>'
      '<span class="num" style="font-size: 14px; font-weight: 400; color: ' + INK3 + '">Born 14 June 1996</span></div></div>'
  + '<div style="height: 1px; background: ' + LINE + '"></div>'
  + rowline("On the record as", "IBRAHIM MUSA WENG", True) + '</div>',
  '<div' + hook("", "soon") + ' style="display: flex; align-items: center; gap: 6px; height: 40px">'
  '<span style="font-size: 14px; font-weight: 700; color: ' + ACC_TEXT + '">Something here is wrong</span>'
  + chev(11, ACC_TEXT_HEX, 2.2) + '</div>',
  sub="This came back from the record against those digits. I did not type it.")
who += obfoot("Yes, that is me", "Face")
write("Who", who)

# ---------- five ----------
face = account(2,
  '<div style="position: relative; height: 232px; border-radius: ' + R_CARD + '; background: ' + FILL
  + '; overflow: hidden; display: flex; align-items: center; justify-content: center">'
  # 200 is not a radius, it is a way of saying "as round as this box can be".
  # Both the browser and the extractor clamp it to half the shorter side, so
  # the oval stays an oval and snap() leaves it alone.
  + '<div style="width: 138px; height: 168px; border-radius: 200px; border: 3px solid ' + ACC
    + '; margin-bottom: 26px; display: flex; align-items: flex-end; justify-content: center; padding-bottom: 14px">'
    + icon("person", 58, LINE2, 1.4) + '</div>'
  + '<span style="position: absolute; left: 0; right: 0; bottom: 14px; text-align: center; font-size: 14px; '
    'font-weight: 500; color: ' + INK2 + '">Hold still and look at the camera</span></div>',
  '<div style="display: flex; gap: 9px; align-items: flex-start; padding-top: 12px">'
  + icon("eye", 16, INK3, 1.6, "; margin-top: 2px")
  + '<span style="font-size: 14px; font-weight: 400; line-height: 1.45; color: ' + INK2
  + '; text-wrap: pretty">The photo is kept on this phone. It is not a profile picture and nobody else sees it.</span></div>')
face += obfoot("Take it", "Passcode")
write("Face", face)

# ---------- six ----------
passcode = account(3, '<div style="display: flex; justify-content: flex-start">' + pindots(3, 6) + '</div>',
  foot=NUMPAD_H, tail=
  '<div style="display: flex; gap: 9px; align-items: flex-start; padding-top: 10px">'
  + icon("lock", 16, INK3, 1.6, "; margin-top: 2px")
  + '<span style="font-size: 14px; font-weight: 400; line-height: 1.45; color: ' + INK2
  + '; text-wrap: pretty">Not your year of birth, and not 123456.</span></div>') + numpad()
write("Passcode", passcode, "", True)

# ---------- the few seconds it actually takes ----------
opening = account(-1, foot=60)
write("Opening", opening, "", True)

# ---------- and in ----------
def canrow(t, on=True, last=False):
    return ('<div style="display: flex; align-items: center; gap: 12px; height: 50px'
      + ('' if last else '; border-bottom: 1px solid ' + LINE) + '">'
      + (tickmark("", 20) if on
         else '<div style="width: 20px; height: 20px; border-radius: ' + PILL + '; border: 1.5px dashed ' + LINE2
              + '; flex-shrink: 0"></div>')
      + '<span style="flex-grow: 1; font-size: 15px; font-weight: 500; color: ' + (INK if on else INK3) + '">' + t + '</span></div>')

ready = account(-2, "", foot=118, tail=
  '<div style="padding-top: 18px; display: flex; flex-direction: column; gap: 14px">'
  + '<div style="' + cardstyle("2px 16px") + '; display: flex; flex-direction: column">'
    + canrow("Receive money from any Nigerian bank")
    + canrow("Send up to &#8358;50,000 a day")
    + canrow("Buy airtime, data and pay bills")
    + canrow("Hold dollars", False)
    + canrow("Send up to &#8358;1,000,000 a day", False, True) + '</div>'
  + '<div' + hook("Finish") + ' style="' + bordered("14px", "22px") + ' display: flex; align-items: center; gap: 12px">'
    + rowglyph("shield", ACC_TEXT_HEX, SURF, 24, 32)
    + '<div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 1px">'
      '<span style="font-size: 15px; font-weight: 700; letter-spacing: -0.015em; color: ' + INK + '">Finish setting up</span>'
      '<span style="font-size: 13px; font-weight: 400; color: ' + INK3 + '">Two minutes, and the last two come on</span></div>'
    + chevbtn() + '</div></div>')
ready += obfoot("Take me in", "Main", "", False)
write("Ready", ready)

# ---------- the part that waits ----------
# The same list, a second time. Three more questions, weeks later, from a row on
# the Ready screen rather than from a cold start.
#
# One thing is drawn differently here and it is on purpose. In the first run the
# questions not reached yet are not on the screen, because a keypad is up and
# there is no room for them. Here they are, greyed, below the open one. This run
# is optional, so a person is deciding whether to bother at all, and they cannot
# decide that without seeing the whole of what they are agreeing to.
#
# Nothing here blocks anything. Whatever is finished is kept, and the account
# carries on working at the limits it already has.

MORE = [
  ("Where you live", "home", "#FF8A4C",
   "Street, town and state. No utility bill, and nothing arrives in the post."),
  ("A photo of an ID", "camera", "#FF3B8E",
   "A driver&#8217;s licence, a passport or a voter&#8217;s card. Any of the three will do."),
  ("Where your money comes from", "receive", "#8B5CF6",
   "One tap. It is the last question, and every bank has to ask it."),
]
MORE_DONE = ("Everything is on", "You can send a million naira a day and hold dollars now.")

def quietnote(ic, t):
    """A line that is not an instruction and not a warning. It sits under the
    control at the smallest size on the screen, for the person who wants to know
    why before they answer."""
    return ('<div style="display: flex; gap: 9px; align-items: flex-start; padding-top: 12px">'
      + icon(ic, 16, INK3, 1.6, "; margin-top: 2px")
      + '<span style="font-size: 14px; font-weight: 400; line-height: 1.45; color: ' + INK2
      + '; text-wrap: pretty">' + t + '</span></div>')

def typedfield(v, hint=""):
    """Somewhere to have typed. The answer is the biggest thing in the field and
    the field is quiet around it, because the field is not the point."""
    return ('<div style="background: ' + FILL + '; border-radius: ' + R_FIELD + '; padding: 14px 16px; '
      'display: flex; flex-direction: column; gap: 4px">'
      '<div style="display: flex; align-items: center">'
      '<span style="font-size: 17px; font-weight: 700; letter-spacing: -0.02em; color: ' + INK + '">' + v + '</span>'
      + '<div class="caret" style="width: 2px; height: 20px; background: ' + ACC + '; margin-left: 3px"></div></div>'
      + (('<span style="font-size: 13px; font-weight: 400; color: ' + INK3 + '">' + hint + '</span>') if hint else '')
      + '</div>')

def pickline(t, on=False, last=False):
    """One of a few answers, drawn as bare rows rather than tiles. The list of
    questions above it is bare, and an answer to one of them should not arrive
    looking heavier than the question."""
    mark = (tickmark("", 22) if on else
      '<div style="width: 22px; height: 22px; border-radius: ' + PILL + '; border: 1.5px solid ' + LINE2
      + '; flex-shrink: 0"></div>')
    return ('<div' + hook("", "soon") + ' style="display: flex; align-items: center; gap: 14px; height: 56px'
      + ('' if last else '; border-bottom: 1px solid ' + LINE) + '">'
      '<span style="flex-grow: 1; font-size: 17px; font-weight: 400; color: ' + INK + '">' + t + '</span>'
      + mark + '</div>')

# ---------- one ----------
# The reason to bother goes under the whole list, because it is the reason for
# all three questions and not for the one that happens to be open.
finish = account(0, typedfield("12 Bode Thomas Street", "Surulere, Lagos State"), "",
  foot=118, steps=MORE, ahead=True,
  below='<div style="padding-top: 20px; display: flex; flex-direction: column; gap: 10px">'
    + label("What it opens")
    + '<div style="' + cardstyle("2px 16px") + '; display: flex; flex-direction: column">'
      + canrow("Send up to &#8358;1,000,000 a day", False)
      + canrow("Hold dollars", False)
      + canrow("Borrow against your history", False, True) + '</div>'
    + quietnote("lock", "This is the same check every Nigerian bank runs. We ask once, and we do not sell it.")
    + '</div>')
finish += obfoot("Continue", "Idcard")
write("Finish", finish)

# ---------- two ----------
idcard = account(1,
  '<div style="position: relative; height: 196px; border-radius: ' + R_CARD + '; background: ' + FILL
  + '; overflow: hidden; display: flex; align-items: center; justify-content: center">'
  + '<div style="width: 246px; height: 152px; border-radius: 16px; border: 3px solid ' + ACC
    + '; margin-bottom: 22px"></div>'
  + '<span style="position: absolute; left: 0; right: 0; bottom: 14px; text-align: center; font-size: 14px; '
    'font-weight: 500; color: ' + INK2 + '">Lay it flat and fill the frame</span></div>',
  quietnote("eye", "I read the name and the number off it and keep nothing else. The photo does not leave your phone."),
  foot=118, steps=MORE, ahead=True)
idcard += obfoot("Take it", "Income")
write("Idcard", idcard)

# ---------- three ----------
income = account(2,
  '<div style="display: flex; flex-direction: column">'
  + pickline("A salary", True)
  + pickline("My own business")
  + pickline("Family or friends")
  + pickline("Something else", False, True) + '</div>',
  "", foot=118, steps=MORE, ahead=True)
income += obfoot("Continue", "Full")
write("Income", income)

# ---------- and the limits come off ----------
full = account(-2, "", "", foot=118, steps=MORE, ahead=True, done=MORE_DONE,
  below='<div style="padding-top: 18px">'
  + '<div style="' + cardstyle("2px 16px") + '; display: flex; flex-direction: column">'
    + canrow("Send up to &#8358;1,000,000 a day")
    + canrow("Hold dollars")
    + canrow("Borrow against your history")
    + canrow("Everything you could already do", True, True) + '</div></div>')
full += obfoot("Take me in", "Main", "", False)
write("Full", full)

# ================= COMING BACK, AND NOT GETTING IN =================
# Two things the flows promised and did not draw. The Sign in link on the door
# went nowhere, and there was no screen for the one question in opening an
# account that can actually fail.

def plaintop(title, sub, ic=None, color=None, wash="#2A6AF5"):
    """The head of a screen that is not part of a run. Same shape as an open
    question, without a list above it, because there is nothing settled yet."""
    return (steplight(wash)
      + '<div class="pgin" style="position: relative; z-index: 1; flex-shrink: 0; padding-top: 24px; '
        'display: flex; flex-direction: column; gap: 7px">'
      + (fglyph(ic, 30, color, BG) if ic else mark(30))
      + '<span style="font-size: 30px; font-weight: 800; letter-spacing: -0.035em; line-height: 1.08; color: '
      + INK + '">' + title + '</span>'
      + '<span style="font-size: 15px; font-weight: 400; line-height: 1.42; color: ' + INK3
      + '; text-wrap: pretty">' + sub + '</span>')

def plainpage(inner, foot=NUMPAD_H):
    return ('<div class="pg" style="position: relative; height: 852px; padding: 0 20px; '
      'display: flex; flex-direction: column">' + inner + '</div>'
      + '<div style="height: ' + str(foot) + 'px; flex-shrink: 0"></div></div>')

# ---------- the door swings both ways ----------
signin = plainpage(
  plaintop("Welcome back", "Your number, and then six digits from a text. Nothing else, because "
           "the account is already yours.")
  + '<div style="padding-top: 14px">' + bigfield("0803 214 4471") + '</div>') + numpad()
write("Signin", signin, "", True)

signcode = plainpage(
  plaintop("Six digits", "Sent to 0803 214 4471 a moment ago. On a phone I already know, your "
           "passcode alone would have been enough.")
  + '<div style="padding-top: 14px; display: flex; justify-content: flex-start">' + pindots(4, 6) + '</div>'
  + '<div' + hook("", "soon") + ' style="display: flex; align-items: center; gap: 6px; height: 38px">'
    '<span style="font-size: 14px; font-weight: 700; color: ' + ACC_TEXT + '">I did not get it</span>'
  + chev(11, ACC_TEXT_HEX, 2.2) + '</div>') + numpad()
write("Signcode", signcode, "", True)

# ---------- when the digits come back with nobody attached ----------
# The one question in opening an account that can fail on its own. Eleven digits
# either match a record or they do not, and a person who mistyped one of them
# needs to be told that and nothing worse. It is not a refusal, so the screen
# does not look like one: the same amber a hard stop uses, said once, and the
# way back is the button.
nomatch = account(1,
  '<div style="' + cardstyle("16px") + '; display: flex; flex-direction: column; gap: 10px">'
  + '<div style="display: flex; align-items: center; gap: 12px">'
    + rowglyph("warn", IC["amber"], SURF, 26, 34)
    + '<span style="font-size: 17px; font-weight: 700; letter-spacing: -0.02em; color: ' + INK
    + '">Nothing came back</span></div>'
  + '<span style="font-size: 15px; font-weight: 400; line-height: 1.45; color: ' + INK2
    + '; text-wrap: pretty">No record matches 1234 5678 90. One wrong digit is the usual reason, '
      'so it is worth reading them again.</span></div>',
  aline("If the digits are right and it still says this, your BVN will work instead. It is the "
        "same eleven digits from a different register.", "16px")
  + '<div' + hook("", "soon") + ' style="display: flex; align-items: center; gap: 6px; height: 40px">'
    '<span style="font-size: 14px; font-weight: 700; color: ' + ACC_TEXT + '">Talk to someone</span>'
  + chev(11, ACC_TEXT_HEX, 2.2) + '</div>',
  sub="Eleven digits from your NIN or your BVN. These ones did not match anything.",
  foot=118, steps=STEPS)
nomatch += obfoot("Try again", "Nin")
write("Nomatch", nomatch)

# ================= WHICH POCKET IT LEAVES FROM =================
# Dollars are not a destination in this product. They are a property of money,
# so you meet them where money moves: here on the way out, and on the Receive
# sheet on the way in. A person who never holds a dollar never opens either.
#
# It came up from the send screen and it goes back to it, so it is a sheet with
# a handle and a word at the bottom, not a page with a back arrow.

def pocketpick(name, sub, ic, on=False, last=False, go=""):
    """A place the money can leave from. The one it is leaving from now carries
    the tick, because a list of two with nothing marked is a question rather
    than an answer."""
    mark = (tickmark("", 22) if on else
      '<div style="width: 22px; height: 22px; border-radius: ' + PILL + '; border: 1.5px solid ' + LINE2
      + '; flex-shrink: 0"></div>')
    return ('<div' + hook(go, "" if go else "soon") + ' style="display: flex; align-items: center; gap: 14px; height: 76px'
      + ('' if last else '; border-bottom: 1px solid ' + LINE) + '">'
      + badge(ic, None, 44, R_ICON, 22)
      + '<div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px">'
        '<span style="font-size: 17px; font-weight: 700; letter-spacing: -0.02em; color: ' + INK + '">' + name + '</span>'
        '<span class="num" style="font-size: 14px; font-weight: 400; color: ' + INK3 + '">' + sub + '</span></div>'
      + mark + '</div>')

payfrom_inner = (
  '<div style="display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 2px 0 18px 0">'
  + badge("send", None, 60, "19px", 29)
  + '<span style="font-size: 22px; font-weight: 700; letter-spacing: -0.025em; color: ' + INK + '; margin-top: 8px">Pay from</span>'
  + '<span style="font-size: 16px; font-weight: 400; color: ' + INK3 + '; text-align: center; text-wrap: pretty">'
    'Two places the money can leave</span></div>'
  + '<div style="display: flex; flex-direction: column">'
  + pocketpick("Everyday", "&#8358;640,300 in naira", "bank", True)
  + pocketpick("Dollars", "$412.60, about &#8358;640,300 today", "dollar", False, True, "PayDollars") + '</div>'
  + '<div style="padding-top: 14px">'
  + aline("Sarah is paid in naira either way. From dollars I convert at the rate on the "
          "next screen, and you see it before anything moves.", "16px") + '</div>')

write("PayFrom", pay + sheetup(payfrom_inner))

if EMIT:
    print("built:", ", ".join(sorted(f for f in os.listdir(OUT) if f.endswith(".dc.html"))))
