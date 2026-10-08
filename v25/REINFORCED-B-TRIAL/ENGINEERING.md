# Reinforced B fixture: failure and evidence

## Physical observation and working choice

On October 7, the user reported that the fit coupons fell apart and confirmed the failure was in the thin sample body. They selected the middle fit, B, as the best working assumption. Fracture photographs, the precise printed kit, material settings and cycle/load measurements are unavailable. This is a reported fixture failure, not a demonstrated bearing or formed-head failure. Thin sample stock is a plausible contributor, not a proven exclusive cause.

The previous strength coupon floor was 2.2 mm thick. This trial adds 3.8 mm beneath that reference plane for a nominal 6 mm fixture floor. Running cuts clear the deeper backing; a continuous full-depth spine, 4 mm wide and 26 mm long, remains on each side. B labels are engraved instead of added above the tray plane. The backing is specific to the trial and does not prescribe a thicker production case.

The moving bore is Ø2.10 mm around Ø1.75 mm filament, with Ø1.95 mm fixed bores. Two 2.5 mm fixed bearings support the 3.2 mm moving bearing across 0.4 mm gaps. The barrel diameter, roots, local gussets and two Ø3.2 × 0.6 mm formed heads in Ø3.5 recesses match the prior strength design. Heat-forming uses the user's heated tool; the physical head quality and process setting remain unverified.

## Verification

The build compares actual bearing material inside the barrel envelope with the prior S2 source and verifies the fixture spines remain solid. It checks retention in both directions, raw-filament withdrawal without heads, sampled 0–180° folding at 2° increments, curved board samples and actual V24 whole-board/empty-tray clearance. It then checks CAD validity, STEP/STL readback, connected/watertight meshes, plate positions and geometry-only 3MF.

Reference parts are V24 revision 8085e9d79ffff3c69f07a1cca67595994237869e. The empty-tray and board checks do not load original Cat/Witch flats or flat capstones; no loaded-piece clearance is claimed. V24 and earlier print files are preserved. These samples do not retrofit printed V24 parts.

`reports/geometry.json` records the command, source hashes, dependency/platform versions and failures remain in `reports/build.log`. `slice.py` checks all four mesh readbacks, profiles and embedded G-code using installed ElegooSlicer 2.4.2. The inherited bed-temperature warning is retained explicitly, not removed from the report.

Six previews use actual exported STEP geometry. `package.py` verifies syntax, links, profile/source hashes, archive CRC and payload hashes. `reproduce.py` rebuilds from a fresh extraction and compares four STL surfaces and extents within 0.002 mm and volumes within 0.05 mm³. Digital passage does not establish physical durability.

## Reproduce

The archive has one `v25` root, shared CAD helpers, a retained prior-strength source for bearing parity checks, reference V24 sources and pinned dependencies in `requirements.txt`. From that `v25` directory:

```sh
python REINFORCED-B-TRIAL/source/build.py
python REINFORCED-B-TRIAL/source/render.py
```

The slicer entry point requires the installed ElegooSlicer and matching CC2/material profiles. The next evidence gate is the reinforced B physical cycle/pull trial, followed by a whole loaded case only after success. No physical acceptance, load rating, full-case integration or printer completion is claimed.
