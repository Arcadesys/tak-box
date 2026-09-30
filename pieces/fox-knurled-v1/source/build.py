"""Build one fox flat and geometry plates; check actual current tray placement."""
from pathlib import Path
import hashlib
import json
import sys
import cadquery as cq
import numpy as np
import trimesh
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
import flats as f

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO / 'v16-field-book/source'))
from mesh_export import export_stl
import tak_book as book


def bounds(shape):
    box = Bnd_Box()
    BRepBndLib.AddOptimal_s(shape.val().wrapped, box, False, False)
    return np.array(box.Get()).reshape(2, 3)


def package(name, mesh, count):
    scene = trimesh.Scene()
    for n in range(count):
        moved = mesh.copy()
        moved.apply_translation((18 + n % 7 * 25, 18 + n // 7 * 25, 0))
        scene.add_geometry(moved, node_name=f'fox-flat-{n+1:02d}', geom_name=f'fox-flat-{n+1:02d}')
    path = ROOT / 'plates' / f'{name}.3mf'
    path.write_bytes(scene.export(file_type='3mf'))
    readback = trimesh.load(path, force='scene')
    assert len(readback.geometry) == count
    assert np.allclose(readback.bounds, scene.bounds, atol=.001)
    assert np.all(scene.bounds[0] >= -.001) and np.all(scene.bounds[1][:2] < 256)
    return {'objects': count, 'bounds_mm': scene.bounds.tolist(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    for directory in ('models', 'plates', 'reports', 'previews'):
        (ROOT / directory).mkdir(parents=True, exist_ok=True)
    obj = f.flat()
    assert obj.val().isValid() and len(obj.val().Solids()) == 1
    exact = bounds(obj)
    assert np.allclose(exact, [[-9.75, -9.75, 0], [9.75, 9.75, 8]], atol=1e-6)
    path = ROOT / 'models/fox-flat.stl'
    weld = export_stl(obj, path)
    cq.exporters.export(obj, str(path.with_suffix('.step')))
    mesh = trimesh.load_mesh(path, process=True)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
    assert len(mesh.split()) == 1
    # Check stack interfaces and every orientation used as a standing wall.
    overlap = obj.intersect(obj.translate((0, 0, f.HEIGHT))).val().Volume()
    assert overlap < 1e-6
    walls = []
    for angle in (0, 90, 180, 270):
        wall = (obj.rotate((0, 0, 0), (0, 0, 1), angle)
                .rotate((0, 0, 0), (1, 0, 0), 90).translate((0, f.HEIGHT, f.WIDTH / 2)))
        b = bounds(wall)
        assert abs(b[0, 2]) < 1e-6 and np.allclose(b[1] - b[0], [19.5, 8, 19.5])
        walls.append((b[1] - b[0]).tolist())
    lanes, pocket, _ = book._ins_layout()
    z = book.DR_Z0 + book.DR_FLOOR + book.INS_FLOOR
    placed = []
    for x0, x1, y0, y1 in lanes:
        assert x1 - x0 >= f.WIDTH and y1 - y0 >= 5 * f.WIDTH
        for n in range(5):
            placed.append(obj.translate(((x0 + x1) / 2,
                y0 + (y1 - y0 - 5 * f.WIDTH) / 2 + (n + .5) * f.WIDTH, z)))
    x0, x1, y0, y1 = pocket
    assert min(x1-x0, y1-y0) >= f.WIDTH
    placed.append(obj.translate(((x0+x1)/2, (y0+y1)/2, z)))
    assert len(placed) == 21
    group = cq.Workplane(obj=cq.Compound.makeCompound([s.val() for s in placed]))
    collisions = {}
    for name, obstacle in [('insert', book.tray_insert_a()), ('tray', book.tray_a()),
                           ('closed_board_plate', book.plate('A'))]:
        volume = group.intersect(cq.Workplane(obj=obstacle)).val().Volume()
        assert volume < 1e-6, (name, volume)
        collisions[name] = volume
    report = {'units': 'mm', 'exact_dimensions_mm': (exact[1]-exact[0]).tolist(),
        'mesh': {'watertight': bool(mesh.is_watertight), 'winding_consistent': bool(mesh.is_winding_consistent),
                 'solids': len(mesh.split()), 'volume_mm3': float(mesh.volume), 'triangles': len(mesh.faces),
                 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'vertex_weld': weld},
        'knurl': {'depth_mm': f.KNURL_DEPTH, 'groove_width_mm': f.KNURL_WIDTH,
                  'horizontal_pitch_mm': f.KNURL_PITCH, 'z_band_mm': f.KNURL_Z},
        'stack_overlap_mm3': overlap, 'wall_envelopes_mm': walls,
        'tray': {'placed_stones': len(placed), 'source': 'v16-field-book/source/tak_book.py',
                 'source_sha256': hashlib.sha256((REPO/'v16-field-book/source/tak_book.py').read_bytes()).hexdigest(),
                 'lane_width_mm': lanes[0][1]-lanes[0][0], 'lane_length_mm': lanes[0][3]-lanes[0][2],
                 'side_clearance_mm': (book.LANE-f.WIDTH)/2,
                 'five_stone_end_slack_mm': lanes[0][3]-lanes[0][2]-5*f.WIDTH,
                 'obstacle_overlap_mm3': collisions},
        'plates': {'sample': package('fox-sample-first', mesh, 1),
                   'set': package('fox-21-flats', mesh, 21)},
        'physical_acceptance': 'not printed or tested'}
    (ROOT / 'reports/verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
