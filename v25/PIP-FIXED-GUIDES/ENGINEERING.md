# Engineering and reproduction

Units: mm. Source parent `9eeef7bcd351c5c23f4851a763b39f779db867ea`; retained V24 reference `8085e9d79ffff3c69f07a1cca67595994237869e`. Current user clarification: remove the removable tray, retain **fixed guides**. This supersedes the earlier interpretation that removed all guides. Version remains V25; a V26 name was suggested but not selected.

The exact earlier tray guide shapes are `pocket_rims()` translated `(1,0,1.2)` and `capstone_rim()` translated `(1,-0.5,1.2)`, mirrored for the right. Each guide is fused individually into the floor with 0.01 mm overlap; exporting an overlapping compound as the fuse tool initially left multiple disconnected solids and was rejected by connectivity checks. The successful build must have exactly one solid per complete body. No tray floor or handles are added. Original nominal flat pockets have 0.35 mm clearance on each side. Guide top Z6.9 mm, floor Z3.4 mm, stone top Z11.4 mm. Grasp openings and rear fingertip access are retained. Physical fit is unverified.

Prior empty-well STEP bodies are included as hashed reference inputs under `reference/plain-bodies`; set-difference checks verify that all added body material is confined to the fixed guides, including unchanged PIP roots/pivots, outside dimensions and cover interfaces. Piece checks use the exact original flat-piece package: 42 Cat/Witch 20×20×8 mm flats and two supplied 8 mm V23 flat capstones. Straight removal is sampled at 1, 4, 8 and 12 mm; lateral restraint at four 3 mm shifts with 0.4 mm upward slack. These are rigid nominal checks, not loose packing or dump/transport simulations.

Use Python 3.12 and `../requirements.txt`. Run from the extracted kit or repository:

```sh
python v25/PIP-FIXED-GUIDES/source/build.py
python v25/PIP-FIXED-GUIDES/source/trial.py
python v25/PIP-FIXED-GUIDES/source/render.py
python v25/PIP-FIXED-GUIDES/source/slice.py
python v25/PIP-FIXED-GUIDES/source/slice.py --trial
python v25/PIP-FIXED-GUIDES/source/package.py
python v25/PIP-FIXED-GUIDES/source/reproduce.py
```

ElegooSlicer 2.4.2 is required at the recorded macOS application path. Reports record commands, dependency runtime and source/input/profile hashes. Geometry checks cover connected solids, guide material and seating/removal/restraint, fingertip access, cover sliding and sampled loaded folding, opposed axial capture, PIP clearance, roots, STEP/STL/3MF readback and bed bounds. Sliced readback verifies source meshes, profile settings and paired assembly grouping. The actual extrusion check samples radial gaps using conservative 0.50 mm beads and checks support centerline exclusion in each bearing cavity; continuous clearance and release force are unproven. Both projects retain build-plate-only supports, 0.8 mm support XY separation and no brim.

Fresh archive extraction rebuilds complete bodies and the hinge strip and compares all four meshes within 0.002 mm surface/size tolerance and 0.05 mm³ volume difference. Earlier kits and user-extracted folders remain untouched. Physical fit, grasping, dumping, hinge release/strength/fatigue, covered loaded retention and transport remain open. Material/profile changes require reslicing. No printer job is initiated.
