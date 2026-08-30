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
| `Display/Bold 32` | 32 | Bold | 1 | the balance |
| `Heading/Semibold 20` | 20 | Semibold | 2 | the kobo tail, and Activities |
| `Label/Semibold 14` | 14 | Semibold | 34 | row titles, amounts, buttons, chips |
| `Label/Regular 14` | 14 | Regular | 14 | row subtitles and card copy |
| `Caption/Semibold 12` | 12 | Semibold | 4 | Today, Yesterday, the FX chip, the health score |
| `Caption/Regular 12` | 12 | Regular | 7 | shortcut labels and small notes |

`Display/Bold 32`, `Heading/Semibold 20` and `Caption/Semibold 12` were made for this.
The other nine styles were left alone on purpose. `Body/Bold 16` alone is on 108
text nodes elsewhere on the `test` page and `Label/Regular 14` is on 110, so
editing `Display/ExtraBold 36` down to 32 would have moved several hundred nodes
on screens nobody asked about. New styles change one screen. Edited styles
change the file.

Three of the changes were not just a smaller number:

- The balance was 36 ExtraBold and is 32 Bold. That is what takes ExtraBold off
  the screen, and it is why there are two weights now instead of three.
- `Today` and `Yesterday` were 16 Regular. At 14 Regular they would have been
  the same size and weight as the timestamp under every row, which is the one
  line they have to be told apart from, so they are 12 Bold. Small and firm
  reads as a separator. The same size as a row does not.
- `Up 4 since July` was 11px SF Pro on `Caption2/Regular`, a style belonging to
  some other file. It is 12px SF Pro Text on `Caption` now, so the screen
  is down to one family.

The Pay button used to hold its label as three separate text nodes, `Pay `, `₦`
and `8,000 now`, placed by hand, so shrinking the type left gaps in the middle
of the words. Figma trims the trailing space out of `"Pay "` when it measures
the box, and auto layout can only give equal gaps, so three fragments could
never be spaced correctly. It is one text node reading `Pay ₦8,000 now` in a
horizontal auto-layout frame now, centred on both axes and still filling its
row. `Group`, which holds the health score over its ring, is the one frame left
without auto layout, because a number centred on a ring is not a stack.

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

### One spacing grid, one icon system

Every gap and every padding in `build.py` is a multiple of 4. Values round to
the nearest one and ties go up, because the ask on this project has been for
more air rather than less. That rule replaced 19 gap values and 13 paddings.
The odd numbers in the Figma file, rows padded `15,0,15,0` and cards padded
`13,16,13,16`, were never drawn by hand: `extract.mjs` reads the rendered CSS,
so whatever `build.py` sets is what the file inherits. Fixing it here is the
only fix that stays fixed.

A 1px gap on a baseline-aligned row is kerning between a naira sign and its
digits rather than layout, and it rounds to 0, which keeps money tight.

`SPACE` and `RADII` in `tokens.py` were brought onto the same grid afterwards,
because they had not been: `SPACE` still allowed 2 and 6, and `RADII` still
allowed 10 and 14, so the code and the Figma file disagreed about a radius the
file had already been snapped to. `SPACE` is now 4 8 12 16 20 24 32 40 56 72 and
`RADII` is 12 16 20 24 28, which moved `R_TILE`, the rounded square behind a
48px service icon, from 14 to 16. Radii below 8 are artwork and are never
snapped, and anything round is written `PILL`.

Icons had drifted further than the spacing. `badge()` was called with twelve
container sizes between 26 and 64, each with its own glyph, so two rows in one
list could carry a 38 and a 44:

| | Sizes |
|---|---|
| Badge containers | 32, 40, 48, 64 |
| Badge glyphs | always exactly half the container |
| Bare glyphs | 16, 20, 24, 28, 32, 56 |
| Chevrons | 12, or 16 beside a full row |
| Marks | 24, 32, 40 |
| Tickmarks | 24, 56 |

Both keypads drew the same delete glyph at two sizes, 26 and 30. Their keys are
68 to 76 across, so both are 28.

The whole pass was checked by building the screens twice and measuring all 92:
78 grew, none shrank, the median screen gained 12px, and no screen gained any
horizontal overflow. `193:1566` is not built by `build.py`, so it was brought
onto the same grid by hand: 56 values moved, its feed icons all became 40 with a
20px glyph, and seven rows whose padding grew past a fixed height were set to
hug instead, which is what a row should have been doing anyway.

### The type ramp is four sizes and two weights

A ramp is the closed set of sizes text is allowed to be, together with the
weights each size may take. This one was read off the home screen and then
applied to everything else, so `193:1566` and the 91 generated screens finally
agree about how big a balance is.

The face is **SF Pro Text**. Tracking comes out of the font rather than out of
anybody's judgement: SF ships Apple's optical tracking in its `trak` table, and
the normal-track value for each size is what the ramp carries. It is identical
across all five weights, so tracking belongs to the size and not to the cut.
Note which way the curve runs. SF Pro Text is drawn for small text, so the
larger it is set the more it has to be pulled in, which is the opposite of the
way Plus Jakarta Sans was tuned here.

| Style | Size | Weight | Tracking | Carries |
|---|---|---|---|---|
| `Display/Bold 36` | 36 | Bold | −3.42% | the ceiling. Named, bound to nothing, nothing rounds up into it |
| `Display/Bold 32` | 32 | Bold | −3.32% | a balance |
| `Heading/Semibold 20` | 20 | Semibold | −2.69% | a page title, a heading over a group, the kobo tail |
| `Label/Semibold 14` | 14 | Semibold | −1.07% | a row title, a button, a value, a chip |
| `Label/Regular 14` | 14 | Regular | −1.07% | a second line, and everything the model says |
| `Caption/Semibold 12` | 12 | Semibold | 0% | a day separator, a badge, a small firm number |
| `Caption/Regular 12` | 12 | Regular | 0% | a note under a field |

Semibold, not Bold, carries the emphasis. SF sets heavier at a given weight than
Jakarta did, and Semibold is the weight iOS itself emphasises with. True Bold
survives at one size, the balance at 32, and `_ramp()` puts it there without
being asked, because 700 is the only weight that size offers.

**`extract.mjs` has to know the ramp's weights or nothing binds.** Its `STYLE`
map is keyed `size/weight` and is what decides whether a text node arrives
carrying a style name. Moving the emphasis from Bold to Semibold made every
`20/600`, `14/600` and `12/600` fall through it, so 113 nodes that should have
been styled came over loose. Keyed correctly, 2,532 of 2,645 text nodes carry a
style, and the 113 that do not are the on-screen keyboard and the payment card,
which opt out on purpose.

That is also how the share sheet was found. It had been sitting in Figma at
22px and 16px, sizes the ramp dropped a long time ago, because those nodes were
never bound to anything and so no later pass over the styles could reach them.
The fix is the same shape as the icons: read the style name and path for every
text node out of the extracted JSON, walk it into the file, bind, then re-apply
the geometry. Twelve nodes in each of the eight `Share ...` components, and
every instance on Flows followed.

**Changing the face moves every text box.** The widths in the file are the
browser's measurements, so a wider face makes anything with a pinned width wrap.
The fix is not to re-send the screens, which would cost the 785 reactions and
the components again; it is to re-measure. `extract.mjs` is run over the new
build and, for every text node, the file is told what the render now says: hug,
or a fixed width, or a fixed box with coordinates when its parent is not auto
layout. Only 213 of 2,645 text nodes are not hugging, so the payload is small
and the rest correct themselves. Nodes inside a component are collected by
`(main component, path within it)` and applied once at the component, so the
tool panels and docks are fixed in one place rather than in every instance.

This is a phone, so the ramp starts small and never climbs. 36 exists so nobody
invents a size above 32 later, and it is deliberately left out of `TYPE`, which
is the list a stray number is allowed to land on. Everything else went down:
36 to 32, 22 to 20, 16 to 14, and ExtraBold to Semibold. `Tag/Bold 10` folded into
`Caption/Semibold 12`, which is the one place in the app where type got bigger, and
it was chosen knowingly for 55 badges and initials.

`_sized()` enforces it on the way out. Every inline style in the markup is
rewritten before it reaches disk: the size moves to the nearest legal one,
`_near` breaking a tie downwards, the weight moves to one that size permits, and
the line height and tracking are overwritten from the style too, because a style
that only half applies is not a style. So the markup can say 17px and the screen
says 14px.

Measured across all 92 built screens: **2,496 text nodes on four sizes and two
weights, and none off the ramp by accident.** 111 more are off it on purpose,
all of them carrying `class="chrome"`, which is the opt-out for surfaces this
product does not draw: the on-screen keyboard, the payment card and the meter
token. Chrome reaches Figma bound to no style, which is how to tell it apart in
the file.

Retyping shrank almost everything, which was the point: 86 screens got shorter,
3 grew by 2 or 3px, the median screen lost 34px, and no screen gained horizontal
overflow. Across the app 52 elements used to be cut by the dock edge and 33 are
now.

Six styles the new ramp no longer reaches are still in the Figma file, renamed
`Retired/…` rather than deleted, because they are still bound to text on screens
that have not been re-sent. Deleting a style strips those nodes back to loose
type. They go when the last screen is retyped.

Counting the raw literals in `build.py` and calling that the shipped type is a
mistake, and one this README made until it was measured against the built
screens instead.

### Retyping the file without sending it again

The file was brought onto this ramp by editing the frames that were already
there, not by sending the screens again. Sending them again was the plan until
the two versions were compared: **every one of the 92 screens had a byte
identical element tree to the one last sent.** Nothing had been added, removed
or re-nested. Only sizes had changed. So there was nothing a rebuild could do
that an edit could not, and a rebuild costs a great deal.

What it costs is the point. `emit.mjs` removes a frame and builds a new one, so
every reaction pointing at it and every reaction it carried are gone. Flows
holds **785 of them** across 26 sections, and 23 of the screens are components
with instances scattered through those sections, which a rebuild would also
break and which would then need remaking and re-instancing.

The edit was possible because the bindings already carried the answer. Every
line the old ramp covered was bound to one of its styles and chrome was bound to
none, so the whole retype is six style-to-style swaps, and `setTextStyleIdAsync`
carries size, weight, tracking and line height across together:

| From | To |
|---|---|
| `Display/ExtraBold 36` | `Display/Bold 32` |
| `Heading/ExtraBold 22` | `Heading/Semibold 20` |
| `Heading/Bold 22` | `Heading/Semibold 20` |
| `Body/Bold 16` | `Label/Semibold 14` |
| `Body/Regular 16` | `Label/Regular 14` |
| `Tag/Bold 10` | `Caption/Semibold 12` |

907 text nodes moved, 243 gaps, 55 paddings and 73 corner radii snapped to the
4-point grid, and 91 icon containers resized with their glyphs. The walk stops
at every INSTANCE, so a component drives its own copies rather than collecting
overrides, and it only enters SECTION children, so the founder's résumé frames
and images sitting on the same page are never touched. Radius is snapped on
boxes only and never on a VECTOR, because a vector's corner radius is artwork.

Afterwards: **785 reactions, no dead destinations, nothing left on a retired
style.** The sizes still off the ramp are the payment card and the keyboard,
which are chrome and are meant to be.

**The wiring is now written into the file.** Before any of this ran, every
reaction was captured with a stable key, the section name, the screen name and
the chain of child indices from the screen frame down to the control, and stored
in the document's shared plugin data under the namespace `leorio`, in `wire0`
and `wire1`, with `wireRows` holding the count. Read it back by concatenating
the chunks and parsing the JSON. It is the restore map for the day a real
re-send is needed, and it should be re-captured before that day, because it is a
snapshot rather than a live record.

### The drafts on the test page

The `test` page holds the founder's own drawings rather than anything
`build.py` makes: the home screen component, a newer home frame, five copies of
`Main11111 mine`, and roughly thirty hand-drawn screens that predate the
pipeline. They were brought onto the ramp too, in two passes, because they
needed different treatment.

The first pass was the same six style swaps as everywhere else and moved 245
nodes. The second pass had to deal with 1,228 text nodes bound to no style at
all, because the drafts were drawn by hand and never used the system. Those
cannot be swapped, so they were snapped: size to the nearest of 12, 14, 20 and
32 with ties going down, weight through the same table `build.py` uses, and then
forced to Bold at 20 and 32 because those sizes have no regular. 1,196 were
bound that way, with 435 gaps, 484 paddings, 97 radii and 91 icon containers
brought over as well.

Three kinds of text were left loose on purpose:

- **27 nodes at 22 Regular**, which is the on-screen keyboard and the payment
  card. Those are chrome in the built screens too, so they stay off the ramp.
- **5 italics**, the spoken phrases like *2k data for mum*. The ramp has no
  italic style to bind, so only their size was snapped, 16 down to 14.
- **The three `Design System —` sheets**, on Typography, Color, and Spacing and
  Radii. These are documentation, not product. The typography sheet holds one
  specimen per style sitting beside a label naming it, so retyping the specimens
  without rewriting the labels would make the sheet state one thing and show
  another. They are untouched and now describe a ramp the file no longer uses,
  which is worth rebuilding rather than patching.

### The three design system sheets

`Design System — Typography`, `— Color` and `— Spacing & Radius` sit on the
`test` page at 1280 wide. They are documentation rather than product, and they
were left out of the retype at first because the typography one is a specimen
sheet: one text node per style beside a label naming it, so retyping the
specimens without rewriting the labels would have made it state one thing and
show another. They were rebuilt properly instead.

**Typography.** Nine rows became seven, one per live style, in size order from
the 36 ceiling down to `Caption/Regular 12`. Each specimen is now *bound* to the
style it documents, so the sheet cannot go stale again: change a style and the
sheet follows. Each row names the style, its size, line height and tracking, and
what it carries. The meta column was widened from 200 to 300 and set to hug,
because three lines at 200 clipped.

**Spacing & Radius.** The spacing rows are the ten values in `SPACE`, from 4 to
72, with the 2 gone. The radius examples are the five in `RADII` plus the pill.

**Color.** The values were all still correct, so this one only needed its own
type bringing onto the ramp, except for two things that were wrong. `error` was
`#FF3B8E`, which is pink; the error colour is `WARN`, `#FF3B30`. And the three
surfaces that go with it on a payment that did not go through, `WARN_SOFT`,
`WARN_EDGE` and `WARN_TEXT`, were missing entirely. All four are right now.

The swatches also carried no visible labels at all, so reading a hex meant
clicking the layer. All of them now show their token name and hex, in black or
white depending on the swatch's own luminance, and the narrow ramps read
vertically because a 35px column cannot hold `#FAFAFA` on one line.

**`FILL2` and `LINE2` are gone.** Putting them on the ramp is what showed why:
`FILL2` was 1.7 of 255 from `LINE` and `LINE2` was 1.0 from `FILL3`, both below
what an eye can separate, in a ramp where every other step is 4 to 27 apart. The
system was carrying four greys in a band that holds two. Neither was dead code,
`FILL2` had 9 uses and `LINE2` 15, so this was a decision rather than a cleanup.

`FILL2` folded into `LINE` and `LINE2` into `FILL3`, 24 references in `build.py`
and one in `prototype.py`. The surviving comments absorbed the roles, because
otherwise the names would lie: `LINE` is the hairline round a bordered card *and*
a card's own footer strip, and `FILL3` is a quiet block inside a grey card *and*
the edge of a dashed one, which is why `DASH` now reads `dashed FILL3`.

In the file, 192 paints were repointed, 136 on Flows, 32 on Components and 24 on
test, and the ramp went back to twelve steps. The two collapsed colours appear
nowhere in the built screens or in any of the five pages.

All three sheets are on the ramp themselves now, so they are examples of the
system as well as descriptions of it: four sizes, two weights, no Medium
anywhere.

### The Icon set, and how the glyphs got their names

Every glyph in the file is an instance of one component set, `Icon`, in the
`Icons` section on the Components page. 97 variants, one property, `glyph`.
Colour and size stay overrides on the instance, because the same icon is drawn
black on a row, white on a dark button and coloured on a tile.

**Glyphs are named at source now, and that is the whole point.** Every `<svg>`
`build.py` draws carries a `data-icon` attribute, `extract.mjs` reads it, and the
frame arrives in Figma called `Glyph · chevron` rather than `Glyph`. Componentising
is then a lookup, not a guess.

It is a lookup because guessing failed, expensively. The first set was built by
stripping every number out of the path data and treating what was left as a
fingerprint, on the theory that it is stable across sizes. It is stable across
sizes. It is also stable across *different icons*: a three point chevron and a
three point check normalise to the same string. 97 icons collapsed into 58
buckets. The worst bucket held `back`, `check`, `check-small` and `chevron`
together, so promoting one member to stand for all of them put a tick where 470
instances wanted a back arrow or a row chevron. Seven more buckets were nearly as
bad — eight arrows under `up`, six crosses under `plus`, four clock shapes under
`clock`. A bucket name tells you nothing about what it draws.

Repairing it needed a source of truth outside the file. The extracted JSON is
that source: it holds the real name and the exact child-index path of every glyph
in every screen. Walking a screen with that map assigns each glyph independently,
so a screen whose tree has drifted loses only the paths that moved instead of
everything after the first difference. Each screen was checked before it was
touched, by requiring the mapped paths and the icon instances actually present to
be a bijection — same count, every path landing on an icon. 59 of 67 screens on
Flows passed on the first pass. The eight that failed all turned out to be the
same thing: their home surface is an instance of the founder's `Home screen`, so
fixing that one component fixed all eight at once.

The buckets then paid for themselves. Recomputing them from the new set gives,
for any damaged instance, the exact list of icons it could possibly have been —
46 of the 58 have only one candidate, so those are decidable with no map at all,
and for the rest a map is only trusted when it proposes a candidate the geometry
allows. That validator is what made the founder's drafts on `test` safe to touch:
it accepted 47 assignments and rejected 4.

**Swapping cost the prototype twice, and the capture paid for itself twice.**
The glyph promoted into a component happened to be a control that navigated, so
every instance inherited a reaction; stripping it took 21 real links with it.
Later, restructuring the 23 screen components discarded override reactions on
their instances across the Flows page, losing 41 more. Both were restored from
the 785-row capture in the document's shared plugin data, keyed by section,
screen and child-index path. Anything that restructures a component should
expect this and check the count afterwards: Flows should read 785 with no dead
destinations.

Flows, the Components page and the `Home screen` component are wholly on the new
set. 156 glyphs are not: they are in superseded drafts on `test` whose trees
match neither the current home screen nor `build.py`, so there is no map for
them and the geometry leaves more than one candidate. The old set is still in the
file, renamed `Icon (old — superseded)`, only because those instances point at
it. It goes when they do.

The three design system sheets moved off `test` into a `Design system` section
on the same page, so the whole system is in one place.

### The components

Three pages now, not two. **Components** holds the design system, in three
sections.

**Screens** are the 23 that appear in more than one flow, from `Confirm` (x5)
and `DoneSend` (x5) down to the eight `Share ...` and `Done ...` receipts that
differ only in what they are a receipt for. **Parts** are the seventeen things
that appear in more than one screen: the passcode key and the keypad it fills,
the keyboard, the three docks, the four ask bars, the three tool panels, the
sheet row, `Answer head`, `Status pill`, `Field · typing`, and the `Button`,
`Bubble`, `Page head`, `Top bar`, `Tool row` and `Tool panel` sets. **Icons** holds
the `Icon` set and the mark, at the two sizes it is drawn at.

`Bubble` is now the most used component in the file: 61 instances directly, and
157 counting the ones that arrive through the screen components and the home
screen. Four variants under one `who` property — `Amana`, `Amana · with a
title`, `You`, `You · typed`. Amana speaks on a tint at 16 all round and fills
the width it is given; you speak on black at 12 and 16 and the bubble hugs the
words, with the microphone when it came off the voice sheet rather than the
keyboard.

Componentising them fixed something as a side effect. 45 of the bubbles had no
auto layout at all: `tune()` had measured too much drift and fallen back to
absolute placement, so when SF Pro Text made the words taller the frame did not
follow and the tint ran short of the last line. An instance of a hugging
component cannot do that.

**What the model renders is four things.** `Tool panel` is the tool's own
surface running inside the chat, and the three that existed separately are one
set of three variants now. Inside it, `Tool row` is a field the model filled in:
the glyph on the left says how far along it is, so it is swapped for step-done,
step-work or step-todo rather than being a variant, and `go=yes` carries the
chevron for a value that can be corrected. `Status pill` is the dot and the word
beside the tool's name. `Answer head` is the line that says Amana is the one
talking, the mark at 28 over what the card is about, and at 96 instances it is
the second most used component in the file.

The answer card itself is deliberately not a component. Its shell is always a
bordered white card holding a head and a Bubble, but what comes after that is a
row of actions, or a card and a button, or nothing, and Figma cannot add a child
by override. A component that only fitted a third of them would be worse than
none.

**Two things went wrong here and are worth remembering.** The `go=no` row was
cloned from a screen where `tune()` had fallen back to absolute placement, so
the master had no auto layout and its value could not move to the right edge
when the row was widened; every panel clipped until the master was given a real
horizontal layout with the value on FILL and aligned right. And the four rows
that navigate lost their link, because a swap carries text and glyphs across but
not reactions. Flows dropped to 783 before it went back to 787. The link cannot
live on the master either: Figma rejects a NAVIGATE whose destination is on
another page, and the masters are on **Components** while `Amend` is on
**Flows**, so it stays an override on the four instances.

**Headers are two things, not one.** `Page head` is what a page says it is: the
title at Heading/Semibold 20 over the line under it at Label/Regular 14, eight
apart, filling the width it is given and hugging its own height. 45 masters were
swapped onto it, which reads as 53 instances and covers 52 screens, and a second
variant carries a glyph beside the title for the one page that wants one.
`Top bar` is the bar above it on a screen that came from somewhere: back arrow
left, title centred, in a plain variant and a `Amana` variant for the screens
you are talking on.

**The back arrow is why `Top bar` was worth checking twice.** Every one of the
14 wired arrows turned out to carry the same thing, `{action:{type:'BACK'}}`,
with no destination to lose, so the action sits on the master and every instance
inherits it instead of being wired one at a time. That also closed a hole: two
`Confirm` instances, in *When it does not go* and *Pay from your dollars*, had a
visible back arrow with nothing behind it. Flows reads 787 now rather than 785,
and the two extra are those. Had the arrows carried per-screen destinations this
would have gone the other way, and the capture in the shared plugin data is
there for exactly that case.

**The fields are mostly not fields.** The app asks for very little typing, and
what it does ask for goes through surfaces that were already components: the
three ask bars, the two keypads, the dock. What was left over is
`Ask bar · typed`, the ask bar with something in it and a caret where the next
letter lands (4 uses), and `Field · typing`, the answer set at Display/Bold 32
with the caret after it, for a phone number or an NIN (5 uses). Two more are
genuinely one of a kind and were left alone: the bordered confirm field on
`LimitStop` and the inline typed line on `Finish`.

`Button` is one set of twelve variants, two properties: `tone` (black, grey,
white, blue) and `size` (44, 48, 56). Every button carries a leading and a
trailing glyph slot, both hidden by default, so the glyph in the master is a
placeholder and the real one is an override on the instance. 58 buttons across
the file were swapped onto it and 23 more inside the screen components, and the
785 reactions survived it.

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

## One rule for icon weight, one scale for icon size

The set had neither, so it had scatter. At 20px the app drew nine different
stroke weights, and 2,588 of the 2,705 icon vectors in Figma carried a weight
of their own rather than the master's. Sizes were worse: `badge()` and
`circicon()` size a glyph as a fraction of the thing it sits in, and
`round(size * 0.5)` lands on 23, 25, 26, 30, 38 — numbers nobody chose.

The rule was not invented. It is the one 326 of the app's 597 stroked icons
were already on:

    a glyph — a drawn thing with a body — takes 0.075 of its size
    a mark  — a bare path, nothing enclosed — takes 0.10
    what the eye sees is held between 1.1 and 3.2px

1.5px at 20 and 2.4 at 32 for a glyph; 1.6 at 16 and 2.4 at 24 for a mark.
Eight of the sixteen hand-drawn marks — the chevron, the back arrow, the plus
on the action button, the tick in a status badge — already sat exactly there.
The rest was scatter around the same two numbers.

`stroke_for(name, size, box)` in build.py is the only place a stroke width is
decided. `icon()` no longer takes one; the 51 call sites that passed a stroke
passed fifteen different values between them. Sizes go through `icon_size()`
onto 12, 16, 18, 20, 22, 24, 28, 32, 40, 48, 56.

Left alone on purpose, and named in both build.py and figma/audit.js: the
money-health ring, the payment QR, the numbered dial and the stepper are drawn
marks rather than glyphs and carry their own weight and size. So does anything
knocked out of a filled shape — a clock hand, a card stripe — which is part of
the drawing rather than the glyph's outline.

## Two traps this pass fell into

**Stripping an argument shifts every argument after it.** Removing the stroke
from `icon(name, size, colour, sw)` turned fourteen calls that also passed
`extra` into `icon(name, size, colour, extra)`, so a style string arrived where
a number was expected. The census of the built HTML caught it because those
svgs no longer parsed. The rule from CLAUDE.md applies to argument position as
much as to a constant: change one, then grep for everything keyed on it.

**Pulling a text box back on both axes shrinks it on the wrong one.** A pass
meant to stop a wide text box running under the chip beside it also ran down
the vertical axis, where every child of a row overlaps every other, and set
thirteen text heights to 8px. Caught by reading the result rather than the
return value. An axis-symmetric fix for an axis-specific problem is a bug
waiting for a row.

## Auto layout, and where it stops

355 frames in the app screens held more than one child with no auto layout.
301 of them now do, and 55 do not. Every conversion is checked: the frame's
children are recorded, the layout is applied, and if any child moves more than
2.5px the frame is put back exactly as it was.

The 55 that remain fail for one reason. The Figma tree lost some wrapper frames
— a 36px cell holding a 28px glyph, a 22px box holding the camera — so a row
whose gaps are all 12 in the browser measures 16, 115 and 11.6 in Figma, and no
single `itemSpacing` can say that. Restoring those wrappers means re-sending the
screens, which costs the 787 prototype links. Worth doing when the wiring can be
rebuilt from the capture, not before.

Two things the conversion found rather than caused: a row where a text box
widened by SF Pro runs under the chip beside it, and 25 ask-bar placeholders
spilling out of their pill because Figma has no ellipsis. Both are fixed — the
text boxes are pulled back to the gap the row uses, and the placeholders are one
line tall, which is what the browser shows.

## The Components page, arranged

The page had grown by accretion: 23 screens in one 11,400px strip in no
particular order, Parts spilling outside its own section, two icon sets stacked
on top of each other, and nothing anywhere saying what any of it was for.

It now reads top to bottom as four sections, each 2,818px wide, each opening
with its name and a line or two on what belongs in it:

    Screens         24 components, grouped: Home, Sending and receiving,
                    Confirming, Receipts, Share sheets
    Parts           21 components, grouped: Asking, Keys, Chrome, Actions,
                    The assistant
    Icons           the 97 glyph set, packed 12 across in alphabetical order,
                    and the model's mark at its two sizes
    Design system   type and space on one row, colour below

Every one of the 48 components carries a one-line description, so it shows in
the assets panel and in Dev Mode without anyone opening this page.

Two things were found while tidying, and both mattered more than the tidying.
**A live component master was sitting on the `test` page** — `Home screen`,
with 30 instances on Flows — so deleting that page would have broken every one
of them. And **`Action button` was stranded on Flows** with 23 instances
depending on it. Both were moved into the library first. The retired 58-variant
icon set and the 39 superseded drafts on `test` are gone; every instance in the
file now resolves to a master on the Components page, and Flows still reads 787
reactions with no dead destinations.

Two gotchas worth keeping:

**Moving a section carries its children.** Laying children out and *then*
setting `section.x/y` drags everything by the same delta, so the content lands
outside the box you just sized. Position the section first, measure the
coordinate offset, then place.

**A section has no `description` property.** Only components and component sets
do. A section's description has to be a text layer on the canvas.

## The passcode gate became a sheet, and nothing was re-sent

Confirm, ConfirmBuy and ConfirmMeter were full pages. They are the passcode
gate — amount, who, four digits — which is the last thing between a person and
their money, so it belongs over the screen that asked for it rather than in
place of it. Each now rises as a sheet over a dimmed copy of Chat, Buy or
Meter, with a handle at the top and the dim carrying BACK.

The interesting part is how it was done. The three screens were **ten frames,
nine of them instances of two masters**, so the surgery was on three nodes. But
restructuring a master discards override reactions on its instances, and each
instance's twelve keys pointed at a different receipt. So:

1. Capture all 104 links inside the gates — path, name, reaction JSON — into
   shared plugin data.
2. Rebuild the masters: drop the top bar, clone the background in, add a scrim
   and a sheet, move the content column across.
3. Restore by translating each path: content moved from `0.0` to `3.1`, and
   every child shifted down one index as the top bar left.

94 of the 104 survived without restoring, because the content column was
**moved** rather than recreated, and a moved node keeps its id and its
reactions. The 10 that did not were the back arrows that no longer exist.

Two things worth keeping:

**A cloned background brings its links with it.** Chat, Buy and Meter arrived
carrying 11 reactions, which would have made the unreachable, blurred scenery
clickable. Clear them, or the prototype grows paths that exist only by
accident.

**A frame that is FIXED on its primary axis does not shrink when you take a
child out of it.** Removing the top bar left the column still 700 tall holding
632 of content, and the sheet came out nearly full height. `primaryAxisSizingMode
= 'AUTO'` after the removal, and set the remaining children to FILL so they
follow the new width.

## The rename to Amana, and the trap under it

The product was called Leorio, which was a placeholder. It is Amana now — Hausa,
from Arabic *amānah*, a thing given to someone for safekeeping. See
`../BRANDING.md`.

The rename was 13 strings in `build.py`, and in Figma **37 text nodes across 95
screens, without re-sending a single screen**. A rename is text, and text is the
one thing that can be edited in place, so re-sending would have paid the whole
cost of a swap — reactions, styles, overrides — to change a word.

Only **7 of the 37 needed touching**. The other 30 arrived through four masters
on Components: `title=Amana` in `Top bar`, and `tool=Transfers`, `tool=Requests`
and `tool=Airtime` in `Tool panel`. Edit the master, and every instance without
an override follows. The 7 were loose text on Flows plus one instance override
on the Dollars card. Wiring held at 771 reactions with no dead destinations, and
4444 of 4958 texts stayed bound to a style — the same numbers as before.

Three variant values were renamed too: `who=Amana` and `who=Amana · with a
title` on `Bubble`, `title=Amana` on `Top bar`. Renaming a variant is safe;
instances point at the component's id, not its name, and nothing detached.

### A wider word can break a layout that never moved

**The extractor bakes `justify-content: center` into asymmetric padding.** The
chat header row came across FIXED at 249 wide with `primaryAxisAlignItems: MIN`
and padding of **84.5 left, 89.5 right** — numbers that centred a 24px mark, an
8px gap and the word "Leorio" at 43px, and centred nothing else. "Amana" is
*wider* than "Leorio" despite being shorter to read (one `m` beats an `i` and an
`r`), so at 47px the content needed 253 in a box holding 249, and the title
pushed 4px out of its own row on 14 screens.

The fix is not new padding. It is to say what the browser says: set
`primaryAxisAlignItems = 'CENTER'` and the padding to 0. Everything moved 0.5px
and the row now re-centres whatever it is given.

The same shape appeared once more, as stale fixed widths: the MyCode account
column was FIXED at 140 holding text that had grown to 148. The browser measures
that column at 153.14 and its row at 209.14 — it hugs. Setting both to HUG gave
148 and 204, and the card re-centred them.

**So after any text change, check for overflow, not just for the word.** Walk up
from every changed text node and compare its right edge against each ancestor's
inner right edge. Two containers were wrong; both were invisible, because
`clipsContent` is false everywhere and the spill landed in empty space. It would
have shown up the first time someone dragged the frame.

## The receipt that leaves the app

The eight share screens are the in-app record with a sheet over it, and the
sheet offers four ways out — WhatsApp, photos, PDF, anywhere else. Every one of
them sends the same thing, described in the sheet as "the picture, ready to
send". That picture had never been drawn. The rows led nowhere, and the only
artefact of this product another person ever holds existed as a sentence.

`sharecard()` in `build.py` is that picture, and the `Receipt` screen shows it
before it goes. Three things make it different from the receipt inside the app,
and all three are the point:

- **It says who drew it.** A letterhead: the mark at 32 and `Amana` at 20, with
  the status chip on the right. Inside the app nobody needs telling whose app
  they are in. On a copy going to a landlord, it is the whole job.
- **The balance is gone.** The share sheet has promised "your balance is left
  off every copy that leaves the phone" since the day it was written, and the
  in-app receipt has been printing `Balance after` the whole time. A picture
  that keeps the promise had to be a different rendering, not a flag.
- **Nothing can be tapped.** `rref()` is `rid()` without the copy button, and
  From reads `Ibrahim Musa / Amana · 0102 4457 88` rather than `Everyday`,
  which is the nickname only its owner uses.

`donepill()` was lifted out of `rhero()` so the chip on the screen and the chip
on the picture cannot drift, and `obfoot()` — back plus one action, the Task
bottom bar — moved up beside `dock()` and `dockback()`, since it is no longer
only onboarding's.

### Sending it

`node emit.mjs Receipt`, then prepend the page and the placement:

    const PAGE='127:2';const PLACE={Receipt:{parent:'225:2',x:3038,y:80}};

A name that is not in `emit.mjs`'s `ORDER` gets `i = -1` and lands at
(-493, -972), so a new screen needs `PLACE` or it appears off in the corner.
Sections hold their children in page coordinates, and `Send it by voice` starts
at (0,0), so 3038 is both. The section was 3018 wide for six screens and had to
be resized to 3511 for seven — a child outside a section's bounds stays a child
but sits outside the box.

It came in at 52 nodes, 25 of 25 texts bound to a style, and 17 of 18 frames on
auto layout. The eighteenth is the hero column, and it is right to be hand
placed: `write()` gives the naira sign a 0.05em left margin, which at 32px is
1.6px, so the amount's box starts 1.6px in while the two lines under it start
at 0. `tune()` measured 1.6 against `TOL = 1` and put the column back. Auto
layout there would flatten an optical inset the browser really renders.

Three reactions went with it — the WhatsApp row into it, its button on to
DoneSend, and its own back — taking Flows from 771 to **774, none dead**. The
row is an override on one instance of the share sheet, so the other seven share
screens are untouched: they still show the pattern without claiming a picture
that has not been drawn for them.

## Drawing the mark, and one master for 301 copies

The mark was a closed ring at 55% opacity — the shape Figma draws when nobody
has decided. It is now a ring left open 100 degrees at the top, holding a dot:
something goes in and it stays, which is what *amana* means. `BRANDING.md` §4
has the four it beat and why.

**The whole change in Figma was two nodes**, because every copy of the mark is
an instance of `glyph=mark` (582:2092) in the `Icon` set. 301 copies, one edit.
Worth checking for before any bulk change: count instances against loose
vectors first, and if the ratio is good the job is a component edit, not a
re-send.

Two things about editing a vector in place:

- **`vectorPaths` has no arc command.** Figma takes M, L, C, Q and Z only, so an
  SVG `A` throws `Failed to convert path. Invalid command at A`. The arc has to
  be written as cubics.
- **Split the arc where the circle touches its own box.** Cut at -40, 0, 90, 180
  and 220 degrees and the control hull is exactly the curve's bounding box, so
  the node lands where you put it. Split evenly instead and the control points
  poke outside, Figma sizes the node to the hull, and the glyph sits off centre.

The dot came in from r2.9 to r2.7 and the ring went to full opacity, which is
what fixes it at 28px — the bubble avatar, and 119 of the 301.

### What it turned up

Making the marks auditable made the audit see them for the first time, and it
found two things that had been true for a long time:

**`Mark · 34` was off the icon scale.** Two hand-built specimen components,
`Mark · 34` and `Mark · 32`, drew the mark with their own loose vectors, so
`isIcon()` was false and neither was ever checked. Both now hold an instance of
the real master. `Mark · 34` had 52 instances at a size `build.py` never emits;
they were swapped onto `Mark · 32` and the component deleted. Five of the 52
were inside component masters (`Confirm`, `ConfirmBuy`, `Pay`, `Sent`), where
resizing a nested instance child silently does nothing — the master's own node
is the one to resize.

**Figma draws 119 marks at 28 and the browser draws none.** Every call site in
`build.py` is `mark(32)`, `mark(24)` or `mark(40)`; the extractor measures 24,
32 and 40 and nothing else. The 28 is a Figma-side decision from before, written
down in this file as deliberate. It is on the icon scale so nothing flags it,
but it is 4px of drift on the most repeated element in the product, and it is
the assistant's own avatar. Left alone on purpose: it is a visible change in 119
places and it belongs to whoever owns the design, not to an audit.

## The app icon

`appicon()` in `build.py`, next to `mark()`, so the icon and the mark are one
drawing. `brand.py` saves it out and `brandshot.mjs` cuts the PNGs; both write
to `design/ai-banking/brand/`.

Two things differ from the badge inside the app, and nothing else does:

- **Full bleed.** The rounded corner on a home screen is the operating
  system's. Bake one in and it gets masked twice. `appicon(size, mask=True)`
  draws the iOS corner anyway, for a favicon, a deck, or a specimen.
- **58% of the tile, not 53%.** Four were rendered at 180, 120, 80, 60 and 40
  and set beside plain colour tiles at 60. 52% is what the app badge does and
  it is timid on a home screen, a lot of empty blue. 64% pushes the arms of the
  mouth into the corner. A version nudged up 1.5 to correct for the mouth being
  at the top just read as misaligned — the ring is geometrically symmetric, so
  raising it only enlarges the gap underneath.

In Figma it is one component, `App icon` (811:2304), in the `Icons` section
beside the mark, drawn masked so the specimen reads as an icon. It is a
specimen, not a source: the source is `appicon()`.

Deleting `Mark · 34` left the mark specimen stranded at x 174, so it moved back
to 80 and the section caption, which promised the badge "at the two sizes it
appears in", now names the mark and the icon.

## The wordmark

`brand.py` sets `Amana` in Fraunces SemiBold at −0.02em and **outlines it to a
single path**, then composes the lockups round it. `BRANDING.md` §4 has why
Fraunces and why a serif; three things here are about the making.

**The interface font could not be the logo.** SF Pro is licensed for designing
and developing interfaces for Apple platforms, which the screens are and a
logotype is not. That is a hard constraint, not a preference, and it is the one
thing the wordmark turned up that nothing else would have.

**The outline was checked against the browser, not trusted.** The path is
composed on advance widths alone, so kerning would be silently lost if Fraunces
had any for these five letters. Rendering the browser's text in red over the
path at 100px showed them landing on the same pixels: no kerning, nothing
dropped. Worth doing again for any other string.

**`vectorPaths` in Figma is cubics only, and so is this.** The path is written
with `SVGPathPen(ntos=…)` rounding to two decimals at EM 100 — 0.002px at the
size the lockup draws — which halves the file and lets the same string go into
the SVG asset and into Figma.

### Two traps in composing an asset

**Scaling the viewBox is not scaling the art.** The first `wordmark()` wrote
the size into the viewBox and left the path at EM, so the word sat in the
corner of a box twice its size. The group carries the scale.

**A fractional box clips.** The lockup came out 267.44 wide, the browser
snapped the element to 267, and the last `a` lost its edge in every PNG. `_box()`
now ceils the canvas to whole pixels and centres the art in it, which is what a
shipped asset wants anyway.

### In Figma

One component, `Lockup` (815:2303), in the `Icons` section beside the mark and
the app icon. It holds an **instance** of `glyph=mark` plus the outlined word,
so changing the mark still changes the lockup. Positions are absolute, not auto
layout: the mark centres on the middle of the cap height, which is half a pixel
off what `counterAxisAlignItems: CENTER` would give, and a logo is the wrong
place to accept half a pixel.

## Changing the blue

`#2A6AF5` → `#213ACA`. `BRANDING.md` §1 has why; this is how it was done to a
file of 96 screens without re-sending one.

**The accent was in six places in the source that were not the constant.**
`steplight`, `wheelword`, `plaintop`'s wash default, the canvas theme control
and the link hover all carried a literal. They reference `ACC_HEX` now, and
`ACC_HOVER` was added beside `ACC_TEXT_HEX` so the darker link is derived rather
than typed. That is CLAUDE.md's second rule: change a constant, then find
everything keyed on it. The next accent change is one line.

**`recolor.mjs` said what to look for, but the colour map is what applied it.**
Two extractions of the same 96 screens, before and after, diff to a clean
one-to-one map of six values:

    #2a6af5 -> #213aca   x326      the accent
    #255dd8 -> #1d33b2   x123      ACC_TEXT, the accent one step down
    #f0f5fe -> #eff1fb   x116      ACC_SOFT, the panel the model speaks from
    #d3ddf2 -> #9ca5d8    x23
    #2a6af5|0.22 -> #213aca|0.22   x22   ACC_EDGE
    #0034a6 -> #0a1b7e     x1

Because the map is one-to-one, a blanket swap over every fill and stroke is
exact, and it does what the path-walking script cannot: it reaches inside
instances and past the overlay screens whose top child was replaced by a Home
screen instance. The path script painted 14 of 53 on its trial bundle and
reported the other 39 rather than guessing — which is the tool working, and the
signal to swap by colour instead.

**Gradients carry the accent too.** Six stops did. A sweep that only walks
`fills[].color` misses them and leaves the Start screen's wash on the old blue;
the stops need remapping with their alpha kept.

**Check the hex written as text.** Two labels in the Design system section spelt
`#2A6AF5` out. A colour sweep does not touch a string.

Afterwards: 560 fills and 216 strokes on Flows, 55 and 50 on Components, nothing
left on the old palette on any page, and 774 reactions with none dead.

## The mark was 28px in 119 places

`build.py` draws the mark at 24, 32 and 40 and nothing else. Figma drew 119 of
them at **28**, and nothing ever flagged it, for two reasons worth remembering.

**28 is a real size on the icon scale**, so the audit's off-scale check had no
opinion about it. A number can be wrong and on the scale at the same time.

**And the layout paid for it.** `Answer head` set the mark to 28 and added
padding of `[4, 4, 0, 4]` around it. Four plus twenty-eight plus the eight-gap
is forty, which is exactly where the browser puts the text with a 32 mark and
no padding; and the row hugged to 32 either way. So it measured right, looked
right, and the mark was 12.5% small. The record screens' offer row did the same
thing more simply: the mark at 28 in a card fixed at 72, centred, so only the
text's start moved — 56 where the browser says 60.

The fix was **ten nodes**: the mark inside `Answer head` (which carries 90 of
the 119) with its padding zeroed, and the offer row's mark on eight record
masters plus the parked `Done` copy. Everything else followed by instance. The
source needed no change and no screen was rebuilt — this was Figma catching up
with what `build.py` already said.

Afterwards the mark reads 24, 32 and 40 on Flows and nothing else, and the
`Answer head` row on Main measures 32 tall with the mark at 32 and the text at
40, which is the browser node for node.

**The general shape of this one:** when a measurement is off, look for
something nearby paying for it. A wrong number that has been compensated for
is invisible until you compare against the source rather than against how it
looks.

## A second family, and what it cost the pipeline

Money is set in Fraunces now. The pipeline had exactly one font in it —
`emit.mjs` opened with `const F='SF Pro Text'` and put every text node in it —
so a second family meant teaching three things.

**`extract.mjs` computes the family but was throwing it away.** `typo()` read
it; `textNode()` built its object field by field and never copied it across, so
the JSON came out with 2746 nodes and not one family among them. Two lines.
Worth remembering the shape: a value that is computed and then not carried
looks exactly like a value that was never computed.

**Merging runs has to agree on the family.** `sameTypo` decides whether two
inline runs become one Figma text node, and a text node there carries one font.
Without the family in that test, a money run beside a word would merge and one
of the two would silently lose its face.

**The weight names differ.** SF Pro calls it `Semibold`, Fraunces calls it
`SemiBold`, and Fraunces has no `Medium` at all, so `ST(w)` takes the family
now and answers for it.

The family is carried **only when it is not SF Pro**, so a screen that never
mentions money extracts byte for byte as it did before.

### Four money styles

`Money/Bold 32`, `Money/Semibold 20`, `Money/Semibold 14`, `Money/Regular 14` —
each mirroring the style the amount used to take and changing only the family,
so the size and the tracking stay on the ramp. 574 nodes on Flows and 104 on
Components were rebound, which is why the audit's bound count did not move:
rebinding is not detaching.

Identify a money node in Figma the same way `build.py` does — by content, a
currency sign and no letters. Not by size, and not by which style it is
wearing.
