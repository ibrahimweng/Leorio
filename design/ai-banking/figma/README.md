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
| `Heading/Bold 20` | 20 | Bold | 2 | the kobo tail, and Activities |
| `Label/Bold 14` | 14 | Bold | 34 | row titles, amounts, buttons, chips |
| `Label/Regular 14` | 14 | Regular | 14 | row subtitles and card copy |
| `Caption/Bold 12` | 12 | Bold | 4 | Today, Yesterday, the FX chip, the health score |
| `Caption/Regular 12` | 12 | Regular | 7 | shortcut labels and small notes |

`Display/Bold 32`, `Heading/Bold 20` and `Caption/Bold 12` were made for this.
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
  some other file. It is 12px Plus Jakarta Sans on `Caption` now, so the screen
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

| Style | Size | Weight | Carries |
|---|---|---|---|
| `Display/Bold 36` | 36 | Bold | the ceiling. Named, bound to nothing, nothing rounds up into it |
| `Display/Bold 32` | 32 | Bold | a balance |
| `Heading/Bold 20` | 20 | Bold | a page title, a heading over a group, the kobo tail |
| `Label/Bold 14` | 14 | Bold | a row title, a button, a value, a chip |
| `Label/Regular 14` | 14 | Regular | a second line, and everything the model says |
| `Caption/Bold 12` | 12 | Bold | a day separator, a badge, a small firm number |
| `Caption/Regular 12` | 12 | Regular | a note under a field |

This is a phone, so the ramp starts small and never climbs. 36 exists so nobody
invents a size above 32 later, and it is deliberately left out of `TYPE`, which
is the list a stray number is allowed to land on. Everything else went down:
36 to 32, 22 to 20, 16 to 14, and ExtraBold to Bold. `Tag/Bold 10` folded into
`Caption/Bold 12`, which is the one place in the app where type got bigger, and
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
| `Heading/ExtraBold 22` | `Heading/Bold 20` |
| `Heading/Bold 22` | `Heading/Bold 20` |
| `Body/Bold 16` | `Label/Bold 14` |
| `Body/Regular 16` | `Label/Regular 14` |
| `Tag/Bold 10` | `Caption/Bold 12` |

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
differ only in what they are a receipt for. **Parts** are the fourteen things
that appear in more than one screen: the passcode key and the keypad it fills,
the keyboard, the three docks, the three ask bars, the three tool panels, the
sheet row, and the `Button` set. **Icons** holds the `Icon` set and the mark, at
the two sizes it is drawn at.

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
