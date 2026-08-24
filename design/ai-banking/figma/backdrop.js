// Puts the real home screen behind the seven screens that are drawn over it.
//
// Seven of the screens in the flows are not pages of their own. They are the
// home screen with something on top: a voice sheet, a keyboard, a chooser. The
// converter builds that backdrop from the same markup as every other screen,
// so it arrives as the home feed this repo draws. The home screen in the file
// is the one the founder drew, and it is not that feed, so the first step of a
// flow and the second step of the same flow disagree about what the app looks
// like.
//
// Nothing here can be fixed in the markup without redrawing their screen, so
// it is fixed in the file: strip the backdrop the converter built, and clone
// theirs in behind the overlay instead.
//
// Paste this whole file into the Figma MCP use_figma tool, with the file key
// in ../README.md, after re-sending any of the seven. It is safe to run twice.

// The home screen the founder drew, on the test page.
const SOURCE = '70:5533';
// The screens that are something drawn over the home screen.
const OVER = ['Ask', 'AskReq', 'AskSvc', 'Receive', 'Typed', 'TypedAsk', 'TypedBuy',
              'Draft', 'Actions'];
// What the converter leaves at the top level of one of those screens for the
// backdrop: the feed, the group holding the feed and the ask bar, the ask bar
// on its own, and the clone a previous run of this script put there. Anything
// else at the top level is the overlay, and it stays.
const BACKDROP = ['Page', 'Group', 'Dock', 'Home behind'];
// Their page is a shade off white. The bar that fades the page out from under
// the typed line was built to fade into ours, which is pure white, and against
// theirs that reads as a band rather than as a fade.
const PAGE_HEX = 250 / 255;

const page = figma.root.children.find(p => p.name === 'Flows');
if (!page) throw new Error('no Flows page');
await figma.setCurrentPageAsync(page);

const home = await figma.getNodeByIdAsync(SOURCE);
if (!home) throw new Error('no home screen ' + SOURCE);

const done = [], missing = [];
for (const name of OVER) {
  const frames = page.query('FRAME[name=' + name + ']').toArray().filter(f => f.parent.type === 'SECTION');
  if (!frames.length) { missing.push(name); continue; }
  for (const fr of frames) {
    const old = fr.children.filter(k => BACKDROP.indexOf(k.name) >= 0);
    const clone = home.clone();
    clone.name = 'Home behind';
    fr.insertChild(0, clone);
    clone.x = 0;
    clone.y = 0;
    for (const o of old) o.remove();

    // Only the frame's own fill and the fades sitting on top of the clone can
    // still be carrying our white. The clone itself is theirs and is left alone.
    fr.fills = [{ type: 'SOLID', color: { r: PAGE_HEX, g: PAGE_HEX, b: PAGE_HEX } }];
    for (const k of fr.children) {
      if (k === clone || !Array.isArray(k.fills)) continue;
      const fills = JSON.parse(JSON.stringify(k.fills));
      let hit = false;
      for (const f of fills) {
        if (f.type !== 'GRADIENT_LINEAR') continue;
        if (!f.gradientStops.every(s => s.color.r === 1 && s.color.g === 1 && s.color.b === 1)) continue;
        f.gradientStops = f.gradientStops.map(s => ({ ...s, color: { ...s.color, r: PAGE_HEX, g: PAGE_HEX, b: PAGE_HEX } }));
        hit = true;
      }
      if (hit) k.fills = fills;
    }

    done.push({ screen: name, frame: fr.id, section: fr.parent.name, stripped: old.length, clone: clone.id });
  }
}

return { mutatedNodeIds: done.map(d => d.frame), done, missing };
