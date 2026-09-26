"""Digital checks for the v6 design sketch (tak_case_v6.py).

Same pass/fail bar as v5's export_validate.py: valid single solids, zero
overlap through the fold and lid-open sweeps, and the 42 flats + 2 keystones
still clear of the new well features. This does not slice or print anything.
"""
import json
from pathlib import Path
import cadquery as cq
import tak_case as base
import tak_case_v6 as v6

OUT = Path(__file__).resolve().parent

pair0 = v6.lid_pair(0)
pair2 = v6.lid_pair(2)
bodies = [pair0[0], v6.center_row(), pair2[0]]
lids = [pair0[1], pair2[1]]
pieces = [base.pieces(i) for i in (0, 2)]

checks = {}


def is_clear(a, b):
    return a.intersect(b).Volume() < 1e-4


solids_ok = all(x.isValid() and len(x.Solids()) == 1 for x in bodies + lids)
checks['solids_valid'] = solids_ok

resting = [b.BoundingBox().zmin for b in bodies]
checks['open_resting_plane'] = all(abs(z + 20.1) < 1e-5 for z in resting)

lid_seal_ok = True
lid_sweep_ok = True
for index, lid in ((0, lids[0]), (2, lids[1])):
    lid_seal_ok &= is_clear(bodies[index], lid)
    for angle in range(0, 111, 5):
        moving = v6.lid_open(lid, index, angle)
        if not all(is_clear(moving, other) for other in bodies):
            lid_sweep_ok = False
checks['lid_rests_clear_of_shell'] = lid_seal_ok
checks['lid_open_sweep_0_110'] = lid_sweep_ok

fold_ok = True
for angle in range(0, 91, 5):
    posed_bodies = [v6.posed(bodies[i], i, angle) for i in range(3)]
    posed_lids = [v6.posed(lids[0], 0, angle), v6.posed(lids[1], 2, angle)]
    for i, j in ((0, 1), (0, 2), (1, 2)):
        if not is_clear(posed_bodies[i], posed_bodies[j]):
            fold_ok = False
    for lid in posed_lids:
        if not all(is_clear(lid, other) for other in posed_bodies):
            fold_ok = False
    if not is_clear(posed_lids[0], posed_lids[1]):
        fold_ok = False
checks['main_fold_sweep_0_90'] = fold_ok

pieces_ok = True
for index, lid in ((0, lids[0]), (2, lids[1])):
    group = pieces[0 if index == 0 else 1]
    for p in group:
        if not (is_clear(bodies[index], p) and is_clear(lid, p)):
            pieces_ok = False
checks['pieces_clear_of_v6_features'] = pieces_ok

all_pass = all(checks.values())
report = {'all_pass': all_pass, 'checks': checks}
print(json.dumps(report, indent=2))

if all_pass:
    def export_step(path, items):
        a = cq.Assembly(name='Tak v6 sketch')
        for name, shape, color in items:
            a.add(shape, name=name, color=cq.Color(*color))
        a.save(str(path), exportType='STEP')

    white = (.94, .94, .91)
    stone = (.56, .32, .16)
    items = [('wing shell 0', bodies[0], white), ('center row', bodies[1], white),
             ('wing shell 2', bodies[2], white),
             ('lid 0 open', v6.lid_open(lids[0], 0, 105), white),
             ('lid 2 open', v6.lid_open(lids[1], 2, 105), white)]
    items += [(f'flat or keystone {i}-{n}', p, stone)
              for i, group in enumerate(pieces) for n, p in enumerate(group)]
    export_step(OUT / 'tak-v6-sketch-access.step', items)
    print('wrote tak-v6-sketch-access.step')
