# Fonts

Two typefaces, cut down to only the characters these screens use, so the
whole design can carry its own fonts.

- `LibreFranklin-subset.woff2` is used for money and interface text.
- `Newsreader-subset.woff2` and `NewsreaderItalic-subset.woff2` are used for
  anything the model wrote.

Both are under the SIL Open Font License, and the licences are in this folder.

## Why they are embedded rather than loaded from Google Fonts

Google serves these fonts in pieces, and none of the pieces contain the Naira
sign. Loading them the normal way would leave every Naira sign in a different
typeface from the digits beside it. The full font files do contain the sign, so
`build.py` writes a cut down copy straight into each screen.

## Making them again

The files were cut down from the full variable fonts with fonttools:

- Libre Franklin keeps weights 400 to 700.
- Newsreader is fixed at optical size 20 and keeps weights 400 to 500.
- Newsreader Italic is fixed at optical size 20 and weight 400.

The character set is basic Latin, Latin-1, common punctuation and the Naira,
pound and euro signs.
