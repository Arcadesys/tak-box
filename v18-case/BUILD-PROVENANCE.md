# V18 first full-build evidence

Prepared October 5, 2026. Source base: `2589129` (`codex/recover-tak-v18-recessed-clasp`), with the integrated changes in this package pinned by `PACKAGE-MANIFEST.json`. Original v17 body baseline: `bad9d0f1e4b0ed55a9e6f35ae5434a32523039d1`. Frozen clasp recovery references original `36ffe69465d09e3d64d8873b35efcef5642be556`.

Environment: isolated Python 3.12.13 (`uv`), CadQuery 2.7.0, OCP 7.8.1.1.post1, trimesh 5.1.1, NumPy 2.5.3, SciPy 1.18.1, VTK 9.3.1 and Matplotlib 3.11.2. Exact installed Python packages are in `requirements.txt`. macOS ElegooSlicer CLI identifies as ElegooSlicer-2.4.2 (installed app client 1.5.3.5). Exact CC2 0.4 nozzle, Generic PLA and process settings are retained in `profiles/`; profile hashes and full slice commands are in `reports/slicing.json`.

## Current checks

| Evidence | Result |
|---|---|
| `reports/geometry.json` and `build.log` | 50 valid-solid, STEP/STL, original-piece, release/retention and sampled motion checks pass |
| `reports/field.json` | 25 cell surface and 12 recessed grid probes pass; 180 mm / 36 mm pitch |
| `reports/hardware.json` | 14 open/closed hardware clearance checks pass; three steel rods and four printed caps |
| `reports/plates.json` | Five named-object geometry plates; bed/build-height/separation/readback checks pass |
| `reports/slicing.json` | All five CC2 dry slices pass, no skipped/outside objects; embedded named manifold geometry retained |
| `reports/layer-inspection.json` | Whole deposition XY bounds pass; selected critical layers reviewed on all five plates |
| Original clasp freeze | 70 pinned files, 67 original manifest entries, CRC and source/report hash checks pass |

Total sliced estimate: **122309 seconds (33 h 58 min 29 s), 564.61 g**, including supports and brims. These estimates belong to the retained starting profiles. Confirm actual tested spool settings and reslice if they differ. The slicer reports `bed_temperature_too_high_than_filament` because the PLA softening entry is 45 °C while the bed is 60 °C. Installed vendor PLA defaults use the same values; the warning remains recorded. No material or physical performance is qualified by this build.

## Reproduction commands

Run from repository root, or extracted kit root, with Python 3.12 and installed macOS ElegooSlicer:

```sh
python -m venv .cad-venv
.cad-venv/bin/pip install -r v18-case/requirements.txt
.cad-venv/bin/python v18-case/source/build_case.py
.cad-venv/bin/python v18-case/source/verify_field.py
.cad-venv/bin/python v18-case/source/verify_hardware.py
.cad-venv/bin/python v18-case/source/package_case.py
.cad-venv/bin/python v18-case/source/slice_case.py
.cad-venv/bin/python v18-case/source/render_case.py
.cad-venv/bin/python v18-case/source/inspect_case_layers.py
# Inspect the new critical-layer sheets and record observations before packaging.
.cad-venv/bin/python v18-case/source/package_release.py
python scripts/verify_v18_freeze.py
```

The actual run used `.slicer-work/cad-venv/bin/python` with the same commands. After geometry was fixed, plates 01/02/04 were regenerated and resliced; plate 02 was then moved 3 mm inward and regenerated/resliced. Unchanged slice evidence for other plates was reused only after matching input, sliced-project and profile hashes. Final layer plots were regenerated from those actual Gcodes. VTK depth-buffered previews avoid the old Matplotlib painter-order artifacts; all previews use exported STEP geometry, including hardware.

## Repaired failures

- The v17 study assumed 19.5 mm flats; current original CAD is 20 mm. Rebuilt drawers provide 20.7 mm seats, retaining field size.
- Mirroring the left housing duplicated a hinge family. The integrated housing now uses the baseline's separate left/right hinge families.
- The cap bay conflicted with an independent board strap. Its width is 87 mm, preserving both original capstones and released-board clearance.
- Hatch root fusion filled the steel bore. The final bore is cut after union and hardware readback passes.
- A drawer stop arm/root obstructed motion. Final stop location and maintenance-release geometry clear the drawer path; positive overlap barriers are recorded at 169, 170 and 172 mm. The initial one-cubic-millimetre threshold rejected the first 0.9 mm³ contact; the final test requires a positive barrier at all three positions.
- Inherited bridge suppression left broad board undersides without dense support. `bridge_no_support=0` supplies the required support.
- Front-end-down housings trapped support in their long tunnels. Rear-end-down orientations and short stop ramps remove that support stem. Selected current tunnel layers are blank; physical removal still needs observation.
- Plate 02's generated brim reached Y=0.144 mm. Moving its geometry +3 mm in Y brought the complete deposition inside the bed.
- Exact rounded triangle comparison rejected float32 recentering in sliced projects. Named volume/triangle/extent checks plus vertex and triangle-centroid nearest-neighbour checks now allow less than 0.00003 mm, with manifold checks retained.

`geometry.json` records the source snapshot at CAD validation time. Only print placement, preview and layer-inspection helpers changed afterward; the CAD-defining `case.py` and `build_case.py` hashes still match that run. Current helper/dependency hashes are in `reports/provenance.json`, and all final payload hashes are pinned by the manifest.

Physical record: the user reports the clasp trial printed; no whole-case observations exist. Force, fatigue, support removal, quiet retention, finger comfort and loaded spill-free operation remain unchecked. Motion sampling is not a continuous sweep proof, and assumed flex poses are not FEA. `ACCEPTANCE.md` is the remaining physical record. No printer job was initiated.
