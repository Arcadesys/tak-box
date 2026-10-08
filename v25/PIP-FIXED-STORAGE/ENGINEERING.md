# Engineering and reproduction

Units: mm. Source parent: `671606d96ef515fa9543db7ec0616fe2c357fd86`; retained V24 reference: `8085e9d79ffff3c69f07a1cca67595994237869e`. The PIP pin/socket and 8 mm full-height roots come from `../reference/v24/source/case.py`. Fixed floor stock is relieved before union so it cannot refill the opposing swept clearance or erase the captive pivots. Both bodies print as one assembly with build-plate-only supports, 0.8 mm support XY separation and zero brim.

Use Python 3.12 with the dependencies in `../requirements.txt`. Run these from the extracted kit or repository:

```sh
python v25/PIP-FIXED-STORAGE/source/build.py
python v25/PIP-FIXED-STORAGE/source/trial.py
python v25/PIP-FIXED-STORAGE/source/render.py
python v25/PIP-FIXED-STORAGE/source/slice.py
python v25/PIP-FIXED-STORAGE/source/slice.py --trial
python v25/PIP-FIXED-STORAGE/source/package.py
python v25/PIP-FIXED-STORAGE/source/reproduce.py
```

Slicing requires ElegooSlicer 2.4.2 at the recorded macOS application path. The source records commands, runtime, source/board hashes and output checks. Reproduction rebuilds exported body and trial meshes from fresh ZIP extraction, independently of the checkout. The archive preserves named bodies and exact V24 board reference inputs. The optional hinge trial is two additional printed parts, not part of a complete case.

Geometry checks cover single connected bodies, fixed floor/open wells, 44 original pieces, released-cover slides, sampled folding, opposed axial capture, pivot surface clearance, full-height roots, STEP/STL/3MF readback, bed bounds and assembly grouping. Sliced projects are checked against their source meshes and retain one build item with two components. Actual extrusion checks exclude support centerlines in bearing cavities and sample running gaps with a conservative 0.50 mm bead-width estimate. These probes do not prove continuous extrusion clearance, release force, fatigue or loaded transport.

B's 2.10 mm filament bore is not used by PIP. Previous filament and reinforced-B packages remain preserved history. Physical acceptance is false in every report. Retained V24 covers and hook require physical compatibility checks; the cover-catch/lip/rounded-cover work remains open. Original flat pieces only; no weighted-piece acceptance. Material/profile changes require reslicing.
