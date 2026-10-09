# Reproduce
Install the dependencies in `requirements.txt` into a separate Python environment. Run `python build.py`, then `python package_plate.py`, then `python render.py`. `common.py` is included locally. Historical workspace search paths in the scripts are optional fallbacks; normal installed modules/local files suffice outside that workspace.

The slicing profile and reports are provided for analysis only. Use PrusaSlicer 2.9.2 with `slicing/generic-pla-coupon.ini` and the plate 3MF for a comparable local dry slice. This generic profile has disabled heating and warning start/end text; it is not a machine-ready print profile. No machine code is included. `slicing/inspect_layers.py` takes the temporary analysis file path defined at the top of the script.

The reviewed geometry version is the build.py checksum in `validation.json` and the independent review. CAD STEP assemblies do not provide a true flexible-body solver; the pressed poses are generated from the explicitly documented deformation assumption.
