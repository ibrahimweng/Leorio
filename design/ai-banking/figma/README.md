# Sending the screens to Figma

This turns the built screens into real Figma layers. Not a screenshot: every
frame comes out as text, vectors, rectangles, gradients, shadows and background
blurs that can be selected and edited.

The file is **AI Banking Screens**, key `BKwjYfTZbP7HzKeGyQr5ba`. Every frame
is 393x852.

Three pages matter. **test** holds the screens on their own, in the order of
the review canvas, and the home screen the founder drew. **Flows** holds
twenty sections, one per way of doing a thing, read left to right: send,
receive and services, each reached by voice, by camera, by typing at the model
and by tapping; then the half of a bank that is not the happy path, what runs
on its own, what the black circle opens, the one number for the habits, what
you set, and putting money away. A screen that appears in more than one flow
appears in each of them, so a section can be read straight through without
jumping pages, but only one of those is the drawing: the rest are instances of
it. **Components** holds what they are instances of.

## Running it

    cd design/ai-banking
    python3 build.py                      # writes every .dc.html screen
    npm i playwright-core                 # only dependency

    export SP=/some/work/dir
    sh figma/rev.sh $SP                   # resolve {{accent}} into a real hex
    CHROME=/opt/pw-browsers/chromium \
      node figma/extract.mjs              # $SP/figma/<Name>.json
    node figma/emit.mjs                   # $SP/figma/bundle/<n>.js

Then paste each bundle whole into the Figma MCP `use_figma` tool as its `code`,
with the file key above. Each script is self contained and removes any frame of
the same name first, so sending a screen again replaces it rather than stacking
a second copy. `emit.mjs` takes screen names as arguments if only some of them
changed, and packs as many as fit under the tool's character limit.

**A section's children are placed relative to the section, not to the page.**
This is the opposite of a group and it is the easiest thing in the file to get
wrong, because a section at the origin behaves as though it were absolute and
everything below it silently lands at twice its own offset. Set a child to
`PAD`, never to `sec.y + PAD`. Checking it by measuring `child.x - sec.x`
cancels the mistake out and reports the right numbers for the wrong reason;
measure `absoluteBoundingBox` against the section's own box instead.

Prefix a bundle with `PAGE` and `PLACE` to aim it. `PAGE` is a page id; `PLACE`
gives each screen its x and y, and optionally the `id` of the exact node it
replaces, which is what to use on a file where two pages hold a frame of the
same name:

    const PAGE='127:2';
    const PLACE={Meter:{x:9860,y:-2000},DoneSend:{x:10846,y:-2000}};

### Sending less than a whole screen

Two smaller tools exist for the common case where a screen is nearly one that
is already in the file.

`repatch.mjs <base> <next> <node-id>` compares the two extracted trees with the
words and colours stripped out. If the shapes match it writes a script that
walks the text nodes in order and sets the new words, carrying each line's
sizing mode and measured box with it. Use it for a screen that differs only in
what it says.

`graft.mjs` adds selected top-level subtrees to a frame that already exists,
with an optional list of indices to strip first. Use it when a screen gains or
loses a section rather than changing its words.

When a screen has to go back in whole, a PLACE entry may name a `parent` and
an `index` as well as the node it replaces:

```
const PAGE='127:2';
const PLACE={Settings:{id:'219:145',parent:'225:4738',index:1,x:573,y:80}};
```

The parent matters because the Flows page is sections, and appending to the
page would lift the screen out of the flow it belongs to. The index is what
keeps it in the same place in the row. And x and y are then read as the
section's own coordinates, per the rule further down. Check for instances
inside the frame before doing this: whatever was bound to a component is a
plain frame again afterwards, and has to be put back.

`recolor.mjs` is for a change that is only colour, where re-sending forty
screens would throw away every instance, backdrop and component binding in the
file to repaint a few hundred squares. Build the old design into a second
directory, extract both, and it walks the two trees together and writes down
every fill, stroke and glyph colour that differs, as a path of child indices
from the screen frame. `emit-recolor.mjs` turns that into a script that walks
the same path in Figma. Four hundred edits fit in one call.

```
git archive <old-commit> design/ai-banking | tar -x -C $SP/old --strip-components=1
(cd $SP/old/ai-banking && python3 build.py && bash figma/rev.sh $SP/old)
CHROME=/opt/pw-browsers/chromium SP=$SP/old node figma/extract.mjs
CHROME=/opt/pw-browsers/chromium SP=$SP      node figma/extract.mjs
SP=$SP OLD=$SP/old node figma/recolor.mjs    # writes recolor.json
SP=$SP node figma/emit-recolor.mjs           # writes recolor/1.js
```

Three things make it safe to run against a page where some screens are
instances and some are not. It refuses to descend into an INSTANCE and says so,
which is the right answer: the master gets painted once and the instances
follow. It checks the name of the node each path lands on before painting it.
And it is idempotent, so a call that times out half way is fixed by running it
again.

**A path counted from the tree can be one step out at the top.** The nine
screens with a rebuilt backdrop have had their leading children replaced by a
single instance, so a child that was fourth in the extraction is third in the
file. Each edit therefore carries the name of the top-level child its path
starts at, and the script looks for that name before it starts counting. Below
the top level the two trees agree exactly, because the converter built them.

**Do not sweep by colour value.** The obvious shortcut, repainting every small
square that holds one of the palette colours, turns the green tick on a
finished payment into a grey circle. A tick, a warning triangle, a switch that
is on and a progress bar are all small and all coloured, and none of them is an
icon square. Where a sweep is the only option, restrict it to nodes the
converter named `Icon`, skip anything named `Mark`, and read back what it
touched before trusting it: on the twenty component masters that list was
seven, and three of the seven were wrong.

### The nine screens drawn over the home screen

`Ask`, `AskReq`, `AskSvc`, `Receive`, `Typed`, `TypedAsk`, `TypedBuy`, `Draft`
and `Actions` are not pages of their own. Each is the home screen with something on top: a voice
sheet, a keyboard, a chooser. The converter builds that backdrop from the same
markup as everything else, so what arrives is the home feed this repo draws,
and the home screen in the file is the one the founder drew. Left alone, the
first step of a flow and the second step of the same flow disagree about what
the app looks like.

`backdrop.js` fixes that in the file, because it cannot be fixed in the markup
without redrawing their screen. Paste it whole into `use_figma` after
re-sending any of the seven: it strips the backdrop the converter built and
clones theirs in behind the overlay instead. It finds the frames by name, so
the node ids can change underneath it, and running it twice is the same as
running it once.

### The components

Three pages now, not two. **Components** holds the design system, in three
sections.

**Screens** are the five that appear in more than one flow: `Confirm` (x5),
`DoneSend` (x5), `Done` (x4), `ConfirmBuy` (x2) and `Sent` (x2). **Parts** are
the thirteen things that appear in more than one screen: the passcode key and
the keypad it fills, the keyboard, the three docks, the three ask bars, the
three tool panels and the sheet row. **Icons** holds the mark, at the two sizes
it is drawn at.

Which parts earn a component is decided from the file, not from memory: hash
every subtree on Flows, count what repeats, and take what still repeats once
the things above it are folded in. Build them smallest first, bind, then build
the next size up from a frame that is already bound, or the master will hold a
copy where the page holds an instance and nothing will match.

The home screen is the exception. It is a component too, but it stays on the
**test** page where the founder drew it, because making a copy the master would
leave two homes in the file and only one of them true. Sixteen places use it:
nine as the first step of a flow, seven as the backdrop behind an overlay.

`components.js` binds Flows to all of that. A screen that is sent again arrives
as a plain frame, so the instances in it go back to being copies; run this and
they are instances again. It works from the smallest component up, because the
keypad inside a fresh `Confirm` has to become an instance before the `Confirm`
itself can match the `Confirm` component. Matching is by shape, not by name, and
a subtree that is already an instance is skipped, so a clean file reports
nothing swapped.

Run it after `backdrop.js`, since the home screen goes in last.

## How it works

`extract.mjs` opens each screen in headless Chromium and walks the DOM, reading
geometry and style from the browser's own computed values. So what lands in
Figma is what the screen actually renders, not a second reading of the source.
Each node comes out as one of three kinds: a rectangle, a run of text, or an
SVG.

Two things are worth knowing.

**Text width.** Figma's metrics run a hair wider than the browser's, so a line
pinned to its measured width re-wraps and breaks the layout. Only text that
already wrapped in the browser gets a fixed width. Everything else is left to
size itself, which is what the `ml` flag on a text node means.

**Colour.** Chromium resolves `color-mix()` to `color(srgb r g b)` with values
from 0 to 1, not 0 to 255. Reading those as bytes turns every mixed colour
black, so the parser handles that form separately. A colour written into an SVG
attribute is a different matter: the browser never computes it, so a
`color-mix()` there travels all the way to Figma as a string nothing can read.
`build.py` resolves those at the boundary instead.

**Progress rings.** Figma's SVG import drops `stroke-dasharray`, so a ring drawn
as a dashed circle arrives as a closed one and a savings goal a third of the way
along reads as finished. The visible part is drawn as an arc path instead.

`emit.mjs` wraps a screen's nodes in the plugin code that rebuilds them. The
same glyph appears four or five times on a screen, so SVGs are stored once in a
lookup and referenced by index, which keeps every script under the 50,000
character limit on the tool.
