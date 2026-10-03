"""Compact single-level home board. Dimensions in millimetres.

Reuse the full-size stones, capstones and lift-out board without scaling.
Keep the stacked-cassette package intact as a separate option.
"""
from pathlib import Path
import importlib.util
import cadquery as cq

ROOT = Path(__file__).resolve().parents[2]
BASE_PACKAGE = ROOT/'full-size-pagoda-v1'
spec = importlib.util.spec_from_file_location('compact_piece_baseline', BASE_PACKAGE/'source/design.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
load_source = base.load_source
box = base.box
FLAT, HEIGHT, PITCH, FIELD = base.FLAT, base.HEIGHT, base.PITCH, base.FIELD
BOARD = base.BOARD
BOARD_Z = 36.0
PLATFORM = (240.0,232.0,42.0)
TRAY = (112.2,174.0,30.0)
SIDE_WALL = 2.5
LANE_WIDTH = base.LANE_WIDTH
LANE_COUNTS = base.LANE_COUNTS
LANE_END = base.LANE_END
FLAT_SEAT_Z = base.FLAT_SEAT_Z
DIVIDER_TOP_Z = base.DIVIDER_TOP_Z
CAP_SEAT_Z = base.CAP_SEAT_Z
CAP_GRIP_WIDTH = base.CAP_GRIP_WIDTH
CAP_GRIP_BOTTOM_Z = base.CAP_GRIP_BOTTOM_Z
CONTACT_CHAMFER = base.CONTACT_CHAMFER
DIVIDER_CHAMFER = .4
TAB_WIDTH = 36.0
TAB_DEPTH = 6.0
TAB_TIP_BOTTOM = 28.0
TAB_CENTER_X = TRAY[0]/2
TRAY_ORIGINS = ((-112.6,-87.0,4.0),(.4,-87.0,4.0))
PAD_XY = ((-98,-100),(98,-100),(-98,100),(98,100))
SIDE_CLEARANCE = .4
CAP_CENTER_X = SIDE_WALL + 43/2


def lanes():
    return [(SIDE_WALL+i*(LANE_WIDTH+1.6), LANE_END-(count*FLAT+1),
             LANE_WIDTH,count*FLAT+1) for i,count in enumerate(LANE_COUNTS)]


def flat_positions():
    result = []
    for (x,y,width,_),count in zip(lanes(),LANE_COUNTS):
        result.extend((x+width/2,y+.5+FLAT/2+i*FLAT,FLAT_SEAT_Z) for i in range(count))
    return result


def tab():
    # The underside grows outward by 1 mm per 1 mm layer height. The outer
    # lip is 2 mm thick rather than ending in a sharp zero-thickness tip.
    return (cq.Workplane('YZ').polyline([
        (0,TAB_TIP_BOTTOM-TAB_DEPTH),(-TAB_DEPTH,TAB_TIP_BOTTOM),
        (-TAB_DEPTH,TRAY[2]),(0,TRAY[2])
    ]).close().extrude(TAB_WIDTH).translate((TAB_CENTER_X-TAB_WIDTH/2,0,0)))


def tray():
    result = box(*TRAY,x=TRAY[0]/2,y=TRAY[1]/2)
    for x,y,w,length in lanes():
        result = result.cut(box(w,length,31,x=x+w/2,y=y+length/2,z=FLAT_SEAT_Z))
    result = result.cut(box(43,32,31,x=CAP_CENTER_X,y=20,z=CAP_SEAT_Z))
    grip = box(CAP_GRIP_WIDTH,12,20,x=CAP_CENTER_X,y=4,z=CAP_GRIP_BOTTOM_Z)
    result = result.cut(grip.edges('|Z').fillet(2))
    result = result.cut(box(107.2,131,20,x=TRAY[0]/2,y=105.5,z=DIVIDER_TOP_Z))
    x,y,width,_ = lanes()[2]
    result = result.cut(box(width+3.2,28,20,x=x+width/2,y=28,z=DIVIDER_TOP_Z))
    for x,y,width,_ in lanes():
        notch = box(base.FINGER_NOTCH_WIDTH,12,12,x=x+width/2,y=y-5,z=base.FINGER_NOTCH_Z)
        result = result.cut(notch.edges('|Z').fillet(2))
    front = tab()
    rear = front.mirror('XZ').translate((0,TRAY[1],0))
    result = result.union(front).union(rear).clean()
    for level in (DIVIDER_TOP_Z,CAP_GRIP_BOTTOM_Z):
        edges = [e for e in result.val().Edges()
                 if abs(e.BoundingBox().zmin-level)<1e-6 and
                    abs(e.BoundingBox().zmax-level)<1e-6]
        amount = DIVIDER_CHAMFER if level==DIVIDER_TOP_Z else CONTACT_CHAMFER
        result = result.newObject(edges).chamfer(amount)
        assert result.val().isValid(), ('contact chamfer',level)
    edges = [e for e in result.val().Edges()
             if abs(e.BoundingBox().zmin-30)<1e-6 and abs(e.BoundingBox().zmax-30)<1e-6
             and any(abs(e.BoundingBox().ymin-y)<1e-6 and abs(e.BoundingBox().ymax-y)<1e-6
                     for y in (-TAB_DEPTH,TRAY[1]+TAB_DEPTH))]
    assert len(edges)==2
    result = result.newObject(edges).chamfer(CONTACT_CHAMFER)
    assert result.val().isValid(), 'tab lip chamfer'
    return result.clean()


def platform():
    result = box(*PLATFORM).edges('|Z').fillet(4)
    result = result.cut(box(230,218,33.1,z=3))
    result = result.cut(box(BOARD[0]+.6,BOARD[1]+.6,7,z=BOARD_Z))
    for y in (-116,116):
        result = result.cut(box(44,20,19,y=y,z=24))
    # One low frame leaves .4 mm at both outside edges and a .8 mm gap
    # between trays. No narrow centre rail intrudes into that gap.
    frame = box(229.2,178,6.1,z=2.9).cut(box(226,174.8,6.3,z=2.8))
    result = result.union(frame)
    for origin in TRAY_ORIGINS:
        for dx in (-35,35):
            for y in (-60,60):
                result = result.union(box(14,14,1.1,x=origin[0]+TRAY[0]/2+dx,y=y,z=2.9))
    # The board bears on four wide pads and the perimeter ledge, keeping
    # the front/back finger corridors beside the lift tabs unobstructed.
    for x,y in PAD_XY:
        result = result.union(box(12,12,BOARD_Z-2.9,x=x,y=y,z=2.9))
    return result.clean()


def grip_coupon(front=True):
    section_y = 4 if front else TRAY[1]-4
    return tray().intersect(box(40,20,31,x=TAB_CENTER_X,y=section_y))


def finger_proxies(origin, insertion=2):
    # A labelled geometry proxy, not an assertion about any person's hand:
    # 28 mm wide, 14 mm deep, 12 mm tall. It enters 2 mm under the tab tip.
    x = origin[0]+TAB_CENTER_X
    front_y = -107+insertion
    rear_y = 107-insertion
    return (box(28,14,12,x=x,y=front_y+7,z=18),
            box(28,14,12,x=x,y=rear_y-7,z=18))
