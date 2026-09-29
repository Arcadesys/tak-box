"""v7: the filament-pin case (tak_case_pin) reshaped to fold into a flush box.

v5/pin wing walls stop 2.5 mm short of both board ends so the center row's
two flat end feet can drop in beside them when folded. That leaves the 1 mm
play-face plate overhanging the wall along each wing end (the part the
slicer supports with trees), and the folded ends step in and out.

v7 changes, hinges and wells untouched:
- Wing end walls run out to x = 0 / 205, so the plate no longer overhangs.
- Each center-row foot is a quarter disc centred on its seam's hinge axis,
  hanging down toward the center row. Because it is centred on the axis it
  turns in place as the wing folds, so it never sweeps through the wing; the
  wing only needs a matching quarter-disc notch in its seam-side corner. When
  folded, the foot fills that notch flush and the end face is flat.
  The foot is annular (inner r 2.6) so the Ø4.4 filament feed channel stays open.
- 1 mm 45-degree chamfers on the folded box's short edges: the center row's
  play-face ends, the lids' play-face ends and the wings' outer-wall ends.
- Rubber-foot pockets: four Ø8.6 x 1.4 mm pockets in each wing floor for
  stick-on Ø8 x 2.2 mm hemispherical bumpers (3M Bumpon SJ5302 size), which
  then stand 0.8 mm proud. Folded, the two wing floors face each other across
  a 0.8 mm gap (wing A y faces wing B 205 - y), so the two wings' bumpers are
  staggered in x and each bumper faces a Ø9.6 x 0.6 mm clearance pocket.
  Each pocket prints closed by a 0.2 mm first-layer skin (otherwise the
  slicer tree-supports it); cut the skin out before fitting the bumper.
  With bumpers fitted the open board stands on rubber; the center-row feet
  then sit 0.8 mm above the table and act as a backstop if it is pressed.
"""
import math
import cadquery as cq
import tak_case_pin as m
from tak_case import box, wing_y, lid_blank, cylinder

D = m.D
S = D.board_size                 # 205
R_FOOT = 20.1                    # reaches the open-board table plane (z -20.1)
R_IN = 2.6                       # clears the Ø4.4 feed channel on the axis
FOOT_T = 2.2                     # foot thickness in x
NOTCH_CLR = 0.4                  # radial clearance around a folded foot
END_T = 2.5                      # wing end-wall extension (old setback)
EDGE_MARGIN = math.radians(2.0)  # keeps the folded foot off the wing plate
FUSE = math.radians(5.0)         # overlap into the center-row plate
CHAMFER = 1.0
BUMPER_POCKET = (8.6 / 2, 1.4)   # radius, depth: Ø8 x 2.2 bumper, 0.8 proud
CLEAR_POCKET = (9.6 / 2, 0.6)    # faces the other wing's bumper when folded
FLOOR_Z = -20.1
SKIN = 0.2                       # one first layer closes each pocket at the bed; knife it out
BUMPERS = {0: [(22, 15), (183, 15), (22, 64), (183, 64)],        # wing-local (x, y)
           2: [(40, 190), (165, 190), (40, 141), (165, 141)]}


def _sector_x(y, z, r0, r1, a0, a1, x0, length):
    """Annular sector in the YZ plane about (y, z), angles from +Y toward +Z,
    extruded along +X from x0."""
    pt = lambda r, a: (y + r * math.cos(a), z + r * math.sin(a))
    am = (a0 + a1) / 2
    wp = (cq.Workplane('YZ', origin=(x0, 0, 0))
          .moveTo(*pt(r0, a0)).lineTo(*pt(r1, a0))
          .threePointArc(pt(r1, am), pt(r1, a1)).lineTo(*pt(r0, a1))
          .threePointArc(pt(r0, am), pt(r0, a0)).close())
    return wp.extrude(length).val()


def _seam(seam_i):
    """Hinge axis y and which way the center row lies from it (+1 / -1)."""
    return D.seam_y[seam_i], (1 if seam_i == 0 else -1)


def foot(seam_i, x0):
    """Quarter-disc foot under the center row, hanging from seam seam_i."""
    y, s = _seam(seam_i)
    # The edge along the center-row plate runs 5 deg up into it so they fuse;
    # the downward edge stops 2 deg short of vertical, which is the edge that
    # ends up against the wing's plate when folded.
    if s > 0:   # center lies toward +Y
        a0, a1 = -math.pi / 2 + EDGE_MARGIN, FUSE
    else:       # center lies toward -Y
        a0, a1 = -math.pi - FUSE, -math.pi / 2 - EDGE_MARGIN
    return _sector_x(y, D.hinge_z, R_IN, R_FOOT, a0, a1, x0, FOOT_T)


def notch(seam_i, x0, length):
    """The folded foot's home inside the wing's seam-side corner."""
    y, s = _seam(seam_i)
    if s > 0:   # wing A lies toward -Y of seam 0
        a0, a1 = -math.pi, -math.pi / 2
    else:       # wing B lies toward +Y of seam 1
        a0, a1 = -math.pi / 2, 0.0
    return _sector_x(y, D.hinge_z, 0.0 + 1e-3, R_FOOT + NOTCH_CLR, a0, a1, x0, length)


def _chamfer_x_along_y(x_edge, z_edge, y0, y1, sx, sz, c=CHAMFER):
    """Wedge removing a c x c 45-degree chamfer from an edge that runs along Y
    at (x_edge, z_edge); material lies toward (sx, sz)."""
    pts = [(x_edge, z_edge), (x_edge + sx * c, z_edge), (x_edge, z_edge + sz * c)]
    pts = [(x - sx * 0.01, z - sz * 0.01) if i == 0 else (x, z) for i, (x, z) in enumerate(pts)]
    wp = cq.Workplane('XZ', origin=(0, y1, 0)).polyline(pts).close()
    return wp.extrude(y1 - y0).val()        # XZ normal is -Y: extrudes from y1 down to y0


def _chamfer_x_along_z(x_edge, y_edge, z0, z1, sx, sy, c=CHAMFER):
    """Same for an edge that runs along Z at (x_edge, y_edge)."""
    pts = [(x_edge - sx * 0.01, y_edge - sy * 0.01), (x_edge + sx * c, y_edge), (x_edge, y_edge + sy * c)]
    wp = cq.Workplane('XY', origin=(0, 0, z0)).polyline(pts).close()
    return wp.extrude(z1 - z0).val()


def center_row():
    # Preserve the validated playing slab and all knuckles. The v5 rectangular
    # skirts cannot rotate inside v7's quarter-disc wing notches.
    part = m.shell(1).cut(m.center_outer_skirt())
    part = part.fuse(center_closure_skirt())
    y0, y1 = D.seam_y
    for x, sx in ((0, 1), (S, -1)):                    # play-face ends
        part = part.cut(_chamfer_x_along_y(x, 4.0, y0 - 3, y1 + 3, sx, -1))
    return part.clean()


def center_closure_skirt():
    """Fill the roof gap, with circular feet matching the actual v7 wings.

    Wing end walls extend to x=0/205. Keep the roof 0.4 mm inside their
    2.5 mm depth, and put only R20.1 feet inside the R20.5 end cutouts.
    The notch cuts 2.6 mm deep, leaving 0.4 mm behind each 2.2 mm foot.
    """
    clearance = 0.4
    y0, y1 = D.seam_y
    inset = END_T + clearance
    roof = box(S - 2 * inset, y1 - y0 - 2 * clearance, 3.6,
               inset, y0 + clearance, -3.6)
    for y in D.seam_y:
        roof = roof.cut(cylinder(m.SEAM_R + clearance, S + .2, -.1, y, D.hinge_z))
    for seam_i in (0, 1):
        y, sign = _seam(seam_i)
        for x in (0, S - FOOT_T):
            rounded = foot(seam_i, x)
            # A constant linear clearance also protects the inner end of the
            # sector; a fixed 2-degree angular margin alone is too small there.
            if sign > 0:
                keep = box(FOOT_T, 41, 30, x, y + clearance, -21)
            else:
                keep = box(FOOT_T, 41, 30, x, y - clearance - 41, -21)
            rounded = rounded.intersect(keep)
            rounded = rounded.cut(cylinder(m.SEAM_R + clearance, FOOT_T + .2,
                                           x - .1, y, D.hinge_z))
            roof = roof.fuse(rounded)
    return roof.clean()


def shell(index):
    """Wing with end walls out to x = 0 / 205 and a foot notch at the seam corner."""
    part = m.shell(index)
    y0 = wing_y(index)
    body_y0, body_y1 = (y0, y0 + 78) if index == 0 else (y0 + 4, y0 + 82)
    for x in (0, S - END_T):
        block = box(END_T, body_y1 - body_y0, 21.1, x, body_y0, -20.1)
        part = part.fuse(block)
    seam_i = 0 if index == 0 else 1
    for x in (-0.1, S - END_T - 0.1):
        part = part.cut(notch(seam_i, x, END_T + 0.2))
    # re-open the seam feed channel through the new end blocks
    edge_y = D.seam_y[seam_i]
    part = m.feed_channels(part, edge_y, D.hinge_z)
    outer_y = y0 if index == 0 else y0 + 82
    sy = 1 if index == 0 else -1
    for x, sx in ((0, 1), (S, -1)):                    # outer-wall ends (folded: box bottom)
        part = part.cut(_chamfer_x_along_z(x, outer_y, -20.2, 1.2, sx, sy))
    return part.clean()


def bumper_pockets(part, index):
    """Rubber-foot and clearance pockets, each sealed at the bed by a one-layer
    skin so build-plate-only supports can't grow into it (knife the skin out
    before fitting the bumper). Cut last and never .clean()ed: clean() leaves
    the sealed voids' shells invalid."""
    other = 2 if index == 0 else 0
    for (x, y), (r, depth) in ([(b, BUMPER_POCKET) for b in BUMPERS[index]] +
                               [((x, 205 - y), CLEAR_POCKET) for x, y in BUMPERS[other]]):
        part = part.cut(cq.Solid.makeCylinder(r, depth - SKIN, cq.Vector(x, y, FLOOR_Z + SKIN)))
    return part


def lid_blank_v7(index):
    lid = lid_blank(index)
    y0 = wing_y(index)
    for x, sx in ((0, 1), (S, -1)):                    # play-face ends (folded: box corners)
        lid = lid.cut(_chamfer_x_along_y(x, 4.0, y0 - 1, y0 + 83, sx, -1))
    return lid


def lid_pair(index, d=D):
    """tak_case_pin.lid_pair on the v7 wing and lid blanks."""
    L, GAP, COUNT, CLR = m.L, m.GAP, m.COUNT, m.CLR
    base_part, lid = shell(index), lid_blank_v7(index)
    axis_y = 0 if index == 0 else 205
    for k in range(COUNT):
        cut = cylinder(m.LID_R + CLR, L + 2 * GAP, m.knuckle_x(k) - GAP, axis_y, m.LID_Z)
        if k % 2 == 0: lid = lid.cut(cut)
        else: base_part = base_part.cut(cut)
    for k in range(COUNT):
        x = m.knuckle_x(k)
        barrel = cylinder(m.LID_R, L, x, axis_y, m.LID_Z)
        if k % 2 == 0:
            base_part = m.bore(base_part.fuse(barrel), k, True, axis_y, m.LID_Z)
        else:
            barrel = barrel.fuse(box(L, 3.0, 0.4, x, axis_y - 1.5, 3.6))
            lid = m.bore(lid.fuse(barrel), k, False, axis_y, m.LID_Z)
    base_part = m.feed_channels(base_part, axis_y, m.LID_Z)
    lid = m.feed_channels(lid, axis_y, m.LID_Z)
    latch_y = 75 if index == 0 else 130
    for x in (42, 163):
        base_part = base_part.cut(cq.Solid.makeCylinder(m.p.MAG_R, m.p.MAG_D, cq.Vector(x, latch_y, 1), cq.Vector(0, 0, -1)))
        lid = lid.cut(cq.Solid.makeCylinder(m.p.MAG_R, m.p.MAG_D, cq.Vector(x, latch_y, 1), cq.Vector(0, 0, 1)))
    return bumper_pockets(base_part.clean(), index), lid.clean()


sol = m.sol
posed = m.posed
lid_open = m.lid_open
overlay = m.overlay
filament = m.filament
