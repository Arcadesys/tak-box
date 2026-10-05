# Tak collaboration instructions

## Start here

Read README.md, docs/TAK_PROJECT_BRIEF.md, CODEX.md, the affected package README, and any more specific instructions in that package. The user explicitly advanced the current hook-and-pin case to v19 on October 5 to provide a single clear print package. Read v19/START-HERE.md, v19/BUILD-PROVENANCE.md and docs/V19_CHECKPOINT.md. V19 preserves the checked side-hook geometry, 1.75 mm filament hinges, four-leaf common axis and full field; it is a version/package cleanup, not a new physical-fit result. The five current CC2 projects are in v19/PRINT. The ZIP contains only one v19 folder, with necessary source dependencies under source/vendor. Earlier v18 packages and docs/V18-FREEZE.json remain historical and intact. V16 remains the printed baseline; the premium pagoda is separate.

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
