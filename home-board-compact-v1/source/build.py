"""Export and verify the compact variant without touching the original package."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import cadquery as cq
import numpy as np
import trimesh
import design as d

PACKAGE = Path(__file__).resolve().parents[1]
helpers = d.base.load_source('compact_export_helpers','full-size-pagoda-v1/source/build.py')
helpers.PACKAGE = PACKAGE
helpers.REPORT = {'units':'mm','source_revision':subprocess.check_output(
    ['git','rev-parse','HEAD'],cwd=d.ROOT,text=True).strip(),
    'physical_fit':'not tested','parts':{},'plates':{},'checks':{}}
REPORT = helpers.REPORT


def overlap(a,b):
    return a.intersect(b).val().Volume()


def clear(a,b,label):
    amount = overlap(a,b)
    assert amount < 1e-6,(label,amount)
    return amount


def main():
    for name in ('models','plates','reports','previews'):
        (PACKAGE/name).mkdir(exist_ok=True)
    tray, platform = d.tray(),d.platform()
    models = {'tray':helpers.save('tray',tray),
              'platform':helpers.save('platform',platform),
              'grip-coupon-front':helpers.save('grip-coupon-front',d.grip_coupon()),
              'grip-coupon-rear':helpers.save('grip-coupon-rear',d.grip_coupon(False))}
    # Share the exact existing backing and board plates; no smaller field.
    for name in ('board-felt-backing','board-grooved-option'):
        for extension in ('step','stl'):
            shutil.copyfile(d.BASE_PACKAGE/'models'/f'{name}.{extension}',
                            PACKAGE/'models'/f'{name}.{extension}')
        models[name] = trimesh.load_mesh(PACKAGE/'models'/f'{name}.stl',process=True)
        helpers.check_mesh(name,models[name])
        obj = cq.importers.importStep(str(PACKAGE/'models'/f'{name}.step'))
        assert obj.val().isValid() and len(obj.val().Solids())==1
        assert np.allclose(models[name].extents,d.BOARD,atol=.002)
    for name in ('platform','tray','board-felt-backing','board-grooved-option'):
        mesh = models[name]
        helpers.package(name,[(name,mesh,(4-mesh.bounds[0,0],4-mesh.bounds[0,1],-mesh.bounds[0,2]))])
        if name.startswith('board-'):
            # Keep exact existing byte identity and matched prior slice evidence.
            shutil.copyfile(d.BASE_PACKAGE/'plates'/f'{name}.3mf',PACKAGE/'plates'/f'{name}.3mf')
    coupons = []
    for i,name in enumerate(('grip-coupon-front','grip-coupon-rear')):
        mesh = models[name]
        coupons.append((name,mesh,(10+i*50-mesh.bounds[0,0],10-mesh.bounds[0,1],-mesh.bounds[0,2])))
    helpers.package('grip-coupons',coupons)

    assert d.LANE_COUNTS == (5,5,6,5)
    positions = d.flat_positions()
    assert len(positions)==21
    for (_,_,width,length),count in zip(d.lanes(),d.LANE_COUNTS):
        assert abs(width-d.FLAT-.6)<1e-6 and abs(length-count*d.FLAT-1)<1e-6
    loaded = {}
    floor,felt = d.base.stone_floor(),d.base.felt_reference()
    for team in ('cat','fox'):
        body = d.base.stone_body(team)
        assert np.allclose(helpers.bounds(body)[1]-helpers.bounds(body)[0],[25,25,10],atol=1e-6)
        maximum = 0
        for position in positions:
            for part in (body,floor,felt):
                maximum = max(maximum,clear(tray,part.translate(position),(team,position)))
            assert overlap(tray,body.translate((position[0],position[1],position[2]-.01))) > .1
            for dz in (0,1,10):
                clear(tray,d.box(25,25,10,x=position[0],y=position[1],z=position[2]+dz),'flat envelope removal')
        cap = trimesh.load_mesh(d.BASE_PACKAGE/'models'/f'{team}-capstone-storage-reference.stl',process=True)
        cap.apply_translation((d.SIDE_WALL-4,0,0))
        cap.export(PACKAGE/'models'/f'{team}-capstone-storage-reference.stl')
        helpers.check_mesh(team+'-capstone-storage-reference',cap)
        assert np.all(cap.bounds[0] >= [d.SIDE_WALL,4,d.CAP_SEAT_Z]-np.array([1e-5]*3))
        assert np.all(cap.bounds[1] <= [d.SIDE_WALL+43,36,30]+np.array([1e-5]*3))
        bounds_box = d.box(*cap.extents,x=cap.bounds.mean(axis=0)[0],
                          y=cap.bounds.mean(axis=0)[1],z=cap.bounds[0,2])
        clear(tray,bounds_box,'conservative actual-capstone bounding box')
        loaded[team] = {'flats':21,'maximum_cad_overlap_mm3':maximum,
            'capstone_local_bounds_mm':cap.bounds.tolist(),
            'capstone_to_board_mm':d.BOARD_Z-(4+float(cap.bounds[1,2])),
            'flat_to_board_mm':d.BOARD_Z-(4+d.FLAT_SEAT_Z+10)}

    board = d.base.board().translate((0,0,d.BOARD_Z))
    placed = [tray.translate(origin) for origin in d.TRAY_ORIGINS]
    clear(platform,board,'seated board')
    clear(placed[0],placed[1],'neighbour cassettes')
    assert overlap(platform,board.translate((0,0,-.01))) > 1
    # Each wide pad reaches the board, not just a nominal floating plane.
    for x,y in d.PAD_XY:
        witness = d.box(10,10,.01,x=x,y=y,z=d.BOARD_Z-.01)
        assert abs(overlap(platform,witness)-witness.val().Volume())<1e-6
    for obj in placed:
        clear(platform,obj,'seated cassette')
        clear(board,obj,'cassette below board')
        assert overlap(platform,obj.translate((0,0,-.01))) > .1
    for dx,dy in ((.39,0),(-.39,0),(0,.39),(0,-.39)):
        for i,obj in enumerate(placed):
            clear(platform,obj.translate((dx,dy,0)),'cassette lateral allowance')
            clear(placed[1-i],obj.translate((dx,dy,0)),'neighbour clearance')
    clear(placed[0].translate((.39,0,0)),placed[1].translate((-.39,0,0)),'both trays towards centre')
    offsets = (0,.1,.3,1,3,10,40,80,180)
    for dz in offsets:
        clear(platform,board.translate((0,0,dz)),'board vertical removal')
        for i,obj in enumerate(placed):
            clear(platform,obj.translate((0,0,dz)),'cassette vertical removal')
            clear(placed[1-i],obj.translate((0,0,dz)),'cassette removal with neighbour retained')
    # Finger proxies approach down the clear end corridors, then insert
    # 2 mm below each lip. They move with the cassette during a loaded lift.
    for i,origin in enumerate(d.TRAY_ORIGINS):
        for insertion in (0,1,2):
            for finger in d.finger_proxies(origin,insertion):
                clear(platform,finger,'finger corridor')
                clear(placed[i],finger,'finger insertion')
                clear(placed[1-i],finger,'finger neighbour clearance')
        for finger in d.finger_proxies(origin):
            for dz in offsets:
                clear(platform,finger.translate((0,0,dz)),'finger plus cassette lift')
    for y in (-112,112):
        clear(platform,d.box(28,14,12,x=0,y=y,z=24),'board finger opening')
    # Tab load path has a real solid join and a 2 mm outer lip before chamfer.
    for y in (.5,d.TRAY[1]-.5):
        witness = d.box(20,1,2,x=d.TAB_CENTER_X,y=y,z=27)
        assert abs(overlap(tray,witness)-witness.val().Volume())<1e-6
    assert np.allclose(models['platform'].extents,d.PLATFORM,atol=.002)
    assert np.allclose(models['tray'].extents,[112.2,186,30],atol=.002)
    REPORT['checks'] = {'platform_mm':list(d.PLATFORM),'packed_with_felt_mm':[240,232,43],
        'previous_packed_mm':[248,240,73],'field_mm':[210,210],'pitch_mm':42,
        'board_shared_dimensions_mm':list(d.BOARD),'tray_body_mm':list(d.TRAY),
        'tray_with_tabs_mm':[112.2,186,30],'row_counts':list(d.LANE_COUNTS),
        'capstone_pocket_mm':[43,32],'front_opening_mm':28,'capstone_seat_z_mm':5,
        'flat_seat_z_mm':18,'flat_above_dividers_mm':8,'flat_to_board_mm':4,
        'tab_width_mm':d.TAB_WIDTH,'tab_depth_mm':d.TAB_DEPTH,
        'tab_tip_thickness_before_chamfer_mm':2,'tab_roof_slope_degrees':45,
        'capstone_and_tab_chamfer_mm':.5,'divider_chamfer_mm':d.DIVIDER_CHAMFER,
        'two_loaded_cassettes':loaded,
        'board_support_pads':4,'board_support_pad_mm':[12,12],
        'support_contact_probes_passed':True,'lateral_samples_mm':[-.39,.39],
        'board_and_each_cassette_removal_offsets_mm':list(offsets),
        'finger_proxy_mm':[28,14,12],'finger_insertion_mm':[0,1,2],
        'board_lift_opening_width_mm':44,'board_under_edge_access_mm':12,
        'board_finger_proxy_mm':[28,14,12],
        'finger_plus_cassette_lift_samples_passed':True,
        'finger_proxy_caution':'Geometric empty-volume check only; actual hand comfort/strength untested',
        'transport_retention':'No latch, lid or spill-free transport acceptance',
        'compatibility':'Existing full-size pieces and board retained; platform/cassettes replace the stacked geometry'}
    sources = [*sorted((PACKAGE/'source').glob('*.py')),
        d.BASE_PACKAGE/'source/design.py',d.BASE_PACKAGE/'source/build.py',
        d.ROOT/'v16-field-book/source/mesh_export.py',
        Path(d.base.weighted.__file__),Path(d.base.fox.__file__),Path(d.base.original.__file__)]
    REPORT['source_sha256'] = {str(p.relative_to(d.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    REPORT['shared_geometry_sha256'] = {str(p.relative_to(d.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted((d.BASE_PACKAGE/'models').glob('*.stl'))}
    (PACKAGE/'reports/verification.json').write_text(json.dumps(REPORT,indent=2)+'\n')
    print(json.dumps({'valid_meshes':len(REPORT['parts']),'valid_plates':len(REPORT['plates']),
                     'packed_mm':[240,232,43],'checks':'passed','loaded':loaded},indent=2),flush=True)


if __name__=='__main__':
    main()
