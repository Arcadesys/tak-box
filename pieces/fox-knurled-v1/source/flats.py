"""Fox flats: millimetres, smooth base at z=0; subtractive side knurl."""
from functools import lru_cache
from math import sqrt
import cadquery as cq

WIDTH = 19.5
HEIGHT = 8.0
CORNER_RADIUS = 1.8
CHAMFER = .5
ENGRAVE = .4
KNURL_DEPTH = .4
KNURL_WIDTH = .8  # measured perpendicular to each 45-degree groove
KNURL_PITCH = 2.4  # horizontal spacing, both diagonal directions
KNURL_Z = (1.4, 6.6)
KNURL_SPAN = 15.0  # avoids the rounded corners


def fox_cutter():
    """Bold ears, long cheeks, pointed muzzle; islands meet the stack plane."""
    outline = [(-6.4, 6.6), (-2.1, 4.6), (0, 3.8), (2.1, 4.6),
               (6.4, 6.6), (5.6, .3), (3, -2.8), (0, -5.3),
               (-3, -2.8), (-5.6, .3)]
    z = HEIGHT - ENGRAVE
    cutter = cq.Workplane('XY', origin=(0, 0, z)).polyline(outline).close().extrude(ENGRAVE + .1)
    islands = [
        [(-5.35, 5.0), (-3.25, 4.0), (-4.95, 2.65)],
        [(5.35, 5.0), (3.25, 4.0), (4.95, 2.65)],
        [(-4.1, .75), (-1.45, .1), (-2.35, -.65)],
        [(4.1, .75), (1.45, .1), (2.35, -.65)],
        [(-2.35, -2.25), (0, -1.25), (2.35, -2.25), (0, -4.25)],
    ]
    for points in islands:
        island = cq.Workplane('XY', origin=(0, 0, z - .1)).polyline(points).close().extrude(ENGRAVE + .3)
        cutter = cutter.cut(island)
    # A separate nose depression in the pale muzzle island.
    nose = (cq.Workplane('XY', origin=(0, 0, z))
            .polyline([(-.7, -2.05), (.7, -2.05), (0, -2.85)]).close().extrude(ENGRAVE + .1))
    return cutter.union(nose)


def side_knurl():
    """One recessed crosshatch band on the front face, clipped at both ends."""
    face_y = -WIDTH / 2
    clip = (cq.Workplane('XY')
            .box(KNURL_SPAN, KNURL_DEPTH + .2, KNURL_Z[1] - KNURL_Z[0])
            .translate((0, face_y + KNURL_DEPTH / 2, sum(KNURL_Z) / 2)))
    half = KNURL_WIDTH / sqrt(2)
    tools = []
    for direction in (-1, 1):
        for index in range(-6, 7):
            intercept = index * KNURL_PITCH
            low, high = -2.0, HEIGHT + 2.0
            # x = intercept + direction * (z - HEIGHT/2)
            xa = intercept + direction * (low - HEIGHT / 2)
            xb = intercept + direction * (high - HEIGHT / 2)
            points = [(xa - half, low), (xa + half, low),
                      (xb + half, high), (xb - half, high)]
            tool = (cq.Workplane('XZ', origin=(0, face_y - .1, 0))
                    .polyline(points).close().extrude(-(KNURL_DEPTH + .2)))
            tools.append(tool.val())
    grooves = cq.Workplane(obj=cq.Compound.makeCompound(tools)).intersect(clip)
    return grooves


@lru_cache(None)
def flat():
    body = (cq.Workplane('XY').box(WIDTH, WIDTH, HEIGHT, centered=(True, True, False))
            .edges('|Z').fillet(CORNER_RADIUS)
            .faces('>Z or <Z').edges().chamfer(CHAMFER))
    grooves = side_knurl()
    for angle in (0, 90, 180, 270):
        body = body.cut(grooves.rotate((0, 0, 0), (0, 0, 1), angle))
    return body.cut(fox_cutter()).clean()
