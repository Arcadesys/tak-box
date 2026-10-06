# V24 four-colour integration evidence

The accepted celestial artwork now forms real, separate printable inlays on **V24** boards. The face is Z16.5, underside Z11.8; 0.6 mm flush inlays occupy Z15.9–16.5. The default board 3MF has two registered board assemblies, each with body, grid, stars and two accent parts. Slots are 1 black, 2 white grid/stars, 3 silk accent 1 and 4 silk accent 2. Gold and purple are examples. The generic silk placeholders are not actual spool profiles: select both actual profiles and reslice before printing.

The changed surfaces retain the full 180 mm 5×5 / 36 mm field and V24's wider hinge-corner reliefs, catches, rails and grips. Case mechanics, 102.5×200×35 mm envelope, two removable loaded trays, original flats and 8 mm flat capstones are unchanged. No exterior artwork is added: playing faces fold inward.

## Current checks

- [Board geometry receipt](board-inlays/reports/geometry.json): 207 checks covering valid CAD, STEP readback, welded watertight STL meshes, no material overlaps, flush inlays, exact filled-board envelope and unchanged geometry below the inlays, all 25 cell surfaces and white grid lines, exact original stored pieces, loaded slides at 2 mm samples through 106 mm, and folding against the opposite loaded half at 5° samples through 180°. Exported grouped geometry 3MFs are read back for named parts, mesh coordinates, bed placement, group separation and four material assignments.
- [Hardware interfaces](board-inlays/reports/hardware-interfaces.json): five additional checks cover paired folding and full released sliding past the retained hook pivot/collar, folding past the parked hook, closing the hook over the coloured boards and the unchanged complete closed envelope.
- [CC2 slicing receipt](board-inlays/reports/slicing.json): new board and small trial dry slices in ElegooSlicer 2.4.2; each sliced project's named meshes, triangle counts, world transforms, four assignments, profiles, bed containment and embedded G-code hashes are read back. Board maximum vertex error remains below 0.00004 mm.
- [Actual deposition receipt](board-inlays/reports/colour-layers.json): six checks confirm white, accent 1 and accent 2 deposit on the actual model in every one of the six inlay layers for both projects. The prime tower lies outside the inspected model regions. [Layer image](board-inlays/previews/05-sliced-colour-layer.png) is generated from embedded G-code.
- [Unchanged mechanics](reports/unchanged-mechanics.json): current hashes prove retained mechanical source, original mechanical STEP/STL references, profiles, three unaffected full projects and two mechanical trials match the pre-inlay V24 delivery. Prior mechanical checks are reused on that basis; unaffected base/tray/hook tests are not rerun.
- [Preview review](reports/inlay-preview-review.json): actual component STEP files supply all four surface colours in open/play and trays-beside-board views. The closed view correctly hides the inward-folded artwork. Large captions, clear white grid and decorative-only colour meaning are inspected. Existing storage/hinge/tray previews are preserved because their geometry is unchanged.

The slicer GUI was showing an unsaved base project and an active device print. Its New Window action did not expose a separate controllable review window, so the existing project was left intact. No GUI import/material-panel verification is claimed. The exported project metadata and actual sliced model deposition are independently checked. No print job was sent or altered.

## Historical evidence

Before-inlay V24 archive: `v24/release/archive/tak-v24-before-board-inlays.zip`, SHA-256 `5d48e11d789e2d2e1de48067df9993958c19a91a95c3c81998b7d06d61d66a9d`. It is preserved in the repository, not nested inside the current kit. Baseline merge is `b766181`; original mechanical geometry source is `1078f0e`.

[Historical identity provenance](reports/historical-identity-provenance.json), [identity receipt](reports/identity.json), [validation origin](reports/validation-origin.json) and [earlier build notes](reports/validation-notes.md) describe the earlier V24/V23 R2 equivalence. Their whole-kit identity, 238-check totals, monochrome board slicing and groove-only field checks are **historical**, not current multipart-board validation. Current [provenance](reports/provenance.json) separates new surface evidence from unchanged mechanical evidence. Original V23, V23 R2 and all earlier archives remain intact.

The `models/board-*.step` and original `models/assembly-*.step` are retained monolithic mechanical references. Active colour CAD lives in `board-inlays/models`; the default print project and current assembled previews use those real parts. Do not use the old monolithic references as a multicolour print project.

## Reproduce

Use the retained `.slicer-work/cad-venv/bin/python` environment: Python 3.12.13, CadQuery 2.7.0, OCP 7.8.1.1.post1; versions in requirements.txt and the receipts. Artwork is vendored locally from V16; the accepted V23 role split is adapted to V24 geometry. All dimensions are millimetres.

Run from the repository root with that Python executable:

```text
python v24/board-inlays/source/build.py
python v24/board-inlays/source/verify_hardware_interfaces.py
python v24/board-inlays/source/slice.py
python v24/board-inlays/source/inspect_layers.py
python v24/board-inlays/source/install.py
python v24/board-inlays/source/render.py
python v24/source/render_revision.py --only 01-open
python v24/source/render_revision.py --only 02-closed
python v24/source/render_revision.py --only 03-table-setup
python v24/source/record_provenance.py
python v24/source/package_release.py
```

Parent CAD captions are composed with a deterministic DejaVu Sans font after rendering because the macOS VTK glyph atlas intermittently dropped leading characters. Wait for renders before recording hashes. Original mechanical build/package scripts remain; `package_case.py` and `slice_case.py` now leave plate 02 to the multipart pipeline, preventing an accidental monochrome overwrite. Fresh mechanical rebuild instructions remain in the historical build notes and require their own checks if those sources change.

The current ZIP audit verifies one `v24` root, four default PRINT projects, three trial projects, every manifest hash, JSON/Python syntax, nested 3MF integrity and local Markdown links. `release/AUDIT.json` stays outside the ZIP to avoid a circular hash. Archive provenance does not claim a physical print.

## Estimates and remaining physical work

The four complete projects estimate **61,242 s / 326.85 g** (17 h 0 min 42 s), excluding 42 original flats. The board pair is **29,275 s / 121.16 g**; the colour trial **4,348 s / 19.45 g**. Existing hinge trial: 2,448 s / 9.41 g; tray trial: 3,404 s / 21.52 g. Estimates depend on actual filament/purge profiles. Boards use 0.10 mm layers (0.20 mm initial), four walls, 20% gyroid and a prime tower; unchanged mechanical plates retain 0.20 mm layers.

The build and slices passed without geometry or slicer failures. VTK captions dropped leading characters on two assembled renders; deterministic caption composition corrected them. Headless slicer thumbnail/OpenGL warnings are retained in logs; CAD and G-code previews provide the inspected views. Generic PLA temperature metadata warnings do not establish actual silk suitability.

Motion is sampled, catch flex is assumed and checks are not FEA/fatigue tests. Physical silk bonding, colour purity, full-board warping, catch friction, hinge durability, tray grip and loaded transport remain pending on the [acceptance sheet](ACCEPTANCE.md). No actual silk spool has been selected and no printer job or merge is performed by this integration.
