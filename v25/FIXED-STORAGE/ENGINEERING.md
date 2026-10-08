# V25 fixed storage: scope and evidence

The user removed the removable piece tray on October 7 and prefers tipping the pieces onto the table. The new bodies replace the tray-floor space with a fixed case floor, cover the old low locating stops and leave open wells. No removable tray, tray handle or pocket divider is exported. Both original full-size case halves are rebuilt; no printed V24 parts or earlier archives are changed.

B is the assumed best middle fit: 2.10 mm moving bore around 1.75 mm filament. Two supported three-knuckle joints connect the case halves at front and rear; each has two fixed bearings and one moving bearing, eight-millimetre roots, gussets and two recessed formed heads. The assembled axes retain X98 / Z17.5 mm. Two approximately 12 mm starting filament lengths are formed to nominal 9 mm axles. Physical head strength, tightness, fatigue and the heat setting are unverified.

The full-body floor is 3.4 mm, using the former tray's 1.2 mm within the same external envelope. The 6 mm reinforced B floor belongs only to the small sample. Full-case stiffness cannot be inferred from that fixture or from connected CAD solids.

## Checks

`source/build.py` checks connected solids, exposed-well stock, the continuous raised floor, both-direction axle retention, all 44 fitted reference pieces, nominal 0.4 mm roof slack and cover lift blocking at 0.6 mm. Released-cover sliding is sampled every 2 mm through 106 mm travel. Body/cover folding is sampled every 2° through 180°; the specified packed piece layout is sampled every 10°. This is rigid digital evidence, not a loose-body or continuous motion simulation.

The exact piece package is **42 original Cat/Witch 20×20×8 mm flats and two supplied 8 mm V23 flat capstones**, seated at Z3.4 mm. No weighted, old sculpted or alternate capstones are qualified. The nominal packing layout shows capacity; random packing and physical dumping are unverified.

The ten current V24 four-colour STEP inputs are copied without alteration and hashed in the geometry report. They retain black board bodies, white grid/stars and independent orange/purple accents. Their source revision is 8085e9d79ffff3c69f07a1cca67595994237869e. No artwork is regenerated or recoloured into new printable components. The broad lip and rounded-cover changes remain local trials, not complete-case integration.

Affected bodies receive STEP/STL and geometry-only 3MF export/readback checks. `slice.py` checks both CC2 PLA meshes, embedded G-code and profiles with installed ElegooSlicer 2.4.2. The inherited bed-temperature warning remains in the report. Four full-case previews render exported bodies, piece references and exact board input geometry.

Reports record command, Python/CadQuery/platform, source/input hashes, geometry checks, slicing and archive evidence. `package.py` checks syntax, links, hashes, archive CRC and profiles. `reproduce.py` rebuilds from a fresh archive and compares both printed body meshes within 0.002 mm surface/size and 0.05 mm³ volume tolerances.

## Reproduce

Use the pinned dependencies in `v25/requirements.txt`. From the `v25` root:

```sh
python FIXED-STORAGE/source/build.py
python FIXED-STORAGE/source/render.py
```

The archive includes shared CAD helpers, reference source and exact board STEP inputs. Slicing requires the installed ElegooSlicer and matching material/printer profiles. Only the two bodies are printable outputs here; filament and stored pieces are reference hardware.
