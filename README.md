# Tak board with lift-up storage lids — CAD prototype

**v5 level-base correction:** The former center end walls reached 40 mm below the playing face while the storage wings reached 20.1 mm. The center walls now reach 20.1 mm too, so all three structural sections contact the same plane when open. The printed v4 center row must not be combined with this set.

![Open-board support heights before and after the correction](center-support-comparison.png)

The 205 × 205 mm board still folds in a 2 + 1 + 2 row arrangement. Its two outer playing panels lift on pinned hinges. Each panel covers one broad, open well for 21 loose flat stones and a separate sideways recess for one rook-shaped keystone. A thumb notch in the border opens each lid; inset magnets hold it shut. The pieces can be scooped out from above, rather than fed through a channel.

![Playing face](play-face-cad.png)

![Both lids lifted](lifted-lids-cad.png)

The white playing face has a black 5 × 5 grid and the existing cat, witch-hat, moon, and star border. The main folding seams and the two lift-up lids interrupt a few millimetres of black line; the CAD image shows those gaps. This is a mechanical prototype, not a finished decorative surface.

## Files

- `tak_case.py`: editable CadQuery model. `tak_box_base.py` is a local copy of the established dimensions and decoration it imports; no earlier output folder is needed.
- `export_validate.py`: collision, piece-envelope, and solid checks; STEP and STL export.
- `export_fit_coupon.py`, `export_3mf.py`, and `validate_3mf.py`: fit sample and printer projects.
- `render_cad.py`: renders the two CAD views above.
- `tak-open-wells-v5-play.step`: 5 × 5 board with lids closed.
- `tak-open-wells-v5-access.step`: lids lifted, all 42 flats and both keystones shown.
- `tak-open-wells-v5-closed.step`: folded case.
- `*-print.stl`: individual printable shells, lids, grid accents, and hinge pins.
- `validation.json`: measured digital checks.
- `centauri-carbon-2-3mf/`: five separate 3MF projects and `package-validation.json`.

## Measured CAD layout

- Open playing face: 205 × 205 mm.
- Open underside resting plane: Z = −20.1 mm for the center and both wings. The center has two end feet; the broad wing floors also contact the table.
- Folded shell envelope before decorative overlay: approximately 205 × 49 × 88 mm.
- Two flat-stone wells: 152 × 64 × 19.1 mm inner space each.
- Two keystone recesses: 29 × 24 × 21.2 mm inner space each.
- Inventory modeled: 21 flats of 20 × 20 × 8 mm and one keystone of Ø19.8 × 25.4 mm per side.
- The hinge sweeps checked clear from 0–90° for the main fold and 0–110° for each playing lid, sampled every 5°.

## Print order and assembly

1. Open `centauri-carbon-2-3mf/tak-open-wells-v5-cc2-00-fit-coupon.3mf` in ElegooSlicer. It contains a real 45 mm wide section of the well end, playing lid, and lid hinge pin. Print this **first** in white PETG. Fit the actual keystone, seat a Ø4 × 2 mm magnet in each half, and check the hinge and magnetic lid closure by hand.
2. If that fit works, print the three white structural projects `01`, `02`, `03`, then the black raised-grid project `04`. Each file is a separate plate. The black overlays are separate printed parts that attach to the white playing face after the hinges move freely.
3. Install two main folding pins and two lid pins. Install **eight opposite-polarity magnet pairs** (16 Ø4 × 2 mm magnets total): four pairs retain the folded case and two pairs hold each playing lid down. Test polarity before bonding.
4. Load 21 flats and one keystone in each side, close both lids, fold the case, and test normal carrying over a soft surface before trusting it with the full set.

The 3MF files use the locally saved **Elegoo Centauri Carbon 2, 0.4 mm nozzle** profile, 0.20 mm layers, PETG, and a textured PEI plate. Verify that ElegooSlicer shows the correct printer, loaded PETG, and plate on your machine before printing. Three white plates use 35% gyroid infill and four walls for the structural parts; the small-parts plate uses three walls. The black grid is a separate black PETG print.

The exports have passed CAD solid and collision checks, including the level resting plane. All five packaged 3MFs reopen as manifold objects; their actual transformed meshes sit within the 256 × 256 mm plate. The identical v4 coupon geometry sliced in the ElegooSlicer UI with the expected CC2/PETG/textured-PEI settings; the slicer warned of overhangs on the well-end shell. The v5 coupon and four full-size plates have **not** had their toolpaths verified. Inspect each preview before printing. This revision has not been physically printed. Level resting, center stiffness, lid grip, magnet retention, hinge endurance, actual keystone fit, and the loose-stone carrying test remain physical checks. The existing v3 and v4 3MFs belong to earlier geometry and must not be mixed into this revision.
