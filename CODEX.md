# Working on Tak with Codex

Repository: https://github.com/Arcadesys/tak-box
Research: https://chatgpt.com/space/page_1a04af571ecc8191817d9c547cde56ff
Space hub: https://chatgpt.com/space/page_6abdc060969481918381b94ad91155e8

## Session entry

Select Arcadesys/tak-box in a Codex checkout/environment. Read AGENTS.md and docs/TAK_PROJECT_BRIEF.md. Start from the current main branch and create a focused working branch before geometry edits.

The connected GitHub app can read and write this private repo. A repository link in a Page does not mount a checkout or configure a Codex cloud environment. This setup adds durable instructions and source links; it does not attest to a configured cloud runtime.

## Runtime

This is a Python/CadQuery CAD project. Use package-specific dependency files:
- Weighted stones: pieces/weighted-v1/requirements.txt
- Fox/Cat: pieces/fox-cat-capstones-v4/source/requirements.txt

Follow their README environment commands. For v16, inspect imports in v16-field-book/source and install its requirements in an isolated environment; no v16-field-book/requirements.txt was present during this setup. Do not assume OpenSCAD is the build system. ElegooSlicer is needed for slicing/packaging; some render scripts depend on VTK and macOS fonts/paths.

Existing v16 commands:
```sh
python v16-field-book/source/build_all.py --only verify_book
python v16-field-book/source/build_all.py --only verify_meshes
python v16-field-book/source/build_all.py
```

These are existing source entry points, not newly validated execution results. Run build_models first when generated geometry is missing or changed. Read reports and distinguish source checks from stale retained artifacts.

## First useful task

Read issue #18, reconcile which v16 parts have actually been printed, and propose the smallest stiffness/retention trial that preserves the current assembly. For the luxury direction, first produce a separate spill-free motion study; confirm hinge axes, lid order and how the pieces stay supported before detailed geometry.

## Suggested Page prompt

Work in Arcadesys/tak-box. Read AGENTS.md, CODEX.md, docs/TAK_PROJECT_BRIEF.md, the v16 README and issue #18. Summarize the current printed-part status and propose the next small verification or fit trial. Keep the luxury hinged-well design separate from the v16 baseline. For any requested implementation, use a focused branch and PR and report checks actually run.
