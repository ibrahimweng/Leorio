"""Writes the brand assets that are not screens.

The app icon is drawn by build.py's appicon(), so the icon and the mark inside
the app can never be two different drawings. This only saves it out.

    python3 brand.py            # writes brand/
"""
import os, subprocess, sys, tempfile
import build

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brand")
os.makedirs(OUT, exist_ok=True)

# iOS masks the icon itself, so what ships is full bleed. The masked copy is
# for a favicon, a deck, and for looking at.
SIZES = [1024, 180, 120, 80, 60, 40]

open(os.path.join(OUT, "icon.svg"), "w").write(build.appicon(1024))
open(os.path.join(OUT, "icon-masked.svg"), "w").write(build.appicon(1024, mask=True))

# One page holding every size, screenshotted once, then cut up by the shooter.
rows = "".join(
  '<div class="s" data-name="icon-%d"><div>%s</div></div>' % (n, build.appicon(n))
  for n in SIZES)
masked = "".join(
  '<div class="s" data-name="icon-%d-masked"><div>%s</div></div>' % (n, build.appicon(n, mask=True))
  for n in SIZES)
page = ('<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#fff}'
        '.s{display:inline-block;margin:0}</style>' + rows + masked)
open(os.path.join(OUT, "_sheet.html"), "w").write(page)

print("wrote", OUT)
for f in sorted(os.listdir(OUT)):
    print("  ", f)
