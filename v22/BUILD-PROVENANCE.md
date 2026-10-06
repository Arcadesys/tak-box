# V22 seamless exterior — first-print evidence

This revision replaces the corner hook and projecting hinge roots with a centered recessed hook assembly, offset recessed board grips and rounded hinge-end shoulders within the case length. The complete closed outline, including hook, catch and pivot/collar, is **101 × 200 × 32.6 mm**. The earlier V22 kit measured 111.8 × 220.2 × 32.6 mm. Thickness and the full 180 mm, 5×5 / 36 mm-pitch field are preserved. Units: mm.

The original V22 ZIP at source `02f8a0930e1af4da0ae74466eea1ca79128045b1` remains unchanged as `tak-v22-print-kit.zip`; the revised artifact is `tak-v22-seamless-print-kit.zip`. Defining source revision and dependency hashes are recorded in [reports/provenance.json](reports/provenance.json). The revision remains on the focused V22 branch/draft PR; V18–V21 and user-extracted copies are preserved.

Both bases print together flat with 3 mm opposed captive pivots and 0.4 mm nominal radial/face clearance. Rounded shoulders now lie in the front and rear end margins, clear of the playing field. The hook releases through 90° and parks at Z1.5–9.9, below the board underside at Z10.6. Its headed 3 mm catch, 3.2 mm hook and round 2 mm collar are fully recessed. One 8.6 mm length of 1.75 mm PLA provides the hook pivot. The 52×30.2 mm side recess admits a 12 mm thumb-pad clearance probe beside the hook; 30 mm-wide finger wells admit a 7 mm probe beneath the board edge. These are geometric access checks, not measured human comfort.

Current passing checks: 59 solid/mesh/STEP/fit/motion checks; 37 exported field probes; eight hardware checks including the whole folding path; 29 exterior/access/wall probes; 254 preliminary exterior mechanism trial checks; 20 plate/readback checks; three filament-core toolpath checks; 32 captive-hinge checks; 20 capstone checks; eight hinge trial checks; 129 recessed-closure trial checks. Motion is sampled, not a continuous swept-volume proof. Flexing release poses are assumed rather than FEA or measured force.

Three CC2 PLA slices pass with exact named meshes and preserved placement. Full-build estimate is **41,899 s (11 h 38 min 19 s) / 272.16 g**, eight printed parts, 19.3 mm maximum part height. The optional hinge trial is **1,556 s / 5.31 g**; the optional recessed closure trial is **3,175 s / 13.39 g**. Selected actual deposition layers, captive gaps and exported-geometry previews were reviewed. With a conservative 0.50 mm bead-width assumption, sampled captive running gaps are **0.384–0.422 mm**. No support centerlines enter the checked cylindrical bearings; this does not prove all extrusion clearances or physical joint release.

The exact piece package remains 42 original Cat/Witch 20×20×8 mm flats and two supplied one-piece 8 mm Cat/Witch capstones. Capstone geometry is identical to the earlier V22 kit; nominal storage roof gap remains 0.4 mm. Both bases, both boards, hook and collar have changed and must be replaced together. No printed interchangeability is claimed. Older sculpted capstones do not fit; weighted flats remain unqualified. The 1.8 mm closure backing wall, 1.2 mm local recess floor and 2.2 mm floor beneath pieces pass material probes. Rounded captive journal rims still need careful physical release/strength evaluation.

Environment: repository `.slicer-work/cad-venv/bin/python`, Python 3.12.13, CadQuery 2.7.0; [requirements.txt](requirements.txt) pins dependencies. ElegooSlicer 2.4.2 with included CC2 0.4 mm, PLA and process profiles. No new dependencies were installed. Slice reports retain commands/profile/input/project/Gcode hashes. Generic PLA temperature-metadata warnings remain (45°C softening entry versus 60°C bed). CLI OpenGL thumbnail generation is unavailable; separate actual-CAD previews are provided.

Reproduce using the CAD Python environment:

```text
python v22/source/build_exterior_trial.py
python v22/source/build_case.py
python v22/source/verify_hardware.py
python v22/source/verify_exterior.py
python v22/source/verify_field.py
python v22/source/verify_flat_capstones.py
python v22/source/render_case.py
python v22/source/package_case.py
python v22/source/slice_case.py
python v22/source/inspect_case_layers.py
python v22/source/verify_pin_toolpaths.py
python v22/source/build_fitcheck.py
python v22/source/build_closure_fitcheck.py
python v22/source/verify_pip_hinges.py
```

Review regenerated layer sheets and record their observations, then run `record_provenance.py`, `package_release.py` and `verify_package.py` under `v22/source`. Run `scripts/audit_v22_release.py` for fresh extraction, all payload hashes/syntax, local links and independent base/board/capstone reconstruction against packaged STEP. Its receipt is outside the archive at `docs/V22_SEAMLESS_PACKAGE_CHECK.json`. Source scripts resolve their own package paths and work from an extracted kit with the pinned CAD environment.

Resolved trial findings: a direct corner-hook relocation collided with the boards. The narrowed hook, revised pivot/catch heights, board-edge relief and 90° parked position remove those collisions. A high tongue corner briefly touched the recess roof during release; narrowing that tongue resolved it without removing the catch-engagement check. The initial reverse-stop block intruded into the pivot disc; moving it under the thumb foot restored independent rotation and the reverse stop. Hinge relief corners were rounded after the actual-geometry review, then the affected build and slices were regenerated. Earlier V22 separate-object slicing was resolved by keeping the base pair grouped as one assembly; that placement is preserved.

Physical snag resistance, thumb/finger comfort, joint release, stiffness, wear, fit and loaded retention remain unchecked in [ACCEPTANCE.md](ACCEPTANCE.md). No printer job, paid generation or merge was performed.
