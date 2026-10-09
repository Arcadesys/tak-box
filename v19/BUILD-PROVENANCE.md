# V19 package provenance

V19 is the user's October 5 version/package cleanup of the checked hook-and-pin case at commit `1e8944b646a6bf7190b0d1752ce53c1ed5ae7132`. It changes the distribution layout and version labels, with no geometry or print-setting changes.

The ZIP has one root folder, `v19`. `START-HERE.md` is the assembly guide; `PRINT` contains exactly five current CC2 projects. Necessary CAD dependencies are bundled under `source/vendor/body` and `source/vendor/pieces`. Historical clasp packages, old ZIPs and older version folders are excluded.

## Evidence carried forward

The five print projects, their embedded Gcode, geometry-only plates, STEP/STL exports and profiles are byte-identical to the checked source build. `reports/version-migration.json` records original paths, exact hashes and the unchanged CAD-function AST check. The inherited reports retain their original source hashes, version names and commands as historical evidence; they are not misrepresented as a fresh V19 CAD or slicer run. The retained slicer preset may still identify the validated build as V18.

That validation recorded 51 geometry/mesh/piece/motion checks, 37 field probes, 31 hardware/bore checks, five successful CC2 slices and 18 clear filament-core centerline checks. The estimate remains 32 h 18 min 32 s / 499.38 g. Whole-case physical acceptance is still pending.

Current V19 checks verify a single ZIP root, exactly five PRINT projects, CRC and payload hashes, local links, standalone source imports and unchanged CAD functions/parameters. Version-labelled assembly previews are rendered again from the same exported STEP geometry. `PACKAGE-MANIFEST.json` pins the delivered V19 files.

## Reproduction

Use Python 3.12 with `requirements.txt` and the installed macOS ElegooSlicer. The validated dependency environment was Python 3.12.13, CadQuery 2.7.0, OCP 7.8.1.1.post1, trimesh 5.1.1, NumPy 2.5.3, SciPy 1.18.1, VTK 9.3.1 and Matplotlib 3.11.2. Exact settings remain in `profiles` and the housing object overrides in the 3MFs.

From the directory containing the extracted `v19` folder:

```sh
python v19/source/verify_package.py
# A full rebuild, if needed:
python v19/source/build_case.py
python v19/source/verify_field.py
python v19/source/verify_hardware.py
python v19/source/package_case.py
python v19/source/slice_case.py
python v19/source/render_case.py
python v19/source/inspect_case_layers.py
python v19/source/verify_pin_toolpaths.py
# Review new layers and record observations in reports/layer-inspection.json.
python v19/source/record_provenance.py
python v19/source/package_release.py
python v19/source/verify_package.py
```

The fresh-build scripts resolve their dependencies within this package. Slicing writes Gcode scratch files under `v19/.slicer-work`, which is excluded from the ZIP. Rebuilding replaces inherited reports with current evidence. No re-slice is needed solely to use this repackaged kit.

No printer job was started. Physical fit, hook friction after wear, accidental opening, filament-pin strength and loaded transport remain untested; use `ACCEPTANCE.md` after the full print.
