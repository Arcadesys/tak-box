# Tak v14 — field book

**Prototype. Verified in CAD and sliced; nothing has been printed or physically tested.**

A tough little brick for a bag. The board folds in half with its face inside, and there's a snap-in piece tray under each half. It uses no screws, magnets or other hardware. Closed, it's two dark slabs meeting at a seam.

![Closed](previews/01-closed.png)
![Open](previews/02-open-board.png)
![Trays out](previews/03-trays-out.png)
![Press to open](previews/05-press-to-open.png)

## Size

| | mm |
|---|---|
| Closed | 71 × 142 × 48 |
| Open | 136 × 142 × 25, plus the closure tab |
| Board | 5 × 5 at 24 mm pitch (120 mm field), for 19.5 mm flats |

## What changed from v13

- **Closure:** the M3 clasp is gone. The book closes with a **buckle at the far edge**, opposite the hinge.
  - **Closing:** a tab on leaf A's back corner pushes into a slot in leaf B and clicks under a catch.
  - **Opening:** the catch hangs on a spring panel cut into B's outer side wall, near the far corner. Squeeze that panel (about 4.5 N, 1.4 mm of travel) and lift.
  - **On the case:** the panel shows only as two fine slits on the side.
  - **Purse-proof:** pressing alone doesn't open it; the halves also have to be pulled apart.
  - **Print strength:** every flexing part bends within the print layers, not across them.
- **Tougher shell:**
  - The floor skin is 2 mm, up from 1.
  - Plan corners have a 6 mm radius, and every bottom edge has a 2 mm fillet.
  - The back wall is 10 mm deep, to house the buckle.
- **Cover:** a debossed **TAK** on the cover, 0.7 mm deep.
- **Renders:** plain matte black with the white grid and orange and purple accents.

## Carried over from v13

- **Board:** the grid is 0.6 mm inlaid plus 0.4 mm raised, in a second colour.
- **Fold:** the axis sits at the top of the grid, so when closed the two grids meet with the faces 0.8 mm apart.
- **Trays:** a push-button latch in each tray's outer wall. Push the tray in to snap it. To release, press the button 1.45 mm into a 16 mm finger dish in the book's side. The button sits 1.6 mm below the surface.
- **Pieces:** each tray holds 21 flats as 11 two-high stacks plus the capstone, with 0.9 mm under the board.
- **Hinge:** print-in-place knuckles at both ends of the spine.

## Colours and art

Orange and purple are used sparingly, about 1 g of each per print plus purge.

- **Board:** black, with a **raised white grid** (0.6 mm inlaid + 0.4 mm proud).
- **Cells:** kept subtle. A sparse field of white star dots and four small two-arm galaxies, two orange and two purple.
- **Tray floors:** a crescent moon in the player colour (orange for the cat tray A, purple for the witch tray B) and a scatter of white four-point sparkles.
- **Tray fronts and case:** plain black.

All art is flush 0.6 mm inlay with strokes of at least 0.8 mm, so stones slide over it. It stays clear of the grid, fold seam, hinge notches, buckle, lip, thumb groove and tray latch. `verify_book.py` checks this.

![Tray floors](previews/06-tray-art.png)

## Protective lip (for paint)

Each board half has a **1.0 mm raised lip** on its three outer edges, 1.6 mm wide and not across the fold. The hinge axis sits at the top of the lip, so when the book closes the lips meet and nothing else does:
- **Painted faces:** 2.0 mm apart.
- **Raised grids:** 1.2 mm apart.

Keep acrylic paint (and any varnish) below the lip top. The thumb groove is cut into the lip edge.

## Print plates ([plates](plates))

Four ready-to-open 3MFs for the Elegoo Centauri Carbon 2 with its **4-colour filament system**, with G-code in [gcode](gcode). Every project uses the same filament slots:

| Slot | Colour |
|---|---|
| 1 | black |
| 2 | white |
| 3 | orange |
| 4 | purple |

Settings: PLA, 0.4 mm nozzle, 0.2 mm layers, 4 walls, 20% infill, **no supports**, textured PEI, 210 °C / 60 °C. The prime tower sits in the back-right corner.

| Plate | Contents | Colours | Time | PLA | Colour changes |
|---|---|---|---|---|---|
| [00](plates/plate00-fit-trials-black.3mf) | Fit trials: hinge pair, buckle, tray latch | black | 53 min | 20 g | 0 |
| [01](plates/plate01-hinged-bases-black.3mf) | Both bases, open flat, hinge printed in place | black | 2 h 43 min | 89 g | 0 |
| [02](plates/plate02-trays-4colour.3mf) | Trays A and B with moon and sparkle floors | black, white, orange, purple | 1 h 44 min | 46 g | 9 |
| [03](plates/plate03-board-plates-4colour.3mf) | Board plates A and B, face up, with lip, grid, stars and galaxies | all four | 1 h 43 min | 54 g | 12 |

The full set (01–03) takes about 6 h 10 min and 189 g, including purge: 1.9 g orange and 1.9 g purple. Print **plate 00 first**. The times are slicer estimates.

**Assembly**
1. Free the print-in-place hinge on the bases.
2. Glue each board plate onto its base. Keep glue out of the knuckle notches and the buckle slot.
3. Slide the trays in until they click: orange tray under the orange half, purple under purple.

Multi-colour parts are exported as one STL per colour ([stl/full](stl/full), `<part>.<colour>.stl`), all in the same frame, and `package_plates.py` reassembles them.

## Trial prints first ([stl/trials](stl/trials))

1. `trial-hinge-pair`: a spine end, printed in place.
2. `trial-buckle-tab-plate` with `trial-buckle-socket-base` + `trial-buckle-socket-plate`: check that the tab clicks in, can't be pulled out, and releases when you squeeze the panel.
3. `trial-latch-base` + `trial-latch-tray`: the tray latch.

Then complete [ACCEPTANCE.md](ACCEPTANCE.md).

## Digital checks ([reports](reports))

`source/verify_book.py` passes all of these:
- **Fold sweep:** 0–180° is clear. Only the catch touches the tab, in the last 1° of closing.
- **Buckle:** it holds with 0.8 mm engagement when the halves are pulled apart. Squeezing the side panel frees the tab through a 12 mm lift.
- **Strain:** panel strain is 0.6%, and tray-arm strain is 0.75%.
- **Trays:** a locked tray can't be pulled out, and a released tray slides fully out.
- **Pieces:** they fit each tray and clear the pressed arm.
- **Bed:** every part fits a 256 mm bed.

`source/verify_meshes.py` confirms all 12 STLs are closed and correctly oriented.

## Known limits

- **Hinge barrels:** they still sit about 3 mm proud at the spine ends. Hiding them inside the outline would need a ridge across the middle of the board.
- **Buckle tab:** when open, the tab (2.4 × 4.4 × 10.8 mm) stands up at leaf A's far back corner.
- **Centre column:** the fold seam runs through its cells.
- **Squeeze force:** about 4.5 N, from beam theory. It's a guess until the trial is printed.

Rebuild with `python source/build_models.py`, `verify_book.py`, `verify_meshes.py`, `render_book.py`, then `package_plates.py` (needs ElegooSlicer). The source is [tak_book.py](source/tak_book.py).
