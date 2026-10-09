# V24 — identity correction and retained print evidence

The user explicitly named the completed reinforced-hinge/removable-player-tray revision **V24**. This changes its version identity only. The geometry and printing remain those delivered as V23 R2: 8 mm full-height supports, 4 mm captive pivots, rounded 9 mm barrels, two removable loaded trays and a **102.5 × 200 × 35 mm** closed envelope. The full 180 mm / 36 mm playing field and original flats/supplied flat capstones remain.

The accepted geometry source is **1078f0e**, packaged artifacts **919bbf0**, and final prior revision **f80af3c**. The complete original V23 R2 kit is preserved at `v23-r2/release/tak-v23-r2-print-kit.zip`, SHA-256 `7a4ac10b53c1f967d48a39bd2c93892ce8b06412635ec06f95d8a4666318ee12`. Original V23 remains the earlier 101 × 200 × 32.6 mm case; its ZIP and unrelated multicolor work are unchanged.

## Identity evidence

[reports/identity.json](reports/identity.json) establishes:

- **38 CAD files** are byte-identical to the delivered kit.
- **12 3MF archives** are byte-identical: four full geometry plates, four sliced full projects and two pairs of trial geometry/sliced projects. Named meshes, placements, units, metadata and every executable G-code instruction are therefore unchanged. The audit also reads the model objects/transforms and records embedded G-code hashes.
- All **three printer/material/process profiles** are byte-identical. Embedded preset names intentionally retain V23 R2, avoiding any profile or sliced-project edits.
- **20 source files** have equivalent parsed syntax after normalizing version labels and module docstrings. Geometry algorithms and numeric values are unchanged.
- Original V23 kit SHA-256 remains `33510a63581b1a8b5f3c5afde34ed99acf6ecd5ccfb6bc49956e6d6e2b9e1221`.

The prior **238 checks, four complete-build slices and two trial slices** are retained byte-for-byte, including their historical labels and paths. They are accepted evidence for the identical geometry/profile revision, not newly run V24 geometry, motion or slicing checks. [reports/validation-origin.json](reports/validation-origin.json) preserves the original provenance; [reports/validation-notes.md](reports/validation-notes.md) preserves its build notes and resolved failures. Current identity/source/output hashes are recorded in [reports/provenance.json](reports/provenance.json).

The six V24 geometry previews are regenerated from the same exported STEP files, with version labels updated. Existing deposition-layer sheets remain unchanged. Fresh archive verification checks the v24 root, four PRINT projects, two separate trial projects, every payload hash, JSON/Python syntax, ZIP integrity and local Markdown links. Its receipt is `release/AUDIT.json`, outside the archive to avoid a circular ZIP hash.

## Reproduce the identity package

Use the existing repository `.slicer-work/cad-venv/bin/python` environment (Python 3.12.13, CadQuery 2.7.0; dependencies pinned in requirements.txt). No new dependencies or slicing were needed for the rename. In the repository, retain the V23 R2 and original V23 archives at their documented paths, then run:

```text
python v24/source/verify_identity.py
python v24/source/render_revision.py --only 01-open
python v24/source/render_revision.py --only 02-closed
python v24/source/render_revision.py --only 03-table-setup
python v24/source/render_revision.py --only 04-loaded-storage
python v24/source/render_revision.py --only 05-hinge-detail
python v24/source/render_revision.py --only 06-loaded-trays
python v24/source/record_provenance.py --reuse-accepted-validation
python v24/source/package_release.py
```

The equivalent CAD build and check scripts remain under `source/` for a future geometry revision. A fresh full rebuild uses the same command sequence described in the retained build notes, substituting `v24/` for the old package path and using `record_provenance.py` without the reuse flag after all checks. The historical compatibility comparison in `verify_supports.py` also requires the retained sibling `v23/models/board-left.step`. Identity verification deliberately needs both earlier archives; the printable projects themselves are standalone.

## Unchanged limitations

Full-build estimate remains **48,922 s / 321.56 g**. Hinge trial: **2,448 s / 9.41 g**. Tray trial: **3,404 s / 21.52 g**. Supported slicing was ElegooSlicer 2.4.2 for CC2 0.4 mm PLA, 0.20 mm layers, four walls and 20% gyroid. Generic PLA temperature-metadata warnings and unavailable headless OpenGL thumbnails remain as recorded in the original receipts.

The reported earlier V23 hinge-support break is unchanged evidence; its exact fracture site, joint-fusion state and triggering action are unknown. No V24 physical durability, release, tray stiffness, grip, rattle, snag or loaded transport acceptance is inferred. Motion is sampled, catch flex assumed, and structural material probes are not FEA or fatigue/drop tests. Open loaded trays remain upright. No printer job or merge was performed for this rename.
