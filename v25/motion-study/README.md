# Continuous-filament motion study

**A straight full-length axle is not a drop-in change to the current V25 hinge.** The current print kit stays unchanged.

The user asked about running filament all the way through the board to improve stability. This assessment checks the geometry before adopting that idea. It does not establish a physical stability benefit.

## What the current single axis permits

On the current X98/Z17.5 hinge axis, ordinary 1.75 mm filament reaches **1.875 mm above the Z16.5 playing face**. A straight continuous axle would occupy the centre seam through the playing field.

Lowering the axle to Z15.625 makes the filament flush with the face, but the inward-folded boards overlap by 1.75 mm in depth. Lowering it another millimetre for cover makes the overlap 3.75 mm. Actual V24 board-solid intersections confirm both failures. The face-gap relation is `2 × (axis height − face height)`. Changing barrel length does not change this conflict.

[Single-axis section diagram](01-single-axis-conflict.png)

## An alternative needs a new case hinge

An exploratory two-axis spine places two parallel full-length filament axes at X93.25/X102.75, Z13, separated by 9.5 mm. A path that tilts the right board outward, lifts on the spine, then folds inward avoids collision between conservative full-board envelopes, including their raised outside lips. Sampling at 0.25° steps keeps a 0.10 mm separating-axis margin. Closed playing-face gap is 2.5 mm, and the board edges align.

**This is only a board-envelope path.** The spine, knuckles, cover pockets and end retention have not been designed as solids. It needs two continuous filament lengths and a separate connecting spine. It is not the single axle initially proposed, and it is not a chosen V25 architecture.

The unchanged V24 case bodies collide after just 2° of the initial outward tilt; intersection volume is about 2.04 mm³, rising to 294.48 mm³ at 4°. Housing inner-edge clearance and full loaded motion would require new geometry. The board-only result cannot establish a viable complete case, fit within the previously proposed total thickness increase, or compatibility with the raised lip trial.

[Board-only path diagram](02-board-only-path.png)

## Evidence and next step

[REPORT.json](REPORT.json) records **1,330 assessment checks**, source/runtime/command, single-axis conflicts and actual case-body intersections. These checks validate the assessment, including expected rejection; they do not qualify a new hinge. Figures were inspected for legible high-contrast labels. No new printable geometry, slice or physical result is claimed. The existing V25 coupon plate and ZIP remain byte-identical.

Reproduce with the package's compatible CAD environment:

```text
python v25/motion-study/study.py
```

A further continuous-spine design would require a deliberate case/hinge architecture decision, full joint solids, loaded tray/board/hook motion checks and another small physical trial. Until then, the current V25 filament end-hinge coupons remain the available test kit.
