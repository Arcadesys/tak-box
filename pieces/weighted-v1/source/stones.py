"""Two-part Tak stones. Millimetres; assembly floor is at z=0.

The underside rabbet seats a floor plate; a smaller tongue locates in the
ballast cavity. Both shoulders leave an axial adhesive gap. No snap-fit.
"""
from pathlib import Path
import sys
import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import tak_pieces as original

WIDTH, HEIGHT = 20.0, 6.0
OUTER_RADIUS, EDGE = 2.0, 0.4
SEAT_WIDTH, SEAT_RADIUS, SEAT_DEPTH = 18.0, 1.0, 1.2
CAVITY_WIDTH, CAVITY_RADIUS, CAVITY_TOP = 16.8, 0.8, 4.8
FLOOR_THICKNESS, TONGUE_HEIGHT = 1.0, 0.6
CLEARANCE = 0.2  # per side, not total
ENGRAVE = 0.4


def rounded(width, radius, bottom, height):
    return (cq.Workplane('XY', origin=(0, 0, bottom))
            .rect(width, width).extrude(height).edges('|Z').fillet(radius))


def body(team):
    if team not in ('cat', 'witch'):
        raise ValueError(team)
    shell = rounded(WIDTH, OUTER_RADIUS, 0, HEIGHT)
    shell = shell.faces('>Z or <Z').edges().chamfer(EDGE)
    seat = rounded(SEAT_WIDTH, SEAT_RADIUS, -0.1, SEAT_DEPTH + 0.1)
    cavity = rounded(CAVITY_WIDTH, CAVITY_RADIUS, SEAT_DEPTH - 0.01,
                     CAVITY_TOP - SEAT_DEPTH + 0.01)
    spec = original.cat_emblem(1.1) if team == 'cat' else original.witch_emblem(1.0)
    mark = original.emblem_cutter(spec,
        lambda: cq.Workplane('XY', origin=(0, 0, HEIGHT - ENGRAVE)),
        ENGRAVE + 0.1, False)
    return shell.cut(seat).cut(cavity).cut(mark)


def floor(clearance=CLEARANCE, label=None):
    plate = rounded(SEAT_WIDTH - 2 * clearance, SEAT_RADIUS - clearance,
                    0, FLOOR_THICKNESS)
    tongue = rounded(CAVITY_WIDTH - 2 * clearance, CAVITY_RADIUS - clearance,
                     FLOOR_THICKNESS - 0.01, TONGUE_HEIGHT + 0.01)
    result = plate.union(tongue)
    # Coupon IDs are on the inside, away from stacking/contact faces.
    if label:
        mark = (cq.Workplane('XY', origin=(0, 0, FLOOR_THICKNESS + TONGUE_HEIGHT - .2))
                .text(str(label), 3.5, .3, combine=False))
        result = result.cut(mark)
    return result


def body_for_print(team):
    # Broad top on the bed, cavity facing up: no closure bridge or print pause.
    return body(team).rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, HEIGHT))
