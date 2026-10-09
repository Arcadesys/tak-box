# V20 checkpoint — October 5, 2026

Outcome: a self-contained flat-printing full-case kit with fixed piece pockets and sliding lids. User explicitly authorized V20 after choosing sliding storage tops. Scope: replace both drawers and enclosed housing roofs; retain the 180 mm 5×5 field, common hinge axis, 1.75 mm filament axles and side hook. Preserve all V18/V19 deliverables.

Route: short design pass for rail, catch and loading-path uncertainty; bounded implementation and verification use workhorse scope, medium effort. Role mapping read; current desktop context retained, with no model switch or delegation claimed. Usage counters unavailable.

Current state: source geometry on codex/v20-sliding-storage. Sloped rails constrain lift; a square-shouldered thumb catch blocks each lid from sliding out. Pockets shift 4 mm inward from V19 to keep loaded flats clear of catch release. Hatch top thickened 1.4 mm for broad-face printing. Horizontal bore roofs adjusted to print direction.

Evidence: 56 solid/mesh/original-piece/motion checks, 37 field probes, 31 hardware checks, 43 plate/readback checks and 18 nominal pin-core toolpath checks pass. Five CC2 slices pass at 66,374 seconds / 402.19 g. All print heights are <=25.8 mm. Actual layer sheets and STEP access preview reviewed. Board panels retain broad removable underside support; bases/lids have no trapped roof supports in reviewed layers. Optional exact front-section fit check sliced at 5,306 seconds / 33.18 g. Physical acceptance remains false.

Package evidence: v20/release/tak-v20-print-kit.zip has one v20 root, five PRINT projects and the optional FIT-CHECK. CRC and 99 payload hashes pass. A fresh extraction independently verifies source imports, base/lid CAD volumes, original piece dimensions and 11 local guide links. See docs/V20_PACKAGE_CHECK.json. V18 freeze and V19 manifests still pass. No printer job started.

Next physical action: use the optional front-section rail/catch print to check comfortable release and sliding fit, or proceed with the complete five-plate build at the user's discretion. Full-length warping, loaded retention and fatigue remain untested. Repository handoff: sources and verified kit pushed on codex/v20-sliding-storage. Draft PR: https://github.com/Arcadesys/tak-box/pull/25, based on the V19 branch in PR #24. Source commit be279db; generated release commit de08c4d. No remaining digital-build blocker.

Development finding: widening the catch upward caused a rail collision during withdrawal at the old 2.8 mm release. The full-height 20×5.6 mm thumb surface now uses a 4.5 mm inward release; pocket placement and lid relief move to preserve loaded clearance. Digital rechecks pass after also widening the front catch entry relief. Actuation remains a physical test. See v20/reports/development-notes.json.
