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

Flows should read **771 reactions with no dead destinations**. If a number moves,
find out why before doing anything else. A swap carries text and glyphs across but
**not reactions**, and that is how 21, then 41, then 4 links were lost.

The baseline was 787 until the round button came off the 31 record screens; the
16 links that went were the taps on buttons that no longer exist. When a number
drops on purpose, change it here in the same commit, or the next run reads a
deliberate decision as a regression.

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
