# Sending the screens to Figma

This turns the built screens into real Figma layers. Not a screenshot: every
frame comes out as text, vectors, rectangles, gradients, shadows and background
blurs that can be selected and edited.

The file is **AI Banking Screens**, key `BKwjYfTZbP7HzKeGyQr5ba`. Every frame
is 393x852.

Two pages matter. **test** holds the screens on their own, in the order of the
review canvas. **Flows** holds nine sections, one per way of doing a thing:
send, receive and services, each reached by voice, by camera and by typing at
the model. A screen that appears in more than one flow is a separate copy in
each, so a section can be read straight through without jumping pages.

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

### The seven screens drawn over the home screen

`Ask`, `AskReq`, `AskSvc`, `Receive`, `Typed`, `TypedAsk` and `TypedBuy` are not
pages of their own. Each is the home screen with something on top: a voice
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
black, so the parser handles that form separately.

`emit.mjs` wraps a screen's nodes in the plugin code that rebuilds them. The
same glyph appears four or five times on a screen, so SVGs are stored once in a
lookup and referenced by index, which keeps every script under the 50,000
character limit on the tool.
