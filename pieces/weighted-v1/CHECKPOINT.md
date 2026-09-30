# Weighted stones checkpoint

- Outcome: two teams of 21 assembled 20 × 20 × 6 mm stones, fillable bodies and locating floors, with print files and current geometry evidence.
- Scope: new `pieces/weighted-v1` package; existing board and pieces stay available. Existing sculptural capstones accompany the new stones.
- Route: one bounded coordinator execution pass; local parametric CAD and existing emblems avoid cross-component changes. No delegation or model override.
- Source: shared conversation, https://chatgpt.com/share/6abcafaa-25d0-83ea-8db4-6eb9e879bb69 (retrieved 2026-09-30); final user proposal is body plus epoxied floor. Conversation suggestions are design inputs, not measured material results.
- Current state: sources, eight validated printable meshes, assembled STEP references, three geometry 3MFs and three CC2 PETG sliced projects complete.
- Evidence: `reports/verification.json` passes exact envelopes, valid single solids, closed oriented meshes, no floor/body or stack overlap, plate bounds and 43 / 43 / 6 object readback. `reports/slicer-verification.json` records successful native slicing and on-bed, unskipped objects. Preview inspected with large white labels on a dark background and separate construction views.
- Resolved failures: exact CAD bounds avoid cached tessellation deflection; one zero-area Cat capstone triangle removed without reshaping; 3MF runtime dependencies installed; slicer uses absolute paths and Textured PEI bed instead of its unsupported Cool Plate default.
- Next step: print the three-clearance coupon, choose fit and ballast by physical tests, then assemble a sample before the full set.
- Physical gates: fit coupon, ballast bonding/rattle, cured seam, stack stability, wall stability, tactile preference, measured weight, case retention.
- PR route: one bounded coordinator pass for packaging and publication. Branch `codex/weighted-tak-stones` starts at current `origin/main`. The user subsequently requested including the additional tray-insert commit from `feat/tak-v16-tray-insert`; its source, generated artifacts and recorded evidence accompany the weighted package. Existing piece verification reports and sliced project hashes were checked, and the ZIP contents matched current files before staging. Physical gates remain open.
- Integration limit: the existing tray insert has 98 mm lanes sized for five 19.5 mm flats. Five new 20 mm weighted flats need 100 mm before clearance; this prototype is not compatible with that full-lane packing arrangement.
