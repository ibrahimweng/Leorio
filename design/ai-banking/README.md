# AI banking screens

Six iPhone screens for a personal banking app built around a language model.
The screens are a design brainstorm, not code for the Leorio app.

## The screens

- `Main.dc.html` — home, made of cards the model wrote for today
- `Ask.dc.html` — asking by voice
- `Answer.dc.html` — an answer rendered as a card instead of a paragraph
- `Pay.dc.html` — a payment the model filled in for you to confirm
- `Account.dc.html` — an ordinary banking screen with the same input bar on it
- `Rules.dc.html` — the standing instructions the model may run on its own

`canvas.json` places the screens on the canvas and holds the notes.

## Ideas the screens are built on

1. An answer is a card, not a paragraph.
2. One input bar sits on every screen.
3. The model prepares an action and the person confirms it. Nothing moves on its own.
4. Every answer links back to the payments it was added up from.
5. Two type styles. Numbers from the bank are set in Archivo. Anything the model
   wrote is set in Newsreader. You can tell them apart at a glance.
6. One accent colour, used only for the model.
7. You speak to ask and you read the answer. There is no spoken reply.
8. You change an answer by tapping the chips in it, not by asking again.
9. Home is already full, so nobody faces an empty box.
10. Autonomy is handed over one rule at a time, and each rule keeps a log.

## Rebuilding the canvas

The published page is built from these files with the `design` skill's helper.
The built file `ai-banking-screens.html` is not tracked, since it is about 2 MB
and can be made again from the sources here.
