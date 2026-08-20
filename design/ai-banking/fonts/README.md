# Fonts

One typeface, cut down to only the characters these screens use, so the whole
design can carry its own font.

- `PlusJakarta-subset.woff2` covers everything, at weights 400 to 800.
- `PlusJakartaItalic-subset.woff2` is only used for the quotes of what you said.

Plus Jakarta Sans is under the SIL Open Font License, which is in this folder.

## Why it is embedded rather than loaded from Google Fonts

Google serves the font in pieces, and none of the pieces contain the Naira
sign. Loading it the normal way would leave every Naira sign in a different
typeface from the digits beside it. The full font file does contain the sign,
so `build.py` writes a cut down copy straight into each screen.

Plus Jakarta Sans was picked partly for that reason. Of the geometric sans
faces that suit these screens, several have no Naira sign at all, including
Figtree and Manrope.

## Making it again

Cut down from the full variable font with fonttools, keeping weights 400 to
800 for the roman and pinning the italic at 400. The character set is basic
Latin, Latin-1, common punctuation and the Naira, pound and euro signs.
