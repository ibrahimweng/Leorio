# Branding

Working document. Started 29 August 2026 from four answers: the name is open,
the position is peace and reliability, the design system stays as it is, and the
blue stays.

**The name is Amana**, chosen the same day. Section 3 keeps the reasoning and
the names it beat, because the next person to ask "why not something else?"
deserves the answer rather than the conclusion.

---

## 1. What is already settled

**The design system is the visual brand and it is right.** Greyscale carries the
interface, one blue is saved for the thing worth looking at, seven text styles,
one spacing scale, one icon rule. Nothing in this document changes it.

**The blue moved.** `#2A6AF5` → **`#213ACA`**, on 29 August. The old one sat in
the iOS system blue's neighbourhood, and the app icon proved what that cost: on
a home screen beside other blue banks it did not separate itself at all, and the
shape was doing every bit of the work. The new one is a few degrees toward
indigo and darker — night rather than daylight, which is the position.

It also fixed something nobody had measured. White on `#2A6AF5` was **4.69**,
over the 4.5 floor by a hair: the primary button's own label was scraping the
minimum. White on `#213ACA` is **8.32**, and the accent as small text on white
goes from 5.78 to 9.68.

Three others were drawn and rejected — the same blue merely taken down (still on
the shelf), a much deeper ink (dusty, and it lost its life on the icon), and a
small nudge toward cyan (changed nothing, 4.77).

**The voice exists and is the best thing in the file.** It was written, not
designed. Section 5 writes down the rules it is already following.

**The name is Amana**, and it is already in the product — 13 strings in
`build.py`, 17 screens, and every text node in Figma. See section 3.

---

## 2. What this brand is for

In your words: *someone looking for peace, comfort and a reliable platform. Not
noisy, not fast. Just reliable every time, and trustworthy.*

**"Not fast" is the sharpest thing here.** Every Nigerian fintech competes on
speed — instant transfers, instant loans, instant everything. Choosing *reliable
every time* over *fast* is a real position, and it is one nobody else is
standing on. It should be the centre, not a footnote.

It also sets a test for every decision below: **does this feel like something
that will be the same when I come back?**

---

## 3. The name

**Settled: Amana.** Hausa, from Arabic *amānah* — a thing given to someone for
safekeeping. The rest of this section is why, and what it beat.

### A constraint that has not been stated

The name is not just the company. It is **the assistant's name**. The chat
header says it. The tool panels say `Amana Transfers`, `Amana Requests`,
`Amana Airtime`. The paid tier is `Amana Plus`. The account is held at it.

So the name has to survive being spoken to: *Ask ___. ___ found three accounts.
___ moves them on the 28th.* That rules out a lot of good nouns. `Ask Canopy`
does not work. `Ask Amara` does.

A rename cost 13 strings in `build.py`, 17 built screens and 37 text nodes in
Figma — half a morning, done the day the name was picked. It would not have
been half a morning after launch, when the name is also on cards, statements,
an App Store listing and other people's bank apps.

### On butterflies and flowers

Honestly, and then it is your call.

A butterfly means transformation, fragility and a short life. A flower means
growth, and then it dies. Both are beautiful and both say the opposite of
*reliable every time* — which is the position you just chose. For a bank, a
butterfly risks reading as flighty.

**The strong version of your instinct is a tree.** Shade, shelter, roots, fruit,
and it is there every time you come back. Nature, comfort, safety and prosperity
are all in it, and so is permanence, which a butterfly cannot give you. In
Nigeria the tree people gather under is a shared, real image, not a metaphor.

There is also one narrow way the butterfly survives, and it is worth knowing:
**the eyespot on a wing is a ring inside a soft shape** — which is exactly the
mark already drawn 181 times in this app. If you want the wing, that is the
door.

### The test

A name here has to live inside sentences the product already writes. Judge every
candidate by reading these aloud, not by looking at it:

    Ask ___.
    ___ Transfers        ___ Requests        ___ Airtime
    Get ___ Plus
    ___ · 0102 4457 88
    Or send a screenshot straight to ___ from WhatsApp.

A name that is beautiful on a page and awkward in "Get ___ Plus" is the wrong
name, because the product says that and never says the other thing.

### A correction to the last draft

**Iroko is not available in Nigeria.** iROKOtv is one of the best known Nigerian
technology companies. I recommended it before checking, which was careless. The
tree is still the right idea; that word is not.

### Shortlist

**The three I would actually put in front of a room**

| Name | Where it comes from | Why it is strong |
|---|---|---|
| **Amana** | Hausa, from Arabic *amānah* — a thing given to someone for safekeeping | The meaning is the product. Not "trust" as an adjective, but a specific old word for *money you are holding for someone else*. Warm, three syllables of nothing, reads as a person and as an institution at once. "Ask Amana." "Amana · 0102 4457 88." |
| **Shea** | The West African tree. Its butter is called women's gold | Nature, comfort and prosperity in one object, and a shea tree takes fifteen years to fruit and then gives for two hundred. That is *reliable every time* as a living thing. Short, soft, and already a person's name. |
| **Alafia** | Yoruba, and Hausa *lafiya*, from Arabic — peace, health, being well | It is a **greeting**. Across West Africa you say it to ask whether someone is well. A bank named after the question "are you alright?" is a good bank. Slightly long in "Get Alafia Plus". |

**Also worth saying aloud**

| Name | Meaning | Honest read |
|---|---|---|
| **Odan** | Yoruba, the big shade tree people gather under | Short, drawable, and the image *is* comfort. Less familiar than Iroko, which is now an advantage. |
| **Ìtura** | Yoruba, comfort and relief | Precisely one of your four words. Does not explain itself to a non-Yoruba speaker. |
| **Udo** | Igbo, peace | Short and strong. Also a common German first name. |
| **Èso** | Yoruba, fruit | Three letters, prosperity from a tree, very clean in "Eso Transfers". Collides with Spanish *eso* and a large video game. |
| **Ìrì** | Yoruba, dew | Dew arrives every morning without fail, quietly. Lovely and tiny; possibly too slight to carry a bank. |
| **Gida** | Hausa, home | Safety and comfort, plainly. Home-named banks are a crowded genre. |

**Do not use**

| Name | Why |
|---|---|
| Iroko | iROKOtv |
| Palm, anything palm | PalmPay |
| Anchor | Anchor is a Nigerian banking-as-a-service company |
| Obi | Igbo for *heart* and *home*, and perfect — but politically loaded in Nigeria right now |
| Ndidi | Igbo for *patience*, which is the position exactly, but every Nigerian hears the footballer |
| Zuma | Hausa for *honey*, and Zuma Rock, but the political reading swamps both |
| Monarch, Sage, Bloom, Petal | Already fintechs elsewhere |

### What I would pick

**Amana.** Of everything here it is the only name whose meaning is the business
rather than a metaphor for it. A bank is a thing that holds what is not its own,
and there is a word for that which millions of Nigerians already know. It works
spoken, it works as the assistant, it is short enough for an app icon, and it
carries no cuteness that will look silly in five years.

**Shea** is the one to pick if you want the nature to be literal and visible —
it gives you a tree, a fruit, a butter and a colour, which is a lot of material
for a mark.

One thing to hold on to now that it is chosen: Amana reads as Islamic finance
to some ears, and there are Amana banks in Tanzania and Sri Lanka and an Amana
fund in the US. In a country that is half Muslim and half Christian that is a
reading to answer on purpose — in the mark, in the first screen, in how the
account is described — rather than one to discover from a review. It is in the
open list below.

---

## 4. The mark

**Drawn, 29 August 2026.** A ring left open at the top, holding a dot, in the
rounded square the whole icon set uses. Something goes in and it stays, which
is what *amana* means. It replaces a closed ring at 55% opacity that was the
shape Figma draws when nobody has decided.

Five were drawn and looked at together at 28, 32, 48, 64 and app-icon size:

| | Why not |
|---|---|
| **Now** | The 55% ring vanished small. At 28 it was a dot with a haze. |
| **Aperture** | Legible at every size and completely generic — a record button. |
| **Cradle** | `( • )` is the universal broadcast symbol. Wrong for a bank. |
| **Seed** | Lovely at 64, mush at 28, and it reads as a smile. |
| **Kept** | Chosen. |

The mouth is **100 degrees**. That is the widest that still reads as a ring
rather than a U, and the narrowest that survives 28px — at 70 degrees and below
it closes up and becomes Aperture again at the sizes that matter. The dot came
in from 2.9 to 2.7 to give the ring room, and the ring went to full weight on
the same stroke rule as every other glyph, which works out at 1.8 in the 24 box
for every size between 15 and 42.

Rules that held, and still hold:

- **It was drawn at 32px first**, then checked upward. 32 is the ask bar, on
  every screen; 28 is the bubble avatar and the hardest size; 40 is the opening
  screen. A logo designed large and shrunk would have died at 32.
- One colour on white, and white on the blue. No gradients — nothing else in
  this design system has one.
- It is **one master**. 301 copies across the file, every one an instance, so
  the next change is one edit. That is how this one was made.

### The app icon

Drawn the same day. It is the same mark and only two things change.

**It is full bleed.** The rounded corner on a home screen belongs to the
operating system; baking one in gets it masked twice.

**The glyph takes 58% of the tile**, not the 53% it takes in its badge. 53 is
right for a 32px chip beside a line of text and timid on a home screen — a lot
of empty blue. 64 crowds the arms of the mouth into the corner. Everything
inside the glyph is held exactly, so the icon *is* the mark, larger, rather
than a second drawing of it.

It is written by `appicon()` in `build.py`, beside `mark()`, so the two cannot
drift. `brand.py` saves it out to `design/ai-banking/brand/` — an SVG master
and PNGs at 1024, 180, 120, 80, 60 and 40, full bleed and masked.

This icon is what settled the blue. Sitting it beside plain colour tiles at
60px made it obvious that `#2A6AF5` did not separate from the other blue banks
at all — the shape was carrying the whole thing. Section 1 has the new one.

### The wordmark

**Amana is five letters and three of them are `a`.** Whatever the `a` does, the
wordmark does. Six faces were set and the letter looked at on its own first,
because that was the actual decision.

**It is set in Fraunces SemiBold**, tracking −0.02em, capital A. Two reasons:

- **A serif, against a category that is entirely sans.** Kuda, Opay, PalmPay,
  Moniepoint — all sans. The position is *not fast, reliable every time*, and a
  serif says permanence and care where a sans says speed and tech. The UI stays
  SF Pro, so the wordmark sits above the interface like a masthead rather than
  fighting it.
- **Warmth over neutrality.** Newsreader is the calmer serif and the safer
  choice; Fraunces has the friendlier `a` and more character, and comfort is
  half the brief. Instrument Serif was the most beautiful at 64px and too thin
  at 14. The three sans all read as "a fintech".

Settings that were tested rather than assumed: 700 is blocky and 500 is light,
so **600**. Tracking at −0.04 crowds the A into the m and 0 reads loose, so
**−0.02**. Lowercase *amana* is softer but loses the proper-noun dignity, and
the UI says Amana everywhere, so **capital A**.

**It could not have been SF Pro.** Apple licenses that face for designing and
developing interfaces for Apple platforms — which is exactly what the screens
are, and exactly what a logotype is not. A wordmark goes on a card, an App
Store listing, a deck, a sign. Fraunces is under the SIL Open Font License,
which permits use in a logo. `fonts/README.md` carries the notice.

**And the shipped wordmark is not a font at all.** `brand.py` outlines it to
one path, so `brand/wordmark.svg` and the lockups are shapes. Nothing needs
Fraunces installed for the logo to be right, which is the only way a logotype
should travel.

### The lockup

Said as proportions of the wordmark's own size **S**, so it holds at any scale:

- **Mark height 0.90S**, which puts it a little taller than the caps.
- **Gap 0.25S.**
- The mark is **centred on the middle of the cap height**, not on the box —
  otherwise it floats high against a word with no descenders.
- **Clear space:** the mark's height on all sides.
- **Smallest sizes:** the wordmark alone holds to 13px, the lockup to S = 16.
  Below that, the mark alone.

Stacked is for a square hole — a share sheet, a sign, an avatar. On the blue,
everything goes white.

---

### The money

**The amount is set in Fraunces too**, at the weight the design already asked
for. So the system is two faces and a rule you can say in one line: **SF Pro
sets the interface, Fraunces sets the name and the amount.** On the shared
receipt the wordmark and the figure under it are now the same face, which is
why that card suddenly reads as one document rather than a logo above a table.

**The face reaches money and nothing else.** `build.py` gives a value slot the
money face only when the slot holds nothing but an amount — a currency sign,
optionally a leading minus, digits, and no letters. That is why `Sarah Adeyemi`,
`GTBank · 0123 4457 8842`, the account number and the session ID all stay in SF
Pro, and why an amount inside a sentence does too: *money as a figure* gets the
face, money mentioned in prose does not.

The subsets carry no letters at all, which is the second lock on the same rule.

**The naira decided which faces were even possible.** Google serves the digits
in one subset and the naira in another, and never both in one file. Manrope,
Instrument Serif, Sora, Outfit and Figtree have no naira anywhere. Of the ones
that do, IBM Plex Mono puts monospace gaps round the comma (`₦595 , 320`), and
Archivo and Newsreader are competent but look so much like SF Pro that they
would have been a third face doing no work. `fonts/README.md` has the details.

---

## 5. The voice, written down

These are not new rules. They are what the copy is already doing.

1. **Say what happened, not what the system did.** "She has it." Not
   "Transaction successful."
2. **Name the thing in the world.** "Ikeja Electric, and last month it was
   ₦7,500." Not "Utility payment."
3. **A number is a fact, so give it plainly.** "3 of 5 covered." "2 still to
   sort."
4. **Offer the next step as a question, not a command.** "Rent again next
   month?" Not "Set up recurring payment."
5. **Admit what you cannot do.** "The token did not work?" is a door, not an
   apology.
6. **Never say sorry for something that is not your fault**, and never say it
   twice.
7. **Say what you are protecting.** "Your balance is left off every copy that
   leaves the phone."
8. **Short sentences. No exclamation marks. No emoji.**
9. **Nigerian, not translated.** Naira, meter tokens, NIN, LAWMA, DStv. Never
   "utility provider".
10. **When there is nothing to say, say nothing.** An empty screen is allowed to
    be empty.

---

## 6. Order of work, once the name is picked

1. ~~**Put the mark on the shared receipt.**~~ Done, and it turned out to be
   more than a logo drop. The picture that goes to WhatsApp did not exist as a
   design at all — the eight share screens are the in-app record with a sheet
   over it, and the sheet's four rows led nowhere. So the artefact itself was
   built: `sharecard()` in `build.py`, and a `Receipt` screen that shows it
   before it goes.

   It carries a letterhead — the mark at 32 and the name at 20 — and it does
   **not** carry the balance, which the share sheet has been promising in
   writing all along and the in-app receipt has been printing anyway. Two
   fields also read differently on a copy going to someone else: From is the
   person's name rather than "Everyday", the nickname only Ibrahim uses, and
   the reference has no copy button, because nothing in a picture can be
   tapped.
2. ~~**Draw the mark at 32px**, then the app icon~~ — both done, section 4.
3. ~~**Rename**~~ — done. 13 strings in `build.py`, one rebuild, 17 screens,
   and 37 text nodes in Figma. Not a single screen was re-sent: the four
   component masters were edited in place and 30 of the 37 followed on their
   own. Wiring held at 771 reactions with no dead destinations.
4. ~~**The wordmark**, last.~~ Done, section 4. It was the least-seen thing on
   the list and it turned up the one genuinely blocking fact in the exercise:
   the interface font cannot be the logo font.

---

## Open

- How Amana answers the Islamic-finance reading. The word is Hausa by way of
  Arabic and it means safekeeping, not a product structure. Half of Nigeria
  will hear the older meaning and half will hear nothing at all; the mark and
  the opening screen should make it a word about keeping, not a claim about
  compliance we are not making.
