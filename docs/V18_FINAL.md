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
A complete integrated v18 case and its final plates have yet to be produced.

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

**Final direction selected; complete-case release pending.** Keep each gate
unchecked until the specific result and revision are recorded here.

## Release gates

- [ ] Coupon assembly and ten gentle cycles pass with removable supports,
  comfortable finger operation and no cracks, whitening, sticking or bolt loss.
- [ ] Press-only and drag-only actions remain held; record force, play and
  guard access. Follow the [coupon experiment](../v18-recessed-clasp/README.md).
- [ ] Integrate the selected clasp into the case; finish board snaps, drawer
  catches/releases and rear capstone hatch while preserving retrieval access.
- [ ] Check actual piece geometry, solids, exported meshes, 3MF readback,
  assembled clearances and full opening/repacking motion for the integrated case.
- [ ] Export the complete v18 parts and plates with exact printer/material
  profiles; inspect critical layers, supports and removal access in the slicer.
- [ ] Verify physical hinge motion, finger access, loaded retention, repeated
  operation and transport behavior. Record component revisions and observations.
- [ ] Pin the accepted integrated sources, exports, build environment and
  printer profiles; produce the final assembly guide and complete-case kit.

Until these gates pass, the available downloadable kit is the clasp coupon kit.
The generic analysis profile is not a machine-ready printer profile.
