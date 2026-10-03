"""Full-size lift-out platform foundation. All dimensions are millimetres.

Reuses the original Cat/Witch emblem CAD, Fox knurl/emblem cutters, weighted
stone closure construction and v16 STL exporter. Legacy packages are untouched.
"""
from pathlib import Path
import importlib.util
import sys
import cadquery as cq

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'pieces'))
import tak_pieces as original


def load_source(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


weighted = load_source('weighted_baseline', 'pieces/weighted-v1/source/stones.py')
fox = load_source('fox_baseline', 'pieces/fox-knurled-v1/source/flats.py')
FLAT = 25.0
HEIGHT = 10.0
PITCH = 42.0
FIELD = 5 * PITCH
BOARD = (232.0, 224.0, 6.0)
BOARD_Z = 66.0
SEAT_CLEARANCE = .3
TRAY = (120.0, 174.0, 30.0)
TRAY_FLOOR = 2.0
TRAY_Z = (4.0, 34.0)
LANE_WIDTH = 25.6
LANE_LENGTH = 126.0
SEAT_WIDTH = 23.0
CAVITY_WIDTH = 21.8
CAVITY_TOP = 8.5
FLOOR_Z = .7
FELT = .6
FLOOR_THICKNESS = 1.0
TONGUE_HEIGHT = .6
FLOOR_CLEARANCE = .2
ENGRAVE = .5
CASSETTE_SIDE_CLEARANCE = .4
REGISTER_XY = ((2, 2), (118, 2), (2, 172), (118, 172))
REGISTER_WIDTH = 2.0
REGISTER_HEIGHT = 1.0
REGISTER_SOCKET_DEPTH = 1.2


def box(w, d, h, x=0, y=0, z=0):
    return cq.Workplane('XY').box(w, d, h, centered=(True, True, False)).translate((x, y, z))


def affine(obj, factors):
    x, y, z = factors
    return cq.Workplane(obj=obj.val().transformGeometry(cq.Matrix([
        [x, 0, 0, 0], [0, y, 0, 0], [0, 0, z, 0], [0, 0, 0, 1]])))


def stone_body(team):
    shell = weighted.rounded(FLAT, 2.0, 0, HEIGHT)
    shell = shell.faces('>Z or <Z').edges().chamfer(.4)
    seat = weighted.rounded(SEAT_WIDTH, 1.0, -.1, 1.9)
    cavity = weighted.rounded(CAVITY_WIDTH, .8, 1.79, CAVITY_TOP - 1.79)
    result = shell.cut(seat).cut(cavity)
    if team == 'fox':
        factors = (FLAT / fox.WIDTH, FLAT / fox.WIDTH, HEIGHT / fox.HEIGHT)
        result = result.cut(affine(fox.fox_cutter(), factors))
        grooves = affine(fox.side_knurl(), factors)
        for angle in (0, 90, 180, 270):
            result = result.cut(grooves.rotate((0, 0, 0), (0, 0, 1), angle))
    elif team in ('cat', 'witch'):
        spec = original.cat_emblem(1.5) if team == 'cat' else original.witch_emblem(1.4)
        cutter = original.emblem_cutter(spec,
            lambda: cq.Workplane('XY', origin=(0, 0, HEIGHT - ENGRAVE)), ENGRAVE + .1, False)
        result = result.cut(cutter)
    else:
        raise ValueError(team)
    return result.clean()


def stone_floor(clearance=FLOOR_CLEARANCE):
    plate = weighted.rounded(SEAT_WIDTH - 2 * clearance, 1.0 - clearance,
                             FLOOR_Z, FLOOR_THICKNESS)
    tongue = weighted.rounded(CAVITY_WIDTH - 2 * clearance, .8 - clearance,
                              FLOOR_Z + FLOOR_THICKNESS - .01, TONGUE_HEIGHT + .01)
    return plate.union(tongue)


def felt_reference():
    # 0.1 mm between pad and floor is the adhesive allowance, not an open
    # manufacturing claim. Measure the finished laminate before batch printing.
    return weighted.rounded(SEAT_WIDTH - .4, .8, 0, FELT)


def body_for_print(team):
    return stone_body(team).rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, HEIGHT))


def floor_for_print(clearance=FLOOR_CLEARANCE):
    return stone_floor(clearance).translate((0, 0, -FLOOR_Z))


def platform():
    # Three inward steps produce a low pagoda plinth without a roof. All
    # later ornament belongs outside the board seat, grip and storage volume.
    result = box(248, 240, 5).edges('|Z').fillet(4)
    result = result.union(box(244, 236, 4, z=5).edges('|Z').fillet(4))
    result = result.union(box(240, 232, 63, z=9).edges('|Z').fillet(4))
    result = result.cut(box(226, 218, 63.1, z=3))
    result = result.cut(box(BOARD[0] + 2 * SEAT_CLEARANCE,
                            BOARD[1] + 2 * SEAT_CLEARANCE, 7, z=BOARD_Z))
    # Wide front/back openings reach below the board for a two-handed lift.
    for y in (-116, 116):
        result = result.cut(box(44, 20, 11, y=y, z=62))
    # The lower cassette sits on the floor inside a low locating frame. The
    # frame limits sideways movement and leaves 0.4 mm clearance per side.
    inside = (TRAY[0]+2*CASSETTE_SIDE_CLEARANCE, TRAY[1]+2*CASSETTE_SIDE_CLEARANCE)
    locator = box(inside[0]+3.2, inside[1]+3.2, 6.1, z=2.9)
    locator = locator.cut(box(*inside, 6.3, z=2.8))
    result = result.union(locator)
    for x in (-40, 40):
        for y in (-65, 65):
            result = result.union(box(16, 16, 1.1, x=x, y=y, z=2.9))
    return result.clean()


def board(grooves=False):
    result = box(*BOARD)
    if grooves:
        for v in range(6):
            coordinate = -FIELD / 2 + v * PITCH
            result = result.cut(box(1.4, FIELD + 1.4, .7, x=coordinate, z=5.4))
            result = result.cut(box(FIELD + 1.4, 1.4, .7, y=coordinate, z=5.4))
    return result.clean()


def lanes():
    return [(4 + i * (LANE_WIDTH + 1.6), 42, LANE_WIDTH, LANE_LENGTH) for i in range(4)]


def tray():
    result = box(*TRAY, x=TRAY[0]/2, y=TRAY[1]/2)
    for x, y, w, d in lanes() + [(4, 4, 43, 32), (58, 5, LANE_WIDTH, LANE_WIDTH)]:
        result = result.cut(box(w, d, 31, x=x+w/2, y=y+d/2, z=TRAY_FLOOR))
    # Lower the lane dividers to expose each stone's upper face. Perimeter
    # remains full-height so the next tray rests on plastic, not on pieces.
    result = result.cut(box(110, 131, 20, x=59, y=105.5, z=12))
    # Outside finger dishes are broad and do not cut into the capstone pocket.
    for x in (0, 120):
        result = result.cut(box(14, 38, 12, x=x, y=85, z=19))
    for x, y in REGISTER_XY:
        result = result.union(box(REGISTER_WIDTH, REGISTER_WIDTH,
                                  REGISTER_HEIGHT+.1, x=x, y=y, z=TRAY[2]-.1))
        socket = REGISTER_WIDTH+2*CASSETTE_SIDE_CLEARANCE
        result = result.cut(box(socket, socket, REGISTER_SOCKET_DEPTH+.1,
                                x=x, y=y, z=-.1))
    return result.clean()


def flat_positions():
    positions = []
    for x, y, _, _ in lanes():
        for j in range(5):
            positions.append((x + LANE_WIDTH/2, y + .5 + FLAT/2 + j*FLAT, TRAY_FLOOR))
    positions.append((58 + LANE_WIDTH/2, 5 + LANE_WIDTH/2, TRAY_FLOOR))
    return positions
