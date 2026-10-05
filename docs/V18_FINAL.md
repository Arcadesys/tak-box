# V18 final version

The user selected **v18 as the FINAL version** on October 4, 2026 (Chicago).
This freezes the design direction: the recessed press-and-slide clasp is the
selected closure, with the four-leaf common-hinge case architecture retained.
Finish and verify this version; reopening the version or design direction
requires an explicit user decision. Measured fit corrections and case integration
stay within v18 and receive review.

## Exact baseline

- V18 clasp recovery commit: `36ffe69465d09e3d64d8873b35efcef5642be556`.
- Clasp source: [`v18-recessed-clasp/build.py`](../v18-recessed-clasp/build.py).
- Coupon: [`tak-v18-recessed-clasp.3mf`](../v18-recessed-clasp/plate/tak-v18-recessed-clasp.3mf).
- Original kit: [`tak-v18-recessed-clasp-coupon-kit.zip`](../v18-recessed-clasp/release/tak-v18-recessed-clasp-coupon-kit.zip).
- Case-body baseline: `v17-four-leaf` at merged commit
  `bad9d0f1e4b0ed55a9e6f35ae5434a32523039d1`.
- [`V18-FREEZE.json`](V18-FREEZE.json) pins every recovered clasp-package file
  by byte count and SHA-256. Run `python3 scripts/verify_v18_freeze.py` from the
  repository root to check that the frozen package remains intact.

The coupon geometry is preserved exactly. The old squeeze buckle and draw-latch
trials remain historical material. The combined v17 plates still contain the
old buckle; use the separate v18 coupon plate for the clasp experiment.
The complete first-print case and plates are now in `v18-case`; the retained
v17 combined plates remain historical.

## Fixed design choices

- All four main leaves share one hinge axis; covered drawers retain the flats.
- Preserve the 180 mm 5×5 field, 36 mm pitch, finger access and original
  Cat/Witch piece envelopes. Weighted and curled sets are not accepted for
  this case until their exact geometry passes clearance checks.
- V18 receiver, keeper and rigid sliding bolt form the closure. Unload,
  press the recessed button, slide 10 mm, then lift. Both closing and opening
  require pressing. Support is required for the supplied coupon orientation.
- V16 printed interfaces stay unchanged; the premium pagoda remains separate.

## Evidence and release status

Current package integrity checks verify original bytes, hashes, ZIP CRC and
Python syntax. Retained reports record sampled CAD/path checks, manifold
exports and an analysis-only support-enabled dry slice. Their scope is the
standalone coupon; they are not new CAD runs or physical results.

**Final direction selected; complete first-print build prepared; physical release pending.** Keep each gate
unchecked until the specific result and revision are recorded here.

## October 5 complete-case build

The user reports the clasp trial has already been printed and requested the
full build. [`v18-case`](../v18-case/README.md) now integrates the selected
clasp, board snaps, retained drawers and a positively latched capstone hatch.
The complete first-print kit has five CC2 PLA projects, 12 printed parts,
three permanent steel hinge axles, reproducible source, actual-geometry
previews, current digital checks and local slicer reports.

The 180 mm field / 36 mm pitch remain. Current original Cat/Witch flats are
20 mm, so the new seats provide 0.35 mm nominal clearance per side. Axle
retaining caps remain outside the field. The full envelope with hardware is
143.5×245.8×32.6 mm. No compactness or physical success is claimed.

The original coupon bytes remain frozen. The first integrated build has its
own package manifest. See [V18_CHECKPOINT.md](V18_CHECKPOINT.md) and
[v18-case/ACCEPTANCE.md](../v18-case/ACCEPTANCE.md). Whole-case physical
acceptance remains unchecked; this is a complete first-print build.

## Release gates

- [ ] Coupon assembly and ten gentle cycles pass with removable supports,
  comfortable finger operation and no cracks, whitening, sticking or bolt loss.
- [ ] Press-only and drag-only actions remain held; record force, play and
  guard access. Follow the [coupon experiment](../v18-recessed-clasp/README.md).
- [x] Integrate the selected clasp, board snaps, drawer catches/releases and
  captured capstone hatch. Floor finger ports aid capstone retrieval; physical
  comfort remains a test.
- [x] Check actual original Cat/Witch CAD, solids, STEP/STL and 3MF readback,
  assembled clearances and sampled loaded fold/release paths. Motion is sampled,
  not a continuous sweep proof.
- [x] Export five full-case CC2 Generic PLA projects with retained exact starting
  profiles; inspect selected critical toolpath layers. Match the actual spool
  before printing. Support removal remains physically unverified.
- [ ] Verify physical hinge motion, finger access, loaded retention, repeated
  operation and transport behavior. Record component revisions and observations.
- [x] Pin first-print sources/exports/environment/profiles and provide the
  assembly guide and complete-case kit. Physical acceptance does not follow
  from this digital build.

The complete first-print kit is available in `v18-case/release`. The original
clasp coupon kit and its generic analysis profile remain retained historical
artifacts. Full-case material settings are starting assumptions; physical
operation and loaded transport still require observation.
