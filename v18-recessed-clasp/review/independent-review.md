# Independent adversarial review: V18 recessed clasp coupon

**Verdict: conditionally suitable as an unprinted, support-required engineering coupon. No confirmed geometric blocker remains in the bounded checks below. This is not a demonstrated bag-safe closure or validated case mechanism.**

Reviewed final source SHA-256: `5f116585bd24d2ddfac74f463e62e62121bf2af9a84129f7541ff0c5430deadc`.

## Evidence and scope

Independent recreation from source, rigid Boolean intersection probes, prescribed leaf-deflection shapes, and visual inspection of the actual dry-slice layer plot. The full straight-axis suite was ultimately rerun on the final floor revision; `final-independent-probes.json` and `final-source-snapshot.py` match the final hash. The older pre-floor result is retained separately as `pre-floor-independent-probes.json`. `final-floor-targeted-probes.json` and `tilt-bypass-probes.json` also match the final hash. Original A files and V18 production geometry were not modified by this reviewer.

## Confirmed CAD findings

- Fixed receiver/bolt and moving +Z keeper are explicitly distinguished. Keeper shelf bears on the rigid bolt underside; rigid rails bear on the receiver roofs. The release leaf detents axial bolt travel rather than carrying the primary +Z opening load.
- The sampled nominal press, 0–10 mm retract, reverse press-and-slide closing, leaf return, and open keeper-lift paths have zero volume interference. Both opening and closing require pressing; no automatic snap-closing claim should be made.
- The relaxed tooth has positive axial shoulders. Unpressed retraction is blocked after the nominal 1 mm take-up. Even with the entire bolt dropped 0.4 mm onto its lower rail ledges, unpressed retraction remains blocked. Forward relaxed travel meets its catch after about 2 mm.
- Initial straight insertion from +X with the keeper absent and leaf pressed is clear across the sampled 0–70 mm forward offsets. Split cage end tabs preserve that assembly tunnel while retaining the keeper flange.
- Normal rearward travel is stopped at approximately 11 mm by the rigid rear wall. The 10 mm released position remains inside the guard footprint. Deliberate pressed forward disassembly with keeper removed remains possible: do not describe the slider as permanently captive.
- Keeper registration permits approximately 1 mm X/Y take-up, then encounters hard boundaries. The added floor permits 0.4 mm downward take-up and blocks a 0.5 mm drop (66 mm³ interference), eliminating the simple downward-drop escape route.
- A sampled diagonal escape hypothesis, keeper +X 1 mm then rear-up tilt about the bolt tip, encounters receiver interference from 2° onward. Later isolated non-interfering positions do not establish a reachable path through earlier collisions. This was a targeted test, not exhaustive pose-space verification.
- Keeper-to-bolt clearance is 0.4 mm and upward bolt-to-roof clearance is another 0.4 mm. Thus the ideal assembled opening take-up can total **0.8 mm** before the rigid load path engages.
- With the bolt floated upward 0.4 mm, nominal 1.8 mm prescribed leaf depression still gives zero volume interference at retract positions 0, 5, and 10 mm, but the critical detent clearance approaches zero. **Unload the keeper before release; reliable loaded release is not demonstrated.**
- The floor interrupts excessive prescribed leaf motion at approximately 2.13 mm nominal tip deflection; 2.12 mm is clear. With the bolt already at its lower 0.4 mm float limit, nominal 1.8 mm depression is at/near the floor. These are geometric stops, not proof that the beam cannot overstress.
- The relaxed button top is 1.7 mm below the 8.5 mm guard; even upward bolt float leaves about 1.3 mm recess. Locked and retracted moving parts stay within the guard's XY footprint. Narrow objects or soft fabric can still enter the recess and combine pressing with sliding; snag immunity is untested.

## Printing, fit, and durability limits

The provided Rx90 orientations require supports. Slider tooth/leaf and far-side receiver detents introduce early-layer islands or cantilevers. The actual dry-slice plot shows magenta support paths near those regions; this addresses the unsupported-island concern at the slicing level only. Open slots and ends offer potential removal access, but clean removal and lack of scarring on bearing/detent surfaces have not been demonstrated. All supports must be removed without damaging the leaf; residual material or cleanup can consume the 0.4 mm running gaps.

No printer/material-specific fit, measured actuation force, spring return, layer adhesion, creep, fatigue, impact, wear, temperature response, or bag/snag test exists. Nominal analytical force/strain estimates are not material validation. Sharp transitions and anisotropic printing remain stress-risk hypotheses. Do not print or deliver the generic analysis G-code as a printer-ready file.

## Failed A: bounded engagement diagnosis

Independent A probes found a nominal insertion route with both beams prescribed inward by 1.2 mm, so the original CAD is not proven intrinsically unassemblable. Its hooks spend roughly 30 mm travelling under deflection in the sleeve; vertical running clearance is only ±0.30 mm, and relaxed shoulder/window axial clearance is 0.30 mm. Square receiver entry edges, print-fit error, surface roughness, and long loaded sliding are plausible engagement problems. The supplied original tests omitted insertion and did not demonstrate self-camming force or print reliability. These are hypotheses from CAD, not a physical failure diagnosis; details are in `failed-A-independent-path-probes.json`.

## Use boundary

Proceed only as a small experimental coupon for checking assembly, cleanup, feel, positive engagement, and release before case integration. The bounded ideal-CAD review found no remaining blocker to that purpose. Stop if parts require force to fit, the tooth does not fully return, support cleanup damages the leaf, or retention/release behaves inconsistently. No physical success, guaranteed containment, or purse-safety claim is justified.
