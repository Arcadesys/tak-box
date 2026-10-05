# Tak box

A 3D-printed travel case for a 5 × 5 game of Tak, with interchangeable themed piece sets for custom gifts. The original pieces are Team Cat / Team Witch. Printed in PLA on an Elegoo Centauri Carbon 2.

## Latest closure trial: [v18 recessed press-and-slide clasp](v18-recessed-clasp)

The recovered v18 package includes reproducible CAD source, STEP/STL parts,
a three-part 3MF coupon plate, assembled release states, renders, review and
slicing reports, and the original downloadable kit. [Recovery checks](v18-recessed-clasp/RECOVERY.md)
confirmed all 67 manifest hashes and both separately saved artifacts.

This is an **unprinted, support-required clasp coupon**, not a complete case.
Both closing and opening require pressing the recessed button while sliding
the rigid bolt. Case integration, physical fit, support removal, strength and
loaded transport retention remain unverified. The v17 body study remains below.

## Current v17 direction: [four leaves on one common hinge](v17-four-leaf)

Two drawer housings and two board leaves share one hinge axis. Covered
sliding drawers keep flats enclosed while the leaves rotate. Board leaves
will snap into their play positions; a [two-piece squeeze buckle](v17-squeeze-latch) is the
current case-closure trial. The 180 mm field and 36 mm pitch remain.

This is a CAD motion study, **not a full-print release**. Paired folding,
independent board rotation, original-flat envelopes, solids and exported
meshes pass the recorded sampled checks. Board snaps, drawer releases,
rear capstone hatch and case-closure integration remain unfinished. The
previous four-part draw-latch trial was rejected as confusing.
The main body is provisionally 101×236×32.6 mm, excluding closure hardware;
it is thinner but longer than v16. No final size saving is claimed yet.

The [screw-clamped draft](v17-compact-folio) was rejected and is history only.
The later pin/sleeve idea was also rejected; it is not the selected closure.

## Previous travel prototype: [v16 field book](v16-field-book)

The separate [full-size pagoda foundation](full-size-pagoda-v1/README.md) uses
25 × 25 × 10 mm weighted flats, scaled existing Fox/Cat capstones and a lift-out
5×5 board above two stacked trays. It is the new premium printed exploration;
v16 remains the travel prototype. Digital geometry and local slicing pass;
physical fit and transport retention remain untested.

![v16 open with trays out](v16-field-book/previews/03-trays-out.png)

The board folds in half with its face inside, and there's a snap-in piece tray under each half.
- **Closing:** a buckle at the far edge. Squeeze the side of the case to open it.
- **Board:** 5 × 5 at 36 mm cells, black with an inlaid white grid and subtle star, galaxy, planet, moon and comet inlays. A raised lip protects paint.
- **Assembly:** the board plates drop onto locating pegs and glue into shallow wells, so they line up without a jig.
- **Size:** 101 × 202 × 51 mm closed.

It has four multi-colour print plates. The user reports physical piece-retention
and closure failures; the exact printed component revisions are unknown.
See the [v16 README](v16-field-book/README.md) for retained plates and source;
its blanket unprinted statement is historical and superseded by those reports.

## Pieces: [pieces](pieces)

Piece designs live in separate packages so custom sets can share the box. Check each package's dimensions and tray compatibility before printing; the packages currently use different stone sizes.

The Cat and Witch flats and capstones, with CAD source, STLs and one CC2 print plate per team in [pieces/plates](pieces/plates).

The [weighted stone prototype](pieces/weighted-v1/README.md) adds 20 × 20 × 6 mm two-part stones for post-print ballast and epoxied floors, with a three-clearance fit coupon and one complete geometry plate per team. Physical fit and feel remain untested.

The [fox knurled flats](pieces/fox-knurled-v1/README.md) add 21 fox-themed 19.5 × 19.5 × 8 mm stones with recessed face emblems and diamond-textured sides. Sample and full-set CC2 plates are included. Geometry fits the current tray insert; physical fit and grip await a sample print.

The [reference-based Fox and Cat capstones](pieces/fox-cat-capstones-v4/README.md) follow a continuous carved nose-to-tail curl. This package contains the fuller Fox tail and the Cat's corrected neck/shoulder, printable STLs, a labeled two-object 3MF, retained reconstruction sources and large labeled previews. Digital v16 compatibility and dry slicing pass; physical fit and tactile acceptance remain untested.

## Archive

- [archive/v15-field-book](archive/v15-field-book): 28 mm cells. Too small to play on: you couldn't grab a stack once the board filled up.
- [archive/v14-field-book](archive/v14-field-book): the first field book, with 24 mm cells. A paper play test showed it was too cramped.
- [archive/v13-book](archive/v13-book): the first two-leaf book, with the M3 clasp.
- [archive/v5-v7](archive/v5-v7): the earlier open-wells, pin-board, hinge-coupon and center-closure designs, with their scripts, coupons and plates. Its [README](archive/v5-v7/README.md) describes v5.

Versions v11 (smooth case) and v12 (chest) live on their own branches: `feat/tak-v11-smooth-case` and `feat/tak-v12-chest`.
