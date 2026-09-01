"""Every design decision in one place.

The system is taken from the Fuse wallet screens. What defines it:

  A pure white page with no grey behind it. Grey appears only as a card fill.
  Titles in true black and heavy. Everything supporting them in a light grey.
  Money split in two, the whole number black and the decimal a pale grey.
  Icons as small rounded squares in a light grey, with a black glyph.
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
FILL3     = "#DEDEE3"   # a quiet block INSIDE a grey card where FILL would vanish, and
                        # the edge of a dashed one. This used to be two tokens: the
                        # other was #DFDFE4, one part in 255 from this, which no eye
                        # can separate, so it went.
LINE      = "#EFEFF1"   # the hairline round a bordered card, and a card's own footer
                        # strip. Also used to be two: the other was #EDEDF0, under two
                        # parts away.

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
IN_TEXT   = "#11823B"   # one step off #12833C, which measured 4.446 against a 4.5 bar
WARN_TEXT = "#CC2A20"
# What the model read out of a picture is boxed where it sits. These two are
# the boxes it is not sure about, written as flat hexes so they survive being
# inlined into an SVG attribute as well as a stylesheet.
WARN_SOFT = "#FBF0EF"
WARN_EDGE = "#F0BFBC"

# The accent. It carries a contextual action, a selected state, a highlighted
# bar, and the model's own panel. Black stays the main action on a screen.
#
# It was #2A6AF5, which is the iOS system blue's neighbourhood, and on a home
# screen it did not separate from the other blue banks -- the shape was doing
# all the work. This one is a few degrees toward indigo and darker: it reads as
# night rather than daylight, which is the position, and white on it goes from
# 4.69 to 8.32, so the primary button's label is no longer scraping the floor.
ACC       = "{{accent}}"
ACC_HEX   = "#213ACA"                                        # Amana blue
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
ACC_HOVER    = _mix(ACC_HEX, 80)   # a link under the cursor, one step down again

CARD_FACE = "linear-gradient(155deg, #1E3A8A 0%, #12235C 48%, #0A0F24 100%)"
ON_DARK   = "#FFFFFF"
ON_DARK_2 = "rgba(255,255,255,0.66)"
ON_DARK_3 = "rgba(255,255,255,0.44)"

# The icon set. Every service used to get a colour and keep it everywhere, so
# you could find electricity by its colour before reading the word. A page with
# eighteen services on it was then eighteen colours, and a thing that shouts
# everywhere cannot point at anything, so the squares went grey and the glyphs
# went black. What is left of this map is the palette, and it is spent in four
# places and no others: green for done, red for trouble, amber for a hard stop,
# and the accent blue for the one item on a screen worth a second look. The
# five glyphs behind the black circle on home keep their colours, because that
# menu is the one place in the product that is meant to feel like a splash.
IC = {
    "blue":   ACC_HEX,
    "orange": "#FF8A4C",
    "purple": "#8B5CF6",
    "green":  "#34C759",
    "pink":   "#FF3B8E",
    "cyan":   "#22B8E8",
    "red":    "#FF3B30",
    "amber":  "#F5A524",
    "black":  "#1C1C1E",
}

# Which colour each icon used to wear. Nothing reads this now: badge() paints
# a grey square and a black glyph, and a caller that wants colour asks for it
# by name. Kept because it is the record of which service is which, and the
# day a chart or a legend needs to tell twelve services apart, it is here.
PAINT = {
    "airtime": "blue",   "data": "purple",  "power": "amber",  "tv": "pink",
    "send": "blue",      "request": "green","card": "black",   "loan": "orange",
    "pot": "green",      "bet": "purple",   "school": "cyan",  "water": "cyan",
    "globe": "blue",     "shield": "green", "more": "black",   "search": "black",
    "grid": "black",     "laptop": "black", "eye": "black",    "chart": "blue",
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
FONT_UI = "'SF Pro Text', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"
FONT_AI = FONT_UI
SERIF   = "font-family: " + FONT_AI

FONT_NAME  = "SF Pro Text"
# Three cuts, one file each. Plus Jakarta Sans was one variable file covering
# 400 to 800; SF Pro Text ships as static weights, so the roman is three faces
# rather than a range. There is no italic: the one place that used to lean, the
# quote of what you said, stands upright now.
FONT_FACES = [("400", "SFProText-Regular-subset.woff2"),
              ("600", "SFProText-Semibold-subset.woff2"),
              ("700", "SFProText-Bold-subset.woff2")]

# Six named styles, read straight off the home screen in Figma. That file is
# the source of truth for type, so the ramp is not a set of sizes any more: it
# is a set of styles, and a size only exists at the weights a style gives it.
# Tracking is a percentage of the size, which is how Figma stores it and what
# keeps it honest as the size changes.
#
# Four sizes are in use and three weights, and Bold reaches only one size. This
# is a phone, so the ramp starts small and never climbs. There was a seventh
# style, Display/Bold 36, named as a ceiling and held in reserve; nothing ever
# snapped to it, so its only appearance in two years was on the specimen sheet
# printing its own name. A style nothing can reach is a style that is not in
# the system, so it is gone from here and from the Figma file.
#
#   Display/Bold 32         the one thing a setup screen asks, and a big figure
#                           that is not money
#   Heading/Semibold 20     a section heading, a sheet title, the digits on the keypad
#   Label/Semibold 14       a row title, a button, a name, a chip that filters
#   Label/Regular 14        a second line, and everything the model says
#   Caption/Semibold 12     a day separator, a badge, a small firm number
#   Caption/Regular 12      a note under a field
#
# Six styles and one face. There were ten and two: Fraunces set the money for a
# while, and it is gone from the interface. It survives in exactly one place,
# the wordmark, where it is outlined to paths and ships as vector rather than as
# a font. An amount is now Label/Semibold 14 or Display/Bold 32 like any other
# text, and what tells it apart is figures of one width, not a second family.
# Tracking is not invented here. SF ships Apple's own optical tracking in the
# font's `trak` table, and these are its normal-track values read straight out
# of the file, in percent of the size. They are identical across all five
# weights, so tracking belongs to the size and not to the cut. Note the shape:
# SF Pro Text is drawn for small text, so the larger it is set the more it has
# to be pulled in, which is the opposite of the way Jakarta was tuned here.
#
# Line height belongs to the size too, for the same reason, and every value is a
# multiple of 4. That is the one place the 4px rhythm legitimately reaches type:
# the grid governs quantities that stack, and leading stacks while a glyph does
# not. Every size below is the value the platforms publish for it, and each
# already lands on the grid without being forced:
#
#   12 / 16   Apple Caption 1 is 12/16. Material bodySmall is 12/16.
#   14 / 20   Material bodyMedium, labelLarge and titleSmall are all 14/20, and
#             so is Atlassian's font.body and Fluent's body1. This replaced the
#             1.14 the browser was giving us, which was too tight to read over
#             more than one line and is tighter than anything either platform
#             ships.
#   20 / 24   Apple Title 3 is 20/25; 24 is that on the grid, and a heading can
#             be led tighter than a paragraph.
#   32 / 40   Material headlineLarge is 32/40 exactly.
#
# Nothing was left on `normal`. A browser default is not a decision, and it was
# reaching Figma as AUTO, which is how 2,746 nodes came to have no leading anyone
# had chosen.
STYLE = {
    (32, 700): ("Display/Bold 32",      "40px", -3.320),
    (20, 600): ("Heading/Semibold 20",  "24px", -2.686),
    (14, 600): ("Label/Semibold 14",    "20px", -1.074),
    (14, 400): ("Label/Regular 14",     "20px", -1.074),
    (12, 600): ("Caption/Semibold 12",  "16px",  0.0),
    (12, 400): ("Caption/Regular 12",   "16px",  0.0),
}
# The sizes a stray number is allowed to land on.
TYPE = [12, 14, 20, 32]
# Which weights a size is allowed to take. Asking for one that does not exist
# is not an error, it is a question about which style was meant, and snap()
# answers it.
WEIGHTS_AT = {}
for _fs, _fw in STYLE:
    WEIGHTS_AT.setdefault(_fs, []).append(_fw)

# ---------------------------------------------------------------- dynamic type
# Four sizes is what the ramp looks like at one setting. iOS has twelve, and a
# person who has turned the text up is not a rare case: presbyopia arrives for
# almost everyone in their forties, and this is a bank for a country whose
# median customer will get there. Apple's own Body runs 17 to 53.
#
# The ramp cannot ride Dynamic Type for free, because it is not Apple's ramp:
# 20 is Title 3 and 12 is Caption 1 exactly, but Apple has no 14 and no 32 at
# the default setting. The supported way to keep a size that is not theirs is
# UIFontMetrics(forTextStyle:).scaledFont(for:), which scales a custom size in
# the proportion its reference style scales. So every style here names the
# Apple style it rides, and the table is that proportion worked out.
#
# APPLE is Apple's published table, read off the Human Interface Guidelines,
# one row per text style and one column per setting.
DT_SETTINGS = ["xSmall", "Small", "Medium", "Large", "xLarge", "xxLarge",
               "xxxLarge", "AX1", "AX2", "AX3", "AX4", "AX5"]
DT_DEFAULT = 3          # Large is the setting every artboard is drawn at

APPLE = {
    "Large Title": [31, 32, 33, 34, 36, 38, 40, 44, 48, 52, 56, 60],
    "Title 1":     [25, 26, 27, 28, 30, 32, 34, 38, 43, 48, 53, 58],
    "Title 2":     [19, 20, 21, 22, 24, 26, 28, 34, 39, 44, 50, 56],
    "Title 3":     [17, 18, 19, 20, 22, 24, 26, 31, 37, 43, 49, 55],
    "Headline":    [14, 15, 16, 17, 19, 21, 23, 28, 33, 40, 47, 53],
    "Body":        [14, 15, 16, 17, 19, 21, 23, 28, 33, 40, 47, 53],
    "Callout":     [13, 14, 15, 16, 18, 20, 22, 26, 32, 38, 44, 51],
    "Subhead":     [12, 13, 14, 15, 17, 19, 21, 25, 30, 36, 42, 49],
    "Footnote":    [12, 12, 12, 13, 15, 17, 19, 23, 27, 33, 38, 44],
    "Caption 1":   [11, 11, 11, 12, 14, 16, 18, 22, 26, 32, 37, 43],
    "Caption 2":   [11, 11, 11, 11, 13, 15, 17, 20, 24, 29, 34, 40],
}

# Which Apple style each of ours rides. Two are exact matches and ride
# themselves. The two 14s must ride the same one or they would come apart at
# the top of the scale, and they sit in the same row on every screen.
DT_REF = {
    "Display/Bold 32":     "Large Title",   # one question, one screen
    "Heading/Semibold 20": "Title 3",       # 20 is Title 3 exactly
    "Label/Semibold 14":   "Body",
    "Label/Regular 14":    "Body",
    "Caption/Semibold 12": "Caption 1",     # 12 is Caption 1 exactly
    "Caption/Regular 12":  "Caption 1",
}

def _snap4(v):
    return int(round(v / 4.0)) * 4

def dt_size(style, i):
    """The size this style takes at setting `i`, in the proportion its Apple
    reference moves. Rounded to a whole pixel, because a half pixel of type is
    a blurred edge on a screen that is already asking for help."""
    ref = APPLE[DT_REF[style]]
    return int(round(_DT_BASE[style] * ref[i] / float(ref[DT_DEFAULT])))

def dt_leading(style, i):
    """Leading keeps its ratio and stays on the 4px grid at every setting, for
    the same reason it does at this one: leading stacks."""
    return _snap4(dt_size(style, i) * _DT_LEAD_RATIO[style])

_DT_BASE = {}
_DT_LEAD_RATIO = {}
for (_fs, _fw), (_nm, _lh, _tr) in STYLE.items():
    _DT_BASE[_nm] = _fs
    _DT_LEAD_RATIO[_nm] = int(_lh[:-2]) / float(_fs)

# Money never renders at the bottom of the ramp: a Naira sign at 12 is too fine
# to read at a glance on a phone. snap() lifts any figure off it. This outlived
# the money face on purpose; the floor was never about the typeface.
MONEY_MIN_PX = 14

# Weights. Regular for anything grey, and Semibold, not Bold, for
# everything else: SF sets heavier at a given weight than Jakarta did, and
# Semibold is the weight iOS itself emphasises with. Bold survives at one size
# only, the balance at 32, and _ramp() puts it there without being asked,
# because 700 is the only weight that size offers.
WEIGHT = {400: 400, 500: 400, 600: 600, 700: 600, 800: 600}

# ---------------------------------------------------------------- shape
# A 4px rhythm, and nothing off it. 2 and 6 used to be kept for the gap between
# an icon and its label and are gone: every gap and padding in this file rounds
# to a multiple of 4 now, ties going up. 56 and 72 are structural, not rhythm.
# 72 is where a page starts, which clears the status bar and leaves the
# breathing room the reference has.
SPACE = [4, 8, 12, 16, 20, 24, 32, 40, 56, 72]
# Five radii, on the same 4px grid. 10 and 14 are gone with 2 and 6. Anything
# round is written as PILL and never snapped.
RADII = [12, 16, 20, 24, 28]
PILL  = "999px"

R_CARD   = "24px"   # the normal card, a flat grey fill
R_CARDLG = "28px"   # the payment card object
R_CARDXL = "28px"   # the answer card
R_PANEL  = "24px"   # a list of rows
R_INNER  = "16px"   # a panel inside a card, including the model's own
R_TILE   = "16px"   # the rounded square behind a 48px service icon
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
DASH      = "border: 1.5px dashed " + FILL3
SHADOW    = ""
SH_RAISE  = "box-shadow: 0 2px 10px rgba(0,0,0,0.05), 0 8px 30px rgba(0,0,0,0.06)"
SH_BTN    = "box-shadow: 0 8px 24px rgba(0,0,0,0.24)"
SH_SHEET  = "box-shadow: 0 -10px 50px rgba(0,0,0,0.14)"
SH_FAB    = "box-shadow: 0 6px 18px rgba(0,0,0,0.22), 0 0 34px rgba(0,0,0,0.10)"

# The blur behind a sheet, and behind the action popup.
SCRIM     = "rgba(120,120,124,0.42)"
BLUR      = "backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px)"
