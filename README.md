# Leorio

This repository holds two separate projects.

## leorio

A Flutter app for ordering food. It has screens for browsing vendors, viewing a
menu, managing a cart and checking out.

The Flutter project lives at the top level of the repository. The source is in
`lib/`.

```bash
flutter pub get
flutter run
```

## beat-studio

A music workstation that runs in a web browser. It has a drum kit, a piano and a
guitar, a step sequencer, recording, and export to WAV, MP3 and MIDI. All the
sound is made in the browser.

The project is in `beat-studio/` and is written in TypeScript. See
`beat-studio/README.md` for the full description.

```bash
cd beat-studio
npm install
npm run dev
```

The two projects do not share any code and neither depends on the other.
