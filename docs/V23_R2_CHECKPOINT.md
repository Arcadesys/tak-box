# V23 R2 — reinforced hinges and removable player trays

Outcome: full-height main-hinge supports and two removable trays, each loaded with 21 original flats plus its supplied flat capstone. Full 180 mm field, 36 mm pitch, sliding covers and recessed side hook retained. New package v23-r2 on codex/v23-durable-player-trays; original V23 kit/source and all earlier kits preserved.

Route: brief big-thinky planning for hinge sweep/tray-floor dependencies, then workhorse/medium implementation and focused verification in one context. Configured role mapping read; current chat model retained, no enforced model switch or delegation claimed. Counters unavailable.

Physical evidence: user reports baseline V23 broke at the thin bar carrying the hinge and expects purse handling. Exact fracture point, whether joints were fused, and the breaking action are unknown. This supersedes blanket unprinted status for that component; no R2 physical result or other acceptance is inferred.

Decision: 35.0 mm closed thickness (+2.4 mm), retaining 2.2 mm case floors and 4.7 mm boards while adding 1.2 mm tray floors directly on the case floor. Final measured closed envelope including barrels/hardware is 102.5×200×35 mm: the stronger barrels add 1.5 mm width, length unchanged. Supports are 8 mm radial/full height rather than the old roughly 2.3 mm upper web; captive pins grow 3→4 mm and barrels 6→9 mm, with 0.4 mm rounded edges. Printed strength is not proven. Trays have broad pinch bars and sampled 14 mm finger access, broad flat undersides, low locating stops and cover containment. Open loaded trays remain upright.

Evidence: all current reports pass for valid solids/exported meshes, full field, support material sections, loaded storage, 1 mm tray lift/repacking samples, cover/pocket containment probes, hinge folding, board travel and hook release. Four full CC2 slices and two actual-section trials preserve named meshes/placement; deposition sheets and geometry previews reviewed. Full estimate 48,922 s / 321.56 g. Hinge trial 2,448 s / 9.41 g; tray trial 3,404 s / 21.52 g. Fresh provenance and package audit are required before delivery.

Resolved failures: a 0.02284 mm³ parked-hook/recess contact removed by extending the local recess 0.8 mm; tray rear-rail contact found at 1 mm lift samples removed by shortening the tray 0.7 mm and moving its capstone bay forward 0.5 mm; a 0.000635 mm tessellation/bounding-box floor discrepancy removed by seating the actual mesh minimum at Z0, retaining strict slicer readback tolerance.

Compatibility: replace both bases, both boards and hook; add both trays. Original flats, flat capstones, collar and 8.6 mm hook filament geometry retained. Do not mix old/new halves. Weighted and older sculpted pieces remain unqualified. Concurrent multicolor board work from merged PR 29 / 82aff2d was fast-forwarded intact; its previous corners are not compatible with the wider R2 hinge reliefs, and artwork adaptation is outside this mechanical revision.

Delivery boundary: commit/push source and checked artifacts, create/attach focused draft PR based on codex/v23-seamless, verify one-root ZIP. No printer job, merge or paid generation. Physical release, grasp, full-tray warp/flex, fatigue, snag/rattle and loaded carry/shake remain pending in v23-r2/ACCEPTANCE.md.
