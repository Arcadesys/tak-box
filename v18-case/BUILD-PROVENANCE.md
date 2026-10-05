# V18 side-hook full-build evidence

Prepared October 5, 2026, from the first integrated case at `08c663b199a36c8e32b333b9aae3f9fc3d63503e` on `codex/v18-complete-build`. The user explicitly selected the side hook and 1.75 mm PLA filament pins. `PACKAGE-MANIFEST.json` pins the resulting package; `reports/provenance.json` records exact defining-source and dependency hashes. Recovery base: `2589129`; original body architecture: `bad9d0f1e4b0ed55a9e6f35ae5434a32523039d1`.

## Current evidence

| Check | Result |
|---|---|
| Geometry, solids, STEP/STL, original pieces and sampled motion | 51 checks pass |
| Exported playing field and grooves | 37 material probes pass; 180 mm field / 36 mm pitch |
| Exported filament hardware and bore material | 31 checks pass |
| Five named-object geometry plates | Bed, height, separation and readback checks pass |
| Five CC2 slices | All printable objects retained, manifold, inside bed; input/profile/project hashes verified |
| Actual filament-passage toolpaths | 18 checked cores clear of model and support extrusion centerlines |
| Visual review | Five critical-layer sheets, three detailed pin sheets and actual-STEP assembly/hook previews inspected |
| Frozen original recessed-clasp package | Original 70 files and 67 manifest entries retained; verified separately |

The retained settings estimate **116312 seconds (32 h 18 min 32 s), 499.38 g**, including supports and brims. There are **13 printed parts**, four filament pins (24.9 / 24.9 / 92 / 9.6 mm), and no printed filament-reference objects. The closed hardware envelope is **112.3 × 245.8 × 32.6 mm**.

The filament-passage test checks centerlines against a nominal 1.75 mm cylindrical core, cropped at passage ends. It does not model bead swell, elephant foot, roughness, dimensional accuracy, force or physical fit. Sampled CAD motion is not a continuous sweep proof. The hook has a friction bearing and reverse stop; there is no spring detent or measured retention force. Actual accidental-opening resistance and wear remain unchecked.

## Environment and commands

Actual environment: `.slicer-work/cad-venv/bin/python`, isolated Python 3.12.13; CadQuery 2.7.0, OCP 7.8.1.1.post1, trimesh 5.1.1, NumPy 2.5.3, SciPy 1.18.1, VTK 9.3.1, Matplotlib 3.11.2. Exact installed dependencies are in `requirements.txt`.

Installed CLI: `/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer`, reporting ElegooSlicer-2.4.2; app client 1.5.3.5. CC2 0.4 mm machine, PLA and process profiles are retained in `profiles`. Full commands and profile/input/project/Gcode hashes are in `reports/slicing.json`; raw CLI output is in each `*-slice.log`.

Run these scripts from the repository or extracted kit root using that environment (or a Python 3.12 environment with the pinned requirements):

```sh
python v18-case/source/build_case.py
python v18-case/source/verify_field.py
python v18-case/source/verify_hardware.py
python v18-case/source/package_case.py
python v18-case/source/slice_case.py
python v18-case/source/render_case.py
python v18-case/source/inspect_case_layers.py
python v18-case/source/verify_pin_toolpaths.py
# Review rendered layers and record observations in reports/layer-inspection.json.
python v18-case/source/record_provenance.py
python v18-case/source/package_release.py
python scripts/verify_v18_freeze.py
```

After each relevant geometry change, affected exports and motion checks were regenerated. The final support correction regenerated/resliced plates 01 and 02 with `--only 01-left-housing-hook-pivot-and-cap-compartment 02-right-housing-and-hook-pin`. Other slice receipts were reused only when exact input/project/profile hashes still matched. Final passage and layer analysis read the retained Gcode from all five current projects. No printer was contacted or started.

Housing objects have a **0.8 mm support side-clearance override** stored in their 3MF metadata. Other objects retain 0.35 mm. The process uses a 30° support threshold, automatic normal supports, 0.20 mm contact gaps and three upper interface layers. Preserve the housing object settings if reslicing. The metadata follows the [upstream OrcaSlicer 3MF implementation](https://github.com/OrcaSlicer/OrcaSlicer/blob/main/src/libslic3r/Format/bbs_3mf.cpp); local exported-project readback confirms the override survives the installed slicer.

The slicer's Generic PLA warning remains recorded: 45 °C softening entry versus 60 °C bed. Match the user's tested spool settings before printing; the defaults do not qualify a material.

## Corrections and failed attempts

- The retained v17 study assumed 19.5 mm flats. The integrated drawer geometry uses the actual original 20×20×8 mm CAD with 20.7 mm seats and 0.4 mm roof clearance. The field stayed unchanged.
- The recessed mechanism was replaced by a separate rigid hook, fixed pivot pad/reverse stop and headed catch. The locked hook blocks opening at a 1° sample; release clears through 0–65° at 1° samples. The released full case clears its sampled fold path.
- Main/hatch bores changed from 3.4 mm to 2.0 mm; collars use 1.9 mm through bores. Earlier small-part slices failed the nominal pin-core test. Current parts were re-exported with welded indexed 3MF connectivity, the hatch axis upright and collars bore-up; the final toolpaths pass. The earlier 3 mm kit is preserved in `release/archive`.
- Bore subtraction before mount union left material in the fixed hook passage. The final circular/45° roof passage is cut after union; exported hardware and actual deposition checks pass.
- The first filament slices placed support in board, fixed-hatch and hook bores. Teardrop roofs and the 30° support threshold cleared those passages.
- Removing internal main-pin stops simplified retention and made the bores through passages. It did not by itself eliminate support routed through the rear knuckles. Narrow support blockers also failed to prevent those support stems, so the final kit contains no blocker volumes. A 0.8 mm housing-only support side clearance solved this: all 18 tested passages now contain no model/support centerline intrusion. Support beneath external roots and the headed catch remains visible in the final layer sheets.
- Collars alone do not stop a whole pin being withdrawn. The guide specifies bonding only the designated fixed housing barrel/ear/mount to the pin, leaving moving joints free. The hook collar lightly contacts its bearing to set friction; main/hatch collars retain 0.5 mm running gaps.

## Physical boundary

The user reports the earlier recessed-clasp trial printed and an earlier 1.75 mm PLA hinge held in place. Exact revisions, loads and cycle counts were not supplied. Those observations do not qualify the new hook or whole case. Keep [ACCEPTANCE.md](ACCEPTANCE.md) unchecked until observed. The next action is the requested full print, then a short filament pass-through check during assembly, empty operation and loaded original-piece testing. No additional coupon is required to receive this full kit.
