# Generates the .dc.html artboards for the AI banking design canvas.
# Light corporate direction. Run: python3 build.py
import os
OUT = os.path.dirname(os.path.abspath(__file__))

ACC = "{{accent}}"
BG      = "#F4F5F7"
SURF    = "#FFFFFF"
FILL    = "#EEF0F4"
LINE    = "#E2E6EC"
LINE2   = "#D5DAE2"
INK     = "#0F1521"
INK2    = "#5A6472"
INK3    = "#8A94A3"
IN      = "#0E7C5A"
WARN    = "#B0453A"
SHADOW  = "box-shadow: 0 1px 2px rgba(15,21,33,0.05)"
SERIF   = "font-family: 'Newsreader', Georgia, 'Times New Roman', serif"

import base64
_FDIR = os.path.join(OUT, "fonts")
_FCACHE = {}
def _b64(name):
    if name not in _FCACHE:
        _FCACHE[name] = base64.b64encode(open(os.path.join(_FDIR, name), "rb").read()).decode("ascii")
    return _FCACHE[name]

def faces(italic=False):
    # Google's webfont subsets leave out the Naira sign, so the fonts ride
    # inside each screen instead. See fonts/README.md.
    out = ("    @font-face { font-family: 'Libre Franklin'; font-style: normal; font-weight: 400 700;"
           " src: url(data:font/woff2;base64," + _b64("LibreFranklin-subset.woff2") + ") format('woff2'); font-display: block; }\n"
           "    @font-face { font-family: 'Newsreader'; font-style: normal; font-weight: 400 500;"
           " src: url(data:font/woff2;base64," + _b64("Newsreader-subset.woff2") + ") format('woff2'); font-display: block; }\n")
    if italic:
        out += ("    @font-face { font-family: 'Newsreader'; font-style: italic; font-weight: 400;"
                " src: url(data:font/woff2;base64," + _b64("NewsreaderItalic-subset.woff2") + ") format('woff2'); font-display: block; }\n")
    return out

def head(anim="", italic=False):
    return ('<!doctype html>\n<html>\n<head>\n  <meta charset="utf-8">\n'
      '  <script src="./support.js"></script>\n</head>\n<body>\n<x-dc>\n<helmet>\n'
      '  <style>\n' + faces(italic) +
      '    * { box-sizing: border-box; }\n'
      '    body { margin: 0; background: ' + BG + '; font-family: \'Libre Franklin\', \'Helvetica Neue\', Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased; }\n'
      '    a { color: #1B3B6F; } a:hover { color: #142C53; }\n'
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

NAIRA = "&#8358;"
def write(name, inner, anim="", italic=False):
    inner = inner.replace(NAIRA, '<span style="margin-right: 0.09em">' + NAIRA + '</span>')
    open(os.path.join(OUT, name + ".dc.html"), "w").write(head(anim, italic) + screen(inner) + FOOT)

# ---------- shared pieces ----------

def mark(size=20, color=ACC, extra=""):
    s = str(size)
    return ('<svg width="' + s + '" height="' + s + '" viewBox="0 0 20 20" fill="none" style="color: ' + color
            + '; flex-shrink: 0' + extra + '"><circle cx="10" cy="10" r="7.3" stroke="currentColor" stroke-width="1.4" opacity="0.4"/>'
            '<circle cx="10" cy="10" r="3.5" fill="currentColor"/></svg>')

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
 "mic": '<rect x="9.4" y="3" width="5.2" height="9.6" rx="2.6"/><path d="M5.6 11.2a6.4 6.4 0 0 0 12.8 0M12 17.6V21"/>',
}

def icon(name, size=22, color=INK2, sw=1.5, extra=""):
    s = str(size)
    return ('<svg width="' + s + '" height="' + s + '" viewBox="0 0 24 24" fill="none" stroke="' + color
            + '" stroke-width="' + str(sw) + '" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink: 0'
            + extra + '">' + ICONS[name] + '</svg>')

def chev(size=13, color=INK3, sw=1.6):
    s = str(size)
    return ('<svg width="' + s + '" height="' + s + '" viewBox="0 0 14 14" fill="none" style="flex-shrink: 0">'
            '<path d="M5 3l4 4-4 4" stroke="' + color + '" stroke-width="' + str(sw) + '" stroke-linecap="round" stroke-linejoin="round"/></svg>')

def back():
    return ('<div style="width: 40px; height: 40px; border-radius: 20px; background: ' + SURF + '; border: 1px solid ' + LINE
            + '; display: flex; align-items: center; justify-content: center; margin-left: -4px; flex-shrink: 0">'
            '<svg width="19" height="19" viewBox="0 0 20 20" fill="none"><path d="M12 4.5 6.5 10l5.5 5.5" stroke="' + INK2
            + '" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg></div>')

def topbar(title="", right=""):
    t = ''
    if title:
        t = '<span style="flex-grow: 1; text-align: center; font-size: 16px; font-weight: 600; letter-spacing: -0.01em">' + title + '</span>'
    r = right if right else '<div style="width: 40px; flex-shrink: 0"></div>'
    return ('<div style="display: flex; align-items: center; height: 44px; gap: 8px">' + back() + t + r + '</div>')

def askbar(placeholder, height=118, tabbar=False):
    inner = ('<div style="flex-grow: 1; height: 56px; border-radius: 28px; background: ' + SURF + '; border: 1px solid ' + LINE2
        + '; ' + SHADOW + '; display: flex; align-items: center; gap: 12px; padding: 0 19px">'
        + mark(20) + '<span style="flex-grow: 1; ' + SERIF + '; font-size: 16px; color: ' + INK3 + '">' + placeholder + '</span>'
        + icon("mic", 18, INK3, 1.5) + '</div>')
    return ('<div style="position: absolute; left: 0; right: 0; bottom: 0; height: ' + str(height)
        + 'px; background: linear-gradient(180deg, rgba(244,245,247,0) 0%, rgba(244,245,247,0.92) 36%, ' + BG
        + ' 64%); display: flex; align-items: flex-end; padding: 0 20px 30px 20px"><div style="display: flex; width: 100%; gap: 10px; align-items: center">'
        + inner + '</div></div>')

def cardstyle(pad="16px", radius="16px", bg=SURF, extra=""):
    return ('background: ' + bg + '; border: 1px solid ' + LINE + '; border-radius: ' + radius
            + '; padding: ' + pad + '; ' + SHADOW + extra)

def tinted(inner, note, pad="13px 15px"):
    return ('<div style="border-radius: 13px; background: color-mix(in srgb, ' + ACC + ' 7%, ' + SURF
        + '); border: 1px solid color-mix(in srgb, ' + ACC + ' 32%, transparent); padding: ' + pad
        + '; display: flex; flex-direction: column; gap: 6px">' + inner
        + '<span style="font-size: 11px; font-weight: 500; letter-spacing: 0.02em; color: color-mix(in srgb, '
        + ACC + ' 86%, ' + INK2 + ')">' + note + '</span></div>')

def slide(label):
    return ('<div style="height: 60px; border-radius: 30px; background: ' + SURF + '; border: 1px solid ' + LINE2
        + '; ' + SHADOW + '; display: flex; align-items: center; padding: 5px">'
        '<div style="width: 50px; height: 50px; border-radius: 25px; background: ' + ACC
        + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
        '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M4 10h11M11 6l4 4-4 4" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></div>'
        '<span class="num" style="flex-grow: 1; text-align: center; font-size: 15.5px; font-weight: 600; color: ' + INK2
        + '; margin-right: 50px">' + label + '</span></div>')

def aline(text, size="17.5px"):
    return ('<div style="display: flex; gap: 10px; align-items: flex-start">' + mark(20, ACC, "; margin-top: 3px")
        + '<div style="' + SERIF + '; font-size: ' + size + '; line-height: 1.42; color: ' + INK
        + '; text-wrap: pretty">' + text + '</div></div>')

def label(t, color=INK3):
    return '<div style="font-size: 9.5px; font-weight: 700; letter-spacing: 0.16em; color: ' + color + '">' + t + '</div>'

def money(whole, dec, size=50, dsize=24, color=INK):
    return ('<div style="display: flex; align-items: baseline; gap: 1px">'
        '<span class="num" style="font-size: ' + str(size) + 'px; font-weight: 600; letter-spacing: -0.035em; line-height: 1; color: '
        + color + '">' + whole + '</span><span class="num" style="font-size: ' + str(dsize)
        + 'px; font-weight: 500; letter-spacing: -0.02em; color: ' + INK3 + '">' + dec + '</span></div>')

def page(inner, gap=14, top=54):
    return ('<div style="padding: ' + str(top) + 'px 20px 0 20px; display: flex; flex-direction: column; gap: '
            + str(gap) + 'px">\n' + inner + '\n</div>')

# ================= HOME =================
def svc_tile(name, ic, big=True):
    return ('<div style="flex-grow: 1; flex-basis: 0; display: flex; flex-direction: column; align-items: center; gap: 7px">'
      '<div style="width: 100%; height: 60px; border-radius: 16px; background: ' + SURF + '; border: 1px solid ' + LINE
      + '; ' + SHADOW + '; display: flex; align-items: center; justify-content: center">' + icon(ic, 22, ACC, 1.6) + '</div>'
      '<span style="font-size: 11px; font-weight: 500; color: ' + INK2 + '">' + name + '</span></div>')

home = page(
  '<div style="display: flex; align-items: center; justify-content: space-between; height: 44px">'
    '<div style="display: flex; flex-direction: column; gap: 4px">' + label("EVERYDAY ACCOUNT")
      + '<span class="num" style="font-size: 12px; color: ' + INK3 + '; letter-spacing: 0.07em">0102 4457 88</span></div>'
    '<div style="width: 38px; height: 38px; border-radius: 19px; background: ' + SURF + '; border: 1px solid ' + LINE2
      + '; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 600; color: ' + INK2 + '">IW</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 12px">' + money("&#8358;248,320", ".75", 48, 23)
    + '<div style="display: flex; gap: 20px; align-items: center">'
      '<div style="display: flex; align-items: center; gap: 7px">'
        '<svg width="13" height="13" viewBox="0 0 14 14" fill="none"><path d="M7 2.5v9M3.6 8.1 7 11.5l3.4-3.4" stroke="' + IN + '" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
        '<span class="num" style="font-size: 13.5px; font-weight: 500; color: ' + INK2 + '">&#8358;640,000 in</span></div>'
      '<div style="display: flex; align-items: center; gap: 7px">'
        '<svg width="13" height="13" viewBox="0 0 14 14" fill="none"><path d="M7 11.5v-9M3.6 5.9 7 2.5l3.4 3.4" stroke="' + INK3 + '" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
        '<span class="num" style="font-size: 13.5px; font-weight: 500; color: ' + INK2 + '">&#8358;391,680 out</span></div></div></div>'
  + '<div style="display: flex; gap: 10px">' + svc_tile("Airtime","airtime") + svc_tile("Data","data")
      + svc_tile("Power","power") + svc_tile("Send","send") + svc_tile("More","more") + '</div>'
  + '<div style="display: flex; align-items: center; gap: 9px; padding-top: 2px">' + mark(20)
      + '<span style="' + SERIF + '; font-size: 15.5px; color: ' + INK2 + '">Three things this morning</span></div>'
  + '<div style="display: flex; flex-direction: column; gap: 11px">'

    + '<div style="' + cardstyle("15px 15px 14px 15px", "18px") + '; display: flex; flex-direction: column; gap: 12px">'
      '<div style="display: flex; align-items: center; gap: 7px">'
        '<div style="width: 6px; height: 6px; border-radius: 3px; background: ' + ACC + '"></div>' + label("DUE ON THURSDAY", ACC) + '</div>'
      '<div style="' + SERIF + '; font-size: 16.5px; line-height: 1.42; text-wrap: pretty">Your Ikeja Electric bill lands on Thursday. Last month it was &#8358;7,500.</div>'
      '<div style="display: flex; gap: 9px; align-items: center">'
        '<div style="flex-grow: 1; height: 46px; border-radius: 23px; background: ' + ACC + '; color: #FFFFFF; display: flex; align-items: center; justify-content: center; font-size: 14.5px; font-weight: 600">Pay &#8358;8,000 now</div>'
        '<div style="width: 46px; height: 46px; border-radius: 23px; border: 1px solid ' + LINE2 + '; background: ' + SURF + '; display: flex; align-items: center; justify-content: center">'
        '<svg width="15" height="15" viewBox="0 0 16 16" fill="none"><path d="M4.5 4.5l7 7M11.5 4.5l-7 7" stroke="' + INK3 + '" stroke-width="1.6" stroke-linecap="round"/></svg></div></div></div>'

    + '<div style="' + cardstyle("15px", "18px") + '; display: flex; flex-direction: column; gap: 12px">'
      '<div style="' + SERIF + '; font-size: 16.5px; line-height: 1.42; text-wrap: pretty">Your data usually runs out about now. The same 5GB is &#8358;2,500.</div>'
      '<div style="display: flex; align-items: center; gap: 11px; height: 46px; border-radius: 13px; background: ' + FILL + '; padding: 0 14px">'
        + icon("data", 20, INK2, 1.6)
        + '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 1px">'
          '<span style="font-size: 13.5px; font-weight: 600">5GB for 30 days</span>'
          '<span style="font-size: 11.5px; color: ' + INK3 + '">MTN &#183; your line</span></div>'
        '<span class="num" style="font-size: 14px; font-weight: 600">&#8358;2,500</span></div>'
      '<div style="display: flex; align-items: center; gap: 6px; height: 30px">'
        '<span style="font-size: 14px; font-weight: 600; color: ' + ACC + '">Buy it again</span>' + chev(13, ACC) + '</div></div>'

    + '<div style="' + cardstyle("15px", "18px") + '; display: flex; flex-direction: column; gap: 12px">'
      '<div style="' + SERIF + '; font-size: 16.5px; line-height: 1.42">You spent &#8358;86,400 on food last month.</div></div>'
  + '</div>', 14) + askbar("Ask, or just say what you need", 132)
write("Main", home)

# ================= ALL SERVICES =================
def grid_tile(name, ic):
    return ('<div style="flex-grow: 1; flex-basis: 0; display: flex; flex-direction: column; align-items: center; gap: 8px">'
      '<div style="width: 100%; height: 64px; border-radius: 17px; background: ' + SURF + '; border: 1px solid ' + LINE
      + '; ' + SHADOW + '; display: flex; align-items: center; justify-content: center">' + icon(ic, 23, ACC, 1.6) + '</div>'
      '<span style="font-size: 11px; font-weight: 500; color: ' + INK2 + '; text-align: center">' + name + '</span></div>')

def listrow(name, ic, sub="", last=False):
    border = "" if last else "border-bottom: 1px solid " + LINE + "; "
    s = ''
    if sub:
        s = '<span style="font-size: 11.5px; color: ' + INK3 + '">' + sub + '</span>'
    return ('<div style="' + border + 'display: flex; align-items: center; gap: 13px; height: 54px; padding: 0 14px">'
      '<div style="width: 36px; height: 36px; border-radius: 11px; background: ' + FILL
      + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">' + icon(ic, 19, INK2, 1.6) + '</div>'
      '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 2px">'
      '<span style="font-size: 14.5px; font-weight: 500">' + name + '</span>' + s + '</div>' + chev() + '</div>')

services = page(
  topbar("All services")
  + '<div style="height: 52px; border-radius: 26px; background: ' + SURF + '; border: 1px solid ' + LINE2 + '; ' + SHADOW
    + '; display: flex; align-items: center; gap: 11px; padding: 0 17px">' + icon("search", 19, INK3, 1.6)
    + '<span style="flex-grow: 1; ' + SERIF + '; font-size: 15.5px; color: ' + INK3 + '">Search, or say what you need</span>'
    + icon("mic", 18, INK3, 1.5) + '</div>'
  + '<div style="display: flex; flex-direction: column; gap: 12px">' + label("YOU USE THESE MOST")
    + '<div style="display: flex; gap: 10px">' + grid_tile("Airtime","airtime") + grid_tile("Data","data") + grid_tile("Power","power") + grid_tile("Send","send") + '</div>'
    + '<div style="display: flex; gap: 10px">' + grid_tile("Cable TV","tv") + grid_tile("Betting","bet") + grid_tile("Loan","loan") + grid_tile("Cards","card") + '</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 11px">' + label("BILLS")
    + '<div style="background: ' + SURF + '; border: 1px solid ' + LINE + '; border-radius: 16px; ' + SHADOW + '; overflow: hidden">'
      + listrow("Internet", "globe", "Spectranet, Smile, Starlink")
      + listrow("Water", "water", "State water boards")
      + listrow("Waste", "waste", "LAWMA and others")
      + listrow("School fees", "school", "WAEC, JAMB, tuition", True) + '</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 11px">' + label("SAVE AND BORROW")
    + '<div style="background: ' + SURF + '; border: 1px solid ' + LINE + '; border-radius: 16px; ' + SHADOW + '; overflow: hidden">'
      + listrow("Savings pot", "pot", "Put money aside")
      + listrow("Fixed savings", "clock", "Lock it for a set time", True) + '</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 11px">' + label("MONEY")
    + '<div style="background: ' + SURF + '; border: 1px solid ' + LINE + '; border-radius: 16px; ' + SHADOW + '; overflow: hidden">'
      + listrow("Request money", "request", "Ask someone to pay you")
      + listrow("Send abroad", "globe", "Pounds, dollars and euros", True) + '</div></div>', 15)
services += ('<div style="position: absolute; left: 0; right: 0; bottom: 0; height: 90px; background: linear-gradient(180deg, rgba(244,245,247,0) 0%, '
  + BG + ' 72%)"></div>')
write("Services", services)

def offer(text, action):
    return ('<div style="' + cardstyle("14px", "16px") + '; display: flex; flex-direction: column; gap: 10px">'
      '<div style="display: flex; gap: 10px; align-items: flex-start">' + mark(19, ACC, "; margin-top: 2px")
      + '<div style="' + SERIF + '; font-size: 15.5px; line-height: 1.4; text-wrap: pretty">' + text + '</div></div>'
      '<div style="display: flex; align-items: center; gap: 6px; height: 30px">'
      '<span style="font-size: 14px; font-weight: 600; color: ' + ACC + '">' + action + '</span>' + chev(13, ACC) + '</div></div>')

def quote(t):
    return ('<div style="display: flex; flex-direction: column; gap: 8px">' + label("YOU SAID")
      + '<span style="' + SERIF + '; font-size: 17px; font-style: italic; color: ' + INK2 + '">' + t + '</span></div>')

def avatar(t, size=38, bg=FILL, fg=INK2):
    s = str(size)
    return ('<div style="width: ' + s + 'px; height: ' + s + 'px; border-radius: ' + str(size//2) + 'px; background: ' + bg
      + '; display: flex; align-items: center; justify-content: center; font-size: ' + str(round(size*0.36,1))
      + 'px; font-weight: 600; color: ' + fg + '; flex-shrink: 0">' + t + '</div>')

def plainrow(k, v, last=False, vcolor=INK, chevron=False):
    border = "" if last else "border-bottom: 1px solid " + LINE + "; "
    c = chev() if chevron else ""
    return ('<div style="' + border + 'display: flex; align-items: center; height: 50px; padding: 0 15px; gap: 10px">'
      '<span style="flex-grow: 1; font-size: 13.5px; color: ' + INK2 + '">' + k + '</span>'
      '<span class="num" style="font-size: 14.5px; font-weight: 500; color: ' + vcolor + '">' + v + '</span>' + c + '</div>')

def bundle(size, price):
    return ('<div style="flex-grow: 1; flex-basis: 0; height: 56px; border-radius: 14px; background: ' + SURF
      + '; border: 1px solid ' + LINE2 + '; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px">'
      '<span style="font-size: 13.5px; font-weight: 600">' + size + '</span>'
      '<span class="num" style="font-size: 11.5px; color: ' + INK3 + '">' + price + '</span></div>')

# ================= BUY AIRTIME / DATA =================
airtime = page(
  topbar()
  + quote("2k data for mum")
  + aline("5GB for 30 days, on your mum&#8217;s MTN line.")
  + '<div style="' + cardstyle("14px", "18px") + '; display: flex; flex-direction: column; gap: 10px">'
    + tinted('<div style="display: flex; align-items: center; gap: 12px">' + avatar("M")
        + '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 2px">'
          '<span style="font-size: 15px; font-weight: 600">Mum</span>'
          '<span class="num" style="font-size: 12.5px; color: ' + INK2 + '">0803 214 4471 &#183; MTN</span></div>' + chev() + '</div>',
        "The number you top up most")
    + tinted('<div style="display: flex; align-items: center; gap: 12px">' + icon("data", 21, INK2, 1.6)
        + '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 2px">'
          '<span style="font-size: 15px; font-weight: 600">5GB for 30 days</span>'
          '<span style="font-size: 12.5px; color: ' + INK2 + '">It will not renew on its own</span></div>'
        '<span class="num" style="font-size: 16px; font-weight: 600">&#8358;2,500</span></div>',
        "The bundle you bought last month")
    + '<div style="border: 1px solid ' + LINE + '; border-radius: 13px; overflow: hidden">'
      + plainrow("From", "Everyday &#183; 0102 4457 88", False, INK, True)
      + plainrow("You get back", "&#8358;25", True, IN) + '</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 11px">' + label("OTHER BUNDLES")
    + '<div style="display: flex; gap: 8px">' + bundle("1GB", "&#8358;800") + bundle("2GB", "&#8358;1,500") + bundle("10GB", "&#8358;4,000") + '</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 11px">' + label("YOU ALSO TOP UP")
    + '<div style="display: flex; gap: 14px; align-items: center">'
      + avatar("D", 46) + avatar("K", 46) + avatar("B", 46) + avatar("T", 46)
      + '<div style="width: 46px; height: 46px; border-radius: 23px; border: 1px dashed ' + LINE2
      + '; display: flex; align-items: center; justify-content: center">' + icon("plus", 18, INK3, 1.7) + '</div></div></div>', 15)
airtime += ('<div style="position: absolute; left: 0; right: 0; bottom: 0; padding: 30px 20px 30px 20px; background: linear-gradient(180deg, rgba(244,245,247,0) 0%, '
  + BG + ' 40%)">' + slide("Slide to buy &#8358;2,500") + '</div>')
write("Airtime", airtime, "", True)

# ================= ELECTRICITY, PAID =================
power = page(
  topbar()
  + '<div style="display: flex; flex-direction: column; gap: 14px; align-items: flex-start">'
    '<div style="width: 52px; height: 52px; border-radius: 26px; background: color-mix(in srgb, ' + ACC
      + ' 10%, ' + SURF + '); border: 1px solid color-mix(in srgb, ' + ACC + ' 26%, transparent); display: flex; align-items: center; justify-content: center">'
      + icon("check", 24, ACC, 2.0) + '</div>'
    '<div style="display: flex; flex-direction: column; gap: 5px">' + money("&#8358;8,000", "", 38, 20)
      + '<span style="font-size: 14px; color: ' + INK2 + '">Paid to Ikeja Electric</span></div></div>'
  + aline("Type this into your meter. I have sent it to your messages as well.", "16.5px")
  + '<div style="' + cardstyle("16px", "18px") + '; display: flex; flex-direction: column; gap: 12px">'
    + label("METER TOKEN")
    + '<span class="num" style="font-size: 21px; font-weight: 600; letter-spacing: 0.02em; color: ' + INK + '">4471 8823 0195 6640 3277</span>'
    + '<div style="display: flex; align-items: center; justify-content: center; gap: 8px; height: 46px; border-radius: 23px; background: ' + FILL + '">'
      + icon("copy", 17, ACC, 1.6) + '<span style="font-size: 14px; font-weight: 600; color: ' + ACC + '">Copy the token</span></div></div>'
  + '<div style="background: ' + SURF + '; border: 1px solid ' + LINE + '; border-radius: 16px; ' + SHADOW + '; overflow: hidden">'
    + plainrow("Meter", "0102 4457 8891")
    + plainrow("Units", "38.4 kWh")
    + plainrow("Reference", "IKJ-90441-2286", True) + '</div>'
  + offer("Want me to pay this every month when the bill lands?", "Set it up"), 15)
power += ('<div style="position: absolute; left: 0; right: 0; bottom: 0; padding: 30px 20px 30px 20px; display: flex; gap: 10px; background: linear-gradient(180deg, rgba(244,245,247,0) 0%, '
  + BG + ' 40%)">'
  '<div style="flex-grow: 1; height: 52px; border-radius: 26px; background: ' + SURF + '; border: 1px solid ' + LINE2
  + '; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 14.5px; font-weight: 600; color: ' + INK2 + '">Share receipt</div>'
  '<div style="flex-grow: 1; height: 52px; border-radius: 26px; background: ' + ACC
  + '; display: flex; align-items: center; justify-content: center; font-size: 14.5px; font-weight: 600; color: #FFFFFF">Done</div></div>')
write("Power", power)

# ================= BILLS =================
def chip(t, color, bg):
    return ('<span style="font-size: 10.5px; font-weight: 600; letter-spacing: 0.03em; color: ' + color
      + '; background: ' + bg + '; border-radius: 9px; padding: 4px 8px; white-space: nowrap">' + t + '</span>')

def bill(name, ic, sub, amount, chp, last=False, dim=False):
    border = "" if last else "border-bottom: 1px solid " + LINE + "; "
    nc = INK3 if dim else INK
    return ('<div style="' + border + 'display: flex; align-items: center; gap: 13px; height: 64px; padding: 0 15px">'
      '<div style="width: 38px; height: 38px; border-radius: 11px; background: ' + FILL
      + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">' + icon(ic, 19, INK2, 1.6) + '</div>'
      '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 3px">'
      '<span style="font-size: 14.5px; font-weight: 500; color: ' + nc + '">' + name + '</span>'
      '<div style="display: flex; align-items: center; gap: 7px"><span style="font-size: 11.5px; color: ' + INK3 + '">' + sub + '</span>' + chp + '</div></div>'
      '<span class="num" style="font-size: 14.5px; font-weight: 600; color: ' + nc + '">' + amount + '</span></div>')

bills = page(
  topbar("Bills")
  + '<div style="' + cardstyle("16px", "18px") + '; display: flex; gap: 10px; align-items: flex-start">' + mark(20, ACC, "; margin-top: 2px")
    + '<div style="' + SERIF + '; font-size: 16.5px; line-height: 1.42; text-wrap: pretty">&#8358;34,500 of bills this month. Two of them are not covered yet.</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 11px">' + label("THIS MONTH")
    + '<div style="background: ' + SURF + '; border: 1px solid ' + LINE + '; border-radius: 16px; ' + SHADOW + '; overflow: hidden">'
      + bill("Ikeja Electric", "power", "Due Thursday", "&#8358;8,000", chip("I PAY IT", "#FFFFFF", ACC))
      + bill("DStv Compact", "tv", "Due 24 August", "&#8358;12,500", chip("NOT COVERED", WARN, "rgba(176,69,58,0.10)"))
      + bill("Spectranet", "globe", "Due 27 August", "&#8358;15,000", chip("NOT COVERED", WARN, "rgba(176,69,58,0.10)"))
      + bill("LAWMA waste", "waste", "Paid 2 August", "&#8358;2,000", chip("PAID", IN, "rgba(14,124,90,0.10)"), False, True)
      + bill("MTN 5GB", "data", "Paid 4 August", "&#8358;2,500", chip("PAID", IN, "rgba(14,124,90,0.10)"), True, True) + '</div></div>'
  + '<div style="height: 50px; border-radius: 25px; border: 1px solid ' + LINE2 + '; background: ' + SURF
    + '; display: flex; align-items: center; justify-content: center; gap: 9px">' + icon("plus", 17, ACC, 1.8)
    + '<span style="font-size: 14.5px; font-weight: 600; color: ' + ACC + '">Add a bill</span></div>'
  + offer("DStv and Spectranet are the two nobody is watching. Want me to pay them as well?", "Set both up"), 14) + askbar("Ask about your bills", 118)
write("Bills", bills)

# ================= LOAN =================
def rowline(k, v, last=False, strong=False, vcolor=INK):
    border = "" if last else "border-bottom: 1px solid " + LINE + "; "
    kw = "600" if strong else "400"
    ks = "14px" if strong else "13.5px"
    vs = "17px" if strong else "14.5px"
    kc = INK if strong else INK2
    return ('<div style="' + border + 'display: flex; align-items: center; height: 46px; padding: 0 15px; gap: 10px">'
      '<span style="flex-grow: 1; font-size: ' + ks + '; font-weight: ' + kw + '; color: ' + kc + '">' + k + '</span>'
      '<span class="num" style="font-size: ' + vs + '; font-weight: 600; color: ' + vcolor + '">' + v + '</span></div>')

def dchip(t, on):
    if on:
        return ('<div style="flex-grow: 1; flex-basis: 0; height: 44px; border-radius: 12px; background: ' + ACC
          + '; display: flex; align-items: center; justify-content: center; font-size: 13.5px; font-weight: 600; color: #FFFFFF">' + t + '</div>')
    return ('<div style="flex-grow: 1; flex-basis: 0; height: 44px; border-radius: 12px; background: ' + SURF
      + '; border: 1px solid ' + LINE2 + '; display: flex; align-items: center; justify-content: center; font-size: 13.5px; font-weight: 500; color: ' + INK2 + '">' + t + '</div>')

loan = page(
  topbar("Loan")
  + aline("You asked what you could borrow. Here is the whole cost before you decide.", "17px")
  + '<div style="' + cardstyle("16px", "18px") + '; display: flex; flex-direction: column; gap: 14px">'
    + label("HOW MUCH YOU WANT")
    + '<div style="display: flex; align-items: center; gap: 14px">'
      '<div style="width: 42px; height: 42px; border-radius: 21px; border: 1px solid ' + LINE2
      + '; display: flex; align-items: center; justify-content: center">' + icon("minus", 17, INK2, 1.8) + '</div>'
      '<div style="flex-grow: 1; display: flex; justify-content: center">' + money("&#8358;150,000", "", 32, 18) + '</div>'
      '<div style="width: 42px; height: 42px; border-radius: 21px; border: 1px solid ' + LINE2
      + '; display: flex; align-items: center; justify-content: center">' + icon("plus", 17, INK2, 1.8) + '</div></div>'
    + '<div style="display: flex; flex-direction: column; gap: 7px">'
      '<div style="height: 6px; border-radius: 3px; background: ' + FILL + '; overflow: hidden"><div style="width: 60%; height: 6px; border-radius: 3px; background: ' + ACC + '"></div></div>'
      '<div style="display: flex; justify-content: space-between"><span class="num" style="font-size: 11px; color: ' + INK3 + '">&#8358;10,000</span>'
      '<span class="num" style="font-size: 11px; color: ' + INK3 + '">&#8358;250,000 is your limit</span></div></div>'
    + '<div style="display: flex; gap: 9px">' + dchip("30 days", False) + dchip("60 days", False) + dchip("90 days", True) + '</div></div>'
  + '<div style="background: ' + SURF + '; border: 1px solid ' + LINE + '; border-radius: 16px; ' + SHADOW + '; overflow: hidden">'
    + rowline("You get today", "&#8358;150,000")
    + rowline("Interest, 4% a month", "&#8358;18,000")
    + rowline("One off fee", "&#8358;1,500")
    + rowline("You pay back in all", "&#8358;169,500", False, True)
    + rowline("Three payments of", "&#8358;56,500")
    + rowline("First payment", "19 September", True) + '</div>'
  + '<div style="display: flex; gap: 9px; align-items: flex-start">' + icon("lock", 16, INK3, 1.6, "; margin-top: 2px")
    + '<span style="' + SERIF + '; font-size: 14.5px; line-height: 1.4; color: ' + INK2
    + '; text-wrap: pretty">Pay late and it costs &#8358;2,000 a day. Late loans are reported to the credit bureau.</span></div>', 14)
loan += ('<div style="position: absolute; left: 0; right: 0; bottom: 0; padding: 30px 20px 30px 20px; background: linear-gradient(180deg, rgba(244,245,247,0) 0%, '
  + BG + ' 40%)">' + slide("Slide to take &#8358;150,000") + '</div>')
write("Loan", loan)

# ================= VIRTUAL CARD =================
def act(name, ic):
    return ('<div style="flex-grow: 1; flex-basis: 0; display: flex; flex-direction: column; align-items: center; gap: 8px">'
      '<div style="width: 100%; height: 52px; border-radius: 15px; background: ' + SURF + '; border: 1px solid ' + LINE
      + '; ' + SHADOW + '; display: flex; align-items: center; justify-content: center">' + icon(ic, 20, ACC, 1.6) + '</div>'
      '<span style="font-size: 11px; font-weight: 500; color: ' + INK2 + '">' + name + '</span></div>')

vcard = page(
  topbar("Virtual card")
  + '<div style="height: 194px; border-radius: 20px; background: ' + ACC + '; padding: 20px; display: flex; flex-direction: column; justify-content: space-between; '
    + SHADOW + '">'
    '<div style="display: flex; align-items: flex-start; justify-content: space-between">'
      + mark(24, "#FFFFFF") + '<span style="font-size: 10px; font-weight: 700; letter-spacing: 0.16em; color: rgba(255,255,255,0.7)">NETFLIX ONLY</span></div>'
    '<div style="width: 34px; height: 25px; border-radius: 5px; background: rgba(255,255,255,0.22); border: 1px solid rgba(255,255,255,0.28); display: flex; flex-direction: column; justify-content: center; gap: 3px; padding: 0 5px">'
      '<div style="height: 1.5px; background: rgba(255,255,255,0.45)"></div>'
      '<div style="height: 1.5px; background: rgba(255,255,255,0.45)"></div></div>'
    '<div style="display: flex; flex-direction: column; gap: 16px">'
      '<span class="num" style="font-size: 20px; font-weight: 500; letter-spacing: 0.12em; color: #FFFFFF">5399 &#8226;&#8226;&#8226;&#8226; &#8226;&#8226;&#8226;&#8226; 4471</span>'
      '<div style="display: flex; align-items: flex-end; justify-content: space-between">'
        '<div style="display: flex; flex-direction: column; gap: 4px">'
          '<span style="font-size: 9px; font-weight: 600; letter-spacing: 0.14em; color: rgba(255,255,255,0.55)">CARD HOLDER</span>'
          '<span style="font-size: 13px; font-weight: 500; letter-spacing: 0.06em; color: #FFFFFF">IBRAHIM WENG</span></div>'
        '<div style="display: flex; flex-direction: column; gap: 4px">'
          '<span style="font-size: 9px; font-weight: 600; letter-spacing: 0.14em; color: rgba(255,255,255,0.55)">EXPIRES</span>'
          '<span class="num" style="font-size: 13px; font-weight: 500; color: #FFFFFF">09/28</span></div>'
        '</div></div></div>'
  + '<div style="display: flex; gap: 10px">' + act("Reveal","search") + act("Freeze","freeze") + act("Fund","plus") + act("Rules","list") + '</div>'
  + '<div style="' + cardstyle("15px", "16px") + '; display: flex; gap: 10px; align-items: flex-start">' + mark(19, ACC, "; margin-top: 2px")
    + '<div style="' + SERIF + '; font-size: 15.5px; line-height: 1.4; text-wrap: pretty">This card has paid Netflix four times, &#8358;21,000 in all.</div></div>'
  + '<div style="' + cardstyle("15px", "16px") + '; display: flex; flex-direction: column; gap: 11px">'
    + '<div style="display: flex; align-items: baseline; justify-content: space-between">'
      '<span style="font-size: 13.5px; color: ' + INK2 + '">Spent this month</span>'
      '<span class="num" style="font-size: 15px; font-weight: 600">&#8358;21,000 of &#8358;50,000</span></div>'
    + '<div style="height: 7px; border-radius: 4px; background: ' + FILL + '; overflow: hidden"><div style="width: 42%; height: 7px; border-radius: 4px; background: ' + ACC + '"></div></div>'
    + '<span class="num" style="font-size: 12px; color: ' + INK3 + '">&#8358;29,000 left before it stops working</span></div>'
  + '<div style="height: 50px; border-radius: 25px; border: 1px solid ' + LINE2 + '; background: ' + SURF
    + '; display: flex; align-items: center; justify-content: center; gap: 9px">' + icon("plus", 17, ACC, 1.8)
    + '<span style="font-size: 14.5px; font-weight: 600; color: ' + ACC + '">Make another card</span></div>', 14) + askbar("Ask about this card", 118)
write("Card", vcard)

# ================= ASKING BY VOICE =================
ANIM = ('    @keyframes sweep { 0% { transform: translateX(-22%); } 100% { transform: translateX(22%); } }\n'
        '    .sweep { animation: sweep 2.6s ease-in-out infinite alternate; }\n')

def wave():
    hs = [10,18,30,14,38,24,44,20,32,12,26,40,16,28,10,22,34,14,8,18,10,6]
    ops = [0.3,0.5,0.7,0.5,1,0.8,1,0.7,0.85,0.4,0.7,1,0.5,0.75,0.3,0.6,0.85,0.35,0.25,0.4,0.22,0.18]
    out = '<div style="display: flex; align-items: center; gap: 3px; height: 44px">'
    for h, o in zip(hs, ops):
        out += ('<div style="width: 3px; height: ' + str(h) + 'px; border-radius: 2px; background: ' + ACC
                + '; opacity: ' + str(o) + '"></div>')
    return out + '</div>'

def sugg(t):
    return ('<div style="height: 44px; border-radius: 22px; border: 1px solid ' + LINE2 + '; background: ' + SURF
      + '; display: flex; align-items: center; padding: 0 16px; font-size: 14px; font-weight: 500; color: ' + INK2 + '">' + t + '</div>')

ask = ('<div style="padding: 54px 20px 0 20px; display: flex; flex-direction: column; gap: 15px; opacity: 0.42">'
  '<div style="display: flex; align-items: center; justify-content: space-between; height: 44px">'
    '<div style="display: flex; flex-direction: column; gap: 4px">' + label("EVERYDAY ACCOUNT")
    + '<span class="num" style="font-size: 12px; color: ' + INK3 + '; letter-spacing: 0.07em">0102 4457 88</span></div>'
    '<div style="width: 38px; height: 38px; border-radius: 19px; background: ' + SURF + '; border: 1px solid ' + LINE2 + '"></div></div>'
  + money("&#8358;248,320", ".75", 48, 23)
  + '<div style="display: flex; gap: 10px">' + svc_tile("Airtime","airtime") + svc_tile("Data","data")
    + svc_tile("Power","power") + svc_tile("Send","send") + svc_tile("More","more") + '</div></div>')
ask += ('<div style="position: absolute; left: 0; right: 0; top: 318px; bottom: 0; background: ' + SURF
  + '; border-top-left-radius: 28px; border-top-right-radius: 28px; box-shadow: 0 -10px 30px rgba(15,21,33,0.09); overflow: hidden; display: flex; flex-direction: column">'
  '<div style="height: 2px; width: 100%; overflow: hidden; flex-shrink: 0"><div class="sweep" style="height: 2px; width: 100%; background: linear-gradient(90deg, rgba(0,0,0,0) 0%, '
  + ACC + ' 50%, rgba(0,0,0,0) 100%)"></div></div>'
  '<div style="display: flex; justify-content: center; padding: 12px 0 0 0"><div style="width: 38px; height: 4px; border-radius: 2px; background: ' + LINE2 + '"></div></div>'
  '<div style="padding: 24px 20px 16px 20px; display: flex; flex-direction: column; gap: 22px; flex-grow: 1">'
    '<div style="display: flex; align-items: center; gap: 9px">' + mark(20) + label("LISTENING", ACC) + '</div>'
    '<div style="' + SERIF + '; font-size: 27px; line-height: 1.32; color: ' + INK + '; text-wrap: pretty">send 2k airtime to<span style="color: ' + INK3 + '"> mum</span></div>'
    + wave()
    + '<div style="display: flex; flex-direction: column; gap: 12px">' + label("OR TRY ONE OF THESE")
      + '<div style="display: flex; flex-direction: column; gap: 8px">'
      + sugg("Pay my light bill") + sugg("How much did I spend on data?") + sugg("What can I borrow?") + '</div></div></div>'
  '<div style="padding: 0 20px 30px 20px; display: flex; gap: 10px; align-items: center">'
    '<div style="flex-grow: 1; height: 56px; border-radius: 28px; background: color-mix(in srgb, ' + ACC + ' 8%, ' + SURF
    + '); border: 1px solid ' + ACC + '; display: flex; align-items: center; justify-content: center">'
    '<span style="font-size: 15px; font-weight: 600; color: ' + ACC + '">Release to send</span></div>'
    '<div style="width: 56px; height: 56px; border-radius: 28px; background: ' + FILL + '; border: 1px solid ' + LINE2
    + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">'
    '<div style="width: 14px; height: 14px; border-radius: 3px; background: ' + INK3 + '"></div></div></div></div>')
write("Ask", ask, ANIM)

# ================= ANSWER =================
def bar(h, accent=False):
    c = ACC if accent else "#C7CEDA"
    lc = INK2 if accent else INK3
    return ('<div style="flex-grow: 1; display: flex; flex-direction: column; justify-content: flex-end; gap: 9px; align-items: center">'
      '<div style="width: 58%; height: ' + str(h) + 'px; border-radius: 5px; background: ' + c + '"></div>'
      '<span style="font-size: 10px; color: ' + lc + '">MONTH</span></div>')

def barm(h, m, accent=False):
    return bar(h, accent).replace("MONTH", m)

def mrow(name, ic, count, amount, last=False):
    return ('<div style="display: flex; align-items: center; gap: 12px">'
      '<div style="width: 36px; height: 36px; border-radius: 11px; background: ' + FILL
      + '; display: flex; align-items: center; justify-content: center; flex-shrink: 0">' + icon(ic, 18, INK2, 1.6) + '</div>'
      '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 2px">'
      '<span style="font-size: 14.5px; font-weight: 500">' + name + '</span>'
      '<span class="num" style="font-size: 12px; color: ' + INK3 + '">' + count + '</span></div>'
      '<span class="num" style="font-size: 14.5px; font-weight: 600">' + amount + '</span></div>')

def qchip(t):
    return ('<div style="height: 44px; border-radius: 12px; border: 1px solid ' + LINE2 + '; background: ' + SURF
      + '; display: flex; align-items: center; gap: 6px; padding: 0 11px">'
      '<span style="font-size: 13px; font-weight: 500; color: ' + INK + '">' + t + '</span>'
      '<svg width="11" height="11" viewBox="0 0 12 12" fill="none"><path d="M3 4.5 6 7.5l3-3" stroke="' + INK3 + '" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></div>')

answer = page(
  '<div style="display: flex; align-items: center; justify-content: space-between; height: 44px; gap: 12px">' + back()
    + '<div style="display: flex; flex-direction: column; align-items: flex-end; gap: 3px">' + label("YOU ASKED")
    + '<span style="font-size: 13px; color: ' + INK2 + '">how much do I spend on airtime and data</span></div></div>'
  + aline("&#8358;18,900 on airtime and data last month. That is your highest month this year.")
  + '<div style="' + cardstyle("18px 16px 8px 16px", "20px") + '; display: flex; flex-direction: column; gap: 18px">'
    + '<div style="display: flex; align-items: flex-end; justify-content: space-between">' + money("&#8358;18,900", "", 40, 20)
      + '<div style="display: flex; align-items: center; gap: 5px; height: 28px; padding: 0 11px; border-radius: 14px; background: rgba(176,69,58,0.10); margin-bottom: 4px">'
      '<svg width="11" height="11" viewBox="0 0 12 12" fill="none"><path d="M6 9.5v-7M3 5.5 6 2.5l3 3" stroke="' + WARN + '" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
      '<span class="num" style="font-size: 12.5px; font-weight: 600; color: ' + WARN + '">&#8358;4,200</span></div></div>'
    + '<div style="display: flex; gap: 9px; height: 84px; align-items: stretch">'
      + barm(38,"Feb") + barm(50,"Mar") + barm(41,"Apr") + barm(56,"May") + barm(47,"Jun") + barm(68,"Jul", True) + '</div>'
    + '<div style="display: flex; flex-wrap: wrap; gap: 7px">' + qchip("Airtime and data") + qchip("Last month") + '</div>'
    + '<div style="border-top: 1px solid ' + LINE + '; display: flex; align-items: center; gap: 9px; height: 48px">'
      + icon("list", 15, INK3, 1.5)
      + '<span class="num" style="flex-grow: 1; font-size: 12.5px; color: ' + INK3 + '">Added up from 14 top ups, 1 to 31 July</span>' + chev() + '</div></div>'
  + '<div style="display: flex; flex-direction: column; gap: 13px">' + label("WHERE IT WENT")
    + '<div style="display: flex; flex-direction: column; gap: 15px">'
    + mrow("MTN data", "data", "5 top ups", "&#8358;12,500")
    + mrow("MTN airtime", "airtime", "7 top ups", "&#8358;4,400")
    + mrow("Glo airtime", "airtime", "2 top ups", "&#8358;2,000") + '</div></div>'
  + '<div style="' + cardstyle("14px", "16px") + '; display: flex; gap: 10px; align-items: flex-start">' + mark(19, ACC, "; margin-top: 2px")
    + '<div style="' + SERIF + '; font-size: 15.5px; line-height: 1.4; text-wrap: pretty">A 10GB monthly plan is &#8358;4,000 and would save you about &#8358;1,800.</div></div>', 13) + askbar("Ask about this", 118)
write("Answer", answer)

# ================= SEND MONEY =================
pay = page(
  topbar()
  + quote("send Sarah 50k for the flat deposit")
  + aline("Here it is, ready to go. Check the three parts I filled in.")
  + '<div style="' + cardstyle("14px", "18px") + '; display: flex; flex-direction: column; gap: 10px">'
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
    + '<div style="border: 1px solid ' + LINE + '; border-radius: 13px; overflow: hidden">'
      + plainrow("From", "Everyday &#183; 0102 4457 88", False, INK, True)
      + plainrow("Arrives", "In a few seconds", False, INK, True)
      + plainrow("Fee", "Free", True, IN) + '</div></div>'
  + '<div style="display: flex; gap: 9px; align-items: flex-start">' + icon("lock", 16, INK3, 1.6, "; margin-top: 2px")
    + '<span style="' + SERIF + '; font-size: 14.5px; line-height: 1.4; color: ' + INK2
    + '; text-wrap: pretty">Nothing moves until you slide. Face ID checks it after that.</span></div>', 15)
pay += ('<div style="position: absolute; left: 0; right: 0; bottom: 0; padding: 30px 20px 30px 20px; background: linear-gradient(180deg, rgba(244,245,247,0) 0%, '
  + BG + ' 40%)">' + slide("Slide to send &#8358;50,000") + '</div>')
write("Pay", pay, "", True)

# ================= STANDING INSTRUCTIONS =================
def switch(on):
    if on:
        return ('<div style="width: 50px; height: 30px; border-radius: 15px; background: ' + ACC
          + '; padding: 3px; display: flex; justify-content: flex-end; flex-shrink: 0; margin-top: 2px">'
          '<div style="width: 24px; height: 24px; border-radius: 12px; background: #FFFFFF"></div></div>')
    return ('<div style="width: 50px; height: 30px; border-radius: 15px; background: #D7DCE4'
      '; padding: 3px; display: flex; justify-content: flex-start; flex-shrink: 0; margin-top: 2px">'
      '<div style="width: 24px; height: 24px; border-radius: 12px; background: #FFFFFF; border: 1px solid ' + LINE2 + '"></div></div>')

def rule(title, desc, log, link, on):
    tc = INK if on else INK3
    dc = INK2 if on else INK3
    foot = ''
    if log:
        foot = ('<div style="display: flex; align-items: center; height: 30px; border-top: 1px solid ' + LINE + '; padding-top: 4px">'
          '<span class="num" style="flex-grow: 1; font-size: 12px; color: ' + INK3 + '">' + log + '</span>'
          '<span style="font-size: 13px; font-weight: 600; color: ' + ACC + '">' + link + '</span></div>')
    return ('<div style="' + cardstyle("14px", "16px") + '; display: flex; flex-direction: column; gap: 11px">'
      '<div style="display: flex; align-items: flex-start; gap: 14px">'
      '<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 6px">'
      '<span style="font-size: 15.5px; font-weight: 600; color: ' + tc + '">' + title + '</span>'
      '<span style="' + SERIF + '; font-size: 14.5px; line-height: 1.4; color: ' + dc + '; text-wrap: pretty">' + desc + '</span></div>'
      + switch(on) + '</div>' + foot + '</div>')

def never(t):
    return ('<div style="display: flex; align-items: center; gap: 11px">' + icon("lock", 15, INK3, 1.5)
      + '<span style="font-size: 14px; color: ' + INK2 + '">' + t + '</span></div>')

rules = page(
  topbar()
  + '<div style="display: flex; flex-direction: column; gap: 8px">'
    '<span style="font-size: 25px; font-weight: 600; letter-spacing: -0.02em">Standing instructions</span>'
    '<span style="' + SERIF + '; font-size: 16px; color: ' + INK2 + '">What I can do without asking you first.</span></div>'
  + '<div style="display: flex; flex-direction: column; gap: 10px">'
    + rule("Pay the Ikeja Electric bill", "When it lands, up to &#8358;10,000.", "Paid 3 times &#183; &#8358;22,400", "See log", True)
    + rule("Buy 5GB when my data runs out", "Once a month at most.", "Bought twice &#183; &#8358;5,000", "See log", True)
    + rule("Cover a bill from Savings", "Tops you up when a bill would bounce. It tells you every time.", "", "", False) + '</div>'
  + '<div style="display: flex; flex-direction: column; gap: 11px">' + label("I WILL ALWAYS ASK FIRST")
    + never("Paying anyone you have not paid before")
    + never("Anything over &#8358;20,000")
    + never("Taking a loan on your behalf") + '</div>'
  + '<div style="height: 50px; border-radius: 25px; border: 1px solid ' + LINE2 + '; background: ' + SURF
    + '; display: flex; align-items: center; justify-content: center; gap: 9px">' + icon("plus", 17, ACC, 1.8)
    + '<span style="font-size: 14.5px; font-weight: 600; color: ' + ACC + '">Add an instruction</span></div>', 14)
rules += askbar("Ask me to set one up", 112)
write("Rules", rules)

print("built:", ", ".join(sorted(f for f in os.listdir(OUT) if f.endswith(".dc.html"))))
