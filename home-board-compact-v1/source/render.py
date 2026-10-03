"""Actual-mesh compact-board previews, with conserved piece inventories."""
from pathlib import Path
import json
import numpy as np
import trimesh
import design as d

PACKAGE = Path(__file__).resolve().parents[1]
r = d.load_source('compact_render_helpers','full-size-pagoda-v1/source/render.py')
r.PACKAGE = PACKAGE


def mesh(name,shared=False):
    root = d.BASE_PACKAGE if shared else PACKAGE
    return trimesh.load_mesh(root/'models'/f'{name}.stl',process=True)


def board(position=(0,0,d.BOARD_Z)):
    parts = [(r.moved(mesh('board-felt-backing'),position),r.DARK)]
    parts.append((r.box([232,224,1],[position[0],position[1],position[2]+6.5]),(.04,.07,.12)))
    for i in range(6):
        c = -105+42*i
        parts += [(r.box([1.4,211.4,.05],[position[0]+c,position[1],position[2]+7.025]),r.WHITE),
                  (r.box([211.4,1.4,.05],[position[0],position[1]+c,position[2]+7.025]),r.WHITE)]
    return parts


def flat_parts(team,position,standing=False):
    color = r.WHITE if team=='cat' else r.FOX
    components = [mesh(team+'-body-assembly',True),
                  r.moved(mesh('stone-floor',True),(0,0,d.base.FLOOR_Z)),
                  r.box([22.6,22.6,.6],[0,0,.3])]
    if standing:
        rotation = trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0])
        for m in components:m.apply_transform(rotation)
        position = np.array(position)-[0,0,min(m.bounds[0,2] for m in components)]
    return [(r.moved(m,position),color) for m in components]


def loaded_tray(team,position,keep=None,cap=True):
    parts = [(r.moved(mesh('tray'),position),r.TRAY_COLOR)]
    for i,p in enumerate(d.flat_positions()):
        if keep is None or i in keep:
            parts += flat_parts(team,np.array(p)+np.array(position))
    if cap:
        parts += [(r.moved(mesh(team+'-capstone-storage-reference'),position),
                   r.WHITE if team=='cat' else r.FOX)]
    return parts


def main():
    platform = [(mesh('platform'),r.DARK)]
    top = d.BOARD_Z+7
    in_play = platform+board()
    in_play += loaded_tray('cat',(-267,-87,0),keep=set(range(6,21)),cap=False)
    in_play += loaded_tray('fox',(155,-87,0),keep=set(range(6,21)),cap=False)
    field = [('cat',(-84,-84,top),False),('cat',(-42,-42,top),False),
             ('cat',(0,0,top),False),('fox',(0,0,top+10),False),('cat',(0,0,top+20),False),
             ('cat',(-42,42,top),True),('cat',(42,-42,top),False),
             ('fox',(84,84,top),False),('fox',(42,42,top),False),
             ('fox',(0,-42,top),False),('fox',(-42,0,top),False),('fox',(84,0,top),True)]
    for team,p,standing in field:in_play += flat_parts(team,p,standing)
    assert sum(t=='cat' for t,_,_ in field)==sum(t=='fox' for t,_,_ in field)==6
    for team,p,color in [('cat',(-84,42,top),r.WHITE),('fox',(84,-42,top),r.FOX)]:
        in_play += [(r.moved(mesh(team+'-capstone',True),p),color)]
    in_play += [(r.box([760,580,5],[0,0,-2.5]),(.16,.19,.23))]
    r.render('01-in-play','Compact Tak home board | in play',
             '240 x 232 x 43 mm | Cat left / Fox right | Same playing field',
             in_play,(0,0,15),(260,-630,690),235,size=(2400,1600))
    packed = platform+board()
    r.render('02-packed','Compact box | both cassettes hidden below',
             '43 mm including felt | Lift-out board | Transport retention still open',
             packed,(0,0,20),(350,-430,345),170)
    exploded = list(platform)
    for team,p in zip(('cat','fox'),d.TRAY_ORIGINS):
        exploded += loaded_tray(team,(p[0],p[1],60))
    exploded += board((0,0,145))
    r.render('03-storage','One level of cassettes | lift board first',
             '21 flats + one capstone each | Front/back lift tabs',exploded,
             (0,0,75),(350,-440,370),175)
    r.render('04-cassette-grip','Compact cassette | front and rear lift tabs',
             '36 mm wide | 6 mm reach | Capstone body opening retained',
             loaded_tray('cat',(0,0,0)),(56,80,14),(295,-200,210),105)
    r.render('05-board-support','Board support | four broad pads and perimeter ledge',
             'Pads stay clear of trays and front/back finger corridors',
             platform,(0,0,18),(350,-440,440),175)
    comparison = [(r.moved(mesh('platform',True),(-155,0,0)),r.DARK)]+board((-155,0,66))
    comparison += [(r.moved(mesh('platform'),(155,0,0)),r.DARK)]+board((155,0,36))
    r.render('06-size-comparison','Current left | compact variant right',
             '73 mm to 43 mm | 6.5% less footprint | Same board and full-size pieces',
             comparison,(0,0,28),(260,-700,350),195,size=(2400,1400))
    (PACKAGE/'reports/rendering.json').write_text(json.dumps({
        'source':'Exported STL geometry; felt/grid reference to shared exact-size template',
        'views':6,'in_play_inventory_per_player':{'field_flats':6,'cassette_flats':15,'capstones':1},
        'accessibility':'Large white labels, contrasting grid and clear component silhouettes; review pending',
        'physical_result':False},indent=2)+'\n')


if __name__=='__main__':
    main()
