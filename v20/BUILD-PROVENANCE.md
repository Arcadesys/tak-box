# V20 build provenance

V20 is a new geometry revision based on V19 commit `1091f7348f525d2b72f17cad1f5f8c680509fae0`. Defining V20 source revision: `be279db7a3d2209e1bebe1ba15c63ca12d8036ef`. Current source/dependency SHA-256 values are recorded in reports/provenance.json and the package manifest. Units are millimetres.

## What changed

Fixed original-piece pockets and removable sliding lids replace both drawers and the integral housing roofs. Sloped rails retain the lids vertically; 20×5.6 mm square-shouldered thumb catches require a nominal 4.5 mm inward release. Pockets shift 4 mm inward to clear that motion. The hatch top grows 1.4 mm so its broad face can contact the bed. Bore roof reliefs follow the new print directions.

The full 180 mm field, 36 mm pitch, four-leaf hinge axis, 1.75 mm filament pin dimensions and external swivel hook remain. STEP symmetric-difference checks in reports/compatibility.json verify that the two boards, hook and collars have unchanged CAD shapes from V19. Bases, sliding lids and hatch are new. Printed interchangeability has not been observed. V18/V19 archives and printed V16 parts remain unchanged.

## Current evidence

- 56 CAD/mesh/detailed-original-piece/motion checks pass, including lid lift retention, rear stop, catch engagement, release, removal and individual flat retrieval.
- 37 exported field probes, 31 hardware checks and 43 plate/readback checks pass.
- All five CC2 slices pass with exact named mesh readback, connected watertight meshes and checked source/project/profile/Gcode hashes.
- 18 nominal filament-core checks pass against actual extrusion centerlines. They exclude extrusion width, bore-end lips, roughness and physical force.
- All five selected layer sheets and the STEP access preview were inspected. Bases and lids print flat; no trapped storage-roof supports were seen. Boards retain broad removable underside support. Some local hinge/clip support remains.
- Maximum part height: 25.8 mm. Full-kit slicer estimate: 66,374 seconds (18 h 26 min 14 s), 402.19 g including supports/brims, versus V19's 116,312 seconds / 499.38 g.
- Optional front-section rail/catch trial: 5,306 seconds / 33.18 g; its geometry, sliced mesh readback and selected layers were checked separately. It does not test full-length warping or rear stops.
- The slicer still reports the Generic PLA softening-entry/bed-temperature warning. No spool qualification or printer job was performed.

Resolved intermediate rail and entry-relief collisions are documented in reports/development-notes.json. Final geometry checks pass. Flex poses are geometric assumptions, not force or fatigue calculations; motion is sampled rather than a continuous sweep proof. The target is the original Cat/Witch CAD, with 20×20×8 mm flats. The old reference Cat capstone STL has an open mesh; valid source CAD was used for fit. Weighted flats and curled capstones remain unverified.

## Environment and reproduction

Used `.slicer-work/cad-venv/bin/python`, Python 3.12.13, with the exact dependencies in requirements.txt. Installed versions are recorded in reports/provenance.json. Slicer: `/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer`, reporting 2.4.2. CC2 0.4 mm machine, Generic PLA and process profiles are included. Full CLI arguments, warnings and hashes are in reports/slicing.json and reports/fit-check.json; raw slicer logs are retained.

From the directory containing v20, with its requirements installed:

```sh
python v20/source/build_case.py
python v20/source/verify_field.py
python v20/source/verify_hardware.py
python v20/source/package_case.py
python v20/source/slice_case.py
python v20/source/render_case.py
python v20/source/inspect_case_layers.py
python v20/source/verify_pin_toolpaths.py
python v20/source/build_fitcheck.py
# Inspect newly generated layer sheets and record actual observations in
# reports/layer-inspection.json and reports/fit-check-layers.json.
python v20/source/record_provenance.py
python v20/source/package_release.py
python v20/source/verify_package.py
```

The layer review step is deliberately not auto-accepted. Slicer scratch/config/Gcode files under .slicer-work are excluded from the kit; sliced projects retain their embedded Gcode. The self-contained ZIP has one v20 root, exactly five full-build projects in PRINT and a clearly separate optional FIT-CHECK folder. Source dependencies are bundled under source/vendor. No earlier-version folders or nested ZIPs are included.

Physical fit, comfortable access/release, pin retention, lid flex/warping, hook friction and loaded transport remain unchecked in ACCEPTANCE.md.
