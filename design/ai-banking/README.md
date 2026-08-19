# AI banking screens

Eleven iPhone screens for a Nigerian personal banking app built around a
language model. They are a design brainstorm, not code for the Leorio app.

Run `python3 build.py` to write the `.dc.html` screens. `canvas.json` places
them on the canvas and holds the notes. The built canvas page is not tracked,
since it is about 3 MB and can be made again from the sources here.

## The screens

Core:

- `Main.dc.html` is the home screen, made of cards written for today
- `Ask.dc.html` is asking by voice
- `Answer.dc.html` is an answer rendered as a card instead of a paragraph
- `Pay.dc.html` is a transfer the model filled in for you to confirm
- `Rules.dc.html` is the standing instructions it may run on its own

Services:

- `Services.dc.html` is the full catalogue
- `Airtime.dc.html` is buying a data bundle for someone else
- `Power.dc.html` is a paid electricity bill and its meter token
- `Bills.dc.html` is everything that repeats, and what is covered
- `Loan.dc.html` is a loan offer with the whole cost on one screen
- `Card.dc.html` is a virtual card made for one merchant

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
5. Two type styles. Money and interface text are Libre Franklin. Anything the
   model wrote is Newsreader, a serif. You can tell them apart at a glance.
6. One accent colour, kept for the model and the action it proposes.
7. You speak to ask and you read the answer. There is no spoken reply.
8. You change an answer by tapping the chips in it, not by asking again.
9. Home is already full, so nobody faces an empty box.
10. Autonomy is handed over one rule at a time, and each rule keeps a log.
11. A loan is never offered unprompted, and its whole cost is on one screen.

## Fonts

The screens carry their own fonts. See `fonts/README.md` for why.
