# V26 mechanism review checkpoint

## Contract and route

Outcome: a reviewable wider sliding-board clip and captive side-hook candidate, with print-ready small trials and current CAD/mesh/3MF/motion/slicer evidence. Scope: new v26 package, controlling guides and focused branch/PR; preserve V25/V24 kits and user-extracted folders. Completion evidence is digital geometry, readbacks, actual CAD previews and dry slices. Physical strength is not inferred.

Route: bounded workhorse / medium in the existing execution context; maintained role mapping read. No model switch claimed; no agents. Named design uncertainty: captive-hook print support and collision-free motion. Resolved with targeted geometry checks before the integrated verification pass.

## Current state

Parent: c101d7d6585c363e23cf140f9059f38a96a8d6c8 on codex/v25-fixed-piece-guides (draft PR #35). V26 branch: codex/v26-captive-hook-catch. Thin-clip report confirmed by user as the small sliding-board clip. User explicitly asks for a PIP hook. Original 1.2 mm arm becomes 2.4 mm, gradual 3.2 mm root and 1.2 mm blend; same 54 mm plan span and assumed 2.8 mm flex travel. No stress, force or fatigue rating claimed.

The hook keeps its closure lever/tooth, enlarges its bearing to 11.6 mm outside diameter and prints parked on an integral foot. Fixed 4 mm axle, 2 mm outer cheek, 0.4 mm radial/face clearances. Existing filament passage is filled, avoiding an isolated internal void. A 7 mm rotating relief clears the foot; the 3.4 mm fixed lower frame bridge sits outside that sweep. Hook moves 0.4 mm inward; board notch extends from X5.7 to X6.2 outside the full field. Original keeper remains.

Rejected first hook fit had 0.454 mm3 overlap at 30 degrees and 0.908 mm3 at 90 degrees. The original export failed the single-component mesh check because the unfilled old pivot bore became an enclosed void (negative 14.763 mm3 inner shell). Neither rejected export is delivered as a print project. Failure records are retained. Final solid topology is checked before slicing.

Fixed guides, main PIP geometry, full field, exact original flat/capstone package and outside dimensions are retained. Both integrated bodies/boards require replacement; hook prints with the left body, no inserted axle or collar. Small trials isolate the hook bearing and complete clip; hook trial has a thickened fixture floor outside the moving envelope. Whole-case loaded strength and rounded-cover underside integration remain pending.

## Evidence and next step

Build: source/build.py; trials: source/trial.py; dry slice/readback: source/slice.py; actual CAD views: source/render.py. Python 3.12 / CadQuery 2.7 / ElegooSlicer 2.4.2 on the recorded host. Reports retain exact commands, profiles, hashes and failures. No printer dispatch or physical acceptance.

Next physical gate: cool and gently free the captive hook, pull along its axle both ways, inspect axle/cheeks after 20/100 cycles; insert/release the full-length clip by hand and inspect its root/effort after 20/100 cycles. Reject fused motion, cracks or excessive release effort. Complete-case print and loaded transport follow only after mechanism trial observations.

The parked lever has underside clearance outside the piece wells. A final audit rejected the original 0.173 mm lever-to-well-corner gap; the revised underside opening clears that region. The 3.4 mm stone floors and fixed guides remain intact.

Final digital evidence: 908 integrated solid, loaded-piece, slide/fold, capture, mesh and 3MF checks; 96 mechanism-trial checks; 51 exported material/clearance/keeper audits. The locked hook obstructs early opening at 179/178/177 degrees; that is nominal geometric retention, not a force rating. Own-body clearance is 0.4 mm through checked 0–90 degree hook travel. Eleven actual dry-sliced hook radial/face-gap and support-centerline checks pass, minimum sampled conservative 0.50 mm bead-edge gap 0.32 mm. Both trial projects preserve named watertight meshes within 0.002 mm surface / 0.05 mm3 volume tolerance. Four walls, 0.20 mm layers, build-plate-only supports, no brim, CC2 PLA; inherited bed metadata warning retained. Hook trial: 1,493 s / 4.93 g; clip trial: 2,537 s / 9.51 g. Seven actual CAD/path images reviewed with large captions and a clear longitudinal bearing section. Review still awaits physical prints; full sliced V26 kit and rounded-cover underside remain open.

Package evidence: all six preceding V25 ZIPs remain byte-identical. An isolated extraction of the V26 review rebuilt both small trials without the checkout; all four rebuilt STL surfaces and volumes match within the recorded tolerances. This does not claim an isolated full-CAD or slicer rebuild. Captions are composed in a separate PIL-only process to avoid dropped leading glyphs after repeated VTK renders. The V26 review is stacked on open draft PR #35; no merge or printer dispatch.

## Combined trial plate

User asks for both trials on one plate. Route: bounded workhorse / medium in the existing context, no model switch or agents. Scope: placement and grouping only; unchanged hook/clip geometry and individual projects. New source/combine.py imports the four actual exported STEP parts, moves both clip parts 32 mm in X, leaves the captive hook/mount unchanged and exports one assembly of four named meshes. Hook-to-clip spacing is 17 mm; all parts fit the CC2 bed. Nineteen placement, topology and 3MF checks pass. New combined slice receives the existing mesh/profile readback and eleven radial/face/support checks; physical acceptance remains unchecked. No complete-case geometry recheck is needed for unchanged parts.

Combined slice passed: 3,925 s / 13.92 g PLA; four named watertight mesh readbacks, preserved one-assembly placement and eleven hook bearing/support checks. Individual projects remain byte-identical to a1a9b2709323d74d3e68bea22fd73d9dbbc3133d. Combined CAD placement preview reviewed; package repacked. Physical strength and release remain pending.


## Board-release ergonomics assessment

User reports that pressing the sliding-board tab while pulling the board was very awkward. A thicker clip does not resolve that simultaneous action. Proposed next direction: remove the individual flex catches and restore solid board margins; let the opened case hook release both boards for withdrawal. User choice between this approach and a separate latch that stays released is pending. No geometry changed in this assessment, and the combined plate still contains the stronger flexible-clip candidate.

Route: bounded workhorse inspection in the existing context; no model switch or delegation. Source revision: eb1a114f773069a6a662d7f2cea9456f901bac51. Environment: existing CadQuery 2.7 / Python 3.12 CAD runtime. Command: import v26/source/build.py; for each side use board(side, c.BOARD_RELEASE), apply c.slide at 0, 1, 2, 3, 4, 5, 6, 8 mm, fold the right board 180 degrees, and measure ov against hook(0) and hook(90). The assumed released clip isolates the hook obstruction from the individual clip.

Results: both seated boards have zero hook overlap; at 1 mm withdrawal the closed hook overlaps left board by 6.416685 mm3 and folded right board by 5.085218 mm3. Closed-hook overlap remains positive at all checked 2–8 mm positions. The parked 90-degree hook has zero overlap with both boards at each checked position. This supports a candidate shared retention mechanism; it does not establish retention force, comfort, or unlatched board security. Full removal, loaded motion, restored-margin clearance, mesh/readback and physical handling must be checked after any geometry change. Existing sliced trials and ZIP remain unchanged.
