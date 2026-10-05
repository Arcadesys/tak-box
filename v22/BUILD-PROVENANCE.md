# V22 hinge candidate evidence

Based on V21 commit `0fd6806`, with main captive pivots adapted from V16 source geometry (3 mm diameter, 0.4 mm radial and face clearance). Units: mm. Defining source and dependency hashes are in reports/provenance.json. This candidate retains V21's 32.6 mm closed thickness and existing rear compartment while capstone direction is unresolved. The deeper-box experiment was discarded.

52 geometry/mesh/piece/motion checks, 37 field probes, 15 remaining-hardware checks, 25 plate/readback checks and eight filament-core checks pass. Three slices pass with exact named meshes and preserved assembly positions. Full candidate estimate: 43,798 s / 283.80 g. The optional shortened hinge pair passes eight checks and slices to 1,290 s / 3.80 g.

32 captive-hinge checks pass: CAD clearance and opposed axial capture, no support centerlines within the cylindrical bearings, and sampled radial toolpath gaps in both full and trial prints. Using a conservative 0.50 mm bead-width assumption, sampled side gaps measure 0.385–0.422 mm. This is not a continuous swept-volume or physical force/strength proof. Selected layers, gap plots and actual STEP previews were visually reviewed.

Environment: `.slicer-work/cad-venv/bin/python`, Python 3.12.13; requirements.txt pins the dependencies. ElegooSlicer 2.4.2, CC2 0.4 mm and included PLA/process profiles. CLI arguments and hashes are recorded in slicing and fit-check reports. No printer job started. Generic PLA temperature-metadata warnings remain. Missing CLI OpenGL thumbnails are replaced by separate actual-geometry previews.

Commands: build_case.py, verify_field.py, verify_hardware.py, package_case.py, slice_case.py, render_case.py, inspect_case_layers.py, verify_pin_toolpaths.py, build_fitcheck.py, verify_pip_hinges.py, then record_provenance.py. Review regenerated layer sheets before marking them reviewed. package_release.py refuses final packaging until DESIGN-STATUS.json records a resolved capstone direction.

Resolved implementation issues: separate-object slicing reported conflicting paths; grouping the two disjoint mesh parts into one assembly fixed it without merging them. Named-mesh readback now resolves individual components and verifies world placement. The gap checker initially mistook internal infill voids for a missing pin; it now measures between the outer pin contours and neighboring socket contours using segment-capsule intersections. No Shapely dependency was added.
