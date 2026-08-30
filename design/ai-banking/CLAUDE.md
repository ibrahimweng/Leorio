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
the six r&eacute;sum&eacute; documents moved to their own page. **Ten text styles** are
defined and all ten are bound to something.

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
- The extractor bakes `justify-content: center` into **asymmetric padding** on a
  FIXED row. Those numbers fit one exact string, so changing the words inside
  breaks the fit silently — nothing clips, because `clipsContent` is false.
  After any text change, walk up from each changed node and compare its right
  edge with every ancestor's inner right edge. Fix it by saying what the browser
  says (`primaryAxisAlignItems = 'CENTER'`, padding 0), not by new padding.
