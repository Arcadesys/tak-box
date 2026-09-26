"""v6 design sketch: four deferred refinements layered onto the v5 case.

Corner radius, a lid registration lip, a well finger scoop, and a well stone
stop. Each is additive or subtractive on top of tak_case's already-validated
shell/lid geometry; the hinge mechanism itself is untouched (that redesign
is the separate filament-pin thread, see tak_pinfit.py). This is a digital
sketch: not sliced, not printed, and the white parts would need a reprint
once it is confirmed by hand.

A fifth idea, a center-row stiffening rib, was tried and reverted: see
center_row()'s docstring for why.
"""
import cadquery as cq
import tak_case as base
from tak_case import box, wing_y, lid_blank
from tak_box_base import D

S = D.board_size  # 205.0

CORNER_R = 3.0
LIP_W, LIP_H, LIP_CLEAR = 1.2, 0.6, 0.2
SCOOP_R = 4.0
STOP_W, STOP_H = 0.8, 1.5

# Per-wing landmarks carried over from tak_case.shell()/lid_blank(): the
# well's Y span, which wall sits next to the thumb notch (finger scoop goes
# there) and which sits next to the main hinge (stone stop goes there).
_WELL = {
    0: dict(y=(8.0, 72.0), lid_y=(6.0, 78.5), thumb_wall=72.0, thumb_dir=+1,
            hinge_wall=8.0, hinge_dir=+1),
    2: dict(y=(133.0, 197.0), lid_y=(127.0, 199.0), thumb_wall=133.0, thumb_dir=-1,
            hinge_wall=197.0, hinge_dir=-1),
}


def _corner_wedge(cx, cy, r, sx, sy, z0, z1):
    """The sliver outside a radius-r arc at corner (cx,cy), material in the
    (sx,sy) quadrant. Subtracting this rounds the corner without depending
    on edge-selection/fillet succeeding on a complex boolean solid."""
    ox = cx if sx > 0 else cx - r
    oy = cy if sy > 0 else cy - r
    wedge = box(r, r, z1 - z0, ox, oy, z0)
    center = cq.Vector(cx + sx * r, cy + sy * r, z0)
    return wedge.cut(cq.Solid.makeCylinder(r, z1 - z0, center, cq.Vector(0, 0, 1)))


def round_corners(shape, corners, r, z0, z1):
    for cx, cy, sx, sy in corners:
        shape = shape.cut(_corner_wedge(cx, cy, r, sx, sy, z0, z1))
    return shape


# corners: (x, y, quadrant sx, quadrant sy) -- material lies toward (sx,sy)
WING_CORNERS = {0: [(0, 0, 1, 1), (S, 0, -1, 1)],
                2: [(0, S, 1, -1), (S, S, -1, -1)]}


LIP_X = 3.5  # clear of the center row's end feet (x 0-2 / 203-205): fold
             # rotation is about the X axis, so an X-disjoint ridge can never
             # collide with them at any angle.


def lip_ridge(index):
    """Registration ridge fused to the shell along both long (x=0/x=S) edges."""
    lo, hi = _WELL[index]['lid_y']
    a = box(LIP_W, hi - lo, LIP_H, LIP_X - LIP_W / 2, lo, 1.0)
    b = box(LIP_W, hi - lo, LIP_H, S - LIP_X - LIP_W / 2, lo, 1.0)
    return a.fuse(b)


def lip_groove(index):
    """Matching shallow groove cut from the lid underside (0.7 mm into a
    3 mm-thick slab, so it never thins a wall)."""
    lo, hi = _WELL[index]['lid_y']
    w = LIP_W + LIP_CLEAR
    a = box(w, hi - lo, 0.7, LIP_X - w / 2, lo, 1.0)
    b = box(w, hi - lo, 0.7, S - LIP_X - w / 2, lo, 1.0)
    return a.fuse(b)


def well_scoop(index):
    """Rounded bite into the well wall next to the thumb notch, so a
    fingertip can curl under the stone stack once the lid is off."""
    w = _WELL[index]
    wall_y = w['thumb_wall']
    return cq.Solid.makeCylinder(SCOOP_R, 19.3,
                                  cq.Vector(84, wall_y, -18.15), cq.Vector(0, 0, 1))


def well_stop(index):
    """Low ridge on the well floor next to the main-hinge wall, corralling
    the stone stack away from that edge (kept to the 1 mm margin before the
    first row of flats, so it can't touch a stone in its resting position)."""
    w = _WELL[index]
    wall_y, d = w['hinge_wall'], w['hinge_dir']
    y0 = wall_y if d > 0 else wall_y - STOP_W
    return box(152, STOP_W, STOP_H, 8, y0, -18.1)


def shell(index, d=D):
    part = base.shell(index, d)
    if index in (0, 2):
        part = round_corners(part, WING_CORNERS[index], CORNER_R, -20.1, 4.05)
        part = part.fuse(lip_ridge(index))
        part = part.fuse(well_stop(index))
        part = part.cut(well_scoop(index))
    return part.clean()


def lid_blank_v6(index):
    lid = lid_blank(index)
    corners = [(0, 0, 1, 1), (S, 0, -1, 1)] if index == 0 else [(0, S, 1, -1), (S, S, -1, -1)]
    lid = round_corners(lid, corners, CORNER_R, 0.9, 4.1)
    lid = lid.cut(lip_groove(index))
    return lid.clean()


def lid_pair(index, d=D):
    """v5's lid_pair, but built on the v6 shell/lid so the hinge knuckles
    still line up; corners/lip/rib/scoop/stop are added first."""
    base_part, lid = shell(index, d), lid_blank_v6(index)
    axis_y = 0 if index == 0 else 205
    step = d.knuckle_length + d.knuckle_gap
    for k in range(d.knuckle_count):
        x = d.knuckle_margin + k * step
        barrel = cq.Solid.makeCylinder(2, d.knuckle_length, cq.Vector(x, axis_y, 1), cq.Vector(1, 0, 0))
        clearance = cq.Solid.makeCylinder(2.2, d.knuckle_length + .1, cq.Vector(x - .05, axis_y, 1), cq.Vector(1, 0, 0))
        bore = cq.Solid.makeCylinder(1.2, d.knuckle_length + .04, cq.Vector(x - .02, axis_y, 1), cq.Vector(1, 0, 0))
        if k % 2 == 0:
            base_part = base_part.fuse(barrel).cut(bore)
            lid = lid.cut(clearance)
        else:
            lid = lid.fuse(barrel).cut(bore)
            base_part = base_part.cut(clearance)
    latch_y = 75 if index == 0 else 130
    for x in (42, 163):
        base_part = base_part.cut(cq.Solid.makeCylinder(2, 2, cq.Vector(x, latch_y, 1), cq.Vector(0, 0, -1)))
        lid = lid.cut(cq.Solid.makeCylinder(2, 2, cq.Vector(x, latch_y, 1), cq.Vector(0, 0, 1)))
    return base_part.clean(), lid.clean()


def center_row(d=D):
    """Unchanged from v5. A below-slab stiffening rib was tried here and
    reverted: the space under the center row is reserved for the folded
    wings' own thickness, and the rib collided with them from 80-90 deg in
    the main fold sweep. A center stiffener would need to sit above the
    slab (under the removable black grid, z 4-4.8mm) or is out of scope."""
    return base.shell(1, d)


def posed(shape, index, degrees):
    return base.posed(shape, index, degrees)


def lid_open(lid, index, degrees):
    return base.lid_open(lid, index, degrees)


if __name__ == '__main__':
    for i in (0, 2):
        b, l = lid_pair(i)
        print('wing', i, 'valid', b.isValid(), len(b.Solids()),
              'lid valid', l.isValid(), len(l.Solids()))
    c = center_row()
    print('center valid', c.isValid(), len(c.Solids()))
