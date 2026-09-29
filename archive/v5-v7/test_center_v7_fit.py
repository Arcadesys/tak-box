"""Regression for the actual v7 wings in ElegooSlicer, not the older v5 walls."""
import unittest
import cadquery as cq
import tak_case_pin as m
import tak_case_v7 as v

class V7CenterFitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.center=v.center_row()
        cls.skirt=v.center_closure_skirt()
        cls.sides={i:v.lid_pair(i) for i in (0,2)}

    def test_previous_rectangular_skirts_reproduce_physical_catch(self):
        previous=m.shell(1)
        for i,(wing,lid) in self.sides.items():
            self.assertGreater(previous.intersect(v.posed(wing,i,90)).Volume(),300)

    def test_circular_feet_fit_v7_through_entire_fold(self):
        self.assertTrue(self.center.isValid())
        self.assertEqual(len(self.center.Solids()),1)
        for i,side in self.sides.items():
            for angle in range(91):
                for part in side:
                    posed=v.posed(part,i,angle)
                    with self.subTest(wing=i,angle=angle):
                        self.assertLess(self.center.intersect(posed).Volume(),1e-3)
                        self.assertGreaterEqual(self.skirt.distance(posed),.4-1e-5)

    def test_feet_fill_circular_cutouts_and_roof_still_fills_gap(self):
        for x in (1,204):
            for y,sign in ((82,1),(123,-1)):
                self.assertTrue(self.center.isInside(cq.Vector(x,y+sign*14,-14)))
                self.assertFalse(self.center.isInside(cq.Vector(x,y+sign*15,-15)))
        for i,y in ((0,96),(2,109)):
            patch=self.center.intersect(m.box(8,4,8,100,y,-4))
            self.assertAlmostEqual(patch.BoundingBox().zmin,-3.6,places=6)
            self.assertAlmostEqual(patch.distance(v.posed(self.sides[i][0],i,90)),.4,places=6)
        self.assertLess(abs(self.center.BoundingBox().zmin+20.1),.05)

    def test_hinges_and_bores_unchanged(self):
        self.assertEqual((m.D_FIXED,m.D_FREE,m.PLUG_HOLE),(1.90,2.20,1.70))
        previous=m.shell(1)
        for y in (82,123):
            region=m.cylinder(2.9,m.knuckle_x(9)+m.L-m.knuckle_x(0),m.knuckle_x(0),y,0)
            a,b=previous.intersect(region),self.center.intersect(region)
            self.assertLess(a.cut(b).Volume()+b.cut(a).Volume(),1e-3)
        for pin in ('seam0','seam1'):
            self.assertLess(self.center.intersect(m.filament(pin)).Volume(),1e-3)

if __name__=='__main__':unittest.main()
