# Branding

Working document. Started 29 August 2026 from four answers: the name is open,
the position is peace and reliability, the design system stays as it is, and the
blue stays.

---

## 1. What is already settled

**The design system is the visual brand and it is right.** Greyscale carries the
interface, one blue is saved for the thing worth looking at, seven text styles,
one spacing scale, one icon rule. Nothing in this document changes it.

**The blue stays.** `#2A6AF5`. One honest note and then it is closed: this is
the iOS system blue, and PalmPay and Moniepoint are also blue. Two ways to keep
it and still own it — shift it a few degrees so it is Leorio's blue rather than
Apple's, or keep it exactly and let the mark and the voice do the work. Either
is fine. The blue is not the problem.

**The voice exists and is the best thing in the file.** It was written, not
designed. Section 5 writes down the rules it is already following.

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

### A constraint that has not been stated

The name is not just the company. It is **the assistant's name**. The chat
header says it. The tool panels say `Leorio Transfers`, `Leorio Requests`,
`Leorio Airtime`. The paid tier is `Leorio Plus`. The account is held at it.

So the name has to survive being spoken to: *Ask ___. ___ found three accounts.
___ moves them on the 28th.* That rules out a lot of good nouns. `Ask Canopy`
does not work. `Ask Amara` does.

A rename costs 13 strings in `build.py`, 17 built screens and the Figma text.
Cheap today, expensive after launch.

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

### Shortlist

**A. A person, rooted in Nigeria** — best fit for a name that is also the
assistant.

| Name | Meaning | Read |
|---|---|---|
| **Amara** | Igbo, *grace* | Warm, a real person, easy to say anywhere. "Ask Amara" is natural. Strongest in this group. |
| **Ayo** | Yoruba, *joy* | Short, warm, unmistakably Nigerian. Very easy to say. |
| **Ife** | Yoruba, *love*; also the ancestral city | Deeply rooted. Mispronounced outside Nigeria. |
| **Ada** | Igbo, *first daughter* | Short and Nigerian, but it is also a programming language. |

**B. Nature, comfort and permanence** — best fit for the position.

| Name | Meaning | Read |
|---|---|---|
| **Iroko** | The Nigerian hardwood. Sacred, long-lived, immovable | Says *reliable every time* better than anything else here. Nigerian, drawable, and it makes your four words true rather than decorative. Works spoken. |
| **Odan** | Yoruba, the big shade tree people gather under | Short, specific, drawable, and the image is comfort itself. |
| **Baobab** | Shelter, longevity, the tree of life | Pan-African rather than Nigerian. Long. |
| **Grove** | A stand of trees | Calm and safe, but it is not a person. |

**C. The flower and wing direction**

| Name | Meaning | Read |
|---|---|---|
| **Iris** | A flower, *and* the coloured ring of the eye, *and* the messenger of the gods | The tightest fit to the mark already drawn: a ring inside a shape. Also the assistant's job is to notice and to carry word. Widely used in biometrics, which is a check to run. |
| **Aster** | A flower whose name means *star* | Pretty, short, works spoken. |
| **Monarch** | The butterfly, and royalty | Already a US budgeting app. |

### What I would pick, and why

**Iroko**, if the position is the priority. A tree that is there every time you
come back is the position, said in one word. It is Nigerian without explaining
itself, it draws well at 32px, and it turns "not fast, just reliable" from a
line in a document into the name on the phone.

**Amara**, if the assistant is the priority. The product talks like a person who
knows you; a person's name makes that literal, and *grace* is the right register
for money that never shouts.

**Iris**, if you want to keep the mark you already have. The ring is drawn 181
times; this name makes that ring mean something.

Three checks before committing to any of them: the domain, the trademark
register, and whether a Nigerian speaker hears anything you did not intend.

---

## 4. The mark

Whatever the name, one thing should survive: **the mark is a ring inside a soft
shape.** It is drawn 181 times across 95 screens — more than the wordmark, the
app icon and the card will ever be seen combined. That is real equity and it
already reads as *an eye that is paying attention*, which is what the assistant
is.

Rules for drawing it:

- **Draw it at 32px first.** That is where it lives — in the ask bar, on every
  screen. Scale up to the app icon. A logo designed large and shrunk will die at
  32px, and 32px is the whole product.
- It must work in three places: 32px in the ask bar, 28px as a bubble avatar,
  64px on a share sheet, and as an app icon beside Kuda and Opay.
- One colour on white, and white on the blue. No gradients — nothing else in
  this design system has one.
- Keep the current icon on the home screen until the new one is drawn, so the
  screens stay whole.

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

1. **Put the mark on the shared receipt.** It is the one artefact that leaves
   the app — sent to WhatsApp after every payment — and it currently carries no
   mark at all. One component, and it is the only thing another person sees.
2. **Draw the mark at 32px**, then the app icon.
3. **Rename** — 13 strings, one rebuild, the Figma text.
4. **The wordmark**, last. It is the least-seen thing on this list.

---

## Open

- The name.
- Whether the blue shifts a few degrees or stays exactly as it is.
- Whether a display face for the naira figures is worth it — the amount is the
  hero of every receipt and is currently set in the same font as a form label.
