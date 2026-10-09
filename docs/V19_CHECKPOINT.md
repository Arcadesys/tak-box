# V19 checkpoint — October 5, 2026

Outcome: deliver one unambiguous v19 print kit with one root folder and five current projects in PRINT. Scope: version/package cleanup of the checked side-hook build at `1e8944b`; no geometry or print-setting changes. The user explicitly authorized v19 after finding multiple version folders in the previous ZIP.

Route: one bounded workhorse pass, medium effort, for dependency relocation, packaging and focused verification. Role mapping read; existing desktop context retained. No model switch or delegation is claimed. Usage counters unavailable.

Current state: v19/START-HERE.md provides the assembly guide; v19/PRINT has the five CC2 PLA projects. Reproducible sources and minimal body/piece dependencies live inside v19. Older complete versions, coupons and archives remain outside its ZIP. Original v18 package bytes and user-extracted folders stay untouched.

Evidence: original print projects, CAD exports, profiles and inherited reports compared by SHA-256; case geometry functions compared by AST; standalone source imports and current version-labelled renders checked. The packager verifies a single v19 root, five PRINT files, no nested ZIPs/old version folders, CRC and payload hashes. The extracted kit is independently checked by verify_package.py. Details are in v19/reports/version-migration.json and BUILD-PROVENANCE.md.

Blocker: none for packaging. Physical fit and retention remain untested. Next action: use the v19 ZIP, open START-HERE.md, then print the five files in PRINT. No new printer job was started.

Existing draft PR #24 carries the full build and this cleanup; it remains based on recovery PR #23. The original v16 plate modification and all extracted v18 folders are outside this change.
