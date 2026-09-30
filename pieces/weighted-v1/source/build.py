"""Export, verify, render, and package the weighted stone set."""
from pathlib import Path
import json
import sys
import cadquery as cq
import numpy as np
import trimesh
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

import stones as s

ROOT = Path(__file__).resolve().parents[1]
MESH_CLEANUP = {}
sys.path.insert(0, str(ROOT.parents[1] / 'v16-field-book' / 'source'))
from mesh_export import export_stl


def bounds(obj):
    # OCC's default bound may include a cached mesh's tessellation deflection.
    box = Bnd_Box()
    BRepBndLib.AddOptimal_s(obj.val().wrapped, box, False, False)
    x0, y0, z0, x1, y1, z1 = box.Get()
    return np.array([x1 - x0, y1 - y0, z1 - z0]), z0


def save(name, obj):
    shape = obj.val()
    assert shape.isValid() and len(shape.Solids()) == 1, name
    path = ROOT / 'models' / f'{name}.stl'
    export_stl(obj, path)
    cq.exporters.export(obj, str(path.with_suffix('.step')))
    mesh = trimesh.load_mesh(path, process=True)
    # OCC can emit a zero-area pole triangle with repeated vertex indices.
    # Remove only these triangles, without moving vertices or changing surfaces.
    degenerate = ((mesh.faces[:, 0] == mesh.faces[:, 1]) |
                  (mesh.faces[:, 1] == mesh.faces[:, 2]) |
                  (mesh.faces[:, 2] == mesh.faces[:, 0]))
    MESH_CLEANUP[name] = int(np.count_nonzero(degenerate))
    if np.any(degenerate):
        assert np.all(mesh.area_faces[degenerate] < 1e-10), name
        mesh.update_faces(~degenerate)
        mesh.remove_unreferenced_vertices()
        mesh.export(path)
        mesh = trimesh.load_mesh(path, process=True)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0, name
    assert len(mesh.split()) == 1, name
    return mesh


def package(name, items):
    scene = trimesh.Scene()
    records = []
    for index, (label, mesh, position) in enumerate(items):
        moved = mesh.copy()
        moved.apply_translation(position)
        scene.add_geometry(moved, node_name=f'{index + 1:02d}-{label}',
                           geom_name=f'{index + 1:02d}-{label}')
        records.append({'label': label, 'position_mm': position})
    assert len(scene.geometry) == len(items)
    assert np.all(scene.bounds[0] >= -.001) and np.all(scene.bounds[1][:2] <= 256)
    path = ROOT / 'plates' / f'{name}.3mf'
    path.write_bytes(scene.export(file_type='3mf'))
    readback = trimesh.load(path, force='scene')
    assert len(readback.geometry) == len(items), (name, len(readback.geometry))
    assert np.allclose(readback.bounds, scene.bounds, atol=.001)
    return {'objects': len(items), 'bounds_mm': scene.bounds.tolist(), 'parts': records}


def main():
    for directory in ('models', 'plates', 'reports', 'previews'):
        (ROOT / directory).mkdir(exist_ok=True)
    meshes = {}
    report = {'units': 'mm', 'assembled_size_mm': [20, 20, 6],
              'floor_side_clearance_mm': s.CLEARANCE,
              'shoulder_glue_gap_mm': s.SEAT_DEPTH - s.FLOOR_THICKNESS,
              'cavity_side_wall_mm': (s.WIDTH - s.CAVITY_WIDTH) / 2,
              'roof_under_emblem_mm': s.HEIGHT - s.CAVITY_TOP - s.ENGRAVE,
              'physical_acceptance': 'not printed or tested', 'teams': {}, 'plates': {}}
    f = s.floor()
    meshes['floor'] = save('stone-floor', f)
    for team in ('cat', 'witch'):
        b = s.body(team)
        assembled = b.union(f)
        dimensions, _ = bounds(assembled)
        assert np.allclose(dimensions, [20, 20, 6], atol=1e-6), (team, dimensions)
        assert b.intersect(f).val().Volume() < 1e-6
        assert b.intersect(assembled.translate((0, 0, 6))).val().Volume() < 1e-6
        assert assembled.intersect(assembled.translate((0, 0, 6))).val().Volume() < 1e-6
        wall = assembled.rotate((0, 0, 0), (1, 0, 0), 90).translate((0, 6, 10))
        wall_dimensions, wall_bottom = bounds(wall)
        assert abs(wall_bottom) < 1e-6 and abs(wall_dimensions[2] - 20) < 1e-6
        meshes[team] = save(f'{team}-body-print', s.body_for_print(team))
        # Assembly is a two-solid STEP reference, not a print STL.
        cq.exporters.export(cq.Compound.makeCompound([b.val(), f.val()]),
                            str(ROOT / 'models' / f'{team}-assembled-reference.step'))
        fill = s.rounded(s.CAVITY_WIDTH, s.CAVITY_RADIUS, 1.9, s.CAVITY_TOP - 1.9)
        report['teams'][team] = {'body_volume_mm3': b.val().Volume(),
            'floor_volume_mm3': f.val().Volume(), 'fill_to_1_9mm_volume_ml': fill.val().Volume() / 1000,
            'body_floor_overlap_mm3': b.intersect(f).val().Volume(),
            'stack_overlap_mm3': assembled.intersect(assembled.translate((0, 0, 6))).val().Volume(),
            'standing_wall_envelope_mm': wall_dimensions.tolist()}
        cap = save(f'{team}-capstone', s.original.capstone(team))
        cap.apply_translation(-cap.bounds[0])
        items = []
        for n in range(21):
            items.append((f'{team}-body', meshes[team], [18 + n % 7 * 25, 18 + n // 7 * 25, 0]))
        for n in range(21):
            items.append(('floor', meshes['floor'], [18 + n % 7 * 25, 100 + n // 7 * 25, 0]))
        items.append((f'{team}-existing-capstone', cap, [195, 18, 0]))
        report['plates'][team] = package(f'{team}-complete-set', items)
    coupon = []
    for index, clearance in enumerate((.15, .2, .25), 1):
        cf = s.floor(clearance, label=index)
        mesh = save(f'coupon-floor-{index}', cf)
        assert s.body('cat').intersect(cf).val().Volume() < 1e-6
        coupon += [(f'body-for-floor-{index}', meshes['cat'], [18 + (index - 1) * 28, 18, 0]),
                   (f'floor-{index}-{clearance:.2f}mm', mesh, [18 + (index - 1) * 28, 48, 0])]
    report['plates']['coupon'] = package('fit-coupon-first', coupon)
    report['meshes'] = {}
    report['zero_area_triangles_removed'] = MESH_CLEANUP
    for path in sorted((ROOT / 'models').glob('*.stl')):
        mesh = trimesh.load_mesh(path, process=True)
        report['meshes'][path.name] = {'watertight': bool(mesh.is_watertight),
            'winding_consistent': bool(mesh.is_winding_consistent), 'solids': len(mesh.split()),
            'volume_mm3': float(mesh.volume), 'dimensions_mm': mesh.extents.tolist()}
    (ROOT / 'reports' / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ('assembled_size_mm', 'teams')}, indent=2))
    print('Plate objects:', {k: v['objects'] for k, v in report['plates'].items()})


if __name__ == '__main__':
    main()
