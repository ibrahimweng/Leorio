"""Every design decision in one place.

The system is taken from the Fuse wallet screens. What defines it:

  A pure white page with no grey behind it. Grey appears only as a card fill.
  Titles in true black and heavy. Everything supporting them in a light grey.
  Money split in two, the whole number black and the decimal a pale grey.
  Icons as small rounded squares in saturated colour with a white glyph.
  Cards that are either a flat grey fill or a dashed outline, and no shadow.
  Pills for every button, black for the main one and blue for a contextual one.
  Sheets that rise from the bottom over a blurred, dimmed page.

Three scales are enforced at build time, so nothing can drift off them:
a type ramp, a spacing rhythm and a small set of corner radii. See snap()
in build.py.

One note on the greys. INK2, INK3 and INK4 are sampled from the reference
screens and are lighter than the accessibility standard allows for small
text. That was a deliberate call to match the reference exactly. INK2 at
22px and above clears the standard for large text.
"""

# ---------------------------------------------------------------- colour
BG        = "#FFFFFF"   # the page, white everywhere
SURF      = "#FFFFFF"   # a card that needs to sit on top of a grey one
FILL      = "#F5F5F7"   # the normal card. Grey lives here only, never under the page.
FILL2     = "#EDEDF0"   # a card's own footer strip
FILL3     = "#DEDEE3"   # a quiet block INSIDE a grey card, where FILL would vanish
LINE      = "#EFEFF1"   # the hairline round a bordered card
LINE2     = "#DFDFE4"   # a dashed edge or a drag handle

INK       = "#000000"   # every title and every figure
INK2      = "#8E8E93"   # a label above a figure, a section heading
INK3      = "#A9A9AE"   # the line under a title, a row's second line
INK4      = "#C4C4C9"   # the decimal half of a money figure

BTN       = "#000000"   # the one action you are meant to take
BTN_INK   = "#FFFFFF"

IN        = "#34C759"   # money coming in, as an icon or a fill
WARN      = "#FF3B30"   # trouble, as an icon or a fill
# The reference never sets green or red as text, so there is nothing to copy
# and no reason not to use a shade that reads. These two are text only.
IN_TEXT   = "#12833C"
WARN_TEXT = "#CC2A20"

# The accent. It carries a contextual action, a selected state, a highlighted
# bar, and the model's own panel. Black stays the main action on a screen.
ACC       = "{{accent}}"
ACC_HEX   = "#2A6AF5"                                        # the reference blue
ACC_TEXT  = "color-mix(in srgb, " + ACC + " 88%, #000000)"   # the accent, one step down, so small text on white reads
ACC_SOFT  = "color-mix(in srgb, " + ACC + " 7%, #FFFFFF)"    # the panel the model speaks from
ACC_EDGE  = "color-mix(in srgb, " + ACC + " 22%, transparent)"
ACC_INK   = ACC_TEXT

def _mix(top, pct, under="#000000"):
    """The hex ACC_TEXT resolves to. An SVG paints through an attribute, not a
    computed style, so color-mix() never reaches the renderer there. This keeps
    a glyph and the words beside it the same blue, from the one accent."""
    a, b, f = top.lstrip("#"), under.lstrip("#"), pct / 100.0
    return "#%02X%02X%02X" % tuple(
        round(int(a[i:i+2], 16) * f + int(b[i:i+2], 16) * (1 - f)) for i in (0, 2, 4))

ACC_TEXT_HEX = _mix(ACC_HEX, 88)

CARD_FACE = "linear-gradient(155deg, #1E3A8A 0%, #12235C 48%, #0A0F24 100%)"
ON_DARK   = "#FFFFFF"
ON_DARK_2 = "rgba(255,255,255,0.66)"
ON_DARK_3 = "rgba(255,255,255,0.44)"

# The icon set. Every service gets a colour and keeps it everywhere it appears,
# so you learn to find electricity by its colour before you read the word.
IC = {
    "blue":   "#2A6AF5",
    "orange": "#FF8A4C",
    "purple": "#8B5CF6",
    "green":  "#34C759",
    "pink":   "#FF3B8E",
    "cyan":   "#22B8E8",
    "red":    "#FF3B30",
    "amber":  "#F5A524",
    "black":  "#1C1C1E",
}

# Which colour each icon wears. One lookup, so a service cannot drift.
PAINT = {
    "airtime": "blue",   "data": "purple",  "power": "amber",  "tv": "pink",
    "send": "blue",      "request": "green","card": "black",   "loan": "orange",
    "pot": "green",      "bet": "purple",   "school": "cyan",  "water": "cyan",
    "globe": "blue",     "shield": "green", "more": "black",   "search": "black",
    "grid": "black",
    "copy": "blue",      "check": "green",  "freeze": "cyan",  "plus": "blue",
    "minus": "orange",   "lock": "purple",  "waste": "amber",  "list": "blue",
    "clock": "purple",   "receipt": "orange","bell": "red",    "mic": "blue",
    "bolt": "black",     "key": "purple",   "chat": "pink",    "star": "green",
    "swap": "cyan",      "person": "orange","gift": "pink",    "bank": "purple",
}

def paint(ic):
    """The colour an icon wears. Anything unnamed falls back to the accent blue."""
    return IC.get(PAINT.get(ic, "blue"), IC["blue"])

# Kept so older calls still resolve. There is one neutral tone.
def tone(name=None):
    return (FILL, INK)
def itone(ic=None):
    return "neutral"
TONES = {"neutral": (FILL, INK)}

WASH = FILL   # nothing washes the page any more, but page() still names it

# ---------------------------------------------------------------- type
FONT_UI = "'Plus Jakarta Sans', -apple-system, 'Helvetica Neue', Arial, sans-serif"
FONT_AI = FONT_UI
SERIF   = "font-family: " + FONT_AI

FONT_FILE  = "PlusJakarta-subset.woff2"
FONT_ITAL  = "PlusJakartaItalic-subset.woff2"
FONT_NAME  = "Plus Jakarta Sans"
FONT_WGHT  = "400 800"

# Six steps, and nothing between them. Taken down a step from the reference
# after a pass over the home screen, so the whole product reads quieter.
#   12 a second line, a caption, a chip
#   14 body, a card title, and everything the model says
#   16 a row title, a button, a value
#   22 a heading over a group
#   26 a page title
#   36 a balance
TYPE = [12, 14, 16, 22, 26, 36]
# The Naira sign loses its crossbars below about twelve and a half pixels, so
# the smallest step is not available to money. snap() lifts any figure off it.
MONEY_MIN_PX = 14
# Three weights, which is all the reference uses. Regular for anything grey,
# bold for anything named, heavy for money.
WEIGHT = {400: 400, 500: 400, 600: 700, 700: 700, 800: 800}

# ---------------------------------------------------------------- shape
# A 4px rhythm, with 2 and 6 kept for the gap between an icon and its label.
# 56 and 72 are structural, not rhythm. 72 is where a page starts, which
# clears the status bar and leaves the breathing room the reference has.
SPACE = [2, 4, 6, 8, 12, 16, 20, 24, 32, 40, 56, 72]
# Seven radii. Anything round is written as PILL and never snapped.
RADII = [10, 12, 14, 16, 20, 24, 28]
PILL  = "999px"

R_CARD   = "24px"   # the normal card, a flat grey fill
R_CARDLG = "28px"   # the payment card object
R_CARDXL = "28px"   # the answer card
R_PANEL  = "24px"   # a list of rows
R_INNER  = "16px"   # a panel inside a card, including the model's own
R_TILE   = "14px"   # the rounded square behind a 48px service icon
R_ACT    = PILL     # a round action button
R_BUNDLE = "16px"   # a bundle or amount chip
R_FIELD  = "16px"   # a field the model filled in, and grouped plain rows
R_CHIP   = PILL     # a chip that edits the question
R_ICON   = "12px"   # the rounded square behind a 40px row icon
R_TAG    = PILL     # a status tag
R_SHEET  = "28px"   # the top corners of a sheet
R_BAR    = "6px"    # a bar in a chart, too small to snap
R_TRACK  = "4px"    # a progress track, too small to snap

def pill(h=None):
    return PILL

# ---------------------------------------------------------------- depth
# The reference is flat. A card is told apart by its fill or its dashed
# outline, not by a shadow. Only three things lift off the page: the button
# you press, the bar you type into, and a sheet.
CARD_EDGE = "border: 1px solid " + LINE
DASH      = "border: 1.5px dashed " + LINE2
SHADOW    = ""
SH_RAISE  = "box-shadow: 0 2px 10px rgba(0,0,0,0.05), 0 8px 30px rgba(0,0,0,0.06)"
SH_BTN    = "box-shadow: 0 8px 24px rgba(0,0,0,0.24)"
SH_SHEET  = "box-shadow: 0 -10px 50px rgba(0,0,0,0.14)"
SH_FAB    = "box-shadow: 0 6px 18px rgba(0,0,0,0.22), 0 0 34px rgba(0,0,0,0.10)"

# The blur behind a sheet, and behind the action popup.
SCRIM     = "rgba(120,120,124,0.42)"
BLUR      = "backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px)"
