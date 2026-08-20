# AI banking screens

Thirteen iPhone screens for a Nigerian personal banking app built around a
language model. They are a design brainstorm, not code for the Leorio app.

There are two things to build.

- `tokens.py` holds every colour, typeface, corner radius and shadow. The
  screens never write one directly, so the look is changed in that one file.
- `python3 build.py` writes the `.dc.html` screens for the review canvas.
  `canvas.json` places them and holds the notes.
- `python3 prototype.py` writes `prototype.html`, a walkable version of the
  same screens with working navigation. It reads the screen markup out of
  `build.py`, so there is one source of truth.

Neither built page is tracked, since together they are about 3.5 MB and both
can be made again from the sources here.

## The screens

Core:

- `Main.dc.html` is the home screen, made of cards written for today
- `Ask.dc.html` is asking by voice
- `Answer.dc.html` is an answer rendered as a card instead of a paragraph
- `Pay.dc.html` is a transfer the model filled in for you to confirm
- `Done.dc.html` is the end of any purchase, and where it offers to repeat it
- `Rules.dc.html` is the standing instructions it may run on its own

Services:

- `Services.dc.html` is the full catalogue
- `Airtime.dc.html` is buying a data bundle for someone else
- `PowerPay.dc.html` is an electricity bill before you pay it
- `Power.dc.html` is the same bill after, with its meter token
- `Bills.dc.html` is everything that repeats, and what is covered
- `Loan.dc.html` is a loan offer with the whole cost on one screen
- `Card.dc.html` is a virtual card made for one merchant

## How the prototype is wired

Screens carry two attributes that the canvas ignores and the prototype reads.

- `data-go` moves you somewhere. The value is a screen name, or `back`, or
  `ask` to raise the voice sheet, or `done|Pay` to finish a purchase.
- `data-act` runs something in place, e.g. picking a bundle, stepping the loan
  amount, flipping a switch or revealing a card number.

`hook()` in `build.py` writes both. Anything that answers `soon` is a screen
the walkthrough does not include.

## How the services fit in

The usual answer is a grid of sixteen coloured tiles, and it breaks as soon as
you add the seventeenth. These screens split the job across three surfaces.

1. The grid is for finding things. Only the handful you use get a tile. The
   rest are grouped rows, which still work at forty services.
2. The sentence is for speed. Buying airtime by hand is five steps. Said out
   loud it is one line, and the model fills the five steps in.
3. The card is for confirming. Every service ends in the same card with the
   same slide, so there is one thing to learn instead of forty.

On top of that, anything that repeats is offered to you rather than waited for.
A bill that is due and a data bundle about to run out both arrive as cards on
the home screen, so the common case never touches the grid at all. Each of
those offers can become a standing instruction, which is how a task turns into
something that just happens.

## The rules the design follows

1. An answer is a card, not a paragraph.
2. One input bar sits on every screen, and it doubles as the service search.
3. The model prepares an action and the person confirms it. Nothing moves on
   its own unless a rule was switched on by hand.
4. Every answer links back to the payments it was added up from.
5. The model always speaks from a soft peach panel with its badge beside it,
   and nothing from your bank ever sits in one. That is how you tell a fact
   from a summary at a glance.
6. Orange is the brand and the model. Black is the one action you are meant to
   take, so a suggestion never looks like a confirmation.
7. You speak to ask and you read the answer. There is no spoken reply.
8. You change an answer by tapping the chips in it, not by asking again.
9. Home is already full, so nobody faces an empty box.
10. Autonomy is handed over one rule at a time, and each rule keeps a log.
11. A loan is never offered unprompted, and its whole cost is on one screen.

## The look

Monochrome structure on a near white page. White cards separated by soft
shadow rather than hairlines. A circle behind every icon, grey for a list and
black for a main action. A black pill for the one thing you are meant to do on
a screen. Sentence case section headings.

The only colour that is not a grey belongs to the model. Its badge is orange
and the panel its words sit in is a five percent tint of that orange. Nothing
else may use it. Green and red are kept for meaning alone, which is money
coming in and a bill nobody is covering.

## The three scales

`tokens.py` holds a type ramp of nine sizes, a spacing rhythm of four pixels
and five corner radii. `snap()` in `build.py` pulls every value in the built
screens onto those scales, so nothing can drift off them.

Before this was enforced there were 31 type sizes, five weights, 18 gap values
and 23 radii, and two of the type sizes were arithmetic accidents nobody had
chosen.

## Contrast

Every text pair was measured against WCAG AA at the size it is used. Fourteen
failed before the clean up and none fail now. No text is set in anything
lighter than the mid grey, which clears 4.5 to 1 on white, on the page and on
a filled panel.

## Fonts and the Naira sign

The screens carry their own font. See `fonts/README.md` for why, and for why
the typeface choice was narrower than it looks.

The Naira sign needs two more things. It gets a hair of space on each side,
because its two crossbars stick out past the N and otherwise read as a line
drawn through the number. And no money is set below about 12.5px, because
below that the crossbars stop rendering and the sign turns into a plain N.
