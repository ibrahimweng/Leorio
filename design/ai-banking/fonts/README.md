# Fonts

One typeface in the interface. SF Pro Text sets everything. Fraunces is here for
the wordmark alone, and even there it ships as outlined paths rather than as a
font. Both are cut down to the characters they draw.

- `SFProText-Regular-subset.woff2` is weight 400.
- `SFProText-Semibold-subset.woff2` is weight 600, which is what carries the
  emphasis: SF sets heavier at a given weight than Plus Jakarta Sans did, and
  Semibold is the weight iOS itself emphasises with.
- `SFProText-Bold-subset.woff2` is weight 700, used at one size only, the
  balance at 32.

There is no italic. The one place that used to lean, the quote of what you
said, stands upright now.

## Why it is embedded rather than loaded

The screens are single files that have to render the same anywhere, including
in the headless browser the Figma pipeline measures them in. A font that has to
be fetched would leave the measurements at the mercy of whether the fetch
landed, so `build.py` writes a cut down copy straight into each screen.

The Naira sign is the other reason. Google serves Plus Jakarta Sans in pieces
and none of them contain it, which would have left every Naira sign in a
different typeface from the digits beside it. SF Pro Text has the sign, and the
subset here keeps it.

## Making it again

Cut down from the five OTFs Apple ships, with fonttools, to the same 216
codepoints the Plus Jakarta Sans subset carried: basic Latin, Latin-1, common
punctuation, and the Naira, pound and euro signs. Nothing that renders today is
missing from the cut. Light and Medium were cut too and are not used; they are
not in the repository.

Note that `trak`, Apple's optical tracking table, does not survive subsetting
and browsers would not read it anyway. Its values were read out of the full
fonts first and live in `tokens.py` as the tracking for each size.

## The money subsets, and the naira

**These files are gone.** `Fraunces-{Regular,SemiBold,Bold}-Money-subset.woff2`
held eighteen characters each — the ten digits, comma, period, plus, hyphen,
minus, space, the naira and the dollar, and not one letter, so a slot the rule
reached by mistake had nowhere to put its letters but back into SF Pro. Money is
set in SF Pro now and the subsets came out with the face.

Two findings from building them are worth keeping, because they will decide the
next typeface too.

**Getting the naira out of Google was the whole problem.** The digits live in
the `latin` subset and the naira lives in `latin-ext`, and no single served file
has both — the same wall this project hit with Plus Jakarta Sans, recorded
below. The fix is to take both subsets, merge them with fontTools, and cut the
result down. That is what made those files 2.5KB each instead of two files and a
`unicode-range` apiece.

**Manrope, Instrument Serif, Sora, Outfit and Figtree have no naira at all.**
Fraunces, Newsreader, Archivo, Space Grotesk, Inter, IBM Plex Mono and Bricolage
Grotesque do. Check before falling in love. For a Nigerian product this is the
first question to ask of a face, not the last — it eliminated five candidates
here before any of them was judged on how it looked.

## Fraunces, and why the wordmark is not SF Pro

`Fraunces-SemiBold-Amana-subset.woff2` holds five glyphs: A, m, a, n and the
notdef. It exists to draw the wordmark once and outline it, not to set type.

**The wordmark could not be SF Pro.** Apple licenses it for designing and
developing interfaces for Apple platforms, which is exactly what the screens
are and exactly what a logotype is not: a wordmark goes on a card, an App Store
listing, a pitch deck, a sign. So it is set in Fraunces, which is under the SIL
Open Font License 1.1 — free to use, modify, embed and redistribute, including
in a logo, with the notice kept.

  Fraunces © The Fraunces Project Authors, https://github.com/undercasetype/Fraunces
  SIL Open Font License 1.1, https://openfontlicense.org

**And the shipped wordmark is not a font at all.** `brand.py` outlines it to a
single path, so `brand/wordmark.svg` and the lockups are shapes. Nothing has to
have Fraunces installed for the logo to be right, which is the only way a
logotype should ever travel. The subset stays here so the outline can be made
again.

## Licence

SF Pro is Apple's, under the Apple licence that comes with it, which allows use
for designing and developing interfaces for Apple platforms. That is what this
is. It does not grant redistribution, and a subset embedded in a committed HTML
file is a copy of the font travelling with the repository, so treat these
screens as internal design artefacts rather than something to publish.
