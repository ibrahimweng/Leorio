"""Every design decision in one place.

Monochrome structure with one warm accent, spent only where the model speaks.
Taken from the reference screens: a near white page, white cards separated by
soft shadow rather than hairlines, circular icon badges, a black circle for a
primary action, and sentence case section headings instead of shouty labels.

Three scales are enforced at build time, so nothing can drift off them:
a type ramp, a spacing rhythm and a small set of corner radii. See snap()
in build.py.
"""

# ---------------------------------------------------------------- colour
# Every text pair below clears WCAG AA at the size it is used.
BG        = "#F5F5F6"   # the page
SURF      = "#FFFFFF"   # a card
FILL      = "#F1F1F3"   # a quiet panel, and the circle behind a row icon
FILL2     = "#DEDEE3"   # a firmer quiet block, e.g. a chart bar
LINE      = "#EAEAEC"   # a hairline, used sparingly
LINE2     = "#DDDDE1"   # a drag handle or a dashed edge

INK       = "#111113"   # 18.9 on white
INK2      = "#52525B"   #  7.7 on white
INK3      = "#6A6A73"   #  5.3 on white, 4.7 on FILL. Nothing lighter carries text.

BTN       = "#111113"   # the one action you are meant to take
BTN_INK   = "#FFFFFF"

IN        = "#0F7A55"   # money coming in, and anything free
WARN      = "#C2361F"   # a bill nobody is covering

# The model, and the only colour in the app that is not a grey. It marks the
# badge the model speaks from and the panel its words sit in. Nothing else.
ACC       = "{{accent}}"
ACC_HEX   = "#E86A00"                                        # badge fill, white glyph on it
ACC_TEXT  = "color-mix(in srgb, " + ACC + " 62%, #111113)"   # the model's links and small print
ACC_SOFT  = "color-mix(in srgb, " + ACC + " 5%, #FFFFFF)"    # the panel the model speaks from
ACC_EDGE  = "color-mix(in srgb, " + ACC + " 24%, transparent)"
ACC_INK   = ACC_TEXT                                         # the name the screens already use

CARD_FACE = "linear-gradient(150deg, #2A2A2E 0%, #17171A 55%, #0E0E11 100%)"
ON_DARK   = "#FFFFFF"
ON_DARK_2 = "rgba(255,255,255,0.66)"
ON_DARK_3 = "rgba(255,255,255,0.44)"

# Icon badges are all one neutral circle now. The function stays so the
# screens keep calling it, but there is one tone.
def tone(name=None):
    return (FILL, INK)
def itone(ic=None):
    return "neutral"
TONES = {"neutral": (FILL, INK)}

# ---------------------------------------------------------------- type
FONT_UI = "'Plus Jakarta Sans', -apple-system, 'Helvetica Neue', Arial, sans-serif"
FONT_AI = FONT_UI
SERIF   = "font-family: " + FONT_AI

FONT_FILE  = "PlusJakarta-subset.woff2"
FONT_ITAL  = "PlusJakartaItalic-subset.woff2"
FONT_NAME  = "Plus Jakarta Sans"
FONT_WGHT  = "400 800"

# Nine steps, and nothing between them. 13 is the floor, which also keeps
# every money figure above the size where the Naira sign loses its crossbars.
TYPE = [13, 14, 15, 17, 20, 24, 30, 36, 44]
# Three weights. Regular for body, medium for anything named, bold for money.
WEIGHT = {400: 500, 500: 500, 600: 600, 700: 700, 800: 700}
MONEY_MIN_PX = 13

# ---------------------------------------------------------------- shape
# A 4px rhythm, with 2 and 6 kept for the gap between an icon and its label.
SPACE = [2, 4, 6, 8, 12, 16, 20, 24, 32, 40, 54]
# Five radii. Anything round is written as PILL and never snapped.
RADII = [8, 12, 16, 20, 28]
PILL  = "999px"

R_CARD   = "20px"   # a card the model wrote, or a draft it prepared
R_CARDLG = "20px"   # the payment card object
R_CARDXL = "20px"   # the answer card
R_PANEL  = "20px"   # a list of rows
R_INNER  = "16px"   # a panel inside a card, including the model's own
R_TILE   = PILL     # the circle behind a service icon
R_ACT    = PILL     # a round action button
R_BUNDLE = "16px"   # a bundle or amount chip
R_FIELD  = "16px"   # a field the model filled in, and grouped plain rows
R_CHIP   = PILL     # a chip that edits the question
R_ICON   = PILL     # the circle behind a merchant or row icon
R_TAG    = PILL     # a status tag
R_SHEET  = "28px"   # the top corners of the voice sheet
R_BAR    = "6px"    # a bar in a chart, too small to snap
R_TRACK  = "4px"    # a progress track, too small to snap

def pill(h=None):
    return PILL

# ---------------------------------------------------------------- depth
SHADOW   = "box-shadow: 0 1px 2px rgba(17,17,19,0.04), 0 4px 16px rgba(17,17,19,0.045)"
SH_RAISE = "box-shadow: 0 2px 4px rgba(17,17,19,0.05), 0 12px 32px rgba(17,17,19,0.09)"
SH_BTN   = "box-shadow: 0 4px 14px rgba(17,17,19,0.20)"
SH_SHEET = "box-shadow: 0 -12px 40px rgba(17,17,19,0.13)"
