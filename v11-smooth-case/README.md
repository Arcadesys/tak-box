# Tak v11 — protected smooth case

**Prototype revision. Physical fit, carrying durability and snag resistance remain untested.**

The projecting tray tabs are removed. The case uses two recessed press catches behind protective end walls. Rounded outer returns cover the keyed rails and close the top edge. The board still folds inward in its **82 + 41 + 82 mm tri-fold**, with the **205 × 205 mm playing field** inside and two lift-out player trays above it. There is no separate end cap.

## Start here

| Project | Purpose | PLA estimate |
|---|---|---|
| [Plate 00](plates/plate00-smooth-case-fit-trial.3mf) | Protected hinge/end section, fitted stop, key fits A/B/C and recessed catch fits A/B/C | Pending final slice |
| [Plate 01](plates/plate01-full-size-smooth-tray-trial.3mf) | Full-size hookless tray and guarded matching fixture | Pending final slice |

Keep 100% scale and the supplied flat print orientations. Profiles use CC2, 0.4 mm nozzle, PLA, 0.2 mm layers, four walls, 210°C nozzle and 60°C bed. Supports are off. Matching G-code is included; no job has been sent to the printer.

**Use these trials for this revision.** The earlier exposed-hook plate and unguarded fixture do not validate the new enclosure. Prior v10, sliding-lid v11 and keyed-player-tray packages are preserved.

## What changed

- Catches are integral to the board frame; trays no longer carry projecting closure hooks.
- Each release has an approximately 18 × 12.5 mm rounded opening. Its press face sits 2.6 mm behind the outer end wall.
- Tongues press inward. A hard stop limits the nominal travel to 0.8 mm; geometric checks use simplified tongue movement, not an elastic simulation.
- End walls and free-edge returns shield the keys and close the upper end pockets. The hinge exterior is enlarged to a rounded Ø10.4 mm profile while retaining the Ø3 mm cone pin and nominal 0.4 mm moving clearance. External corners and release openings are rounded or bevelled.
- The plain backs and fitted underside stop shoes still establish the playing plane independently of the trays.
- Existing grid decoration, 21 flats per player, and actual Cat/Witch capstones are preserved.

Overall open frame: **245.8 × 209.4 mm**. Folded envelope: **245.8 × 51.4 × 89.4 mm**. The added border sits outside the 205 mm playing field. The tray floor remains 0.6 mm above the wing decoration when seated.

## Opening and packing

1. Place the closed case upright on its center spine.
2. Press both recessed end pads inward while easing the wings apart.
3. Unfold the wings down toward the table, keeping the trays seated.
4. Lift the trays straight up off their keyed posts and place them beside the board.
5. Reverse the sequence to pack. Seat both trays and keep all pieces below their rims before closing.

Two-handed release, opening either wing first, and loose-piece behavior still require physical acceptance. Do not force the wings against an engaged catch.

## Trial sequence

Print Plate 00 first. The full end section reproduces the protected hinge, end walls and a default-B catch pair. The separate right-end catch samples A/B/C include the outer wall, finger recess, flex root and travel stop; the left mechanism is mirrored. The matching receiver mates with each sample in its folded orientation.

Fit the stop shoe in the center panel's underside mortise after freeing the print-in-place hinges. If fixing it with adhesive, apply adhesive only under the center-supported region and keep the wing contact surfaces clean. The shoe must sit flush with the table plane. This narrow end sample does not reproduce axial capture by the opposite-facing pins at both ends of the full board.

Choose key and closure fits independently. A/B/C change the localized contact projection to 0.25/0.35/0.45 mm; **B is provisional**. Require comfortable operation and 50 cycles without cracking, shaving or progressive loosening. Test the release with its surrounding wall in place, including fabric sweeps and pressure from broad objects.

Then print Plate 01 with the selected key fit. Its default is B. Load all 21 flats and test both capstones in turn. Check the full lift stroke, bowing, access to every piece and the grip space behind the protective walls. The open-center fixture saves material; it does not validate decoration contact across the complete board.

Complete [ACCEPTANCE.md](ACCEPTANCE.md). Final full-board print projects follow physical fit acceptance. Loaded carrying, accidental release, knocks, hinge strength and playing-plane tests on the complete board remain separate gates.

## Previews and evidence

- [Both ends of the folded case](previews/01-folded-both-ends.png)
- [Recessed release detail](previews/02-release-recess-detail.png)
- [Unfolded board and tray removal](previews/03-open-tray-lift.png)
- [Protected fit samples](previews/04-protected-fit-coupons.png)
- [Actual trial toolpaths](previews/05-toolpath-checks.png)

Digital checks cover 44 sampled inward/asymmetric folds, the tray lift paths, open stops, loaded-piece envelopes, and A/B/C recessed catch engagement/release. The report identifies reused checks for unchanged piece and tray geometry. All 13 trial STLs are closed and consistently oriented. Both prepared plates fit the CC2 bed, and all 12 packaged meshes match their source STL triangle topology and vertices within 0.00002 mm. Selected actual hinge, tongue/stop, window-roof and tooth toolpaths were inspected with no support paths generated.

See [geometry checks](reports/geometry-verification.json), [mesh checks](reports/mesh-verification.json), [saved-project mesh checks](reports/packaged-mesh-verification.json), and [toolpath checks](reports/toolpath-preview.json).

The folded case retains narrow seams and curved hinge joints. Their real fabric behavior still needs the cloth/purse trial. Sampled motion and valid meshes do not establish continuous motion, print strength, operating force or impact resistance.

## Editable CAD

Main source: [tak_drawers.py](source/tak_drawers.py). STEP models are in `models/`; only fit/tray-trial STLs and projects are released. Requires the existing CadQuery/NumPy environment; previews use VTK/Matplotlib and mesh packaging checks use SciPy. Packaging uses ElegooSlicer.

From this package directory:

```sh
python source/build_models.py
python source/verify_geometry.py
python source/verify_meshes.py
python source/package_trials.py
python source/verify_packaged_meshes.py
python source/render_models.py
python source/preview_toolpaths.py
```

`KEY_FIT` and `CLOSURE_FIT` select the independent fit defaults. The full-size plate has explicit flat placement because automatic packing rotated the wide fixture and split it onto separate beds.
