# AI banking screens

Eighteen iPhone screens for a Nigerian personal banking app built around a
language model. They are a design brainstorm, not code for the Leorio app.

There are three things to build.

- `tokens.py` holds every colour, size, corner radius and shadow. The screens
  never write one directly, so the look is changed in that one file.
- `python3 build.py` writes the `.dc.html` screens for the review canvas.
  `canvas.json` places them and holds the notes.
- `python3 prototype.py` writes `prototype.html`, a walkable version of the
  same screens with working navigation. It reads the screen markup out of
  `build.py`, so there is one source of truth.

Neither built page is tracked, since together they are about 4 MB and both can
be made again from the sources here.

## The design system

Taken from the Fuse wallet screens and applied to the whole product. Six rules
carry it.

1. The page is white. Grey only ever appears as a card, never behind one.
2. Titles are true black and heavy. Everything supporting them is a light grey.
3. Money splits in two. The whole number is black and heavy, the decimal is two
   thirds the size and pale.
4. A **thing** that exists is an icon in a rounded square, in its own
   saturated colour with a white glyph. A service keeps its colour everywhere
   it appears, so you find electricity by its colour before you read the word.
   An **action** you can take is the same glyph in the same colour, drawn as a
   bare line with no square behind it. That is the rule the reference follows,
   and it is what keeps a row of four shortcuts from shouting louder than the
   thing it sits next to.
5. A card is either a flat grey fill or a dashed outline. Nothing casts a
   shadow except a button, the ask bar and a sheet.
6. A sheet rises over a page that is dimmed and blurred, and floats clear of
   all four edges.

The accent is a vivid blue. Black stays the action you are meant to take, and
blue is the action that belongs to the thing you are looking at.

## The bar at the bottom

The reference puts three tab icons on the left and a black circle on the right,
with nothing drawn behind them. This product replaces the tabs with the model.

- On home: the cog, then the ask bar, then the black circle.
- On every other screen: back, then the ask bar, then the black circle.

So back lives at the bottom left on every screen, which is where the reference
puts it. The black circle opens send, receive, history and pay a bill over a
blurred page. That is the only place those four live, so no screen has to carry
them, and the grid stays free for services.

Screens that are a task rather than a place drop the ask bar and the circle.
They show back and one slide to confirm, because a payment screen should offer
exactly one action.

## The screens

Home and what opens on top of it:

- `Main.dc.html` is the home screen
- `Actions.dc.html` is the black circle open
- `Receive.dc.html` is the receive sheet
- `Ask.dc.html` is asking by voice

The model at work:

- `Answer.dc.html` is an answer rendered as a screen instead of a paragraph
- `Pay.dc.html` is a transfer the model filled in for you to confirm
- `Done.dc.html` is the end of any purchase, and where it offers to repeat it
- `Rules.dc.html` is the standing instructions it may run on its own

The service stack:

- `Services.dc.html` is the whole catalogue
- `Airtime.dc.html` is a data bundle, prepared from four spoken words
- `PowerPay.dc.html` is electricity before paying
- `Power.dc.html` is electricity after paying, with the meter token
- `Bills.dc.html` is everything that repeats each month
- `Loan.dc.html` is borrowing, with the whole cost on one screen
- `Card.dc.html` is a virtual card made for one merchant
- `Goal.dc.html` is a savings goal, and what is feeding it

The rest:

- `History.dc.html` is every movement, newest first
- `Settings.dc.html` is the account

## Figma

All eighteen screens are also in Figma, as real layers rather than images.
Text is text, icons are vectors, and the gradients, shadows and background
blurs come across. The file is **AI Banking Screens**, key
`BKwjYfTZbP7HzKeGyQr5ba`.

`figma/` holds the converter that puts them there and the notes on how it
works. It reads the built screens, so Figma is refreshed by building again and
resending, never by editing anything by hand twice.

## The three ways to reach a service

A bank with forty services cannot put forty tiles on a screen.

1. **The grid** is for browsing. One flat row of four on home, the full
   catalogue on Services.
2. **The sentence** is for speed. Say what you want and the model prepares it.
   The ask bar is on every screen, so this is always the shortest route.
3. **The card** is for confirming. Recurring things are offered before you go
   looking, so the bill you always pay comes to you.

## The scales

Enforced when the files are generated. `snap()` in `build.py` pulls every size,
weight, gap, padding and radius onto the nearest step, so nothing can drift.

- **Type**: 12, 14, 16, 22, 26, 36. The whole ramp came down a step after a
  pass over the home screen, so the product reads quieter than the reference.
  Money never uses 12, because below about twelve and a half pixels the Naira
  sign loses its crossbars, so `snap()` lifts any figure to 14.
- **Weight**: 400 for anything grey, 700 for anything named, 800 for money.
- **Space**: 2, 4, 6, 8, 12, 16, 20, 24, 32, 40, plus 56 and 72 which are
  structural rather than rhythm. A page starts 72 from the top.
- **Radius**: 10, 12, 14, 16, 20, 24, 28, plus a pill.

## Contrast, and what it cost

The reference greys are lighter than the accessibility standard allows for
small text. Matching them exactly was a deliberate decision, taken knowing the
cost. The type ramp then came down a step, which compounds it: light grey and
small text together. Measured across all eighteen screens, 553 pieces of text:

- 367 pass.
- 186 do not, and every one of them is one of the three greys or the pale
  decimal half of a money figure.

Nothing that carries meaning on its own fails. Titles, figures, amounts, row
names and buttons are black on white. What fails is the second line under a
title, which repeats what the icon and the title already said, and the kobo.

Three things were darkened, because the reference has no equivalent to copy.

- Green as text, for money coming in.
- Red as text, for a bill nobody is covering.
- The accent as small text, one step towards black.

`IN` and `WARN` stay at the reference brightness where they are an icon or a
fill. `IN_TEXT` and `WARN_TEXT` are for words.

To measure it again, render the screens with `{{accent}}` replaced by the hex
value and walk the DOM computing the ratio of each text node against its
resolved background.

## Motion

anime.js v3, which rides inside the built files because a published page cannot
load a script from anywhere else. `vendor/anime.min.js`, MIT, credited in
`vendor/LICENSE-anime.txt`.

What moves, and why:

- Screens slide in and out, and the content above the fold staggers up behind
  them.
- The balance counts up once, on arrival.
- The four actions stagger up out of the black circle, and the circle turns
  into a cross.
- A sheet rises from the bottom while the page behind it blurs.
- The savings ring draws from empty to where you actually are.
- The slide to confirm is a real drag, and a tap also works.

Every animation has a callback that runs once and a timer that forces it. If
the frame loop is throttled, anime has already set opacity to zero, and a
screen must never be left blank because of that.

Everything is skipped under `prefers-reduced-motion`.

## Type

Plus Jakarta Sans, subset and embedded as a data URI in every built file.

It is here for one reason. Google's webfont subsets deliberately leave out the
Naira sign at U+20A6, and Figtree and Manrope have no Naira glyph at all. Plus
Jakarta Sans has one, and subsetting the full variable font from source keeps
it.

The glyph needs help. Its crossbars run to the edges of the letterform and read
as a strikethrough against a digit, so every Naira sign is wrapped in a span
with a small margin on both sides. Below about twelve and a half pixels the
crossbars stop rendering at all. The type ramp starts below that at twelve, so
`snap()` lifts any figure carrying the sign to fourteen instead.

Files and licence are in `fonts/`.

## Gamification

One mechanic, and it is progress towards a goal you set yourself.

The research this was drawn from is clear that points, badges and leaderboards
move engagement in the short run and move behaviour very little, and that
visible progress towards your own goal is what holds up. So the savings ring is
the only score in the product, and it counts money you actually put aside.

- Cashback goes to the goal rather than back as cash. Same money, better place.
- The standing instruction log counts times and amounts, not points.
- Bills use segments, not a percentage, because a percentage is a number you
  can farm.
- Taking a loan gets no tick and no cheer.

There is no credit limit progress bar. That is the single mechanic here that
would reliably lift borrowing, and every competitor uses it. It is left out on
purpose, and that is a decision worth taking knowingly rather than by default.
