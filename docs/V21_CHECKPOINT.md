# V21 checkpoint — October 5, 2026

Outcome: complete self-contained kit where the two boards also close storage. User explicitly authorized V21. Scope: remove separate lids and board hinges, retain the full 180 mm field, filament case hinge and side hook. Preserve V18–V20 and existing printed parts.

Route: short big-thinky design pass for hinge/rail/hook clearance, then bounded workhorse implementation and verification at medium effort. Role mapping read; current context retained without model switch or delegation. Usage counters unavailable.

Decision: boards slide outward in X, away from the centre seam. Only bases hinge, with three interleaved knuckles at each end and 14.9 mm main pins. The side hook moves to the front corner so it can park clear of both board paths without hanging below the table. Rear base/compartment shifts 2 mm for rail clearance. Board underside stays 0.4 mm above original flats. Front catches press 2.8 mm inward and sit outside the playing field. Boards print directly on their flat underside.

Current state: complete V21 geometry and four sliced full-build projects on codex/v21-sliding-boards. Eleven printed parts including five collars. All 52 geometry/mesh/piece/motion, 37 field, 29 hardware, 39 plate/readback and 16 filament-centerline checks pass. Selected layer sheets and actual STEP previews reviewed. Full-kit estimate: 45,289 seconds / 287.29 g; optional shortened rail/catch fixture: 3,587 seconds / 19.26 g. Maximum print height 25.8 mm.

Evidence: v21/reports, v21/previews, exported STEP/STL, named 3MF projects and embedded Gcode. Motion is sampled and flex poses do not establish release force or fatigue. Original Cat/Witch CAD is the target. Physical acceptance remains false; no printer job started.

Next: finish provenance, fresh ZIP extraction audit and draft PR. Earlier packages and user-extracted archives remain unchanged.
