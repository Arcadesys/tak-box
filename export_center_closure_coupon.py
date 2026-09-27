"""Export the revised center and a 30 mm real-geometry closure coupon.

No slicer or printer configuration is required. Existing wing/lid print files
are deliberately not regenerated. Run the regression suite before exporting.
"""
import argparse
import json
from pathlib import Path

import cadquery as cq
import tak_case_pin as case

COUPON_LENGTH = 30.0
# Crop 30 mm from each main hinge into its wing. Preserve the complete X=0
# end skirt and one full + one partial knuckle at both seams.
COUPON_Y0, COUPON_Y1 = 52.0, 153.0


def coupon_parts(center=None, sides=None):
    if center is None:
        center = case.shell(1)
    if sides is None:
        sides = {i: case.lid_pair(i) for i in (0, 2)}
    crop = case.box(COUPON_LENGTH, COUPON_Y1 - COUPON_Y0, 30,
                    0, COUPON_Y0, -21)
    parts = {'center': center.intersect(crop).clean()}
    for i, (wing, lid) in sides.items():
        parts[f'wing-{i}'] = wing.intersect(crop).clean()
        parts[f'lid-{i}'] = lid.intersect(crop).clean()
    return parts


def print_pose(shape, face_down=False):
    if face_down:
        shape = shape.rotate((0, 0, 0), (1, 0, 0), 180)
    bb = shape.BoundingBox()
    return shape.translate((-bb.xmin, -bb.ymin, -bb.zmin))


def export(out):
    out.mkdir(parents=True, exist_ok=True)
    center = case.shell(1)
    sides = {i: case.lid_pair(i) for i in (0, 2)}
    parts = coupon_parts(center, sides)
    printable = {'center-row-revised': print_pose(center, True)}
    printable.update({f'coupon-{name}': print_pose(shape, not name.startswith('wing'))
                      for name, shape in parts.items()})
    for name, shape in printable.items():
        assert shape.isValid() and len(shape.Solids()) == 1, name
        assert abs(shape.BoundingBox().zmin) < 1e-6, name
        cq.exporters.export(shape, str(out / f'{name}.stl'), tolerance=.02, angularTolerance=.1)
    closed = cq.Assembly(name='closure-coupon')
    for name, shape in parts.items():
        if name != 'center':
            i = int(name[-1])
            shape = case.posed(shape, i, 90)
        closed.add(shape, name=name)
    closed.save(str(out / 'coupon-closed.step'))
    cq.exporters.export(center, str(out / 'center-row-revised.step'))
    report = {
        'physical_print_tested': False,
        'clearance_mm': case.CENTER_CLEARANCE,
        'underside_skin_depth_mm': case.CENTER_SKIN_DEPTH,
        'center_end_thickness_mm': case.CENTER_END_T,
        'resting_plane_z_mm': center.BoundingBox().zmin,
        'hinge_axes_yz_mm': {name: case.pin_axis(name) for name in ('seam0', 'seam1', 'lid0', 'lid2')},
        'bores_mm': {'fixed': case.D_FIXED, 'free': case.D_FREE, 'plug': case.PLUG_HOLE},
        'coupon_length_mm': COUPON_LENGTH,
        'coupon_solid_volume_mm3': sum(s.Volume() for s in parts.values()),
        'closed_skirt_to_wing_gap_mm': {
            str(i): case.center_outer_skirt().distance(case.posed(side[0], i, 90))
            for i, side in sides.items()
        },
        'exports': {name: {'single_valid_solid': shape.isValid() and len(shape.Solids()) == 1,
                           'volume_mm3': shape.Volume(),
                           'size_mm': [shape.BoundingBox().xlen, shape.BoundingBox().ylen, shape.BoundingBox().zlen]}
                    for name, shape in printable.items()},
    }
    (out / 'geometry-measurements.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'exports'}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).parent / 'center-closure-coupon')
    export(parser.parse_args().output_dir)
