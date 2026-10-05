# V20 checkpoint — October 5, 2026

Outcome: a self-contained flat-printing full-case kit with fixed piece pockets and sliding lids. User explicitly authorized V20 after choosing sliding storage tops. Scope: replace both drawers and enclosed housing roofs; retain the 180 mm 5×5 field, common hinge axis, 1.75 mm filament axles and side hook. Preserve all V18/V19 deliverables.

Route: short design pass for rail, catch and loading-path uncertainty; bounded implementation and verification use workhorse scope, medium effort. Role mapping read; current desktop context retained, with no model switch or delegation claimed. Usage counters unavailable.

Current state: source geometry on codex/v20-sliding-storage. Sloped rails constrain lift; a square-shouldered thumb catch blocks each lid from sliding out. Pockets shift 4 mm inward from V19 to keep loaded flats clear of catch release. Hatch top thickened 1.4 mm for broad-face printing. Horizontal bore roofs adjusted to print direction.

Evidence: 56 solid/mesh/original-piece/motion checks, 37 field probes, 31 hardware checks, 43 plate/readback checks and 18 nominal pin-core toolpath checks pass. Five CC2 slices pass at 66,374 seconds / 402.19 g. All print heights are <=25.8 mm. Actual layer sheets and STEP access preview reviewed. Board panels retain broad removable underside support; bases/lids have no trapped roof supports in reviewed layers. Optional exact front-section fit check sliced at 5,306 seconds / 33.18 g. Physical acceptance remains false.

Next: finalize reproducible provenance, extract/hash-check the ZIP, commit and open a focused draft PR. No printer job started.

Development finding: widening the catch upward caused a rail collision during withdrawal at the old 2.8 mm release. The full-height 20×5.6 mm thumb surface now uses a 4.5 mm inward release; pocket placement and lid relief move to preserve loaded clearance. Digital rechecks pass after also widening the front catch entry relief. Actuation remains a physical test. See v20/reports/development-notes.json.
