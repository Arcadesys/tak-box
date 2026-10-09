# V25 filament hinge — engineering receipt

On October 7, the user selected filament because their earlier filament hinge worked well, while printed pins broke or did not hold the assembly. They also selected the rounded underside board treatment they remember from V17. This is an explicit change from the initial V25 printed-pin proposal. That earlier coupon kit remains intact at `/Users/arcades/Documents/Codex/2026-10-07/task/v25`; no production V24 file is changed.

## Baseline and chosen interface

Retained V24 source revision: `8085e9d79ffff3c69f07a1cca67595994237869e`, [the four-colour V24 board review](https://github.com/Arcadesys/tak-box/pull/31). The exact CAD dependency files are in `reference/v24/source`; current hashes are in the manifest. V24 uses axis X98/Z17.5, playing face Z16.5, board underside Z11.8, 4 mm captive pivots, 4.8 mm sockets, 9 mm barrels and 8 mm full-height rooted supports. Its reported closed envelope is 102.5 × 200 × 35 mm. The current coupon independently checks V24 constants and actual board/tray CAD.

The earlier `v17-four-leaf/source/folio.py` uses circular clearance for opposite knuckle families; its retained README specifies steel axles. Later integrated filament-hinge sources use 1.75 mm filament bonded only to a fixed housing barrel. The user's V17 label is retained as their physical recollection, without claiming that the archived steel-axle study was their exact printed filament revision. This coupon combines circular clearance with the explicitly selected filament interface.

## Filament and curved underside samples

Three bore diameters — 1.95, 2.10 and 2.25 mm — compare nominal 0.20/0.35/0.50 mm clearance around ordinary 1.75 mm filament. Measure the actual filament; nominal fit is not physical fit. Each pair has a fixed left knuckle from Y4.9 to Y7.6 and a moving right knuckle from Y1.7 to Y4.5. Both retain the original 9 mm barrel and rooted support envelope.

The fixed bore ends at Y7.1, leaving a 0.5 mm blind wall. The filament reference is a 5.4 mm straight cut, from Y1.7 to Y7.1. The blind end blocks inward motion. Digital checks explicitly establish that the unbonded axle can withdraw outward: cured adhesive in the fixed 2.2 mm bore section is required. No printed pin, head, C collar, or claim of two mechanical axial stops remains. The filament appears only as reference hardware in assembled STEP views, never as a printable model or plate component.

Two shared board-edge samples reconstruct the actual V24 board profile at X76–97.8/Y3.1–26 before replacing the square hinge cut with a circular swept-support relief. Its radius is `sqrt(8² + 17.5²) + 0.45`, approximately 19.69 mm, along Y−1–9.6. The radius clears the full-height rotating support, not just the smaller barrel. The local playing field starts at Y10; the relief stays outside it. The samples retain the flat face and local grid, verified against V24 material. They are separate seated samples with no board latch: they demonstrate shape and clearance, not a drop-in board or secure complete case.

Checks include 0–180° hinge, board-edge and original-board sweeps at 5° steps, filament running fit, the blind wall, unbonded withdrawal, single-solid CAD, STEP/STL readback, watertight winding, bed placement and part separation. The original V24 loose joint had 0.8 mm nominal diametral clearance. This coupon reduces nominal clearance but does not establish stiffness, bond strength, layer durability or resistance to rocking before printing.

## Preserved lip trial and concealed-hinge limit

The three broad lip blades remain 28 mm wide, 12 mm free length and 0.8/1.0/1.2 mm thick. Their geometry is preserved from the earlier V25 coupon. The lip/catch seat and short transverse guides test withdrawal/sideways blocking and a 0.65 mm rigid release lift. Elastic flex, PLA fatigue and release force are physical acceptance items. Original V24 tray geometry is used in the local interference checks.

The lip proposal raises each board and the axis by 1 mm, for 37 mm total thickness. Full rails, catch positioning, hook dimensions, full loaded assembly and rear hinges remain future integration. The filament coupon and raised lip specimens are separate studies.

A single fixed axis below the inward-folding playing faces causes closed-board overlap. Rounded underside relief does not move or fully conceal the axis: the retained axis remains above the playing face. The build preserves the rejected lower-axis checks rather than claiming concealment. A concealed linkage needs a separate motion study.

## Reproduction and recorded checks

Use a compatible isolated Python environment with `requirements.txt`. The current verified runtime is `/Users/arcades/.codex/worktrees/tak-v18-print-final/tak-box/.slicer-work/cad-venv/bin/python` (Python 3.12.13, CadQuery 2.7.0). ElegooSlicer 2.4.2 supplies the retained Centauri Carbon 2 machine/process and ordinary PLA profiles. Commands run from the package's parent folder:

```text
python v25/source/build.py
python v25/source/slice.py
python v25/source/render.py
python v25/source/package.py
python v25/source/reproduce.py
```

Commands, dependency environment and source revision are recorded in the geometry/slice reports and repository checkpoint. Readback compares all 14 printed parts, world transforms, mesh surfaces/volumes, settings and embedded G-code. The surface tolerance is 0.002 mm; different triangulation/order does not require exact STL byte identity. `reproduce.py` validates manifest hashes, rebuilds in a fresh ZIP extraction, and compares regenerated surfaces against the delivered geometry.

Physical hinge feel, filament migration after bonding, rounded-board contact, lip fatigue, full-case stiffness and loaded purse retention remain unchecked. No printer job, merge or physical test is performed by these scripts. Source and exported solids stay in millimetres.
