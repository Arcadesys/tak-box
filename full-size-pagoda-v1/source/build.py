"""Build and verify the foundation, without contacting generation or printers."""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import subprocess
import sys
import cadquery as cq
import numpy as np
import trimesh
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
import design as d

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(d.ROOT / 'v16-field-book/source'))
from mesh_export import export_stl
REPORT = {'units': 'mm', 'source_revision': subprocess.check_output(
    ['git', 'rev-parse', 'HEAD'], cwd=d.ROOT, text=True).strip(),
    'physical_fit': 'not tested', 'parts': {}, 'plates': {}, 'checks': {}, 'capstones': {}}


def bounds(obj):
    bound = Bnd_Box()
    BRepBndLib.AddOptimal_s(obj.val().wrapped, bound, False, False)
    v = np.array(bound.Get())
    return np.array([v[:3], v[3:]])


def save(name, obj):
    assert obj.val().isValid() and len(obj.val().Solids()) == 1, name
    path = PACKAGE / 'models' / f'{name}.stl'
    export_stl(obj, path)
    cq.exporters.export(obj, str(path.with_suffix('.step')))
    mesh = trimesh.load_mesh(path, process=True)
    # Remove only repeated-index zero-area tessellation triangles, as in the
    # existing weighted package. No vertex movement or surface repair.
    bad = ((mesh.faces[:, 0] == mesh.faces[:, 1]) |
           (mesh.faces[:, 1] == mesh.faces[:, 2]) |
           (mesh.faces[:, 0] == mesh.faces[:, 2]))
    if bad.any():
        assert np.all(mesh.area_faces[bad] < 1e-10)
        mesh.update_faces(~bad)
        mesh.remove_unreferenced_vertices()
        mesh.export(path)
        mesh = trimesh.load_mesh(path, process=True)
    check_mesh(name, mesh)
    REPORT['parts'][name].update({'solid_valid': True,
        'cad_dimensions_mm': (bounds(obj)[1]-bounds(obj)[0]).tolist(),
        'zero_area_triangles_removed': int(bad.sum())})
    return mesh


def check_mesh(name, mesh):
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0, name
    assert len(mesh.split()) == 1, name
    REPORT['parts'][name] = {'dimensions_mm': mesh.extents.tolist(),
        'volume_mm3': float(mesh.volume), 'watertight': True,
        'winding_consistent': True, 'components': 1}


def package(name, items):
    scene = trimesh.Scene()
    for i, (label, mesh, position) in enumerate(items):
        m = mesh.copy()
        m.apply_translation(position)
        scene.add_geometry(m, node_name=f'{i+1:02d}-{label}', geom_name=f'{i+1:02d}-{label}')
    path = PACKAGE / 'plates' / f'{name}.3mf'
    assert np.all(scene.bounds[0] >= -.001) and np.all(scene.bounds[1][:2] <= 256), name
    path.write_bytes(scene.export(file_type='3mf'))
    read = trimesh.load(path, force='scene')
    assert len(read.geometry) == len(items), name
    assert np.allclose(read.bounds, scene.bounds, atol=.002), name
    assert set(read.geometry) == set(scene.geometry), name
    for key in scene.geometry:
        assert np.isclose(read.geometry[key].volume, scene.geometry[key].volume, rtol=1e-5)
    with ZipFile(path) as z:
        assert z.testzip() is None
        assert b'unit="millimeter"' in z.read('3D/3dmodel.model')
    REPORT['plates'][name] = {'objects': len(items), 'units': 'millimeter',
        'bounds_mm': read.bounds.tolist(), 'labels_and_volumes_match': True,
        'geometry_only': True}


def capstone(species):
    source = d.ROOT / 'pieces/fox-cat-capstones-v4/models' / f'{species}-capstone.stl'
    mesh = trimesh.load_mesh(source, process=True)
    before = mesh.extents.copy()
    # Uniform scaling retains the exact existing sculptural proportions.
    factor = min(25 / max(before[:2]), 35 / before[2])
    mesh.apply_scale(factor)
    mesh.apply_translation([-mesh.bounds.mean(axis=0)[0],
                            -mesh.bounds.mean(axis=0)[1], -mesh.bounds[0, 2]])
    path = PACKAGE / 'models' / f'{species}-capstone.stl'
    mesh.export(path)
    mesh = trimesh.load_mesh(path, process=True)
    assert max(mesh.extents[:2]) <= 25.00001 and mesh.extents[2] <= 35.00001
    check_mesh(f'{species}-capstone', mesh)
    REPORT['capstones'][species] = {'source': str(source.relative_to(d.ROOT)),
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'uniform_scale': factor, 'dimensions_mm': mesh.extents.tolist(),
        'ballast_cavity': False}
    return mesh


def storage_pose(mesh):
    m = mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
    assert np.all(m.extents <= [43, 32, 28]), m.extents
    position = np.array([4+(43-m.extents[0])/2, 4+(32-m.extents[1])/2, d.TRAY_FLOOR])
    m.apply_translation(position - m.bounds[0])
    return m


def main():
    for folder in ('models', 'plates', 'reports', 'previews'):
        (PACKAGE/folder).mkdir(exist_ok=True)
    models = {}
    bodies = {}
    floor = d.stone_floor()
    felt = d.felt_reference()
    models['stone-floor'] = save('stone-floor', d.floor_for_print())
    for team in ('cat', 'fox', 'witch'):
        body = d.stone_body(team)
        bodies[team] = body
        assert np.allclose(bounds(body)[1]-bounds(body)[0], [25,25,10], atol=1e-6)
        assert body.intersect(floor).val().Volume() < 1e-7
        assert body.intersect(felt).val().Volume() < 1e-7
        assembled = cq.Compound.makeCompound([body.val(), floor.val(), felt.val()])
        cq.exporters.export(assembled, str(PACKAGE/'models'/f'{team}-assembled-reference.step'))
        full = cq.Workplane(obj=assembled)
        assert full.intersect(full.translate((0,0,10))).val().Volume() < 1e-7
        for axis in ((1,0,0), (0,1,0)):
            wall = full.rotate((0,0,0), axis, 90)
            bb = bounds(wall)
            assert abs((bb[1]-bb[0])[2]-25) < 1e-6
        models[f'{team}-body-print'] = save(f'{team}-body-print', d.body_for_print(team))
        model = trimesh.load_mesh(PACKAGE/'models'/f'{team}-body-print.stl')
        model.apply_transform(trimesh.transformations.rotation_matrix(np.pi,[1,0,0]))
        model.apply_translation([0,0,10])
        model.export(PACKAGE/'models'/f'{team}-body-assembly.stl')
    models['platform'] = save('platform', d.platform())
    models['tray'] = save('tray', d.tray())
    models['board-felt-backing'] = save('board-felt-backing', d.board())
    models['board-grooved-option'] = save('board-grooved-option', d.board(True))
    caps = {s: capstone(s) for s in ('cat','fox')}
    # Closure coupons keep the established three per-side clearances.
    coupon = []
    for i, clearance in enumerate((.15,.2,.25)):
        name = f'floor-clearance-{int(clearance*100):02d}'
        models[name] = save(name, d.floor_for_print(clearance))
        assert bodies['cat'].intersect(d.stone_floor(clearance)).val().Volume() < 1e-7
        coupon.extend([(f'cat-body-{int(clearance*100)}', models['cat-body-print'],(20+i*32,20,0)),
                       (name,models[name],(20+i*32,52,0))])
    package('closure-coupon',coupon)
    for team in ('cat','fox'):
        package(f'{team}-flats-21',[(f'{team}-body-{i+1}',models[f'{team}-body-print'],
            (18+(i%7)*29,18+(i//7)*29,0)) for i in range(21)])
    package('floors-21', [('floor-'+str(i+1),models['stone-floor'],
            (18+(i%7)*27,18+(i//7)*27,0)) for i in range(21)])
    package('fox-cat-capstones',[(s+'-capstone',caps[s],(25+i*40,25,0)) for i,s in enumerate(('cat','fox'))])
    for name in ('platform','tray','board-felt-backing','board-grooved-option'):
        m = models[name]
        package(name, [(name,m,(4-m.bounds[0,0],4-m.bounds[0,1],-m.bounds[0,2]))])
    # Check all 21 exact piece bodies and closures against the actual tray.
    loaded = {}
    tray = d.tray()
    positions = d.flat_positions()
    assert d.LANE_COUNTS == (5,5,6,5) and len(positions) == 21
    for (_, _, width, length), count in zip(d.lanes(), d.LANE_COUNTS):
        assert width-d.FLAT >= .6-1e-7 and abs(length-count*d.FLAT-1) < 1e-7
    for team in ('cat','fox'):
        maximum = 0.0
        for position in positions:
            for obj in (bodies[team], floor, felt):
                maximum = max(maximum, tray.intersect(obj.translate(position)).val().Volume())
        assert maximum < 1e-6, (team,maximum)
        pose = storage_pose(caps[team])
        assert pose.bounds[1,2] < 30
        # Its entire actual-mesh AABB is inside the carved pocket: a
        # conservative zero-collision proof, no mesh Boolean assumption.
        assert np.all(pose.bounds[0] >= [4,4,2]-np.array([1e-5]*3))
        assert np.all(pose.bounds[1] <= [47,36,30]+np.array([1e-5]*3))
        pose.export(PACKAGE/'models'/f'{team}-capstone-storage-reference.stl')
        loaded[team] = {'flat_count':len(positions),'maximum_cad_overlap_mm3':maximum,
            'capstone_storage_bounds_mm':pose.bounds.tolist(),
            'capstone_to_next_tray_floor_mm':30-float(pose.bounds[1,2])}
    base = d.platform()
    board = d.board().translate((0,0,d.BOARD_Z))
    for z in d.TRAY_Z:
        placed = tray.translate((-60,-87,z))
        assert base.intersect(placed).val().Volume() < 1e-6
        assert placed.intersect(board).val().Volume() < 1e-6
    assert tray.intersect(tray.translate((0,0,30))).val().Volume() < 1e-6
    # Witness a support contact, then sample the specified sideways clearance.
    lower = tray.translate((-60,-87,d.TRAY_Z[0]))
    assert base.intersect(lower.translate((0,0,-.01))).val().Volume() > 1
    assert tray.intersect(tray.translate((0,0,29.99))).val().Volume() > .1
    for dx, dy in ((.39,0),(-.39,0),(0,.39),(0,-.39)):
        assert base.intersect(lower.translate((dx,dy,0))).val().Volume() < 1e-6
        assert tray.intersect(tray.translate((dx,dy,30))).val().Volume() < 1e-6
    for dz in (0,.1,.3,1,3,10,40,80,180):
        assert base.intersect(board.translate((0,0,dz))).val().Volume() < 1e-6
        # Board is removed before either tray is raised.
        for z in d.TRAY_Z:
            assert base.intersect(tray.translate((-60,-87,z+dz))).val().Volume() < 1e-6
    REPORT['checks'] = {'flat_finished_envelope_mm':[25,25,10],
        'felt_mm':d.FELT,'adhesive_allowance_mm':d.FLOOR_Z-d.FELT,
        'roof_under_emblem_mm':d.HEIGHT-d.CAVITY_TOP-d.ENGRAVE,
        'floor_side_clearance_mm':d.FLOOR_CLEARANCE,
        'field_mm':[d.FIELD,d.FIELD],'pitch_mm':d.PITCH,
        'centered_flat_gap_mm':d.PITCH-d.FLAT,'tray_body_size_mm':list(d.TRAY),
        'cassette_registered_size_mm':[120,174,31],
        'cassette_row_counts':list(d.LANE_COUNTS),
        'separate_21st_flat_pocket':False,
        'two_loaded_trays':loaded,'board_seat_side_clearance_mm':d.SEAT_CLEARANCE,
        'platform_size_mm':[248,240,72], 'felt_play_surface_top_mm':73,
        'motion':'Board first, then trays; 9 sampled vertical offsets; no CAD overlaps',
        'transport_retention':'not established; no latch or lid in this foundation',
        'cassette_location':{'frame_clearance_per_side_mm':d.CASSETTE_SIDE_CLEARANCE,
            'lower_supports':4,'stack_registration_pins':4,
            'socket_depth_mm':d.REGISTER_SOCKET_DEPTH,
            'pin_height_mm':d.REGISTER_HEIGHT,
            'lateral_samples_mm':[-.39,.39],'support_contact_probes_passed':True},
        'stacked_tray_load':'Perimeter rim contact with locating pins; pieces remain below next tray floor'}
    # Exact-size felt grid can be printed at 100%; colours do not carry labels.
    lines = []
    for i in range(6):
        x = 11+i*42; y = 7+i*42
        lines += [f'<path d="M{x} 7V217"/>', f'<path d="M11 {y}H221"/>']
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="232mm" height="224mm" viewBox="0 0 232 224"><rect width="232" height="224" fill="#111827"/><g stroke="white" stroke-width="1.4">'+''.join(lines)+'</g></svg>'
    (PACKAGE/'models/felt-grid-100-percent.svg').write_text(svg)
    REPORT['source_hashes'] = {str(p.relative_to(d.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [Path(d.weighted.__file__),Path(d.fox.__file__),Path(d.original.__file__),
                  d.ROOT/'v16-field-book/source/mesh_export.py', *sorted((PACKAGE/'source').glob('*.py'))]}
    (PACKAGE/'reports/verification.json').write_text(json.dumps(REPORT,indent=2)+'\n')
    print(json.dumps({'verified_parts':len(REPORT['parts']), 'verified_plates':len(REPORT['plates']),
        'storage':loaded,'platform_mm':[248,240,72]},indent=2),flush=True)


if __name__ == '__main__':
    main()
