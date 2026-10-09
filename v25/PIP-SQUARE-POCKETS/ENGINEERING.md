# Engineering record

Parent: 9eeef7b; retained V24 source: 8085e9d. Units: mm. Both hinge ends use fixed spans 0.3–2.8 / 6.8–9.3 mm and their rear mirror; moving span 3.2–6.4 mm and rear mirror. Each integral 4 mm post joins its fixed end knuckles. Moving bores are 4.8 mm. Root width 8 mm; barrel diameter 9 mm. Opposing root sweep is relieved before final post union.

Square holders reuse the actual V24 tray rim geometry without the removable floor or handle. Stone pocket clear size 20.7 mm, matched to original 20 mm flats; finger notches retained. Rims join the 3.4 mm fixed floor and top out at 6.9 mm. Capacity 21 flats and one supplied flat capstone per half.

Use Python 3.12 and [the retained requirements](../requirements.txt). Run `source/build.py`, `trial.py`, `render.py`, `slice.py`, `slice.py --trial`, `package.py`, then `reproduce.py` within this package using that interpreter. ElegooSlicer 2.4.2 supplies local dry slicing. Reports record commands, dependency versions, reference hashes, exported mesh/3MF readbacks and actual sliced running gaps.

Checks cover single solids, floor/rim integration, piece seating and vertical removal, planar retention at maximum roof slack, released-cover slide every 2 mm, folding every 2 degrees, packed folding every 10 degrees, axial capture, post connectivity, root material, unchanged envelope and print assembly grouping. Sampling is not continuous motion, a fatigue rating or a physical release test. Both new bodies are required; earlier opposed-pivot or filament bodies do not mate. V24 cover/hook compatibility, broad lip and rounded-cover changes remain open.
