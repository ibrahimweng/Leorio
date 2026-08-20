# Sending the screens to Figma

This turns the built screens into real Figma layers. Not a screenshot: every
frame comes out as text, vectors, rectangles, gradients, shadows and background
blurs that can be selected and edited.

The file is **AI Banking Screens**, key `BKwjYfTZbP7HzKeGyQr5ba`. Eighteen
frames at 393x852, laid out in two rows of nine, in the same order as the
review canvas.

## Running it

    cd design/ai-banking
    python3 build.py                      # writes the 18 .dc.html screens
    npm i playwright-core                 # only dependency

    export SP=/some/work/dir
    sh figma/rev.sh $SP                   # resolve {{accent}} into a real hex
    CHROME=/opt/pw-browsers/chromium \
      node figma/extract.mjs              # $SP/figma/<Name>.json
    node figma/emit.mjs                   # $SP/figma/<Name>.js

Then paste each `<Name>.js` whole into the Figma MCP `use_figma` tool as its
`code`, with the file key above. Each script is self contained and removes any
frame of the same name first, so sending a screen again replaces it rather than
stacking a second copy. `emit.mjs` takes screen names as arguments if only some
of them changed.

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
