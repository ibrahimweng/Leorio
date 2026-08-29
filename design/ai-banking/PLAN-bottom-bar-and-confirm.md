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

## 2. Confirm becomes a sheet

Confirm, ConfirmBuy and ConfirmMeter are full pages today. They are the only
screens in the app that ask a yes-or-no question, and a yes-or-no question
should not take the screen away from what it is about.

They become **one component with three variants**, rising as a tall sheet —
about 80% height — over the page you came from, dimmed and blurred, exactly
like the share sheet already does. The content does not change: the same
summary card, the same slide to pay. Only the container.

`Amend` stays a full page. It is an editing screen, not a yes-or-no.

### The wiring

18 links lead into a confirm, 11 lead out.

In: Chat, ChatTyped, Found, Pay, Meter, Buy, BuyTyped, Short, Reversed,
PayDollars, LimitStop, Amend, Recall, Request, RequestTyped, Draft.
Out: seven to a DoneSend, two to Done, one to Power, one to NoFace.

As a sheet the "in" links stay NAVIGATE but the destination is the same page
with the sheet up, so each source flow needs a sheet-up copy of itself, or the
sheet is drawn as an overlay on the existing frame. **Overlay is the right
answer** — Figma supports OPEN_OVERLAY, and it is what the design actually
means. The "out" links are unchanged.

### What it takes

`build.py` grows a `confirmsheet()` beside the existing `sheet()`, and the
three confirm screens are rebuilt through it. Those three screens are re-sent,
so their links must be restored from the 787-row capture afterwards — 29 links
touched, all recorded.

This is the only one of the three changes that puts the prototype at risk. It
is worth doing once, carefully, with the capture open.

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
