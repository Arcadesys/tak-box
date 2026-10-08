# V26 mechanism review

V26 revises the fragile **sliding-board clip** and makes the **side hook print captive**. The main hinges remain PIP; piece guides remain permanently joined to the case floors. V25 files and print kits are preserved.

The clip arm grows from 1.2 to **2.4 mm** with a gradual **3.2 mm root** and a **1.2 mm inside-radius blend**, keeping its 54 mm plan length and assumed 2.8 mm release travel. This is a durability candidate, not a measured strength rating. Increased stiffness may make release harder; test that before complete covers.

The side hook turns around a **4 mm fixed axle**, retained between two fixed cheeks, including a **2 mm outer cheek** and **3.4 mm frame bridge**. Nominal radial and face gaps are **0.4 mm**. Its broader bearing has an integral printing foot; it prints parked at 90 degrees with its case mount. No inserted filament pivot or separate collar is needed. The closure tooth and opposing keeper are retained.

The full 180 mm / 36 mm-cell field, original four-colour inlays, 3.4 mm floors, 21 flat guides plus capstone guide per side and 102.5 × 200 × 35 mm closed size are retained. Clearance checks use 42 original Cat/Witch 20 × 20 × 8 mm flats and the two supplied 8 mm V23 flat capstones.

Start with [the captive-hook trial](SMALL-TRIALS/01-V26-captive-hook-trial-CC2-PLA.3mf) and [the full-length clip trial](SMALL-TRIALS/02-V26-board-clip-trial-CC2-PLA.3mf). The estimates are about 25 minutes / 5 g and 42 minutes / 9.51 g PLA. These are dry-sliced CC2 PLA projects; match the actual spool/profile and reslice when settings change. The inherited 60°C bed / 45°C vitrification metadata warning remains recorded.

Open each as a project; do not separate or auto-arrange the captive-hook components. Let it cool, remove accessible external support, gently free the hook and check that it stays captured when pulled in either direction. Reject cracks, fusion or chipped axle/cheeks. Slide the clip into its matching seat, release it by hand and inspect its root after 20 and 100 cycles. Record release effort, damage and looseness. Neither trial proves loaded transport durability.

Whole-case CAD and a raw grouped body/hook plate support review. A complete sliced V26 kit, physical fit/strength and the previously requested rounded-cover underside are still pending. No printer job has been started.

Commands use CadQuery 2.7, Python 3.12 and the installed ElegooSlicer 2.4.2. Run `source/build.py`, `source/trial.py`, `source/slice.py`, `source/verify_review.py`, `source/render.py` and `source/package.py` in that order. Source dependencies and reference STEP geometry are bundled; reports record checks, hashes, command paths and rejected attempts.

[Download the V26 mechanism review](V26-MECHANISM-REVIEW.zip) · [Clip comparison](previews/02-board-clip.png) · [Captive hook](previews/03-captive-hook.png) · [Hook cutaway](previews/04-hook-section.png) · [Full game](previews/01-game-open.png).

The parked lever has underside clearance outside the piece wells. A final audit rejected the original 0.173 mm lever-to-well-corner gap; the revised underside opening clears that region. The 3.4 mm stone floors and fixed guides remain intact.
