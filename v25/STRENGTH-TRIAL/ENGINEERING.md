# V25 supported filament hinge: engineering record

## Selected direction

The user wants a strong hinge that will not fall apart and has a heated tool for filament ends. This trial uses that tool to form two captive heads on ordinary 1.75 mm filament. Thermal staking reforms a thermoplastic end into a retaining head; the method is described in [Branson's thermal staking design guidance](https://www.emerson.com/is/content/emerson/en/corporate/branson/precision-welding-and-cleaning/thermal-processing/documents/broch-thermal-staking-design.pdf). That guidance does not validate this PLA filament joint, tool setting or strength.

The moving 3.2 mm bearing sits between two 2.5 mm fixed bearings, with 0.4 mm gaps. Both sides support it. Nine-millimetre outer barrels connect through eight-millimetre roots with local gussets. Gussets begin at X88.2 mm, outside the reference tray floor edge at X87.8 mm. Identifying text sits on the front margin outside the tray footprint.

Both filament heads are nominally 3.2 mm across and 0.6 mm thick, in 3.5 mm recesses. A 1.75 mm shaft runs through 1.95 mm fixed bores and one of three moving bores. The headed reference axle is 9 mm long; roughly 11.81 mm of unformed filament has equivalent volume. About 12 mm is a starting stock length, not a guaranteed forming recipe. Cooling, head shape and axial allowance need physical verification.

The two opposed heads geometrically block withdrawal in either direction. A blind bore with only an entry head would still allow outward withdrawal. There is no printed pin, printed cap or required glue joint in this strength trial.

## Scope and compatibility

This is a local front-edge coupon on the V24 axis X98 / Z17.5 mm. It retains the flat 180 mm field and tests rounded underside board relief. Clearance checks use the actual V24 whole boards and empty removable trays from reference revision 8085e9d79ffff3c69f07a1cca67595994237869e. They do not load the original flats or flat cat/witch capstones; no loaded-piece clearance is claimed. These are reference components, not revised production parts. It does not retrofit the printed V24 case or establish compatibility for a finished case. V24, historical packages and the original V25 coupon archive remain unchanged.

The earlier continuous-axle motion assessment remains valid: a straight full-length hidden axle requires further case geometry changes. Strength and captive retention now control the trial; a continuous axle is optional.

## Reproduce and inspect

Use Python 3.12 and the retained CAD dependencies in the repository's V25 reference requirements. Run these commands from an extracted `v25` directory:

```sh
python STRENGTH-TRIAL/source/build.py
python STRENGTH-TRIAL/source/render.py
```

`build.py` uses the unchanged shared `source/build.py` and `reference/v24/source` helpers. Reports retain command, platform, Python/CadQuery versions, source hashes, solid/STEP/STL and geometry-only 3MF checks. Folding is sampled every 2 degrees through 180 degrees, including actual V24 boards and trays. Sampling is digital evidence, not a continuous mathematical proof or a loaded physical test.

`slice.py` requires the installed ElegooSlicer and matching printer/material profiles. Its report checks settings, embedded G-code and all eight mesh readbacks. Previews are tessellated from actual exported STEP geometry; the longitudinal section intersects exported CAD at X98 mm.

`package.py` checks archive CRC, payload hashes, syntax, links, profiles and 3MF integrity. `reproduce.py` rebuilds from a fresh extraction and compares all eight STL meshes at 0.002 mm surface/size tolerance and 0.05 mm³ volume tolerance. No physical strength, fatigue life, heat-setting qualification, whole-case loaded retention or printer completion is asserted.
