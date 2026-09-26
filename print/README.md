# What to print

Printer setup for every file: **Elegoo Centauri Carbon 2, 0.4 mm nozzle, PETG, textured PEI plate.** Each `.3mf` is one complete plate with its print settings built in. In ElegooSlicer, use **File → Open Project**, and if it asks, load the project (not geometry only). Check the printer, filament and plate in the top bar, slice, look at the preview, then print.

## Current board: v7 — `v7-board/`

Print all four, in order. The file name says which plate it is, its colour and what's on it.

| # | File | Filament | Time | Weight |
|---|---|---|---|---|
| 1 | `tak-v7-board-1of4-white-center-row-plugs.3mf` | white | 1 h 36 m | 37 g |
| 2 | `tak-v7-board-2of4-white-wing-a-lid-a.3mf` | white | 8 h 28 m | 209 g |
| 3 | `tak-v7-board-3of4-white-wing-b-lid-b.3mf` | white | 8 h 28 m | 209 g |
| 4 | `tak-v7-board-4of4-black-grid.3mf` | black | 38 m | 14 g |

Plate 1 is quick: print it first and check the two quarter-circle feet at each end before committing to the wings. On plates 2 and 3, tree supports should appear only along the hinge edge, and none in the small round pockets on the wing undersides.

## Pieces — `pieces/`

| # | File | Filament | Time |
|---|---|---|---|
| 1 | `tak-pieces-1of2-cat-orange.3mf` | orange | about 3 h |
| 2 | `tak-pieces-2of2-witch-purple.3mf` | purple | about 3 h |

Each plate is 21 flat stones plus one capstone, solid infill, no supports.

## Hardware

- 1.75 mm filament for the four hinge pins, any kind (it's never printed): four lengths of about 195 mm.
- 16 magnets, Ø4 × 2 mm: 4 pairs hold the folded case shut, 2 pairs hold each lid down.
- 8 stick-on dome bumpers, Ø8 × 2.2 mm (3M Bumpon SJ5302 or similar).

## Assembly

1. Pull the tree supports off the wing hinge edges.
2. On each wing's underside, cut the thin skin out of the four Ø8.6 mm pockets with a craft knife. The four wider, shallower Ø9.6 mm pockets can stay sealed.
3. Push a 195 mm filament pin through each of the four hinges (two main folds, two lids) from the board edge, through all ten knuckles, then press a plug on each end (8 plugs used, 2 spare).
4. Fold both wings under: each center-row foot should drop flush into its corner notch. Sand the foot's curved edge if it rubs.
5. Check magnet polarity, then glue the pairs in so each pair attracts across the fold or lid.
6. Stick a bumper in each of the Ø8.6 mm pockets.
7. Attach the black grid pieces to the play face once the hinges move freely.
8. Load 21 stones and a capstone per side, close the lids, fold, and test-carry over something soft.

v7 has not been physically printed yet.

## Not for the current board — `archive/`

Earlier iterations and test coupons, kept so their history stays reproducible. See `archive/README.md`. Don't mix their parts with v7.

`package-validation.json` records the automated check (manifold, fits the 256 mm bed) for every file here; `validate_3mf.py` regenerates it.
