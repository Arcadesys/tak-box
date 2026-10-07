# V25 — filament hinges and rounded board relief

**Use ordinary 1.75 mm PLA filament as the axle. No pin or collar is printed.**

Open [the filament hinge and lip trial plate](PRINT/01-V25-hinge-lip-coupons-CC2-PLA.3mf) as a project in ElegooSlicer. Select the actual PLA profile and reslice. This is a local mechanism experiment, not a replacement case or a drop-in V24 part.

The user selected filament because their earlier filament hinge worked well, while printed pins broke or did not hold the assembly firmly. They also selected the rounded underside treatment they remember from V17. Two board-edge samples replace V24's square corner cut with curved underside clearance, outside the playing field. The complete flat 180 × 180 mm, 5×5 field remains required.

The plate has **14 printed parts**: three hinge pairs, two shared rounded board-edge samples, and three board/lip seats. Cut three filament axles; do not print them. H1–H3 and L1–L3 are marked on the fixtures. The two shared board-edge samples work with any H pair; the left sample has its grid line near the outside edge.

| Mark | Fit or blade | Nominal dimensions |
| --- | --- | --- |
| H1 | Tight filament fit | 1.75 mm filament / 1.95 mm bore; 0.20 mm diametral clearance |
| H2 | Middle filament fit | 1.75 mm filament / 2.10 mm bore; 0.35 mm diametral clearance |
| H3 | Free filament fit | 1.75 mm filament / 2.25 mm bore; 0.50 mm diametral clearance |
| L1 | More compliant lip | 28 mm wide × 12 mm free length × 0.80 mm thick |
| L2 | Middle lip | Same width and length; 1.00 mm thick |
| L3 | Stiffer lip | Same width and length; 1.20 mm thick |

Start with **H2 and L2**. Use ordinary PLA, one spool for all printed variants, a 0.4 mm nozzle, 0.20 mm layers, four walls and 20% gyroid. Keep the supplied orientations and avoid hole compensation during the comparison. Local supports and 2 mm brims are included. The verified slice estimates **2 h 55 min / 36.5 g**. This is not a measured print result.

## Assemble the filament hinge

1. Let the parts cool. Clip the brims and remove support in small pieces while holding the thick fixture. Clear each bore gently from its open end. The left bore has a blind end: do not push a drill or support tool through it. Remove strings and burrs only during the first comparison.
2. Choose a straight length of ordinary 1.75 mm PLA filament. Measure its diameter if possible. Cut each coupon axle square to **5.4 mm nominal length**. The fitted axle sits flush at the moving-barrel mouth and bottoms against the 0.5 mm blind wall. Trim if an imperfect cut prevents full seating; record the actual length. These short lengths apply only to this coupon, not a complete case.
3. Dry-fit the filament through the right moving barrel into the left fixed barrel. Check rotation and side rock before adding adhesive. The blind wall stops inward travel; **the unbonded filament can still slide out**. Do not call that temporary fit transport-safe.
4. Remove the moving half. Bond only the last **2.2 mm** of filament into the fixed left barrel with a minimal amount of PLA-compatible adhesive, following its cure instructions. Keep the exposed axle and rotating right bore clean. Let the bond cure fully before reassembly. Do not flood adhesive through an assembled hinge.
5. Slide the moving half over the cured exposed axle. Confirm full flat opening and 180° closing. Try the two shared board-edge samples in their matching positions; their curved cutouts clear the moving support. They rest on the fixtures for comparison and are not latched board replacements.

Bond quality, filament straightness and actual printed bores determine retention and play. Filament is the selected approach based on the user's prior physical experience; this new joint still needs its own tests. A complete case will require front and rear stations and a repeatable assembly sequence.

## Clean and assemble the lip

Hold the thick board body while removing support through the far-edge opening of the recessed flex pocket. Avoid levering on the catch. Stop on whitening, cracks or a fused blade. Slide each L board inward until the wide shoulder catches. Lift the blade about 0.65 mm to release, then slide outward; do not pry the whole board off.

The broad underside blade has a 27 mm catch shoulder and 0.4 mm engagement. Its top remains flat. The short fixture guides test transverse restraint; they are not V24's full rails. Full-case integration proposes raising each board and the hinge axis by 1 mm, for **37 mm total thickness**, 2 mm above V24. Taller rails, full catches and the hook still need integration. The existing side hook remains the intended backup.

## Compare firmness and retention

Record results in [TEST-SHEET.csv](TEST-SHEET.csv). The user reports V24 felt very loose and barely held together, so easy rotation alone is not acceptance.

- **Hinges:** compare binding, rocking, twisting and axial play at assembly, 20 cycles and 100 cycles. Mark the filament at the bore mouth. Pull along the axle in both directions after cure and check for migration or bond failure. Record actual force if measured. Select the tightest bore that rotates freely after cleanup and cycling.
- **Rounded board samples:** open and close the hinge with both samples seated. Record contact, lift, snagging or cracks. The samples test local clearance; they do not establish full-board retention or full-case stiffness.
- **Lips:** latch and release 20 times, then 100 times. Record positive engagement, comfortable release, permanent bend, whitening and cracks. Pull outward and vertically, push sideways in both directions, then try a gentle diagonal pull with the blade unpressed. Deliberate release must still allow complete withdrawal.
- **Repeat:** leave unloaded overnight and check again. Preserve failed specimens and record their orientation. PLA creep and fatigue remain unverified. Use ordinary PLA for the mechanical comparison.

## Evidence and limits

[Print layout](previews/05-print-plate.png) · [Rounded board relief](previews/07-rounded-board-relief.png) · [Open hinge](previews/01-hinge-open.png) · [Closed hinge](previews/02-hinge-closed.png) · [Hinge section](previews/06-hinge-section.png) · [Lip](previews/03-lip.png) · [Lip section](previews/04-lip-section.png).

These views come from exported CAD. The filament is reference hardware in assembled STEP views; it is excluded from every printable STL and 3MF. [Geometry](reports/geometry.json), [slicing](reports/slicing.json) and [engineering](ENGINEERING.md) distinguish completed digital checks from physical work. Individual oriented STLs and STEP files are in `models`; [the geometry-only plate](plates/01-V25-hinge-lip-coupons.3mf) carries no qualified printer settings.

The hinge axis is still above the inward-folding faces. Rounded underside clearance does not establish a fully concealed underside hinge. A full-case assembly, loaded retention, adhesive durability, lip fatigue and purse carry remain untested. V24 and the earlier printed-pin coupon kit are preserved. No printer job was sent.
