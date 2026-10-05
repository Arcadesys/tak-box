# Tak collaboration instructions

## Start here

Read README.md, docs/TAK_PROJECT_BRIEF.md, CODEX.md, the affected package README, and any more specific instructions in that package. The user selected v18 as the FINAL version. Read docs/V18_FINAL.md and docs/V18-FREEZE.json. The selected clasp is v18-recessed-clasp; the case-body baseline is v17-four-leaf, with all four main leaves sharing one hinge axis. Keep completion work within v18; reopening the version or direction requires an explicit user decision. The complete first-print build is in v18-case; read its README and current reports. The original v17 body remains a motion-study baseline. Physical acceptance of the integrated v18 case remains pending. Screw-clamped storage and pin/sleeve closure were rejected; v16-field-book remains the printed baseline. The premium pagoda is separate.

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
