# Working on this design

The screens are generated. `tokens.py` holds the system, `build.py` writes 95
`.dc.html` artboards, `figma/` renders them in a headless browser, measures them
and sends them to Figma. The Figma file is the review surface, not the source.

## Three rules, learned the expensive way

**1. Never infer identity that the source can state.**
Icons were once identified by stripping the numbers out of their vector paths and
treating what was left as a fingerprint. A three point chevron and a three point
check normalise to the same string, so 97 icons collapsed into 58 buckets and 470
glyphs were given the wrong art. The fix was `data-icon` on every `<svg>`, so a
glyph reaches Figma already knowing its name. Before writing any matcher, ask
whether the thing being matched can simply say what it is.

**2. Change a constant, then find everything keyed on it.**
Moving the emphasis weight from 700 to 600 broke `extract.mjs`, whose `STYLE` map
is keyed `size/weight`, and 113 nodes silently stopped binding to a style.
Dropping the italic parameter from `faces()` broke `prototype.py`, which called
`faces(True)`. Both were one `grep` away. Grep for the old value and the function
name before moving on.

**3. Trial on one, then do the rest.**
The bubble swap was tried on `Chat` alone, screenshotted, and only then rolled out
to 56 masters; nothing went wrong. The icon pass was not, and cost a day.

And a habit, not a rule: when a sentence you are writing contains "close enough",
stop. That phrase has appeared once in this project's history, in the commit that
broke the icons, next to two numbers that did not reconcile.

## Before and after any bulk change in Figma

Run `figma/audit.js` through `use_figma`, once before and once after, and compare.
It reports the invariants that have actually been broken here before:

- reactions on Flows, and any whose destination no longer exists
- text nodes not bound to a style, and any font that is not SF Pro Text
- instances still pointing at a retired component
- frames that hold several children with no auto layout
- padding, gaps and radii that are off the scales in `tokens.py`
- icon sizes and apparent stroke widths that are off the icon scale

Flows should read **774 reactions with no dead destinations**. If a number moves,
find out why before doing anything else. A swap carries text and glyphs across but
**not reactions**, and that is how 21, then 41, then 4 links were lost.

The baseline was 787 until the round button came off the 31 record screens; the
16 links that went were the taps on buttons that no longer exist. It went back
up to 774 when the Receipt screen arrived with three: into it from the share
sheet, on from its button, and its own back. When a number moves on purpose,
change it here in the same commit, or the next run reads a deliberate decision
as a regression.

The type numbers on Flows are **4,581 text nodes, 4,469 bound, 112 unbound, and
SF Pro Text is the only unbound family**. Those 112 are the keyboard, the payment
card and the meter token, which opt out of the ramp on purpose. Line heights read
**16 x815, 20 x3118, 24 x418, 40 x118 and AUTO x112** — every set value a multiple
of 4, and the AUTO ones exactly those same 112 opt-outs. Any other family
appearing there, or the bound count falling, is a regression. It read 4,983 until
the six r&eacute;sum&eacute; documents moved to their own page. **Eight text styles** are
defined and all eight are bound to something. One family: any other font family
appearing in the audit's `fonts` line is a regression, not a feature.

## Things that will bite

- Replacing a frame drops any reaction pointing at it.
- Restructuring a component discards override reactions on its instances.
- Figma rejects a NAVIGATE whose destination is on another page, so a link from a
  master on **Components** to a screen on **Flows** has to live on the instances.
- A boolean-bound hidden layer is absent from an instance's `children`, so paths
  into an instance can be one shorter than into its master.
- `node.findAll` does not exist on TEXT or RECTANGLE; check `type` before reaching
  for it, and check it *before* the property, because the access itself throws.
- A failed `use_figma` script is atomic. Nothing ran. Fix and retry.
- A component can **compensate for a wrong size with padding**, and then it
  looks right and measures wrong. `Answer head` held the mark at 28 with 4px of
  padding round it, so the text still landed at 40 and the row was still 32
  tall — pixel for pixel correct, and the mark 12.5% too small in 90 places.
  When a number is off, check whether something nearby is paying for it before
  deciding the number is fine.
- **The file holds more than the product, and a whole-canvas count is not a
  reading of the design.** Six r&eacute;sum&eacute; documents sat loose on Flows for months.
  Every automated read of the file — Figma's own assistant included — correctly
  reported five font families, twelve styles and twenty-three sizes, and every
  one of those numbers was about a CV. They now live on a page called
  `R&eacute;sum&eacute;`. Before quoting a count, say which nodes it covers, and prefer
  counting the screens inside the sections to counting the page.
- **Measuring the build is not measuring the file.** The two disagree whenever a
  screen has not been re-sent, and the disagreement is silent. A count taken from
  `*.dc.html` describes what the next send would produce; a count taken through
  `use_figma` describes what a reviewer is looking at now. Name which one you did.
- **A text node the extractor sized `NONE` is fixed in both directions**, so it
  cannot grow and it cannot rewrap. 38 nodes are like that. If the string inside
  ever needs more width than the box it was measured into, it wraps inside a box
  that will not get taller and the second line lands on whatever is underneath.
  That is how `Limits` came to print a balance across the progress bar: 139px of
  box for 141px of Fraunces. Leading cannot cause it and leading cannot fix it —
  check the width. Sweep for it by re-measuring each string with a probe TEXT
  node set to `WIDTH_AND_HEIGHT` and comparing against the real node's width.
- **Every font size that ships is whole, even and 12 or over, and the build
  refuses otherwise.** The ramp guarantees it for what it touches;
  `_even_check()` covers what it does not. `chrome` opts a surface out of the
  ramp, and what opts out of a rule is what breaks it: the card and the meter
  token carried 9, 10, 13 and 21 from the day they were written. The sizes
  shipping are 12, 14, 16, 20, 22 and 32, and 12 clears Apple's 11pt iOS floor.
- **The faint greys are a decision, not a defect.** Do not "fix" them. See
  BRANDING.md; the numbers are below and the call was made with them in hand.
- **41% of text fails contrast, and 98% of that is three greys.** `INK2`
  `#8E8E93`, `INK3` `#A9A9AE` and `INK4` `#C4C4C9` measure 3.26, 2.34 and 1.74
  on white against a 4.5 bar. Passing needs `#707070` or darker on `FILL`, which
  is one value for what are currently three, so the fix is a redesign of the
  grey ramp and not a nudge. Run `node figma/contrast.mjs .` before claiming
  otherwise. The greys carry the feed's second line, the receipt labels and the
  kobo tail, so none of it is the decoration a faint grey is usually excused by.
- **A sheet is pinned to the bottom, so it grows off the top.** Pages that get
  taller just scroll; a sheet that gets taller walks its own header off the
  screen and there is no gesture that brings it back. At AX3 fourteen of
  eighteen sheets did this before `sheet()` was capped at
  `max-height: calc(100% - 20px)` with `overflow-y: auto`. Anything pinned to
  one edge has this problem; check it at AX5, not at Large.
- **`DT=AX3 OUT=/tmp/x python3 build.py`** draws every screen at any of the
  twelve Dynamic Type settings. Use it before claiming a layout holds.
- **Measure a screen before deciding what kind of screen it is.** Five screens
  were flagged as actions wearing page chrome and queued to become sheets. All
  five hold 675-750px of content, which is 750-825 once a sheet's padding and
  grabber are added, and a sheet past 720 is a page again. The flag was raised
  on their names and their footers. Nothing was wrong with them.
- The extractor bakes `justify-content: center` into **asymmetric padding** on a
  FIXED row. Those numbers fit one exact string, so changing the words inside
  breaks the fit silently — nothing clips, because `clipsContent` is false.
  After any text change, walk up from each changed node and compare its right
  edge with every ancestor's inner right edge. Fix it by saying what the browser
  says (`primaryAxisAlignItems = 'CENTER'`, padding 0), not by new padding.
