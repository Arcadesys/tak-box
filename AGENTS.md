# Tak collaboration instructions

## Current V26 main-hinge correction

The user identifies the current main hinge as different from the captive mechanism discussed. The delivered case plate uses older opposing single-ended peg/socket stations; only the side hook uses an axle between two fixed supports. Clarify and implement the intended main hinge, keeping the tab-free board release. Existing full-kit files are a prior snapshot pending correction; do not describe them as the corrected captive design. Read the latest docs/V26_CHECKPOINT.md entry before further CAD changes.

The user explicitly approves shared case-hook retention, removes the awkward flexible sliding-board tabs and asks to build the full plates without waiting for small physical trials. Read v26/START-HERE.md, v26/README.md and docs/V26_CHECKPOINT.md. Preserve PIP main hinges, fixed integral guides, no removable trays, full playing field, original inlays and flat-piece package. Rigid seating shoulders stop inward board travel; the opened case hook permits outward withdrawal. Keep the 4 mm captive hook axle and 0.4 mm gaps. Physical strength, handling, loaded retention and rounded-cover underside integration remain unchecked. Preserve all V25 packages, the prior V26 mechanism-review ZIP, user-extracted folders and V24. Do not dispatch printer jobs.

## Preserved version: V24

Read v24/START-HERE.md, v24/BUILD-PROVENANCE.md and docs/V24_CHECKPOINT.md first for the reinforced-hinge/removable-tray revision. The user reports a baseline V23 hinge-support break; the exact failure mechanism is unknown. V24 has a 102.5×200×35 mm envelope, full-height 8 mm supports, captive 4 mm pivots and two loaded lift-out trays. Physical V24 acceptance remains pending. Preserve the original v23 source/kit and its separate board-inlay work; V24 is a distinct package and focused draft review. The user explicitly named the completed V23 R2 revision V24; no geometry/profile/print change is implied. Read v24/reports/identity.json to bridge the preserved 238 checks and six slices, which retain historical labels. Preserve the v23-r2 kit too. Historical text below describes the retained baseline.

## Start here

Read README.md, docs/TAK_PROJECT_BRIEF.md, CODEX.md, v23/START-HERE.md, v23/BUILD-PROVENANCE.md and docs/V23_CHECKPOINT.md. The user named the accepted seamless exterior **V23**: centered fully recessed side hook/catch/pivot, offset recessed board grips and rounded integrated captive-hinge ends. This is an identity-only migration of geometry 4859c9c / artifact 19b8773. Keep 101×200×32.6 mm closed size, the full 180 mm field, original 42 20×20×8 mm flats and the supplied solid flat capstones. Both bases print together as one assembly; the only inserted filament pin is the 8.6 mm hook pivot. Use v23/release/tak-v23-print-kit.zip, with three projects under v23/PRINT. Physical acceptance remains unobserved.

V22 source and guide are restored from 02f8a09 to the original corner-hook design (111.8×220.2×32.6 mm). Preserve its ZIP and all 94 manifest payloads unchanged. The previous seamless ZIP is recoverable under v22/release/archive/tak-v22-seamless-before-v23.zip. V23's accepted CAD/motion/slice receipts retain historical V22 labels; identity equivalence and current hashes are in v23/reports/identity.json and provenance.json. Preserve V18–V21, printed V16 parts, user-extracted directories and the separate premium pagoda.

## Design priorities

- Preserve 5×5 playability and finger room around loaded stacks. Do not shrink the board merely to make the case compact.
- Prioritize tactile usability: easy grasp, stable stacks, distinguishable capstones, comfortable release and quiet transport.
- Keep closed storage secure and demonstrate spill-free opening/repacking.
- Keep the current weighted-stone/current-insert mismatch explicit.
- Simplify mechanisms and use small fit trials before expensive complete prints.
- Dimensions are millimetres. Identify the exact piece package used in every clearance check.

## Work and evidence

- Inspect current sources and reports before editing; repository history and actual print observations supersede older chat summaries.
- Preserve existing printed parts and archives. Put broad concept redesigns in a new package/branch.
- For geometry changes, run affected solid, clearance/motion, mesh and 3MF readback checks; regenerate previews from actual exported geometry.
- Run slicer checks only where the installed slicer/profile supports them. Report unavailable steps plainly.
- Record command, dependency environment, source revision, outputs and failures. Never describe a render or digital fit as a successful physical test.
- Reconcile contradictory print status with component-specific records. Keep physical acceptance unchecked until observed.
- Retain reproducible CAD/source, units, named objects, profiles and dependency provenance with deliverables.
- Do not initiate printer jobs, paid generation, or publish private assets unless requested.
- Use a focused branch and pull request for future geometry changes. Include what changed, compatibility with printed parts, checks run, and the next small physical trial.

## Communication

Explain the result in short concrete steps. Lead with the next useful action or key fit failure. Keep proposed choices and confirmed measurements distinct. Update the project brief when decisions change.
