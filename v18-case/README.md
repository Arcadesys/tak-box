# V18 complete case — first full print build

**This is the full build.** Print the five **CC2-PLA** projects below. They include the integrated recessed clasp, all four leaves on one common hinge axis, two retained drawers, board snaps and a latched capstone hatch. [Download the complete kit](release/tak-v18-complete-case-CC2-PLA.zip).

The user reports the clasp trial has already been printed and requested this full build. Whole-case physical fit, operation and transport acceptance remain unchecked.

## The five print plates

| Plate | Contents | Printing orientation |
|---|---|---|
| [01 — Left housing](plates/01-left-housing-clasp-and-cap-compartment-CC2-PLA.3mf) | Left housing, clasp receiver, capstone compartment and fixed hatch hinge | Rear end down; 240.4 mm tall |
| [02 — Right housing](plates/02-right-housing-and-keeper-CC2-PLA.3mf) | Right housing and integrated clasp keeper | Rear end down |
| [03 — Boards](plates/03-board-leaves-CC2-PLA.3mf) | Both board leaves, with external release clips | Playing faces up |
| [04 — Drawers](plates/04-piece-drawers-CC2-PLA.3mf) | Both 21-flat drawers, catches, withdrawal stops and front grips | On their sides |
| [05 — Hatch and small parts](plates/05-hatch-slider-and-four-axle-caps-CC2-PLA.3mf) | Capstone hatch, clasp slider and four permanent axle end caps | Slider uses frozen coupon orientation; cap bores up |

These are **12 printed parts across five plates**. If your printed trial slider is the frozen v18 geometry and is undamaged, it can be reused; skip only that named object on plate 05 and reslice. The coupon receiver and keeper are replaced by integrated housing geometry.

## Before printing

- Printer profile: **Elegoo Centauri Carbon 2, 0.4 mm nozzle**; 256 mm bed/build height.
- Starting material profile: **Generic PLA, 210 °C nozzle / 60 °C textured PEI**. Select your actual tested spool preset before printing, then reslice if it differs.
- Process: **0.20 mm layers, four requested walls, 20% gyroid, supports enabled and 6 mm brim**. Thin spring sections resolve as solid narrow walls; four walls are not possible within every 1.2 mm section.
- Supports are normal automatic with three interface layers, 0.20 mm upper/lower gaps, allowed on model surfaces. Rear-end housing orientations keep support out of the long drawer tunnels; stop ramps grow without support. Side orientations avoid a long unsupported drawer-tunnel roof and keep the spring lengths within the layer plane. Do not scale the parts to adjust fit.
- **Recorded slicer warning:** the generic PLA preset has a 45 °C softening entry while the bed is 60 °C. The vendor's PLA defaults also use this combination. Confirm your spool/bed settings; this build does not qualify a material or suppress that warning.

Fill the recessed grid with a high contrast finish, such as opaque white lines on a dark field. Keep the finish inside the 0.6 mm grooves so the playing face stays flat.

The five plates total **33 h 58 min / 565 g** in the retained starting profile, including supports and brims. Individual estimates are in [slicing.json](reports/slicing.json). No new printer job was started.

## Permanent hinge hardware

Use **3 mm steel rod**:

- Two main hinge axles: **24.9 mm long each**.
- One capstone-hatch axle: **92.0 mm long**.
- Four printed end caps: one at the outer end of each main axle, two for the hatch axle.

Main axles stop at blind ends. The end caps stay outside the 180 mm playing field. The nominal barrel bore is 3.4 mm; cap bore is 3.2 mm with a 3 mm cavity. Bond each cap to its steel rod with approximately 2 mm insertion, retaining 0.5 mm clearance from the rotating barrel. Confirm actual printed stack-up before bonding. Keep adhesive out of the hinge bores. These are permanently retained hinge axles; the case closes with its integrated v18 clasp.

## Assembly

1. Remove supports and brim. Check the drawer tunnels, clasp rails, leaf roots, snap pockets and axle bores. Deburr without enlarging the designed shoulder faces. Stop at cracks, whitening, a stuck spring or a damaged bearing surface.
2. Arrange **left housing, left board, right board, right housing** in the flat open pose shown below. Each has its own interleaved knuckles on the same axis. The playing faces face up; the capstone compartment is at the back, drawer grips at the front.
3. Insert the **front axle from the front** until it reaches the right housing's blind stop. Insert the **rear axle from the back** until it reaches the left housing's blind stop. Check that all four leaves turn freely before bonding the two outer end caps.
4. Fit the capstone hatch between the rear hinge ears. Insert its 92 mm axle and bond its two end caps, preserving free hinge rotation.
5. Insert each drawer from the front. Press its rear stop arm inward to pass the housing's front stop, then release it. Press the broad outer catch while seating the drawer fully. It must latch before folding.
6. Fit the clasp slider into the left housing receiver with its recessed tooth pressed. It is a separate sliding part. Preserve the original press-and-slide action.
7. Pull the board's two external clips outward while lowering it onto its housing; release the clips into their pockets. Both boards must lie flat. Do not force a tooth past an engaged shoulder.
8. Test the empty case first, then load the exact original Cat/Witch set. Complete [ACCEPTANCE.md](ACCEPTANCE.md) before relying on loaded transport.

![V18 open, from exported geometry](previews/01-open.png)

## Operation

- **Drawers:** press the broad outer side button and pull the front grip. The drawer stops at 168 mm travel with all 21 flats uncovered. Keep the case flat and support the drawer on the table. For deliberate removal, press the inner rear stop arm inward as it reaches the front opening, then withdraw the drawer.
- **Board maintenance:** release both external board clips before independently rotating that board. Leave them engaged for normal play and folding.
- **Capstones:** pull the hatch's external clip outward and raise the hatch. Two 12 mm floor finger ports allow an upward push to aid retrieval; the round original capstone bases are larger than the ports. Loaded escape resistance remains a physical test.
- **Case:** fully seat and latch both drawers, close the hatch and engage both boards. With the clasp bolt retracted, fold the right housing and board together. Press the recessed button and slide toward the rear to close. To open, unload the keeper, press approximately 2 mm, slide **10 mm toward the drawer/front end**, then unfold the right pair. Press-only and drag-only actions must remain held.

## Compatibility and size

The **180 mm 5×5 field and 36 mm pitch remain unchanged**. There is no axle or retaining cap through the central playing field.

This build checks current `pieces/tak_pieces.py` Cat/Witch geometry: **20 × 20 × 8 mm flats**, with 20.7 mm seats (0.35 mm nominal clearance per side) and 0.4 mm roof clearance. This corrects the v17 study's 19.5 mm envelope assumption. Each drawer stores 21 flats. Original capstones lie in the rear compartment. The old Cat capstone STL has an open mesh; its valid detailed CAD source is used for the fit checks, with hashes recorded. No piece exports were changed.

Weighted flats and curled Fox/Cat capstones remain unverified for this case. The existing weighted-stone/v16-insert mismatch remains. V16 printed interfaces are unchanged and are not compatible with this architecture. The premium pagoda remains separate.

The printed body and clasp are approximately **143 × 240 × 33 mm** closed. Including retained hinge hardware, the final envelope is recorded in [hardware.json](reports/hardware.json), approximately **144 × 246 × 33 mm**. This is wider than the body-only v17 study because it includes the full frozen clasp; no overall compactness saving is claimed.

## Verification and reproduction

Current reports cover valid single CAD solids, STEP/STL readback, named-object 3MF readback, actual original-piece fit, sampled loaded folding, released board/drawer/hatch paths, positive shoulders, steel-axle clearance, bed/build-height bounds and five CC2 dry slices. Selected critical toolpath layers are rendered directly from the sliced projects. Motion is sampled, not a continuous sweep proof. Flex poses assume a cubic curve; no force, FEA, fatigue or physical acceptance is claimed.

Source retains the frozen clasp and v17 body references without modifying their files. Use Python 3.12 with [requirements.txt](requirements.txt), and installed macOS ElegooSlicer:

```sh
python v18-case/source/build_case.py
python v18-case/source/verify_field.py
python v18-case/source/verify_hardware.py
python v18-case/source/package_case.py
python v18-case/source/slice_case.py
python v18-case/source/render_case.py
python v18-case/source/inspect_case_layers.py
python v18-case/source/package_release.py
python scripts/verify_v18_freeze.py
```

`package_case.py --only ...` and `slice_case.py --only ...` support focused updates; unchanged slice evidence is reused only if input/project/profile hashes still match. Commands, environment, hashes, outputs and repaired failures are recorded in [BUILD-PROVENANCE.md](BUILD-PROVENANCE.md) and `reports/` and [the checkpoint](../docs/V18_CHECKPOINT.md). The downloadable kit includes the source dependencies and assembly guide.
