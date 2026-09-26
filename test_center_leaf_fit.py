"""CAD fit checks for the center leaf before committing to a full wing print.

Run with ``python -m unittest test_center_leaf_fit``. No slicer is required.
"""
import unittest

import tak_case_pin as case


class CenterLeafFitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.center = case.shell(1)
        cls.wings = {i: case.lid_pair(i)[0] for i in (0, 2)}

    def test_alternating_knuckles_have_matching_round_cutouts(self):
        """Both halves of each seam have relief for the other half's barrels."""
        for wing_i, seam_i in ((0, 0), (2, 1)):
            y = case.D.seam_y[seam_i]
            z = case.D.hinge_z
            wing = self.wings[wing_i]
            for k in range(case.COUNT):
                # Check the middle of the knuckle, away from end-face chamfers.
                x = case.knuckle_x(k) + 1
                length = case.L - 2
                barrel = case.cylinder(case.SEAM_R - 0.1, length, x, y, z)
                relief = case.cylinder(case.SEAM_R + 0.3, length, x, y, z)
                center_owns = (k % 2 == 1) if wing_i == 0 else (k % 2 == 0)
                owner, neighbor = ((self.center, wing) if center_owns
                                   else (wing, self.center))
                with self.subTest(wing=wing_i, knuckle=k):
                    self.assertGreater(owner.intersect(barrel).Volume(), 1)
                    self.assertLess(neighbor.intersect(relief).Volume(), 1e-3)

    def test_center_end_skirts_clear_both_wings_through_fold(self):
        """The deep center feet need a print-tolerant gap, not mere non-overlap."""
        for wing_i, wing in self.wings.items():
            for x in (0, 203):
                skirt = self.center.intersect(case.box(2, 37, 20.1,
                                                       x, 84, -20.1))
                self.assertGreater(skirt.Volume(), 1)
                distances = [(angle, skirt.distance(case.posed(wing, wing_i, angle)))
                             for angle in range(0, 91, 5)]
                angle, gap = min(distances, key=lambda reading: reading[1])
                with self.subTest(wing=wing_i, end=x, tightest_angle=angle):
                    self.assertGreaterEqual(gap, 1.2)


if __name__ == '__main__':
    unittest.main()
