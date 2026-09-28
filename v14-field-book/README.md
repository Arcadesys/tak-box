# Tak v14 — field book

**Prototype. Verified in CAD only; nothing has been sliced, printed or physically tested.**

A tough little brick for a bag. The board folds in half with its face inside, and there's a snap-in piece tray under each half. It uses no screws, magnets or other hardware. Closed, it's two dark slabs meeting at a seam.

![Closed](previews/01-closed.png)
![Open](previews/02-open-board.png)
![Trays out](previews/03-trays-out.png)
![Press to open](previews/05-press-to-open.png)

## Size

| | mm |
|---|---|
| Closed | 71 × 142 × 47 |
| Open | 136 × 142 × 24, plus the closure tab |
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
- **Renders:** plain matte charcoal and white.

## Carried over from v13

- **Board:** the grid is 0.6 mm inlaid plus 0.4 mm raised, in a second colour. Print a white plate with a black grid.
- **Fold:** the axis sits at the top of the grid, so when closed the two grids meet with the faces 0.8 mm apart.
- **Trays:** a push-button latch in each tray's outer wall. Push the tray in to snap it. To release, press the button 1.45 mm into a 16 mm finger dish in the book's side. The button sits 1.6 mm below the surface.
- **Pieces:** each tray holds 21 flats as 11 two-high stacks plus the capstone, with 0.9 mm under the board.
- **Hinge:** print-in-place knuckles at both ends of the spine.

## Print pieces ([stl/full](stl/full))

| File | Orientation | Qty |
|---|---|---|
| `bases-hinged-print-in-place.stl` | as exported: both bases open flat, hinge in place | 1 |
| `plate-a.stl` (with the buckle tab), `plate-b.stl` | face up | 1 each |
| `grid-inlay-a.stl`, `grid-inlay-b.stl` | with their plates, in black | 1 each |
| `tray.stl` | upright | 2 |

Free the hinge first, then glue each plate on. Keep glue out of the knuckle notches and the buckle slot.

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
- **Not built yet:** no slicing, G-code or print-time estimate.

Rebuild with `python source/build_models.py`, `verify_book.py`, `verify_meshes.py` and `render_book.py`. The source is [tak_book.py](source/tak_book.py).
