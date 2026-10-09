# V22 first-print kit evidence

V22 keeps the 32.6 mm thin case and replaces the rear compartment/hatch with one-piece flat Cat/Witch capstones beneath the sliding boards. Closed size including hardware is 111.8 × 220.2 × 32.6 mm, 23.6 mm shorter than V21. The 180 × 180 mm, 5×5 playing field remains unchanged. Units: mm. Defining source revision and dependency hashes are in [reports/provenance.json](reports/provenance.json).

Based on V21 commit `0fd6806`, with opposed captive main pivots adapted from V16 source geometry (3 mm diameter, 0.4 mm radial and face clearance). Both bases print together flat in one assembly. Boards, side hook and the remaining hook collar have zero CAD symmetric difference from V21. The only filament pivot is the 9.6 mm side-hook pin. Physical interchangeability has not been observed.

59 geometry/mesh/piece/motion checks, 37 field probes, six hardware checks, 20 plate/readback checks, three filament-core checks and 20 flat-capstone checks pass. Three slices pass with exact named meshes and preserved assembly positions. Full kit estimate: 40,629 seconds (11 h 17 min) / 267.67 g. Eight printed parts; maximum part height 19.3 mm. The optional shortened hinge pair passes eight checks and slices to 1,290 seconds / 3.80 g.

32 captive-hinge checks pass: CAD clearance and opposed axial capture, no support centerlines within the cylindrical bearings, and sampled radial toolpath gaps in both full and trial prints. With a conservative 0.50 mm bead-width assumption, sampled side gaps measure 0.385–0.422 mm. This is not a continuous swept-volume or physical force/strength proof. Selected layers, gap plots and actual STEP previews were visually reviewed.

The exact piece package is 42 original Cat/Witch 20 × 20 × 8 mm flat stones plus two new V22 8 mm flat capstones. Vendored original flat STLs and defining source hashes are retained. Capstones have nominal 0.4 mm roof clearance and 4.5 mm exposed height above the bay rim; loaded folding, sliding, discrete retention poses and vertical retrieval checks pass. Older sculpted capstones do not fit these bays. Weighted flats remain unqualified. The capstone preview shows optional contrast paint; each capstone prints as one solid part.

Environment: repository `.slicer-work/cad-venv/bin/python`, Python 3.12.13; [requirements.txt](requirements.txt) pins the dependencies. ElegooSlicer 2.4.2, CC2 0.4 mm nozzle and included PLA/process profiles. Commands and profile hashes are recorded in slicing and fit-check reports. No printer job started. Generic PLA temperature-metadata warnings remain (45°C softening metadata versus 60°C bed). Missing CLI OpenGL thumbnails are replaced by separate actual-geometry previews.

Run from the repository root using the CAD environment, in order:

```text
python v22/source/build_case.py
python v22/source/verify_field.py
python v22/source/verify_hardware.py
python v22/source/verify_flat_capstones.py
python v22/source/package_case.py
python v22/source/slice_case.py
python v22/source/render_case.py
python v22/source/inspect_case_layers.py
python v22/source/verify_pin_toolpaths.py
python v22/source/build_fitcheck.py
python v22/source/verify_pip_hinges.py
```

Review regenerated layer sheets before marking their reports reviewed, then run `record_provenance.py`, `package_release.py` and `verify_package.py` from the same source directory. The packaged source resolves its own paths and can also run from an extracted kit. Fresh extraction and standalone reconstruction evidence is recorded outside the archive in `docs/V22_PACKAGE_CHECK.json`.

Resolved implementation issues: separate-object slicing reported conflicting paths; grouping the disjoint base meshes into one assembly fixed it without merging them. Named-mesh readback verifies each component and world placement. The gap checker initially mistook internal infill voids for a missing pin; it now uses outer pin contours and segment-capsule intersections. An optional capstone edge chamfer caused a small Witch STEP volume readback discrepancy; removing it restored matching readback while retaining rounded outline corners. A tessellated bounding-box offset was removed from stored-piece placement; exact CAD bottom planes now set the storage height. No new dependencies were added.

Physical acceptance remains unchecked in [ACCEPTANCE.md](ACCEPTANCE.md): hinge release, warping, slider effort, capstone recognition/grip, hook retention and loaded transport require the printed build.
