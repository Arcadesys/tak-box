# Tak project brief

Updated October 4, 2026. This brief combines the current repository with Austen's recent Tak design conversations. Source files and measured print reports take precedence over concept imagery or older conversation summaries.

### Final version decision: v18

The user selected **v18 as the FINAL version** on October 4, 2026 (Chicago).
Finish the recessed press-and-slide clasp with the retained four-leaf
common-hinge case architecture. See [V18_FINAL.md](V18_FINAL.md) for the exact
source freeze, protected choices and remaining release gates. The coupon package
is pinned by [V18-FREEZE.json](V18-FREEZE.json); the integrated complete case
and physical acceptance are still pending. Earlier closure trials are historical.

### v18 recessed press-and-slide clasp coupon

Recovered October 4, 2026 in `v18-recessed-clasp`. The complete saved package
contains CAD sources, three separate printable parts, STEP/STL assemblies,
a generic 3MF plate, four release states, actual-geometry renders, review and
prior slicing evidence. The original ZIP is retained under `release/`.
Recovery verified ZIP CRC, all 67 manifest byte counts/SHA-256 hashes, matching
standalone 3MF/image files and Python syntax. No geometry rebuild or new slice
was performed during recovery.

The receiver, keeper and rigid sliding bolt separate load-bearing shoulders
from the recessed press leaf. Both closing and opening require pressing; to
open, unload the keeper, press approximately 2 mm and slide left 10 mm before
lifting. The assembled coupon is 78×40×10.1 mm. Prior digital checks are recorded
in the package; physical fit, force, fatigue, support removal and loaded-bag
retention remain untested. Supports are required in the provided orientation.
This is a standalone clasp coupon, not a v18 complete-case release or an
integrated change to v17. Next trial: print and inspect the small coupon, then
check assembly, ten gentle cycles and press-only/drag-only retention as described
in its README before case integration. Earlier closure studies remain history.

### v17 common-hinge travel revision

User selected **all four leaves on the same hinge**: two drawer housings
and two board leaves. `v17-four-leaf` records the architecture and motion
study. Each housing has a fixed roof above a sliding flat drawer, so rotating
leaves does not expose pieces. Board leaves will snap to their housings for
play. The four-part over-center trial was rejected as confusing. The current
closure trial is `v17-squeeze-latch`: a two-part side-release buckle with
broad load-bearing shoulders and two exposed squeeze buttons. Closing
pushes the clip into its socket; squeeze both buttons to open. Case
integration and physical spring/strength tests remain unfinished. Closure
pins, sleeves and screws securing access to trays are rejected.

The 5×5 field is 180 mm at 36 mm pitch. Forty-two original 19.5×19.5×8 mm
flats fit single-layer 3×7 drawers. Original Cat/Witch capstone envelopes fit
in a separate rear compartment, outside the field. Two short coaxial steel
axles at the ends leave the middle playing column unobstructed. Axles are
permanent hinge hardware, not a closure pin. Four main hinged modules do
not mean exactly four total printed parts: drawer inserts and a capstone
hatch are additional parts.

Preliminary body envelope 101×236×32.6 mm before closure hardware: thinner,
but longer, than v16. No final closure-envelope size reduction is verified.
Solid, STEP readback, STL and sampled paired/independent leaf motion checks
pass. Exact detailed capstone geometry, continuous swept motion, snap/stop
implementation, capstone hatch and direct case closure remain unresolved.
No complete-print release, slicing or physical retention is claimed.
Next small trials: four-family common-axis hinge, board snap and drawer
release, followed by the two-piece squeeze-buckle coupon before the full case.
Weighted flats and curled Fox/Cat pieces are not verified in this package.
Existing v16 printed interfaces remain incompatible and unchanged.

## Project and collaboration

- Repository: https://github.com/Arcadesys/tak-box (private, main branch).
- Research Page: https://chatgpt.com/space/page_1a04af571ecc8191817d9c547cde56ff
- Tak Space hub: https://chatgpt.com/space/page_6abdc060969481918381b94ad91155e8
- Read AGENTS.md, this brief, and the affected package README before changing geometry.
- Existing code is parametric Python/CadQuery with exported STEP, STL, 3MF, previews, verification and slicer reports. Keep reproducible source with its deliverables.

## Two design directions

### Existing travel prototype

The current main-branch baseline is v16-field-book: a 5×5 board, 36 mm pitch, 180 mm field, folding face inward with a snap-in tray beneath each half. README dimensions are 101×202×51 mm closed. It is designed for the Elegoo Centauri Carbon 2, 256 mm bed. The board has a flush white grid on black, sparse orange/purple astronomical inlays, a protective paint lip and a far-edge squeeze-release buckle.

Issue #18 contains newer physical observations: the board feels too thin and pieces rattle in slightly oversized tray cavities. v16 documentation still has an opening statement that nothing has been printed; later sections discuss printed trays/plates, warping and a stiffened base. Treat physical status as mixed and component-specific; the unchecked acceptance sheet is not a complete print history. Start by recording exactly which revision and parts were printed.

### Crafted luxury concept

Current selected premium direction: an exceptionally ornate **printed low
rectangular pagoda platform**, with the pieces hidden beneath a lift-out board.
The motifs are witch and cat, energy vines and galactic forms. The wooden-box,
bagged-board and swap-shop alternatives preceded this selection.

`full-size-pagoda-v1` establishes a separate unornamented foundation from the
existing GitHub designs: 25×25×10 mm finished weighted flats, uniformly scaled
Fox/Cat capstones within a 25 mm footprint, 42 mm pitch / 210 mm playing field,
and two stacked lift-out piece cassettes, each for 21 flats and a capstone.
The lower cassette has floor supports and a locating frame; four pins/sockets
register the stacked pair. Flat rows hold 5+5+6+5; the third row extends beside
the capstone, replacing the separate 21st-flat pocket without enlarging the
cassette. Each is an open carrier, with separate lids not
included in this revision. Cat is 33.809 mm tall; Fox is 35 mm. Both retain
their existing proportions and looking-back curl. Flat seats are raised 16 mm, placing the flats
2 mm below the rim and 6 mm above the dividers; 18 mm finger openings expose
the leading stone in each row. Loaded flats remain 2 mm below the next cassette.
Capstone seats are raised 3 mm, with a 28 mm front finger opening to grasp the
curled body; both capstones remain below the next cassette floor.
This changes the premium package; v16 and all
its printed interfaces remain unchanged. Full-size pieces do not fit v16's
old 98 mm lanes. Geometry, mesh, 3MF readback and local slicing pass in the new
package; physical cassette fit/release and transport retention remain unresolved.
The shell has no roof above the field. Its felt-covered board remains removable.

The following hinged luxury arrangement is retained as earlier exploration:

Latest conversation direction: a compact square closed object that opens into a rectangular arrangement with a central 5×5 playing board and piece wells on both sides. Desired feel is a beautiful crafted cigar box or heirloom case.

Austen's latest mechanism idea is hinged piece boards/trays that fold outward, followed by removal of a lid for play. Exact lid order, hinge axes, dimensions and the retention method remain unresolved. Do not silently replace the field-book baseline with this concept. Prototype separately and first demonstrate a spill-free opening sequence: pieces must remain supported or enclosed while anything rotates.

Walnut/maple, brass accents and felt-like lining in generated imagery are visual directions, not selected construction materials or verified mechanisms. Prior render feedback explicitly rejected an opening motion that would spill pieces.

## Pieces and tactile goals

- Goal: satisfying weight, grip, stacking and sound; plain plastic feels underwhelming.
- weighted-v1 has two-part 20×20×6 mm stones with separate locating floors and post-print bonded ballast, then adhesive closure. Each team has 21 stones plus a capstone.
- Compare an empty control, bonded sand and bonded fine steel shot. 5–7 g is an experimental target, not a measured result. Record cured mass, rattle, sound, grasp, stack separation and wall stability.
- The current tray insert has 98 mm lanes for five 19.5 mm flats. Five 20 mm weighted stones require 100 mm before clearance. They do not fit that insert arrangement.
- fox-knurled-v1 has 19.5×19.5×8 mm stones and fits the current insert digitally; physical grip/fit needs a sample.
- fox-cat-capstones-v4 retains the looking-over-the-shoulder carved curl concept. Cat neck/shoulder corrected; Fox retained from v3. Rebuild and digital fit/slicing evidence are recorded; creator and physical acceptance remain pending.

## History and lessons

- v5–v7 archive: older open wells, filament pins, hinge coupons and center closures.
- Historical coupon measurements from conversation: 1.90 mm fixed bore, 2.20 mm free bore, 1.70 mm plug hole. These belong to the old pin design, not v16 print-in-place hinges.
- Historical complaints: center leaf too thin, carve-outs and round cut-outs misfit, clasp unreliable; rubber band used as interim closure. Verify applicability before carrying them into a current fix.
- v11 smooth case and v12 chest are retained on named branches.
- v13: two-leaf book with M3 clasp.
- v14: 24 mm cells; paper play test too cramped.
- v15: 28 mm cells; stacks difficult to grasp.
- v16: 36 mm cells, larger piece clearance, revised cradle, roomier trays and base stiffening.
- Earlier galaxy/raised-grid/6×6 artwork is historical exploration. Current request is 5×5; v16 grid is flush.

## Next work

1. Reconcile component print history and observations with issue #18. Record revision, filament, profile and photos; retain unchecked tests until performed.
2. Address board stiffness and molded tray retention without sacrificing easy finger removal, clean closure or existing printed-part compatibility.
3. Develop the selected premium pagoda from `full-size-pagoda-v1`: constrain ornament to the external shell, preserve the lift-out board and cassette removal paths, reduce material where possible and physically test cassette registration/release and resolve transport retention before a complete print. The earlier hinged luxury motion study remains separate.
4. Revise the insert for weighted stones if those pieces are chosen; test a coupon first.
5. Finish one physical Fox/Cat pair test and a weighted-stone feel comparison before batch printing.

## Evidence and reproduction

Read these current packages:
- v16-field-book/README.md and ACCEPTANCE.md
- pieces/weighted-v1/README.md
- pieces/fox-cat-capstones-v4/README.md
- https://github.com/Arcadesys/tak-box/issues/18

Board pipeline: `python v16-field-book/source/build_all.py`. It runs model build, solid verification, mesh verification, rendering and plate packaging, stopping at the first failure. Use `--only verify_book` or `--only verify_meshes` for bounded checks. Full packaging requires ElegooSlicer; do not claim cloud slicing success without that dependency.

Weighted-stone environment and commands are in its README and requirements.txt. Fox/Cat has a separate requirements file and reproduction pipeline. Avoid combining their dependencies blindly; rendering and slicing also contain macOS-specific assumptions. See CODEX.md for the collaboration starting point.

Digital geometry, slicer estimates, physical print results and tactile acceptance must remain distinct.
