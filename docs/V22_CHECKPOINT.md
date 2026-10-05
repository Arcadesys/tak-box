# V22 checkpoint — October 5, 2026

Outcome: separate reproducible kit with sliding boards and print-in-place main folding hinges. User explicitly selected V22. Preserve V18–V21 and existing printed parts. Completion evidence: solid, clearance/motion, mesh, 3MF, actual slicer/toolpath and fresh-package checks, rendered previews, draft PR. Physical acceptance stays unobserved.

Route: short design pass for captive-hinge motion and printable placement; bounded implementation and verification follow at workhorse/medium scope. Role mapping read; no model switch or delegation claimed. Usage counters unavailable.

Design: adapt V16 opposed printed pivots (3 mm diameter, 0.4 mm radial/face clearance, tapered tips and blind sockets) to the ends of V21's two bases. Both bases print together flat. Boards, hatch and hook retain their shapes. Hatch and hook retain filament pivots; main pins and their two collars are removed. Supports must stay out of captive joints and brims must not join the centre seam.

Current: thin-body hinge candidate complete; no V22 release ZIP yet. User rejected a deeper box. Awaiting selection among (1) folding standee capstones, (2) one-piece flat capstones, (3) existing sculpted capstones/rear compartment. Recommendation given: option 2. Do not treat the default async choice as an answer. Current geometry preserves option 3 provisionally; no capstone redesign performed.

Evidence: 52 geometry, 37 field, 15 hardware, 25 plate, 8 filament-core and 32 captive-hinge checks pass. Three slices and selected layers reviewed. Full candidate 43,798 seconds / 283.80 g. Optional actual-section hinge pair: 8 checks, 1,290 seconds / 3.80 g. Captive radial gap samples with 0.50 mm bead assumption measure 0.385–0.422 mm. Physical acceptance remains false.

Resolved: slicer requires the interlocking bases grouped as one assembly; two distinct parts and their relative world positions survive readback. A brief deeper-box experiment was reverted after the user's correction. Earlier V18–V21 packages and user-extracted copies remain untouched.

Next: resolve capstone choice, implement only the selected storage/piece changes, rerun affected checks, then finalize single-root package and PR. No printer job started.
