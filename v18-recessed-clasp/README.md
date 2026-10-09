# V18 — recessed press-and-slide clasp

**Unprinted mechanical test coupon. Not a finished case or proven purse-safe clasp. V17 is unchanged.**

The blue receiver stays on the case base. The teal keeper represents the lifting case half. The gold rigid bolt slides over the keeper's lower shelf. The thin gold spring only controls the bolt's motion; the keeper's opening load goes through rigid bolt/rail/receiver shoulders.

## Operation
1. To assemble the separate printed parts, leave the keeper out, depress the gold button, and insert the bolt from the open right-hand end of the receiver. The cage has an assembly tunnel between its end tabs. Move to the left/open position and release the button.
2. Lower the keeper into the right-hand registration cage. Press the button, slide right into the locked bay, and release. Gently pull the keeper upward to check engagement. **Closing also requires pressing**; this deliberately avoids an easy-camming front face that could let the bolt escape.
3. To open, first let the keeper rest down to unload the bolt; press the recessed button approximately 2 mm and maintain pressure while sliding left 10 mm. Release, then lift the keeper.
4. Pressing alone leaves the keeper blocked. Pulling/dragging the bolt alone encounters square shoulders. A narrow object that simultaneously presses and drags can still operate it; the guard reduces exposure but is not a lock.

The button is 1.7 mm below the guard in the nominal locked position. The retracted bolt is within the receiver outline, rather than sticking out during play. These statements describe this coupon; integrating the mechanism into a flat 5×5 case for the actual 44 pieces remains later work.

## What is included
- `plate/tak-v18-recessed-clasp.3mf`: three separate parts arranged on one plate, millimetres, no printer profile or G-code
- `parts/*.stl` and `*.step`: separate side-oriented parts; `*-assembled.*` preserve mating coordinates
- `parts/assembly.step`: complete locked nominal CAD assembly
- `states/`: four explicit assembled CAD states, including the assumed flexed leaf geometry
- `renders/`: full and sectioned views made directly from those CAD solids
- `build.py`, `package_plate.py`, `render.py`: reproducible sources
- `checks.json`, `review/`: calculated path checks and independent review

## Dimensions and assumptions
- Assembled coupon envelope: 78 × 40 × 10.1 mm
- Bolt-to-keeper overlap: 4 mm nominal; alignment play reduces this, so it is not a guaranteed minimum
- Intentional slide: 10 mm
- Leaf: 22 mm long × 12 mm wide × 1.6 mm thick
- Prescribed leaf-tip deflection: 1.8 mm; centre-button movement about 2.05 mm because of tip rotation
- Keeper-to-bolt gap: 0.4 mm; additional bolt-to-roof gap 0.4 mm gives approximately 0.8 mm vertical take-up before firm bearing
- Rail top and bottom gaps: 0.4 mm each
- The ideal small-deflection beam estimate at an assumed 2 GPa modulus is about 4.15 N and 0.89% root strain. These are **assumptions, not measured force, FEA, fatigue qualification, or a material allowables check**. Printed PLA is orientation-, brand-, temperature-, and process-dependent.

## Digital verification
- All three exported parts are single CAD solids; STL boundary/non-manifold edge check passes.
- PrusaSlicer 2.9.2 imports the three 3MF objects as manifold, one connected part each (`plate/slicer-import.txt`).
- Sampled press path (0–1.8 mm), held-down slide (0–10 mm), assembly insertion, and open keeper lift show zero unintended Boolean overlap.
- Locked bolt retraction and keeper lift encounter positive solid overlap after designed clearance is taken up. Press-only keeper lift remains blocked.
- The CAD deformation uses an assumed cubic cantilever curve. Boolean checks establish nominal geometric compatibility, not that real printed plastic follows that curve.
- Independent review tested additional bypasses and identified revisions, with residual issues in `review/`.
- The support-enabled dry slice completed without warnings. Selected actual toolpath layers were visually inspected (`slicing/layer-inspection.png`); model and support are distinct, and the deposition envelope fits a 200 × 200 mm bed. Support interfaces exist at the floating tabs/leaf. Removal access is available from the open receiver slot/ends and around the separate slider, but removal without surface damage is not physically verified. The complete assembly is not printed in place, so mating gaps are not deliberately filled with support. The final revision includes a floor beneath the keeper to stop downward escape before withdrawal.

## Printing: support-required trial, not a validated print profile
The 3MF uses a side orientation (90° about X) to keep the cantilever length in the layer plane. **Supports are required.** Receiver tabs begin as islands; the slider tooth wing and long leaf also need support in this orientation. Support-removal scars on bearing/leaf surfaces can ruin the intended clearance or initiate cracks. Do not assume this plate is support-free or ready to start printing.

Choose your actual printer and PLA profile, inspect every layer around the tooth and tabs, and arrange removable supports before printing. A 0.4 mm nozzle and 0.2 mm layers with at least four walls are a starting assumption, not calibration. Confirm the leaf is resolved as a continuous wall section, the support interface is accessible, and no island is unsupported. Do not scale the model to tune fit. A local analysis-only dry slice was performed, and its temporary machine code is excluded from the deliverables. No printer was started; no strength or physical fit test was performed. The generic estimate is 23.92 g total PLA (18.04 g model, 5.45 g supports, 0.44 g brim) and 2h 21m 17s. Actual printer results will differ.

## Small first-print experiment
Print only this coupon first. Remove supports carefully; inspect the leaf root and square shoulder corners for cracks/whitening. Do not force a jammed part. Verify assembly with the button pressed, then ten gentle close/open cycles. Check that a straight upward keeper pull stays held with the button untouched and with the button pressed but not slid. Verify a plain drag cannot slide the bolt past its detent. Check that a broad flat object over the guard does not press the button. Measure actual press effort, drag force, vertical play, and any support scars. Stop if it takes a tool, leaves whitening, cracks, sticks down, sheds the bolt, or releases without the two-part motion. A later cycle/loaded-bag test is still needed before relying on it for travel.

## Why this is different from the failed A buckle
A required two side beams to remain squeezed while travelling roughly 31 mm through tight guides, with only about 0.3 mm nominal vertical and final axial clearances and no generous entry funnel. Independent CAD probes found an ideal insertion path, so the actual print's failure cause is not proved. V18 instead separates rigid load-bearing rails from one visible, recessed press leaf and checks the complete commanded assembly/release path. That removes the specific long dual-side squeeze action; it does not guarantee the new print will fit.

No screws, purchases, or printer commands. No changes to earlier versions.
