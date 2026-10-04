# Evidence scope

Command: `python v17-four-leaf/source/build_study.py` from repository root.
Dependencies are pinned in `requirements.txt`; Python/CadQuery versions and
source SHA256 hashes are recorded in `study.json`. See `build.log` for the
actual run, including harmless read-only home/cache warnings.

The first support layout failed independent board rotation. The revised
support columns and separate end straps pass the recorded sampled checks.
Motion samples are every 10 degrees, not a continuous swept-volume proof.
Original flats are 19.5×19.5×8 mm envelopes; capstones are conservative
25.4×19.4×19.4 mm envelopes. No curled or weighted set compatibility claim.

Previews use read-back STEP geometry. Triangle subdivision improves depth
sorting of the large board faces; these are technical geometry views.
STLs are study exports, not print-ready parts. The separate draw-latch coupon includes generic 3MF objects and readback
checks; these are not a complete case release or qualified print orientations.
No ElegooSlicer is installed. Physical acceptance remains unchecked.

Closure command: `python v17-four-leaf/source/build_closure_trial.py`.
See `closure-trial.json` and `closure-build.log`. Its static checks do not
validate the full actuation path, preload, friction or integration with leaves.
