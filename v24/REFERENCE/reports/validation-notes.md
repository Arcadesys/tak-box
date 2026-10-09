# V23 R2 build evidence

This is a fresh geometry/slicing revision, not the earlier V23 identity-only migration. The retained baseline is V23 geometry from 071469c; its ZIP SHA-256 is 33510a63581b1a8b5f3c5afde34ed99acf6ecd5ccfb6bc49956e6d6e2b9e1221. The original V23 package remains unchanged. The concurrent board-inlay additions through 82aff2d are preserved in the branch; no artwork adaptation is included here.

The user reported a broken thin bar carrying the main hinge and requested stronger hinges and two removable loaded player trays for purse use. Exact fracture location, joint fusion and breaking action are unknown. Broadening the support is a design response, not an independently confirmed fracture diagnosis or a strength simulation. The selected 35 mm thickness retains the 2.2 mm case floor and 4.7 mm board body while adding a separate 1.2 mm tray floor. Larger barrels increase closed width by 1.5 mm; total envelope is 102.5 × 200 × 35 mm. No playing-field shrink occurs.

Environment: `.slicer-work/cad-venv/bin/python` in the implementation checkout; Python 3.12.13, CadQuery 2.7.0, OCP 7.8.1.1.post1. Requirements are pinned in `requirements.txt`. ElegooSlicer 2.4.2 and the included CC2 0.4 mm/PLA profiles perform offline slicing. No new dependency, printer job, merge or paid generation was used. Generic PLA softening/bed metadata warnings remain, and headless OpenGL thumbnail generation is unavailable. Separate actual-CAD previews and deposition-layer sheets are supplied.

Run with that CAD Python (or an environment matching the pinned requirements):

```text
python v23-r2/source/build_case.py
python v23-r2/source/verify_field.py
python v23-r2/source/verify_supports.py
python v23-r2/source/verify_hardware.py
python v23-r2/source/verify_trays.py
python v23-r2/source/package_case.py
python v23-r2/source/slice_case.py
python v23-r2/source/inspect_case_layers.py
python v23-r2/source/verify_pin_toolpaths.py
python v23-r2/source/build_fitcheck.py
python v23-r2/source/build_tray_trial.py
python v23-r2/source/verify_pip_hinges.py
python v23-r2/source/render_revision.py
```

Review regenerated previews/layer sheets and record that review, then run `source/record_provenance.py` and `source/package_release.py`. Source scripts resolve paths within this package and include their required vendor CAD code. `reports/provenance.json` pins source revision, dependencies, source/profile/output hashes and check totals. Per-slice reports retain commands, geometry/project/Gcode hashes, warnings and estimates. `PACKAGE-MANIFEST.json` covers every shipped payload; release audit extracts the archive and verifies hashes, JSON/Python syntax, local links and project count.

Evidence includes valid single solids and STEP/STL readback for all ten parts; disjoint assembled parts; sampled 0–180° folding, initial opening, 90° hook release, stops and complete board travel; the full exported 5×5 field; actual original Cat/Witch pieces in both trays; loaded removal/repacking at 1 mm increments; planar seat and pocket containment at nominal cover slack; broad floor and fingertip probes; continuous full-height support material probes; exact named meshes and placement in all four sliced projects and both trials. Nominal captive radial/face gap remains 0.4 mm. Sliced bead-edge gaps are sampled with a conservative 0.50 mm bead model, separately from CAD distance. These do not establish printed joint release or strength.

Resolved findings during this work:

- The first raised hook touched a rounded recess corner by 0.02284 mm³ at 90°. Expanding that recess locally by 0.8 mm in Y resolved the sampled release collision without changing the exterior envelope.
- A coarse tray lift study missed rear-rail contact. Checking every 1 mm identified it. The tray rear edge shortened 0.7 mm and the capstone bay moved forward 0.5 mm; all loaded removal/repacking samples now clear, with 0.5 mm minimum nominal plan gap at the rear rail. Low stops locate the shortened tray.
- OCCT's conservative cached bounding box put a coupon mesh about 0.000635 mm above Z0, so the slicer dropped it and exact-placement readback correctly failed. Placement now seats the actual tessellated minimum on Z0; named mesh/placement checks pass without widening the readback tolerance.

The whole-case estimate is 48,922 s / 321.56 g. The hinge trial is 2,448 s / 9.41 g and the tray trial 3,404 s / 21.52 g. Physical acceptance is false throughout. Motion checks sample rigid poses and assumed catch flex; they are not continuous sweeps, FEA, fatigue/drop tests or measured actuation. Upright open trays do not retain pieces under inversion. Full loaded transport, snag resistance, release, grasp, rattle and floor/hinge durability remain listed in ACCEPTANCE.md.
