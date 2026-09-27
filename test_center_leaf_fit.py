"""Center-only closed-fit regression checks; run with python -m unittest -v.

These measure solid geometry, including both end skirts and all hinge bores.
The folding check samples motion; physical coupon fit remains a separate gate.
"""
import math
import unittest

import cadquery as cq
import tak_case_pin as case
import tak_pinfit


class CenterLeafFitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.center = case.shell(1)
        cls.skirt = case.center_outer_skirt()
        cls.sides = {i: case.lid_pair(i) for i in (0, 2)}

    def test_valid_solids_and_common_resting_plane(self):
        for part in [self.center, *[p for side in self.sides.values() for p in side]]:
            self.assertTrue(part.isValid())
            self.assertEqual(len(part.Solids()), 1)
        for part in [self.center, *[side[0] for side in self.sides.values()]]:
            self.assertAlmostEqual(part.BoundingBox().zmin, -20.1, places=6)

    def test_closed_roof_fills_former_four_mm_gap(self):
        for i, y in ((0, 96), (2, 109)):
            # Local patches avoid confusing a hinge clearance with the roof gap.
            patch = self.center.intersect(case.box(8, 4, 8, 100, y, -4))
            wing = case.posed(self.sides[i][0], i, 90)
            self.assertAlmostEqual(patch.BoundingBox().zmin, -3.6, places=6)
            self.assertAlmostEqual(patch.distance(wing), 0.4, places=6)
            self.assertGreater(patch.intersect(case.box(8, 4, 3.5, 100, y, -3.5)).Volume(), 111)

    def test_end_skirts_fill_side_interfaces(self):
        for x in (0, 202.9):
            foot = self.center.intersect(case.box(2.1, 41, 16, x, 82, -20.1))
            bb = foot.BoundingBox()
            self.assertAlmostEqual(bb.xlen, 2.1, places=6)
            self.assertAlmostEqual(bb.ymin, 82.4, places=6)
            self.assertAlmostEqual(bb.ymax, 122.6, places=6)
            for i, (wing, lid) in self.sides.items():
                self.assertAlmostEqual(foot.distance(case.posed(wing, i, 90)), 0.4, places=6)

    def test_round_skirt_profile_tracks_barrel_cutouts(self):
        # Check the arc itself, at both ends and along the central span.
        # An absent skirt would pass a no-collision test, but fails the outer probes.
        for x in (1, 100, 204):
            for y, sign in ((82, 1), (123, -1)):
                for degrees in (15, 35, 55, 75):
                    a = math.radians(degrees)
                    for radius, present in ((2.85, False), (2.95, True)):
                        point = cq.Vector(x, y + sign * radius * math.cos(a), -radius * math.sin(a))
                        self.assertEqual(self.skirt.isInside(point), present, (x, y, degrees, radius))

    def test_alternating_knuckles_keep_round_relief(self):
        for i, seam in ((0, 0), (2, 1)):
            wing = self.sides[i][0]
            y = case.D.seam_y[seam]
            for k in range(case.COUNT):
                x = case.knuckle_x(k) + 1
                barrel = case.cylinder(2.4, case.L - 2, x, y, 0)
                relief = case.cylinder(2.8, case.L - 2, x, y, 0)
                center_owns = k % 2 == (1 if i == 0 else 0)
                owner, neighbor = (self.center, wing) if center_owns else (wing, self.center)
                self.assertGreater(owner.intersect(barrel).Volume(), 1)
                self.assertLess(neighbor.intersect(relief).Volume(), 1e-3)

    def test_validated_pin_axes_and_actual_bore_sizes(self):
        self.assertEqual((case.D_FIXED, case.D_FREE, case.PLUG_HOLE), (1.90, 2.20, 1.70))
        expected_axes = {'seam0': (82, 0), 'seam1': (123, 0), 'lid0': (0, 1), 'lid2': (205, 1)}
        all_parts = [self.center, *[p for side in self.sides.values() for p in side]]
        for name, axis in expected_axes.items():
            self.assertEqual(case.pin_axis(name), axis)
            for part in all_parts:
                self.assertLess(part.intersect(case.filament(name)).Volume(), 1e-3)
            y, z = axis
            side = 0 if name.endswith('0') else 2
            for k in range(case.COUNT):
                if name.startswith('seam'):
                    fixed = k % 2 == (1 if side == 0 else 0)
                    owner = self.center if fixed else self.sides[side][0]
                else:
                    fixed = k % 2 == 0
                    owner = self.sides[side][0 if fixed else 1]
                radius = 0.95 if fixed else 1.10
                x = case.knuckle_x(k) + case.L / 2
                # Mid-knuckle axial core: empty up to the bore, material just outside.
                for r, present in ((radius - .01, False), (radius + .01, True)):
                    self.assertEqual(owner.isInside(cq.Vector(x, y, z + r)), present)
        plug = tak_pinfit.plug(case.PLUG_HOLE)
        self.assertFalse(plug.isInside(cq.Vector(.84, 0, .7)))
        self.assertTrue(plug.isInside(cq.Vector(.86, 0, .7)))

    def test_full_fold_and_skirt_clearance(self):
        for i, side in self.sides.items():
            for angle in range(0, 91, 5):
                for part in side:
                    moved = case.posed(part, i, angle)
                    with self.subTest(wing=i, angle=angle):
                        self.assertLess(self.center.intersect(moved).Volume(), 1e-3)
                        self.assertGreaterEqual(self.skirt.distance(moved), .3 - 1e-6)

    def test_coupon_is_real_geometry_with_both_hinges(self):
        from export_center_closure_coupon import coupon_parts
        parts = coupon_parts(self.center, self.sides)
        self.assertEqual(len(parts), 5)
        for part in parts.values():
            self.assertTrue(part.isValid())
            self.assertEqual(len(part.Solids()), 1)
            self.assertAlmostEqual(part.BoundingBox().xlen, 30, places=6)
        coupon_volume = sum(p.Volume() for p in parts.values())
        full_volume = self.center.Volume() + sum(p.Volume() for side in self.sides.values() for p in side)
        self.assertLess(coupon_volume, 40000)  # under 40 cm3 for the complete five-piece sample
        self.assertLess(coupon_volume, .2 * full_volume)
        for i in (0, 2):
            wing = parts[f'wing-{i}']
            for angle in (0, 45, 90):
                self.assertLess(parts['center'].intersect(case.posed(wing, i, angle)).Volume(), 1e-3)


if __name__ == '__main__':
    unittest.main()
