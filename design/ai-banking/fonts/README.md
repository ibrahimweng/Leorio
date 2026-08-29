# Fonts

One typeface, cut down to only the characters these screens use, so the whole
design can carry its own font.

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

## Licence

SF Pro is Apple's, under the Apple licence that comes with it, which allows use
for designing and developing interfaces for Apple platforms. That is what this
is. It does not grant redistribution, and a subset embedded in a committed HTML
file is a copy of the font travelling with the repository, so treat these
screens as internal design artefacts rather than something to publish.
