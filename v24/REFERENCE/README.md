# Reference and engineering files

For printing, go up one level and use [START-HERE](../START-HERE.md), **FULL-PRINT** or **SMALL-TRIALS**. Those are the recommended, clearly named projects.

Everything here supports repair, rebuilding or checking the design. Internal `PRINT`, `FIT-CHECK`, `TRAY-FIT`, `INLAY-FIT` and `board-inlays/PRINT` files are build-stage copies. `plates` and `*-geometry.3mf` are geometry-only exports. The old `models/board-*.step` and `models/assembly-*.step` are monolithic mechanical references, not the current four-colour project.

- [Assembly and compatibility](ENGINEERING-GUIDE.md)
- [Build commands and evidence](BUILD-PROVENANCE.md)
- [Four-colour CAD and materials](board-inlays/README.md)
- [Organization and unchanged-project proof](reports/organization.json)
- [Package manifest](PACKAGE-MANIFEST.json)

`HISTORY` in the working checkout preserves prior ZIPs and user-extracted folders. It is excluded from the current download to avoid nesting old kits inside the new kit.

Rebuild source stays relative to this REFERENCE directory. The final delivery command is `python v24/REFERENCE/source/package_release.py`: it copies the accepted build outputs into the seven descriptive user-facing filenames, regenerates PREVIEW.png, verifies preservation and audits a freshly extracted `v24/V24-PRINT-KIT.zip`. `source/delivery.py` is the single mapping of build outputs to FULL-PRINT and SMALL-TRIALS. Run that final command after any appropriately validated rebuild; do not manually rename individual print files.
