# Tak collaboration instructions

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
