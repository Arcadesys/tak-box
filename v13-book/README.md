# Tak v13 — the book (board folds inside, two slide-out trays)

**Prototype. Verified in CAD only; nothing has been sliced, printed or physically tested.**

The board folds in half like a book, with the playing face inside. There is a piece tray under each half. Open the book flat and each player slides a tray out of the front edge. The book is held shut by one clasp on an M3 screw.

![Closed](previews/01-closed.png)
![Open](previews/02-open-board.png)
![Trays out](previews/03-trays-out.png)

## Size

| | mm |
|---|---|
| Closed | 71 × 141 × 45 (68 × 138 body, plus the spine knuckles and clasp) |
| Open | 136 × 141 × 26 |
| Board | 5 × 5 at 24 mm pitch (120 mm field) for 19.5 mm flats |

Two things set the size:
- **Tray width:** three 19.5 mm stacks across each tray.
- **Leaf height:** the capstone lying down (17.3 mm).

## How it works

- **Leaves:** each half is a base (floor, fore wall, seam wall, back wall) plus a glued 2 mm face plate. The plate holds half the board. The grid lines are 0.8 mm wide, set 0.6 mm into the plate and raised 0.4 mm above it, in a second colour (print white plate, black grid).
- **Fold:** the hinge axis sits at the top of the raised grid, so when closed the two grids meet and the faces are 0.8 mm apart. The fold line runs down the middle of the centre column, so those five cells each have a 0.4 mm seam through them.
- **Hinge:** print-in-place knuckles sit at both ends of the spine (Ø3 cone pins, 0.4 mm clearance, same approach as v11). Each end has two small hinge barrels in the border, 3 mm proud of the board. The seam walls give an open stop at about 1–2° past flat.
- **Trays:** 62 × 132 × 18.6 mm each. They slide out of the front end (y = 0) with a finger notch in the front. Each tray **snaps in and locks**. A flexible arm in the tray's outer wall carries a square-faced button that sits in a window in the book's side. A ramp on the back of the button makes the tray snap in when pushed home. To release it, press the button in (1.45 mm of travel) through the 16 mm finger dish on the book's side and pull. The button face sits 1.6 mm below the side surface, so knocks in a bag shouldn't press it. The lock works either way up, which matters because leaf B's tray is upside down when closed. Each tray holds 21 flats as 11 two-high stacks, plus the capstone lying down, with 0.9 mm clearance under the board. The capstone sits next to the latch arm so the arm has room to flex.
- **Clasp:** an M3 × 8 button-head screw goes into a 2.6 mm pilot in leaf A's back wall. The clasp swings up and hooks a stud on leaf B, and swings down to rest flat along the back face.

## Print pieces ([stl/full](stl/full))

| File | Orientation | Qty |
|---|---|---|
| `bases-hinged-print-in-place.stl` | as exported: both bases open flat, hinge in place | 1 |
| `plate-a.stl`, `plate-b.stl` + `grid-inlay-a/b.stl` | face up (the grid is raised); plate white, grid black | 1 each |
| `tray.stl` | upright | 2 |
| `clasp.stl` | flat | 1 |
| M3 × 8 button-head screw | — | 1 |

Glue each plate onto its base after freeing the hinge. Keep glue away from the knuckle notches.

## Trial prints first ([stl/trials](stl/trials))

1. `trial-hinge-pair`: one spine end, print-in-place. Free it and check the swing.
2. `trial-latch-base` + `trial-latch-tray`: the front corner with the push-button latch. Check that it snaps in, holds against a firm pull, and releases with a fingertip.
3. `trial-clasp-base-a`, `trial-clasp-base-b`, `trial-clasp`: pilot hole, stud and hook.

Then complete [ACCEPTANCE.md](ACCEPTANCE.md).

## Digital checks ([reports](reports))

`source/verify_book.py` passes all of these:
- **Parts:** all are valid single solids.
- **Open flat:** no overlap between any parts.
- **Fold:** the sweep from 0 to 180° is clear, in 5° steps.
- **Open stop:** engages by 2° past flat.
- **Closed:** faces meet with the board inside.
- **Clasp:** locked clear, holding leaf B, and it swings clear from 0 to 90°.
- **Trays:** locked trays can't be pulled out. Pressed trays slide fully out. Arm bending strain is 0.75% at full press.
- **Pieces:** fit each tray.
- **Bed:** every part fits a 256 mm bed.

`source/verify_meshes.py` confirms all 13 STLs are closed and correctly oriented.

## Not done / open questions

- **Not built yet:** no slicing, no G-code, no print-time estimate, no physical tests.
- **Seam through the centre column:** five cells have the fold seam through them.
- **Hinge barrels:** 3 mm bumps at the spine ends, in the border.
- **Clasp:** stands about 3 mm proud of the back face.
- **Raised grid:** 0.4 mm proud. Stones slide over it; check that they don't catch during play.
- **Rebuild:** `python source/build_models.py`, `verify_book.py`, `verify_meshes.py`, `render_book.py`. The source is [tak_book.py](source/tak_book.py).
