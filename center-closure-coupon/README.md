# Historical v5-only center correction

**Not compatible with the printed v7 wings. Use [the v7 replacement](../center-closure-v7/README.md), which has circular feet and the active PLA settings.**

The revised center fills the closed case above the existing wing bodies. Only the center's outer shell changes. This package targets the filament-pin board on `main` at `7bc9059`; it does not include the wing narrowing proposed in the separate PR #5.

## What changed

- The underside skin extends 3.6 mm below the original slab. The 4 mm gap above the folded wing bodies becomes 0.4 mm.
- Each end skirt grows from 2.0 to 2.1 mm thick and from 37.0 to 40.2 mm across. Its gap to the wing body becomes 0.4 mm.
- Circular relief follows the existing hinge axes at radius 2.9 mm: a 2.5 mm barrel plus 0.4 mm clearance. This is the circular interface in the repository model; the photo is not a calibrated dimension source.
- The bottom of the feet stays at Z = −20.1 mm, level with both wing floors.
- Wings, lids, playing face, hinge centers, knuckles, and 1.90 / 2.20 / 1.70 mm holes are unchanged.

## Coupon files and assembly

Print all five `coupon-*.stl` files separately, at 100% scale. They are already oriented on the bed: center and lid strips face down, wings bottom down. Use the established PETG board settings; supports should come from the build plate only and must not fill the pin bores.

The coupon is a 30 mm slice along the hinge axis at one end of the board, including both main hinges and 30 mm of each wing. Its five parts contain 36.7 cm³ of solid CAD volume in total. Actual material and time depend on slicing, infill and supports; this package is not pre-sliced.

1. Arrange the center between wing 0 (A) and wing 2 (B), with the playing faces in the same plane. Match the alternating knuckles rather than guessing from the print-bed layout.
2. Thread two pieces of 1.75 mm filament through the main hinges. Start with approximately 26 mm per pin and trim as needed; each pin must span both knuckles. No plugs are needed for this temporary fit check.
3. Seat each loose lid strip on its matching wing. The coupon ends before the outer lid hinges, so these strips are held by hand or removable tape during the check.
4. Fold both wings through 0–90°. Check for free movement and an even narrow gap above each folded wing and beside the end skirt. Use a 0.3–0.5 mm feeler gauge if available. Do not force a bind.
5. Check that the center foot and wing floors sit on the same flat surface when open. `coupon-closed.step` shows the intended folded arrangement.

The full center is `center-row-revised.stl` (or editable-solid `center-row-revised.step`). Print it only after the coupon fits. Reuse the existing full wings and lids. The old repository center STL and old plate 80 do not contain this correction.

## Verification

Verified with CadQuery 2.5.2 / OCP 7.7.2:

- Eight regression tests pass, covering the roof gap, both end skirts, circular relief, alternating knuckles, real bore sizes, filament paths, valid solids, resting plane and coupon construction.
- Both wings and lids clear the center through 0–90° in 5° samples; the added skirt stays at least 0.3 mm away. Both closed skirt-to-wing distances measure 0.4 mm.
- Existing full-board checks pass: main folds, opposing wings, lid motion and overlays, and all four filament paths.
- Before/after solid comparisons find zero changed volume in both wings, both lids, the playing slab and main hinge regions. The old center fails the new roof-fill and end-skirt tests.
- All six printable STLs have positive volume and two faces per mesh edge; each rests at Z = 0 in its print orientation.

See the measurement JSON files and test logs for receipts. The before/after image is a measured section through the CAD, not a photograph or a physical-fit claim. **The revised parts have not been printed or physically fitted.**

## Reproduce from the repository

Use a Python environment with CadQuery. The export has no slicer dependency.

```sh
python -m unittest -v test_center_leaf_fit
python export_pin_board.py --check-only
python export_center_closure_coupon.py --output-dir center-closure-coupon
```
