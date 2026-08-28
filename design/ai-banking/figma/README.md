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

## One ledger

Every figure in the file comes from one account read in order. A receipt's
balance is not chosen, it is what the one above it leaves. Change a number here
and the ones below it have to move with it.

| When | What | Moves | Everyday is left with | Screen |
| --- | --- | --- | --- | --- |
| 27 Aug 09:00 | Netflix, on the virtual card | −5,200.00 | 47,654.51 | DoneCard |
| 27 Aug 11:22 | Ikeja Electric | −8,000.00 | 39,654.51 | Power |
| 27 Aug 16:40 | Pagrin Limited, August salary | +640,000.00 | 679,654.51 | DoneIn |
| 28 Aug 07:30 | Holiday goal, round ups | −280.00 | 679,374.51 | no receipt |
| 28 Aug 07:55 | Sarah Adeyemi, rent part payment | −20,026.88 | 659,347.63 | DoneSend |
| 28 Aug 08:02 | MTN, 5GB for Mum | −2,500.00 | 656,847.63 | Done |
| 28 Aug 09:14 | Sarah Adeyemi, flat deposit | −50,026.88 | 606,820.75 | DoneFlat |
| 28 Aug 10:45 | John Doe, grocery shopping | −8,000.00 | 598,820.75 | DoneShop |
| 28 Aug 12:00 | Netflix, monthly subscription | −3,500.00 | 595,320.75 | DoneSub |

So **Everyday holds ₦595,320.75**, and that is the figure the home screen, the
Pay screens, the pocket picker and the convert screen all show.

The dollars are a second pocket: **$412.60**, which is ₦640,355 at ₦1,552, the
one rate the file uses. The three conversions on the Dollars screen add up to
$412.60 exactly. The Holiday pot holds ₦82,400, and its three feeds add up to
that. Nothing else on any screen is a balance: the ₦29,000 on Limits is what is
left of a daily cap, and the ₦15,000 on Rules is a floor.

One screen sits outside this on purpose. **Short** shows ₦12,480 in Everyday
because it is the scene where there is not enough, and its own four figures add
up. It is a different moment, not a contradiction.

## What each flow is for

Every section on Flows carries a line in the empty band above its screens,
saying what that flow is there to show. Twenty six of them:

| Flow | What it is for |
| --- | --- |
| Send it by voice | The shortest route there is: say it once, check what it filled in, slide. |
| Send it from a photo | Reading account details off a photograph, so nobody types eleven digits. |
| Send it by typing | The same send for a room where talking out loud is not on. |
| Send it by tapping | The route for anyone who does not trust a new way yet: the ordinary form, still ending in a slide. |
| Ask to be paid, by voice | Turning what you are owed into a request the other person pays in one tap. |
| Ask to be paid, by typing | The same request typed, so a noisy bus is not a reason to give up on it. |
| Be paid, from home | The four ways money reaches you, and the one number you hand out. |
| Buy something by voice | Buying data by saying it, with everything the model filled in shown before it goes. |
| Buy something by typing | The same purchase typed, and the check that it got the number and the bundle right. |
| Pay a bill from a photo | A meter number read off a paper bill, and the one question a photograph cannot settle. |
| Pay a bill, the ordinary way | Electricity without a camera, ending on the token you actually came back for. |
| The services drawer | Everything the app does that is not sending or receiving, in one drawer. |
| Look at what happened | The record. Every line in the feed opens a receipt you can read, keep and send on. |
| When it does not go | The four ways a payment stalls, and what the screen says instead of an error code. |
| When it was wrong | The door out of a receipt: pull it back, correct it, or get a person onto it. |
| What runs on its own | Standing instructions: what runs without asking, and where you go to stop it. |
| The button | What the black circle opens, and the note it lets you write before anything moves. |
| How the habits add up | One number for how the month is going, and what sits behind it. |
| What you set | The controls: what opens the app, what it may spend, and which phones are allowed. |
| Putting money away | A goal, the rule that feeds it, and stopping the rule without losing the goal. |
| Opening an account | Four questions to a working account, with everything already answered kept on screen. |
| Keep some in dollars | Holding dollars: where they live, what the rate is, and what you end up with. |
| Pay from your dollars | Spending dollars on a naira payment, with the rate held while you decide. |
| Finishing setting up | The optional half: what the higher limits cost you in questions. |
| Signing in again | Coming back to a phone that already knows you. |
| When the digits do not match | The identity check failing, and a way back that is not a call centre. |

## The page is walkable

Every section on Flows is a flow you can click through. Each screen carries one
reaction to the next, the last one loops back to the first, and each section is
a flow starting point named after itself, so the play button opens a list of the
twenty six flows rather than one long canvas.

Two of them animate rather than dissolve, because the list of questions in
opening an account and in finishing setting up literally morphs from one screen
to the next and a smart animate shows that. Everywhere else the change is a
fourteenth of a second, which is short enough to stay out of the way.

Two rows lead out of the flow they sit in: Sign in on the door, and Finish
setting up on the Ready screen. Those carry their own reaction, because the
frame's reaction takes any click that a child does not.

### The links are on the controls

Not on the frames. A slide goes to the passcode gate, a row opens the thing it
names, the back arrow goes back, and clicking a piece of card does nothing,
because that is what the app does.

The markup already knows all of this: every element that leads somewhere carries
`data-go`, and the ones the walkable prototype handles itself carry `data-act`.
What Figma needs on top is a way to find the same element in a tree that has no
attributes on it, and the answer is the box. `hotspots.mjs` measures every one
of them in the browser, and because Figma's nodes were built from those same
measurements, matching on x, y, width and height finds the node again.

    sh figma/rev.sh $SP
    SP=$SP node figma/hotspots.mjs        # $SP/figma/hotspots.json

Then, per screen: match each box to the deepest node that fits, and set one
reaction on it. `back` becomes Figma's own back. An act, or a slide that writes
a receipt, becomes the next screen in the section. A name becomes that screen,
preferring the copy in the same flow. Once a screen has at least one control
wired, its frame reaction is removed so it stops swallowing clicks; the last
screen of each section keeps one, so no flow dead ends.

Three things do not match, on purpose. The seven overlay screens keep the
founder's home behind them, laid out differently, so anything measured up there
is dropped before it is sent. The camera in the ask bar is smaller than the box
the markup hangs its link on, so it is found as the third thing in the bar
rather than by its box. And a control that names its own screen means "yes,
that one" rather than "go there", so it goes to the next screen instead.

Wiring is not preserved when a screen is sent again. `emit.mjs` removes the old
frame and builds a new one, so the reactions that pointed at it and the ones it
carried both go. After sending anything to Flows, rewire that section.

## Screens that stand in two flows

A screen used by more than one flow is a component on the Components page, under
the section called Screens, and every place it appears is an instance. There are
seventeen: Confirm, ConfirmBuy, Done, DoneSend, DoneIn, DoneCard, Power, Sent,
Receive, Pay, Nin, Who, Share, ShareBuy, ShareIn, ShareCard and SharePower. Home
screen is the founder's and lives on the test page.

Six of those are records. Every line in History opens one, so a receipt is not
something you see once in the seconds after paying and then lose. That is also
why Power is a component now: a bill paid is reached from both bill flows and
from History, and for a while both bill flows ended on the receipt for a data
purchase instead.

Share and ShareBuy are a sheet over a receipt, and the receipt under them is an
instance of DoneSend and of Done rather than a copy. A receipt is the screen most
likely to change, and a share sheet holding a stale copy of one is the exact
failure the shelf exists to prevent.

This is not tidiness. Receive and Pay were two frames apiece for a while and a
change to either left the other quietly stale, which is the one failure nobody
notices until a review.

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

### Gradients

Both kinds go across. A `linear-gradient` becomes a `GRADIENT_LINEAR` with the
angle turned into Figma's transform. A `radial-gradient` becomes a
`GRADIENT_RADIAL`, and only the shape this repo draws is read: an ellipse given
in per cent of its own box, as in

    radial-gradient(126% 92% at 50% -6%, ...)

Figma has no radius and centre to set, only a transform, so the emitter builds
the inverse of the matrix that maps the unit square onto that ellipse. Any other
radial syntax is dropped rather than guessed at, and the fill comes out empty,
which is visible immediately.

The onboarding wash is a radial. It is not given a height: it is the flex item
above the list, so it takes whatever space the list is not using and fades out
inside it. That is why it can never sit under a word, and why it shrinks on its
own as answered questions pile up.

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

### The home screen is theirs, and it is `193:1566`

There are two things in this repo that look like a home screen and only one of
them is the home screen.

**`193:1566` on the `test` page is the home screen.** The founder drew it. It
is a component, it is 393 by 2077, and every `Home screen` on the Flows page is
an instance of it: eighteen of them, at the head of seventeen flows and behind
nine overlays. It is what anybody opening the file sees.

**`Main` is not the home screen.** It is what `build.py` draws so the walkable
prototype has something to start from, and it is never sent to Figma. It looks
like a home screen and it is 852 tall and it is a stand-in.

So: **anything added to home goes into `193:1566`.** Adding it to `home_inner`
in build.py changes the prototype and changes nothing anybody looks at. That
mistake was made twice, once with the money health row and once with the
dollars row, and both times the flow that started at home led to a screen the
home screen had no way of reaching.

`rowgraft.mjs` is how a row gets there. It builds the row here, where the
design system is, and puts that node into their frame, rather than redrawing it
by hand in Figma where it would drift:

```
SP=$SP SRC=Main PICK=4,5 TARGET=70:5590 AT=0 PAGE=70:1340 node figma/rowgraft.mjs
```

`PICK` is indices into the screen's Content column, which is where a page's own
rows live; print them with a few lines of node against the extracted JSON.
`TARGET` is `Frame 5`, the column inside the home screen that holds Activities
and the feed, so `AT=0` puts a row above Activities and under the dark header.
Running it again removes what it added last time, so it is safe to repeat.

### The home screen has four font sizes

The type on `193:1566` runs on four sizes and two weights, and nothing else.
Every one of its 62 text nodes is bound to a style, so there is no loose type
left on it.

| Style | Size | Weight | Nodes | What it carries |
|---|---|---|---|---|
| `Display 32` | 32 | Bold | 1 | the balance |
| `Heading 20` | 20 | Bold | 2 | the kobo tail, and Activities |
| `Label/Bold` | 14 | Bold | 34 | row titles, amounts, buttons, chips |
| `Label/Regular` | 14 | Regular | 14 | row subtitles and card copy |
| `Caption Bold` | 12 | Bold | 4 | Today, Yesterday, the FX chip, the health score |
| `Caption` | 12 | Regular | 7 | shortcut labels and small notes |

`Display 32`, `Heading 20` and `Caption Bold` were made for this. The other six
styles in the file were left alone on purpose. `Body/Bold` alone is on 108 text
nodes elsewhere on the `test` page and `Label/Regular` is on 110, so editing
`Display` from 36 down to 32 would have moved several hundred nodes on screens
nobody asked about. New styles change one screen. Edited styles change the file.

Three of the changes were not just a smaller number:

- The balance was 36 ExtraBold and is 32 Bold. That is what takes ExtraBold off
  the screen, and it is why there are two weights now instead of three.
- `Today` and `Yesterday` were 16 Regular. At 14 Regular they would have been
  the same size and weight as the timestamp under every row, which is the one
  line they have to be told apart from, so they are 12 Bold. Small and firm
  reads as a separator. The same size as a row does not.
- `Up 4 since July` was 11px SF Pro on `Caption2/Regular`, a style belonging to
  some other file. It is 12px Plus Jakarta Sans on `Caption` now, so the screen
  is down to one family.

Two frames on this screen have no auto layout, so their text does not reflow
when its size changes and has to be re-seated by hand. `Button · Pay ` holds
its label as three separate text nodes, `Pay `, `₦` and `8,000 now`, and `Group`
holds the health score over its ring. Both were re-centred after the resize,
and the button needed 3px put back between the word and the amount because a
trailing space at 14px is only about three and a half pixels wide. Anything
that changes type here has to check those two again.

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
