# V21 build provenance

V21 derives from V20 commit `1d03201fd003e3aff38fde6c7f1d94d1befbab54`. Defining source revision: `d928d5116226ef307aee9c3486a08b7268a15716`. Exact source/dependency hashes are recorded in reports/provenance.json and PACKAGE-MANIFEST.json. Units are millimetres.

## What changed

The two playing boards now double as storage lids, sliding outward above fixed original-piece pockets. Separate lids and board hinges are removed. Only the bases hinge. Rails prevent lifting; front catches block withdrawal until pressed rearward 2.8 mm; inner stops locate the seated boards. Boards are fully removable with 106 mm outward travel. Catch poses are geometric assumptions, not force or fatigue calculations.

The full 180 mm field and 36 mm pitch remain. Main filament pins shorten to 14.9 mm. The side hook moves to the front corner to clear board travel, and the rear compartment shifts 2 mm for rail clearance. New bases and boards are required. Exported STEP symmetric-difference checks in reports/compatibility.json confirm unchanged hatch, hook and collar shapes after assembly translation. Printed interchangeability is unobserved. Earlier packages and printed parts remain intact.

## Evidence

- 52 solid, mesh, original-piece clearance and sampled motion checks pass.
- 37 exported field probes, 29 hardware and 39 plate/readback checks pass.
- Four CC2 slices pass, with named object/mesh readback and verified input, profile, project and Gcode hashes.
- 16 filament-core checks pass against extrusion centerlines. They exclude extrusion width, bore-end lips, roughness and physical insertion force.
- All four selected layer sheets and actual STEP previews were reviewed. Broad base floors and board undersides contact the bed. No broad board support blanket appears in selected layers; local hinge/hatch/hook support remains. Slicer support metadata is not a claim of support-free printing.
- Maximum part height: 25.8 mm. Full-kit estimate: 45,289 seconds (12 h 34 min 49 s), 287.29 g including supports/brims.
- Optional shortened front/rear rail and catch fixture: 10 checks pass; sliced mesh readback and selected layers reviewed. Estimate: 3,587 seconds / 19.26 g. It does not test full-board warping, inner stops, hinges or loaded transport.
- Generic PLA softening-entry/bed-temperature warning remains in slicer logs. No spool qualification or printer job was performed.

The target is the original Cat/Witch CAD: 42 flats at 20×20×8 mm plus the original capstones. The old reference Cat capstone STL has an open mesh; valid source CAD supplies fit geometry. Weighted flats and curled Fox/Cat capstones remain unverified. Sampled collision checks are not continuous motion proofs or physical acceptance.

## Environment and reproduction

Used `.slicer-work/cad-venv/bin/python`, Python 3.12.13, with requirements.txt dependencies. Installed versions appear in reports/provenance.json. Slicer: `/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer`, version 2.4.2. CC2 0.4 mm machine, Generic PLA and process profiles are included. CLI arguments, warnings and hashes appear in reports/slicing.json and reports/fit-check.json; raw slicer logs are retained.

From the directory containing v21, with its requirements installed:

```sh
python v21/source/build_case.py
python v21/source/verify_field.py
python v21/source/verify_hardware.py
python v21/source/package_case.py
python v21/source/slice_case.py
python v21/source/render_case.py
python v21/source/inspect_case_layers.py
python v21/source/verify_pin_toolpaths.py
python v21/source/build_fitcheck.py
# Inspect newly generated layer sheets, then record actual observations in
# reports/layer-inspection.json and reports/fit-check-layers.json.
python v21/source/record_provenance.py
python v21/source/package_release.py
python v21/source/verify_package.py
```

Visual review is not auto-accepted. Slicer scratch/config/Gcode under .slicer-work is excluded; sliced projects retain embedded Gcode. The ZIP has one v21 root, four full-build projects in PRINT and a separate optional FIT-CHECK folder. Required source dependencies are bundled in source/vendor. No older version folders or nested ZIPs are included.

Physical fit, comfortable release/retrieval, pin retention, board flex/warping, hook friction and loaded transport remain unchecked in ACCEPTANCE.md.
