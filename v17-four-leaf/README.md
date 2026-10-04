# v17 four-leaf common-hinge study

Selected architecture: two drawer housings and two board leaves rotate independently about one common hinge axis. Four interleaved knuckle families share the same steel axle at each end of the spine. The axle does not fasten the case closed. The board leaves snap onto their respective housings for play; covered sliding drawers allow access without disturbing the assembled board.

The 180 mm, 5×5 field and 36 mm pitch remain. Each drawer holds 21 original 19.5×19.5×8 mm flats in one layer. The taller original Cat/Witch capstones occupy a separate rear compartment, outside the field. This is a mechanism study, not a full-print release. The compartment hatch, drawer stops/releases, board snap fatigue and direct over-center closure still require fit-trial development.

Opening sequence: release the case draw latch; rotate the right housing and its snapped board leaf together until the board is flat; slide the team drawers forward while the case rests flat; the housing roofs uncover them as they emerge. For repacking, fully insert and latch both drawers before folding. A roof fixed to each housing encloses the stored flats throughout rotation. The independent board hinges allow maintenance and assembly without screws through the storage cavities.

The nominal main body is 101×236×32.6 mm closed, before closure hardware, with two short coaxial end axles. Keeping axle material out of the 180 mm field avoids a ridge through the middle playing column. Dimensions are preliminary; compare the final hardware envelope, not this body-only volume, with v16's 101×202×51 mm.

Original flat envelopes are the compatibility target. The rear compartment uses the original Cat/Witch pawn envelopes; curled Fox/Cat and weighted flats are not verified. This redesign does not reuse v16 printed interfaces. The rejected screw-clamped draft and pin/sleeve draft are not selected.

Run `python v17-four-leaf/source/build_study.py` from the repository root. STEP, STL, exported-geometry previews and a sampled paired-leaf fold check are generated. Read reports for actual results and limitations. No slicing, successful physical retention, snap force or latch durability is claimed.

## Direct mechanical closure trial

`python v17-four-leaf/source/build_closure_trial.py` builds a separate,
real hook/lever/keeper coupon. The hook captures a rectangular keeper;
a folding lever draws it down beyond dead center against a stop. There is
no removable closure pin. The 0.25 mm keeper-lift blocking check, released
hook clearance, solids, STL and named-object generic 3MF readback pass.
This proves nominal geometry only. The coupon is not yet integrated into
the case, and preload, actuation force and strength are untested.

Permanent pivots use M2.5 hardware through nominal Ø2.89 mm bores; confirm
printed clearance with a coupon. Nominal fasteners are M2.5×20 and M2.5×16
with washers/nyloc nuts, subject to measured stack-up. Once assembled,
normal opening requires only fingers. The steel hinge axles likewise remain
installed. The trial exports use generic geometry placements, not qualified
print orientations or sliced printer profiles. Do not print the full case.
