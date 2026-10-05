# V18 recovery checkpoint

Recovered the complete saved V18 coupon kit on October 4, 2026 (Chicago).
The original archive is retained in `release/tak-v18-recessed-clasp-coupon-kit.zip`;
its contents are expanded here for review and reproducible development.

Import verification performed during recovery:
- ZIP CRC verification passed.
- All 67 entries in `PACKAGE-MANIFEST.json` matched byte counts and SHA-256 hashes.
- The separately saved 3MF and release-sequence image matched the corresponding kit files byte for byte.
- All recovered Python sources parsed successfully.

No geometry was modified and no CAD rebuild, slice, or physical test was performed
during this import. The included CAD, path, review and slicing reports are retained
prior evidence, not newly executed results.

V18 is an unprinted, support-required recessed press-and-slide clasp coupon.
It is not integrated into the v17 case. Physical fit, support removal, strength,
fatigue and loaded transport retention remain unverified. See README.md and
review/review-verdict.json for the recorded limitations and first-print trial.
