# The bottom of every screen, and what the round button means

Three decisions, taken 29 August 2026. Written down because the bottom bar is
the only thing on all 95 screens, and it currently says different things in
different places without meaning to.

---

## 1. The bottom bar has three states, not two — done

Today 48 screens carry the ask bar and a round black button, 25 carry one
action and no ask bar, and 13 carry nothing. The round button always opens the
Actions sheet — on a receipt as much as on the home screen. That is the
problem: on a receipt the page already has a black button that says "Share
receipt", so there are two black things a thumb-width apart meaning different
things.

The round button means one thing and one thing only: **start something new.**
It therefore belongs only where starting something new is a real option.

| State | Left | Middle | Right | Screens |
|---|---|---|---|---|
| **Home** | settings | ask bar | round + | 6 |
| **Place** | back | ask bar | round + | 11 |
| **Record** | back | ask bar, full width | — | 31 |
| **Task** | back | — | one action | 25 |
| **Bare** | — | — | — | 10 |

**Home** (6) — Main, Ask, AskReq, AskSvc, Actions, Receive. The last four are
the home screen with a sheet over it, which is why they carry the settings gear
rather than back.

**Place** (11) — somewhere you can start a payment from:
Services, History, Bills, Rules, Card, Dollars, Goal, SaveRule, Paused, Ways,
MyCode.

**Record** (31) — a thing that already happened, or a setting. The assistant
stays reachable, because "why was there a fee?" is a fair question about a
receipt. There is nothing to start:
Done, DoneSend, DoneIn, DoneCard, DoneFlat, DoneShop, DoneSub, Power,
Share, ShareBuy, ShareIn, ShareCard, ShareFlat, ShareShop, ShareSub,
SharePower, Sent, Pending, Failed, Reversed, Recall, Short, Wrong, Converted,
Answer, Pick, Settings, Lock, Limits, Devices, Health.

**Task** (25) — unchanged. The source already states the rule and it is a good
one: *a screen that is a task earns one action and nothing else.* Mid-payment
the screen stays quiet.

**Bare** (10) — Scan, ScanBill, Opening, Draft, Typed, TypedAsk, TypedBuy,
NoFace, Rule, Amend.

### A thing that looked like a bug and was not

`Receive` draws the settings gear at the bottom left rather than back. That is
correct: `Receive` is `page(home_inner) + askbar(...) + RECEIVE_SHEET`, which is
the home screen with a sheet over it, not a detail page. `Ask`, `AskReq`,
`AskSvc` and `Actions` are built the same way. An earlier draft of this plan
called it a bug; it was wrong.

### What it took

`dock()` gained a `plus` flag and `dockback()` passes it through. 23 call sites
set it false, which covers 31 screens: the eight share screens are their own
receipt with a sheet over it, so they followed without being touched.

In Figma, nine receipt component masters lost the button from their dock and
every instance followed; the eight share masters hold a receipt instance and so
fixed themselves; 14 more were removed directly on Flows, 11 by deletion and 3
by hiding, which auto layout treats the same. No screen was re-sent.

Flows now reads **771 reactions, no dead destinations**. The 16 that went were
the taps on the buttons that no longer exist — a deliberate drop, not a loss.
771 is the new baseline.

---

## 2. Confirm becomes a sheet — done

Confirm, ConfirmBuy and ConfirmMeter were full pages. They are the passcode
gate: the amount, who it is going to, and four digits. That is the last thing
between a person and their money, and it belongs over the screen that asked for
it rather than in place of it.

An earlier draft of this section said they were a summary card with a slide to
pay. They are not — the slide lives on the screen before. The gate is a keypad.

Each now rises as a sheet, 373 wide and about 690 tall, over a dimmed and
blurred copy of the screen that asked: Chat behind a transfer, Buy behind a
purchase, Meter behind a bill. The top bar is gone, because back from a
passcode is not a place, it is the screen you were already on; there is a
handle at the top and the dimmed part throws it down. NoFace, the same gate
after Face ID misses, is a sheet too — it would be incoherent as a page while
its own success state is a sheet. Amend stays a page: it is editing, not a
yes-or-no.

### How it was done without re-sending anything

The three gates turned out to be **ten frames, nine of them instances of two
masters**: `Confirm` with seven instances including NoFace, `ConfirmBuy` with
two, and `ConfirmMeter` alone as a plain frame. So the surgery was on three
nodes, not ten.

Restructuring a master discards override reactions on its instances, which is
in CLAUDE.md because this project has been bitten by it before. So all **104
links inside the gates were captured first** — node path, name and reaction
JSON — into shared plugin data, then the masters were rebuilt, then the links
were restored by translating each path: the content column moved from `0.0` to
`3.1`, and every child shifted down one index as the top bar left.

In the event, 94 of the 104 survived on their own, because the nodes were
*moved* rather than recreated and a moved node keeps its id and its reactions.
The other 10 were the old back arrows, which no longer exist; the scrim carries
BACK now.

One thing the clone brought with it: the background copies of Chat, Buy and
Meter arrived carrying their own 11 links, which would have made the dim,
unreachable scenery clickable. Cleared.

Flows reads **771 reactions with no dead destinations** — the same number it
started at — and every gate's keys still point where they did: four to their
own DoneSend, two to Done, one to Power, one to NoFace, one to Short, one to
the dollars DoneSend.

---

## 3. The service tiles come down to the scale — done

`grid_tile` drew a **64px tile with a 32px glyph**, which made the eight
service shortcuts the largest icons in the app — larger than the home screen's
own four shortcuts at 22px, and 60% larger than the list rows six pixels below
them on the same page.

They are now a **48px tile with a 24px glyph**, which is the size the unused
`svc_tile` helper had specified all along. `svc_tile` itself is deleted; it was
the same thing at the right size, written and then forgotten.

Applied in `build.py` and in Figma.
