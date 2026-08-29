"""Writes the brand assets that are not screens: the app icon, the wordmark and
the two lockups.

The app icon is drawn by build.py's appicon(), so it and the mark inside the app
can never be two different drawings. The wordmark is outlined here from the
subset in fonts/, so it does not depend on Fraunces being installed anywhere --
a logotype that needs a font is a logotype that renders wrong on somebody's
machine.

    python3 brand.py                 # writes brand/
    CHROME=... node brandshot.mjs    # then cuts the PNGs
"""
import os, io, math
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.misc.transform import Transform

import build
from tokens import ACC_HEX

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "brand")
FONT = os.path.join(HERE, "fonts", "Fraunces-SemiBold-Amana-subset.woff2")
os.makedirs(OUT, exist_ok=True)

WORD = "Amana"
TRACK = -0.02      # em. -0.03 crowds the A into the m, 0 reads loose for a logo.
EM = 100.0         # the box the path is composed in

# ---------- the wordmark, as one path ----------

def outline(text=WORD, em=EM, track=TRACK):
    """One path for the whole word, plus the numbers the lockup needs.

    Composed on advance widths alone. Checked against the browser at 100px by
    laying one over the other: they land on the same pixels, so Fraunces has no
    kerning for these five letters and nothing is being dropped here."""
    f = TTFont(FONT)
    scale = em / f["head"].unitsPerEm
    cmap, gs = f.getBestCmap(), f.getGlyphSet()
    parts, x = [], 0.0
    minx = miny = 1e9
    maxx = maxy = -1e9
    for ch in text:
        g = gs[cmap[ord(ch)]]
        bp = BoundsPen(gs); g.draw(bp)
        if bp.bounds:
            x0, y0, x1, y1 = bp.bounds
            minx = min(minx, x + x0 * scale); maxx = max(maxx, x + x1 * scale)
            miny = min(miny, -y1 * scale);    maxy = max(maxy, -y0 * scale)
        # Two decimals at EM 100 is 0.005 of a unit, which is 0.002px at the
        # size the lockup is drawn. It halves the path and keeps the shape.
        sp = SVGPathPen(gs, ntos=lambda v: ("%.2f" % v).rstrip("0").rstrip("."))
        g.draw(TransformPen(sp, Transform(scale, 0, 0, -scale, x, 0)))
        if sp.getCommands():
            parts.append(sp.getCommands())
        x += g.width * scale + track * em
    d = "".join(parts)
    return {"d": d, "dx": -minx, "dy": -miny,
            "w": maxx - minx, "h": maxy - miny,
            "cap": -miny}          # the A's height above the baseline

WM = outline()

# The lockup, said as proportions of the wordmark's own size so it holds at any
# scale: the mark a touch taller than the caps, and a gap a quarter of the size.
MARK_OF_SIZE = 0.90
GAP_OF_SIZE = 0.25

def _wm_group(size, color, x, y):
    s = size / EM
    return ('<g transform="translate(%.3f %.3f) scale(%.5f)"><path d="%s" fill="%s"/></g>'
            % (x + WM["dx"] * s, y + WM["dy"] * s, s, WM["d"], color))

def wordmark(size=100, color="#000000"):
    """The word on its own. The path is composed at EM, so the group carries the
    scale -- writing the size into the viewBox alone would leave the word in the
    corner of a box twice its size."""
    s = size / EM
    w, h = WM["w"] * s, WM["h"] * s
    return _box(w, h, lambda x, y: _wm_group(size, color, x, y))

def _box(w, h, body):
    """A whole-pixel canvas with the art centred in it. The boxes come out
    fractional, and a browser snapping 267.44 down to 267 shaves the last a off
    the end of the word -- which is a clipped logo, in every asset that ships."""
    W, H = math.ceil(w), math.ceil(h)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
            'fill="none">%s</svg>' % (W, H, W, H, body((W - w) / 2.0, (H - h) / 2.0)))

def _mark(size, on_blue):
    g = build.mark(size, "#FFFFFF" if on_blue else "{{accent}}")
    return g.replace("{{accent}}", ACC_HEX)

def lockup(size=40, on_blue=False, stacked=False):
    """Mark and word as one thing. Horizontal is the default; stacked is for a
    square hole -- a share sheet, a sign, an avatar."""
    colour = "#FFFFFF" if on_blue else "#000000"
    m = size * MARK_OF_SIZE
    gap = size * GAP_OF_SIZE
    ws, wh = WM["w"] * size / EM, WM["h"] * size / EM
    cap = WM["cap"] * size / EM
    if stacked:
        w = max(m, ws); h = m + gap + wh
        def body(ox, oy):
            return ('<g transform="translate(%.2f %.2f)">%s</g>'
                    % (ox + (w - m) / 2.0, oy, _mark(round(m, 2), on_blue))
                    + _wm_group(size, colour, ox + (w - ws) / 2.0, oy + m + gap))
    else:
        # the mark sits centred on the middle of the cap height, not on the box
        my = (cap / 2.0) - (m / 2.0)
        w = m + gap + ws
        h = max(m + max(my, 0), wh + max(-my, 0))
        def body(ox, oy):
            return ('<g transform="translate(%.2f %.2f)">%s</g>'
                    % (ox, oy + max(my, 0), _mark(round(m, 2), on_blue))
                    + _wm_group(size, colour, ox + m + gap, oy + max(-my, 0)))
    return _box(w, h, body)

# ---------- write it out ----------

ASSETS = {
    "icon.svg":            build.appicon(1024),
    "icon-masked.svg":     build.appicon(1024, mask=True),
    "wordmark.svg":        wordmark(200),
    "wordmark-white.svg":  wordmark(200, "#FFFFFF"),
    "lockup.svg":          lockup(80),
    "lockup-white.svg":    lockup(80, on_blue=True),
    "lockup-stacked.svg":  lockup(80, stacked=True),
}
for name, svg in ASSETS.items():
    io.open(os.path.join(OUT, name), "w", encoding="utf-8").write(svg)

SIZES = [1024, 180, 120, 80, 60, 40]
sheet = "".join('<div class="s" data-name="icon-%d"><div>%s</div></div>' % (n, build.appicon(n))
                for n in SIZES)
sheet += "".join('<div class="s" data-name="icon-%d-masked"><div>%s</div></div>' % (n, build.appicon(n, mask=True))
                 for n in SIZES)
sheet += ('<div class="s" data-name="wordmark"><div>%s</div></div>' % wordmark(200)
        + '<div class="s" data-name="lockup"><div>%s</div></div>' % lockup(80)
        + '<div class="s" data-name="lockup-stacked"><div>%s</div></div>' % lockup(80, stacked=True)
        + '<div class="s" data-name="lockup-on-blue" style="background:%s;padding:24px">'
          '<div>%s</div></div>' % (ACC_HEX, lockup(80, on_blue=True)))
io.open(os.path.join(OUT, "_sheet.html"), "w", encoding="utf-8").write(
    '<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#fff}'
    '.s{display:inline-block;margin:0}</style>' + sheet)

print("wordmark: %.2f x %.2f at size 100, cap %.2f, tracking %s"
      % (WM["w"], WM["h"], WM["cap"], TRACK))
print("wrote", OUT)
for f in sorted(os.listdir(OUT)):
    print("   ", f)
