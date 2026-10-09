# Piece Generator v1

A reusable CadQuery generator for custom weighted Tak teams. A TOML preset
controls the regular stone, recessed engraving, subtractive side texture,
ballast volume, positive snap closure and a low-profile capstone.

This package is a new design surface. It does **not** replace
`weighted-v1`, `fox-knurled-v1` or any printed piece set.

## Design invariants

- Regular default envelope: **20 × 20 × 6 mm**.
- Regular pieces remain flat on both stacking faces.
- Engraving is subtractive and may not penetrate the ballast roof.
- Texture is subtractive and restricted to side faces.
- Ballast cavity width is solved from `target_fill_ml`, then capped by
  minimum side-wall and closure geometry.
- Every weighted piece uses a **positive mechanical snap floor plus adhesive**.
  Glue is the seal/reinforcement layer, not the only retention mechanism.
- The capstone is intentionally low and flat, but must remain tactilely
  distinct by profile and/or height.
- CAD verification is not physical acceptance. Print the closure coupon first.

The default regular piece targets about **0.90 mL usable ballast volume**.
With the current 20 mm × 6 mm geometry and 0.4 mm engraving, the solver may
cap this very slightly to preserve the 1.2 mm side wall. The actual generated
volume is written to the verification report.

## Positive closure

The floor has two opposing in-plane cantilever arms cut into its perimeter.
Each arm carries a wedge hook. During one-time assembly the insertion ramp
deflects the arm inward; once seated, the hook springs into a pocket cut into
the body rabbet.

This gives three lines of defense:

1. the rabbet/locating tongue carries lateral loads;
2. snap hooks resist floor pull-out;
3. adhesive seals the seam, immobilizes ballast and reinforces the assembly.

The snap is deliberately a **one-time assembly feature**, not a service hatch.

The builder generates a three-variant closure coupon with 0.20, 0.25 and
0.30 mm nominal hook engagement. Dry-snap these before committing a full set.
Accept a variant only if the floor seats flush with a clean click, the arms do
not crack, and ordinary finger pull cannot release it. Destructive removal is
acceptable for the coupon.

## Preset surface

Copy `presets/example-cat.toml` and change only the parameters you care about.

Engraving kinds:

- `none`
- `text`
- `builtin` with `cat` or `witch`
- `dxf` using a package-relative DXF file

Texture kinds:

- `none`
- `vertical_ribs`
- `diagonal`
- `diamond`

Capstone shapes:

- `octagon` (recommended default)
- `round`
- `clipped_square`

A preset describes one Tak team: 21 regular pieces plus one capstone. Make a
second preset for the opposing team. Mirroring diagonal texture angle is an
easy tactile team distinction.

## Build

From the repository root:

```sh
python -m venv .venv
.venv/bin/pip install -r pieces/piece-generator-v1/requirements.txt
.venv/bin/python pieces/piece-generator-v1/source/build.py \
  pieces/piece-generator-v1/presets/example-cat.toml
```

Outputs are written under this package:

```text
models/<preset>/
  stone-body.stl
  stone-body.step
  stone-floor.stl
  stone-floor.step
  capstone-body.stl
  capstone-body.step
  capstone-floor.stl
  capstone-floor.step
  coupon-*.stl
  coupon-*.step

plates/
  <preset>-complete-set.3mf
  <preset>-closure-fit-coupon.3mf

reports/
  <preset>-verification.json
```

Bodies are exported in print orientation with the broad engraved face down and
the ballast opening up. Floors print separately.

## Verification

The build fails on:

- invalid or multi-solid printable geometry;
- body/floor volume collision in the assembled pose;
- wrong exterior envelope;
- stack overlap;
- standing-wall envelope failure;
- minimum side-wall violation;
- minimum roof-under-engraving violation;
- invalid snap parameter ranges;
- non-watertight exported meshes;
- 3MF readback mismatch;
- insufficient capstone distinction.

The report keeps physical fields false until observed. In particular, CAD
cannot prove snap feel, fatigue, adhesive performance, cured ballast mass,
sound or stack handling.

## First physical trial

Print only the generated closure coupon first.

After choosing a snap fit, print one regular body + floor, load it to the
desired **7–8 g finished mass**, bond the ballast, snap the floor closed with
adhesive, and test stack separation, standing-wall stability, rattle and sound
before making all 42 regular pieces.
