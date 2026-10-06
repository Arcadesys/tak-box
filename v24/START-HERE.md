# V24 — reinforced hinges and removable player trays

**V24 is the user-selected name for the completed reinforced-hinge/removable-tray revision previously delivered as V23 R2.** Geometry, printing, assembly instructions and physical acceptance are unchanged. The earlier V23 R2 kit remains recoverable in the repository. Embedded printer presets retain their historical V23 R2 names so profiles and sliced projects remain byte-identical.

This is the mechanical revision following the user's report that the thin bar carrying the V23 main hinge broke. The exact fracture location, whether a joint was fused and the action causing failure are unknown. Print the small trials first to evaluate this new support and tray design. Digital checks do not establish impact strength or physical fit.

## What changes

- Full-height **8 mm radial hinge supports**, **4 mm captive pivots** and **9 mm barrels** replace the old roughly 2.3 mm upper supports, 3 mm pivots and 6 mm barrels. Barrel rims have 0.4 mm rounding; nominal socket wall is 2.1 mm before rounding and blind outer cap is 1.3 mm. The bases still print together with captive main joints.
- Two separate **76.2 × 182.1 × 9.2 mm** player trays each hold 21 original 20 × 20 × 8 mm flats and one supplied 8 mm flat capstone. An 8 mm-wide, 20 mm-long pinch handle has room for the checked 14 mm fingertip probes on both sides. A broad 1.2 mm floor rests directly on the retained 2.2 mm case floor.
- Low seat stops provide 0.4 mm nominal planar clearance. Covers limit upward movement, with 0.4 mm nominal clearance over pieces and handles. Pocket rims contain the pieces during upright tray handling; open trays are not inversion-retaining.
- Closed envelope including hinge barrels: **102.5 × 200 × 35.0 mm**. Compared with V23, that is 1.5 mm wider at the stronger barrels and 2.4 mm thicker. The 180 × 180 mm, 5 × 5 playing field and 36 mm pitch remain. The boards keep their 4.7 mm body thickness; their corner reliefs widen to clear the stronger supports. The side hook is longer for the raised covers, and its recess clears the parked hook.

The 35 mm choice retains case and board thickness while making room for the independent tray floors. Keeping 32.6 mm would require removing 1.2 mm elsewhere per half, such as thinning the boards to 3.5 mm or case floors to 1.0 mm. Those alternatives were not qualified. Neither the proposed 1.2 mm tray floor nor hinge strength has physical acceptance yet.

Full-build slicer estimate: **13 h 35 min / 321.56 g**, excluding the original 42 flats. The hinge trial is **40 min 48 s / 9.41 g**; the tray trial is **56 min 44 s / 21.52 g**.

## Small trials

1. Open [the hinge/support trial](FIT-CHECK/captive-hinge-fit-check-CC2-PLA.3mf). Its front and rear sections come from the new exported bases, joined by fixture strips. Carefully remove external support, free both joints and cycle them through the whole range. Record whitening, cracks, binding or a fused joint before applying force. This checks local support/joint behaviour, not full-base warping or purse durability.
2. Open [the tray fit/access trial](TRAY-FIT/removable-tray-access-trial-CC2-PLA.3mf). It contains the actual rear section of the tray and its case seat, including three flat pockets, capstone bay and pinch handle. Load three original flats and a supplied flat capstone; check seating, pinch access and upright lifting. The open-ended fixture does not qualify full-case containment or full-tray bending.

[Acceptance sheet](ACCEPTANCE.md) records the remaining physical work.

## Complete build

The four projects in PRINT are for the Centauri Carbon 2, 0.4 mm nozzle, PLA, 0.20 mm layers, four walls and 20% gyroid:

1. Paired bases: print together open flat, preserving their assembly grouping and object-specific support/brim settings.
2. Both sliding boards: flat undersides down, playing faces up.
3. Both removable player trays: broad flat undersides down.
4. Flat capstones, longer side hook and collar.

The only added hardware is the hook's **8.6 mm length of straight 1.75 mm PLA filament**. Main hinges take no inserted pin or glue. Secure the hook pin at its stationary mount and collar, keeping adhesive out of moving parts; set light friction at the collar. No positive hook detent is claimed.

For play: park the side hook, unfold the case flat, press each front release button rearward 2.8 mm, then slide each board outward 106 mm and lift it away. Pinch the rear handle and lift each loaded tray vertically. Set trays upright beside the board and reinstall the boards for play. Repack with the case flat, seat each loaded tray within its stops, install both covers until caught, fold and close the hook. Do not tip an uncovered loaded tray.

## Compatibility

Replace **both bases, both boards and the hook** together; add both trays. Do not mix old and revised halves. The larger supports interfere with the predecessor's board corner geometry. New loaded trays do not fit beneath old covers: the pieces would overlap the old roof by 0.8 mm. Original flats, the supplied V23 flat capstones, the hook collar and the 8.6 mm hook filament reference retain their geometry. Older sculpted/curled capstones and weighted flats remain unqualified.

The original V23 source and ZIP, all earlier kits and user-extracted folders remain intact. This package contains no board artwork changes. The concurrently completed V23 board-inlay package is preserved, but its old corner geometry is not a V24 replacement; adapting its surface to these revised covers is a separate task. See [build provenance](BUILD-PROVENANCE.md) for commands, dependencies, source hashes, checks and limitations.
