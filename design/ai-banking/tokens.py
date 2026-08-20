"""Every design decision in one place.

Taken from the reference screens: a saturated warm wash at the top of a
screen fading into white, white cards separated by soft shadow rather than
hairlines, big soft corners, pastel badges behind every service icon, and a
black pill for the one action you are meant to take.

The screens never write a colour, a typeface or a corner radius directly.
They ask for a role, so changing the look means changing this file.
"""

# ---------------------------------------------------------------- colour
# Surfaces. The page is white and cards lift off it with shadow, not borders.
BG        = "#FFFFFF"   # the page
SURF      = "#FFFFFF"   # a card
FILL      = "#F6F3F0"   # a quiet panel inside a card
FILL2     = "#E7E1D9"   # a firmer quiet block, e.g. a chart bar
LINE      = "#EFEBE6"   # a hairline, used sparingly
LINE2     = "#E4DFD9"   # a firmer warm grey, for a drag handle or a dashed edge

# Text. Warm, so it sits with the orange rather than fighting it.
INK       = "#17130F"
INK2      = "#6B635B"
INK3      = "#9E958C"

# The one action you are meant to take on a screen.
BTN       = "#14110D"
BTN_INK   = "#FFFFFF"

# Meaning, never decoration.
IN        = "#12855C"   # money coming in, and anything free
WARN      = "#D8452F"   # a bill nobody is covering

# The model. It marks what the model wrote, what it filled in and the badge
# it speaks from. It is also the brand, so it carries the wash.
# It stays a template hole so the canvas can offer it as a tweak.
ACC       = "{{accent}}"
ACC_HEX   = "#FF7A1A"
# Written as a mix of the accent so they follow it when it is changed.
ACC_SOFT  = "color-mix(in srgb, " + ACC + " 11%, #FFFFFF)"   # the panel the model speaks from
ACC_EDGE  = "color-mix(in srgb, " + ACC + " 28%, transparent)"
ACC_INK   = "color-mix(in srgb, " + ACC + " 72%, #17130F)"   # the model's small print

# The wash. Top of the home screen, and the two screens that celebrate.
WASH = ("linear-gradient(180deg, #FFA309 0%, #FF7C2B 22%, #FF9A5E 42%, "
        "#FFC9A6 60%, #FFE8D8 74%, #FFFFFF 92%)")
CARD_FACE = "linear-gradient(150deg, #FFA309 0%, #FF6A16 52%, #EF4E0C 100%)"
ON_WASH   = "#FFFFFF"
ON_WASH_2 = "rgba(255,255,255,0.72)"
ON_WASH_3 = "rgba(255,255,255,0.55)"

# Pastel badges behind service and merchant icons, straight from the
# reference. Each is a soft background with a stronger glyph.
TONES = {
    "brand":   ("#FFF2E8", "#EE6A0C"),
    "cool":    ("#EAF1FE", "#2F6BE0"),
    "green":   ("#E6F4EE", "#12855C"),
    "violet":  ("#F2ECFC", "#6B4BC4"),
    "rose":    ("#FDECEA", "#D8452F"),
    "amber":   ("#FEF3E0", "#B3720A"),
    "neutral": ("#F3F0EC", "#6B635B"),
}
def tone(name):
    return TONES.get(name, TONES["neutral"])

# Which badge colour each icon wears, so a row of services reads as a row of
# different things rather than a row of the same grey square.
ICON_TONE = {
    "airtime": "cool",   "data": "violet", "power": "amber",   "send": "green",
    "more": "neutral",   "tv": "rose",     "bet": "violet",    "loan": "green",
    "card": "cool",      "pot": "green",   "school": "amber",  "water": "cool",
    "globe": "cool",     "waste": "neutral", "clock": "neutral", "request": "rose",
    "shield": "green",   "freeze": "cool", "plus": "green",    "search": "violet",
    "list": "amber",     "mic": "neutral", "copy": "neutral",  "check": "green",
    "lock": "neutral",   "receipt": "neutral", "minus": "neutral",
}
def itone(ic):
    return ICON_TONE.get(ic, "neutral")

# ---------------------------------------------------------------- type
# One family. The reference uses a single geometric sans throughout, so the
# model is told apart by the panel it speaks from rather than by a serif.
FONT_UI = "'Plus Jakarta Sans', -apple-system, 'Helvetica Neue', Arial, sans-serif"
FONT_AI = FONT_UI
SERIF   = "font-family: " + FONT_AI     # kept as the name the screens call it

FONT_FILE  = "PlusJakarta-subset.woff2"
FONT_ITAL  = "PlusJakartaItalic-subset.woff2"
FONT_NAME  = "Plus Jakarta Sans"
FONT_WGHT  = "400 800"

# No money is set below this. Under about 12.5px the Naira sign loses its
# two crossbars and turns into a plain N.
MONEY_MIN_PX = 12.5

# ---------------------------------------------------------------- shape
R_CARD   = "24px"   # a card the model wrote, or a draft it prepared
R_CARDLG = "26px"   # the payment card object
R_CARDXL = "26px"   # the answer card
R_PANEL  = "22px"   # a list of rows
R_INNER  = "18px"   # a panel inside a card, including the model's own
R_TILE   = "20px"   # the badge behind a service icon
R_ACT    = "18px"   # a square action button
R_BUNDLE = "18px"   # a bundle or amount chip
R_FIELD  = "18px"   # a field the model filled in, and grouped plain rows
R_CHIP   = "999px"  # a chip that edits the question, fully round
R_ICON   = "14px"   # the badge behind a merchant or row icon
R_TAG    = "999px"  # a status tag, fully round
R_SHEET  = "32px"   # the top corners of the voice sheet
R_BAR    = "6px"    # a bar in a chart
R_TRACK  = "4px"    # a progress track

def pill(h):
    """A control that is fully round on its ends. Pass the height."""
    return str(round(h / 2, 1)).rstrip("0").rstrip(".") + "px"

# ---------------------------------------------------------------- depth
# Separation comes from shadow, so there is almost no border anywhere.
SHADOW   = "box-shadow: 0 2px 10px rgba(23,19,15,0.055), 0 1px 2px rgba(23,19,15,0.04)"
SH_RAISE = "box-shadow: 0 10px 30px rgba(23,19,15,0.12), 0 2px 6px rgba(23,19,15,0.05)"
SH_BTN   = "box-shadow: 0 6px 18px rgba(20,17,13,0.22)"
SH_SHEET = "box-shadow: 0 -12px 40px rgba(23,19,15,0.14)"
