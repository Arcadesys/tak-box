# V26 print plates — captive main hinges and tab-free boards

The main hinges now use the user-confirmed arrangement: each **4 mm printed axle permanently joins two supports on the fixed half**, trapping a **3.2 mm central moving barrel** on the opposite half. Each fixed support is **2.5 mm wide**, with **9 mm outer barrels**, full-height **8 mm roots** and nominal **0.4 mm radial and face gaps**. The case prints as one captive assembly.

[Start printing V26](START-HERE.md) or [download the complete kit](V26-PRINT-KIT.zip). **FULL-PRINT** contains the joined case/hook assembly, the full four-colour board pair and the matching flat capstones. Current total estimate: **17h 46m / 288.66 g PLA**, including the optional capstones.

V26 adds modest outside corner rounds: **4 mm on the case** and **2 mm on the sliding boards**. The inlays, full field and hinge supports stay intact. Review the [corner detail](previews/18-rounded-corner.png).

V26 removes the flexible sliding-board catches. Opening the captive case hook lets the boards slide outward without pressing a release tab. Each board has a rigid **4 × 6.1 × 4.7 mm seating shoulder** outside the playing field; it meets the front rail to stop inward travel and moves away from the rail during withdrawal. The original bevelled board margin replaces the old clip window.

The hook uses a **4 mm fixed axle**, two fixed cheeks, a **2 mm outer cheek** and a **3.4 mm frame bridge**, with nominal **0.4 mm radial and face gaps**. Its broader bearing and integral printing foot print parked at 90° with the case. PIP main hinges, **3.4 mm floors**, **21 flat guides plus one capstone guide per side**, the full **180 mm / 36 mm-cell field**, original four-colour inlays and **102.5 × 200 × 35 mm** closed size remain. No loose hook pin/collar or removable tray.

Clearance checks use **42 original Cat/Witch 20 × 20 × 8 mm flats and the two supplied 8 mm V23 flat capstones**. Weighted and sculpted pieces are not qualified. Replace the V24/V25 bodies and covers for this integrated kit; the original flats and supplied flat capstones retain their geometry. The new covers retain the V26 mechanism-review case/hook interface in CAD.

The user explicitly chose full plates before small physical trials. The revised main hinge passes **947 integrated solid, loaded slide/fold, capture, seating-stop and export checks**, **51 exported geometry audits**, **15 named mesh/3MF readbacks**, and **37 sliced main-hinge/hook gap and support checks**. Sliced support-face gaps are at least **0.32 mm** under a conservative 0.50 mm bead-width assumption. The rounded board and capstone plates are rebuilt from exported CAD with **62 plate checks**; all four inlay roles retain their original geometry. Reports identify current source, project and profile hashes. Physical strength, wear, comfort and loaded transport remain unobserved. No printer job is dispatched. The earlier rounded-cover underside request remains pending.

Build with the bundled dependency versions in `reports/full-provenance.json`: CadQuery 2.7 / Python 3.12 and ElegooSlicer 2.4.2 on the recorded host. Run `source/build.py`, `source/plates_full.py`, `source/verify_review.py`, `source/slice_full.py`, `source/verify_colour.py`, `source/render.py`, `source/package_full.py`. `source/slice_full.py --verify-only` reads back existing full projects without reslicing. Full source, reference STEP parts, profiles, named meshes, raw plates and checks are retained with the kit.

[Game](previews/01-game-open.png) · [Tab removed](previews/02-board-clip.png) · [Hook cutaway](previews/04-hook-section.png) · [Closed](previews/05-closed.png) · [Fixed guides](previews/06-fixed-guides.png).

The earlier [mechanism review archive](V26-MECHANISM-REVIEW.zip), individual trials and combined clip/hook trial are preserved unchanged as history. Their flexible clip is superseded by the current tab-free covers. Rebuild those historical trials from the source inside that archive, rather than the current `source/build.py`. All V25 packages and the user extraction remain intact.

The superseded opposed-pivot full kit and case project are preserved under `archive/previous-main-hinge`. Current geometry evidence is `reports/geometry.json` and `build-double-supported-rounded.log`; `build-double-supported.log` records the pre-rounding captive hinge and `build-full.log` records the earlier tab-free build. The isolated ZIP check audits all payloads and rebuilds board/capstone raw plates from bundled STEP references; it does not independently rerun the full case CAD or slicer.
