# Cat neck correction v4, with unchanged Fox v3

The Cat's broad outlined neck/shoulder strip has been reshaped into continuous shoulder volume on both sides. This goes beyond the rejected v3 ridge smoothing. The facial jaw remains readable; a final bounded cleanup treats the small facets under the chin. The turned pose, eyes, muzzle, ears, torso curl, slender tail and planar base are retained. This is a local mesh correction, not a new generation.

Review `previews/cat-three-quarter-before-after.png` and `cat-front-before-after.png`, plus individual front/left/right/back/three-quarter renders. The original sculpture crop is `references/cat-hero.png`. All model images depict actual exported geometry with identical before/after cameras.

Fox is byte-identical to the delivered v3 Fox. Previous packages remain intact. No new Meshy credits, public release or printer job were used. Prior approved Meshy generation spend is 80 credits across v1/v2.

## Delivery

- `models/cat-capstone.stl`: revised upright Cat in millimeters.
- `models/fox-capstone.stl`: unchanged v3 Fox.
- `models/fox-cat-capstones.3mf`: two separately labeled millimeter objects.
- `models/cat-cc2-proof.3mf`: Cat slicer proof with CC2/0.4 mm PLA, 0.12 mm layers, four walls, 25% infill and tree supports. The Fox proof is copied unchanged.
- Storage-pose diagnostic STLs are generated locally by the fit verifier; they are not tracked print deliverables.

## Current evidence

| Cat check | Result |
| --- | --- |
| Dimensions X × Y × Z | 15.518934 × 17.809479 × 24.084475 mm |
| Exported surface | One watertight, consistently wound positive volume; 119,544 triangles |
| Planar base | 152.084158 mm² |
| COM inside base hull | 5.181051 mm margin |
| Current v16 tray, insert, latch, plate and base | No digital overlaps |
| Mirrored slots, closed box, sampled withdrawal and lift | Pass |
| Enclosing cylinder for all axial rolls | No overlaps; 0.800001 mm headroom |
| Local dry slicing | Pass: 200 layers, 39m 5s, estimated 2.71 g |
| Combined 3MF readback | Labels, units, dimensions and volumes match final STLs |
| Protected exported Cat regions | Within 0.000002 mm serialization tolerance |
| Fox | Byte-identical to v3; its existing verification/slicing evidence reused |

`reports/neck-revision.json` records the deformation and final under-jaw cleanup. `reports/protected-geometry.json` checks retained upper head/ears, far cheek, muzzle, base and tail against the retained original Cat. The subdivision preserves original surface planes exactly before deformation. Maximum local movement is 1.887106 mm; the final jaw-junction cleanup is bounded at 0.35 mm. Overall dimensions remain unchanged.

`reports/verification.json` contains refreshed Cat geometry, fit and motion results plus explicitly reused Fox results. V16 source hashes match. `reports/slicing.json` contains final Cat results and marked Fox reuse. Original v3 reports are retained for that provenance. `reports/package-readback.json` verifies the final combined 3MF.

Visual assessment is based on current actual renders compared with the supplied sculpture, including both sides and the underside transition. Creator acceptance remains pending. Physical fit, tactile identification, grasp, removal, support cleanup, retention and durability remain untested; digital checks do not establish those outcomes.

## Reproduction

Use Python with `source/requirements.txt`, from this repository. Run `python pieces/fox-cat-capstones-v4/source/rebuild.py` to recreate the complete final pair from retained Meshy OBJs. It writes ignored `.build-work/models`, compares both regenerated STLs to the delivery and records `reports/rebuild.json`. The recorded run reproduced both final STLs byte-for-byte with zero paid calls. No earlier untracked revision package is required.

The pipeline finishes the two Meshy v2 sources, applies Fox's v3 tail revision, reconstructs the historical Cat v3 intermediate and applies the final Cat v4 correction. `raw/cat-v3.stl` is retained only for before/after and protected-feature checks; it is not a printable final Cat. `reports/meshy-v2-*` and `v3-*` are labeled historical provenance. The original source sheets, exact image crops and generation task/settings records are retained. Rejected v1 generations and the Fox ribbon patch are excluded.

For rebuilt export readback, run `python pieces/fox-cat-capstones-v4/source/check_package.py --root pieces/fox-cat-capstones-v4/.build-work`. Generate its actual views with `python pieces/fox-cat-capstones-v4/source/render.py --root pieces/fox-cat-capstones-v4/.build-work`. Both are verified in this package's rebuild record and PR checkpoint.

For new geometry changes, run `source/verify.py --species cat`, `source/slice.py --species cat`, `source/check_protected.py` and `source/check_package.py` for affected checks. The verification/slicing CLI outputs contain only newly checked Cat evidence; the delivered reports additionally include explicitly marked Fox v3 evidence reuse. The full verifier defaults to both species when both change.

Use `source/render.py --species cat`, `source/render_revision.py` and `source/render_sheet.py` for delivery previews. Fit scripts import repository `v16-field-book/source/tak_book.py`; its exact checked source is retained in `references/v16-source`. Slicing uses repository `pieces/profiles` and installed ElegooSlicer on macOS. Preview rendering uses VTK and macOS Arial. `source/build.py` supplies source finishing and the 3MF helper; run `rebuild.py` for the complete final pipeline.

## Physical pair test, still pending

Print one upright Fox and Cat pair with the proof settings before a batch. Remove supports and inspect the ears, jaw and tail tip for damage. Check that each flat base rests without rocking and that the piece stays upright during normal board handling.

Test each capstone in both actual v16 trays with the insert installed. Close and release the latch, fold the case, then slide each tray fully out. Grasp the body/tail to remove the capstone and check for rubbing or catches. Confirm tactile distinction between the Cat's rounded tail and Fox's carved fur, and comfortable grasp/release.

Repeat insertion and removal ten times, inspect for scuffs or chips, then check retention during ordinary closed-case carrying. Record the exact print/profile and observed fit, release, retention and wear before calling the physical pair accepted.
