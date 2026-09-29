# Center for the printed v7 wings — PLA

Use **tak-center-v7-rounded-PLA.3mf**. It matches the v7 wing projects inspected in ElegooSlicer, including the extended end walls and their circular cutouts. The earlier v5 rectangular-skirt file catches in those wings and is superseded for this assembly.

The center has four R20.1 circular feet, 2.2 mm thick, seated in the unchanged wings' R20.5 notches. A 0.4 mm linear margin protects the inner end of each sector. The 3.6 mm underside skin is inset 2.9 mm at the ends so it clears the v7 wing walls. Hinge axes, knuckles and 1.90 / 2.20 / 1.70 mm holes remain unchanged. No replacement wings are needed.

The project copies the active ElegooSlicer configuration: Centauri Carbon 2, 0.4 mm nozzle, Elegoo PLA in slot 1, 210°C nozzle, 60°C textured PEI, 0.20 mm layers, 2 walls, 15% infill and build-plate-only tree supports enabled. The file was opened and sliced in ElegooSlicer; its estimate showed 35.87 g. No printer upload or physical fit was performed.

Four regression tests pass. They reproduce over 319 mm³ of interference per wing with the earlier rectangular skirts, then check the corrected center at every degree from 0–90° against both v7 wings and lids: zero overlap and at least 0.4 mm skirt clearance. Tests also check material near the outer circular edge, retained roof fill, unchanged hinge solids and clear filament paths. The actual wing 3MF vertex sets match the original v7 STLs; the corrected project mesh matches the checked center and is closed.

The five coupon STLs form a 30 mm end slice of this version. Their loose lid strips need holding or removable tape during the fold check. The STL center is face down, wings bottom down and lids face down. The 3MF contains only the complete replacement center.

Reproduce the CAD and coupon with CadQuery:

```sh
python -m unittest -v test_center_v7_fit
python export_center_closure_coupon.py --v7 --output-dir center-closure-v7
```

`tak_case_v7.py` brings in the current local v7 wing model that was absent from repository main, with the corrected center implementation. Wing geometry is unchanged. Regenerating STLs does not refresh the separately saved 3MF or copy current user filament settings; open the regenerated center STL in ElegooSlicer using the PLA profile above and save a new project.
