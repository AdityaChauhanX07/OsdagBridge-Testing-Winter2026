**Title:** [Bug] Deck-edge grillage lines get the full plate-girder section and are designed as girders: 4-girder bridge is checked as 6 girders, per-girder self-weight moment = 0.67 x wL²/8

### What happens
With a positive deck overhang (the default), the grillage has `n + 2` longitudinal lines: `n` girders plus the two deck-edge lines. The edge lines are given the **same plate-girder section** as the real girders, so they attract a full girder's share of the load. The design check then treats all `n + 2` lines as girders (`design_results.n_girders = 6`, `per_girder` G1-G6 for a 4-girder bridge). The real girders' demands come out too low (unconservative), and the girder labels no longer match the bridge.

### Environment
Windows 11, Python 3.12, `dev` @ `d74f56dd7f22925fb8148cabf5740ed8d1e39ff3` (unmodified). Also reproduced headlessly on Linux.

### Steps to reproduce
Homepage: span 30 m, carriageway 7.5 m, skew 0, Optimized, default materials (4 girders @ 2.1 m, overhang 1.05 m). Click **Design**. Inspect `design_results` in the output dictionary (or the per-girder tables in the report).

### Expected / actual (TC00)
* Self-weight is applied only on the 4 girder lines (log: `Self weight line load @ z=1.050 / 3.183 / 5.317 / 7.450 m: 2741.12 N/m`). A simply supported girder therefore needs M_SW = wL²/8 = 2.741 x 30² / 8 = **308.4 kNm**.
* Actual `per_girder[*].demand.M_girder_sw_kNm` = **206.16 / 205.42 / 205.18 / 205.18 / 205.42 / 206.16** kNm for **six** "girders". 6 x 205.4 = 4 x 308.4: the load is shared by 6 equal-stiffness lines instead of 4.
* `design_results.n_girders = 6`, `per_girder` keys G1-G6, while the input has `typical_section.no_of_girders = 4`. The output dock lists G1-G4 ([`output_dock.py#L830`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/desktop/ui/docks/output_dock.py#L830)) and looks results up by those labels. So "G1" in the dock is the deck-edge line, and the fourth real girder (line 5) cannot be selected.

The ratio follows n/(n+2) across all the girder counts the suite ran:

| Case (fresh session) | Girders | Lines checked | M_SW / (wL²/8) | n/(n+2) |
|---|---|---|---|---|
| cw 4.25 m | 3 | 5 | 0.601 | 0.600 |
| TC00 cw 7.5 m | 4 | 6 | 0.669 | 0.667 |
| span 40 / cw 11 m | 5 | 7 | 0.714 | 0.714 |
| cw 20 then 11 m | 9 | 11 | 0.818 | 0.818 |
| cw 23.6 m | 10 | 12 | 0.859 | 0.833 |

It works only for zero overhang. Then `n_l = n` and the extreme lines are real girders (see #91 for the self-weight bug in that case).

### Evidence
Suite checks C01 (design-check girder count) and C05 (SW moment) fail in every positive-overhang run: [`SUMMARY.md`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/blob/main/suite_runs/headless_linux_2026-11-15/SUMMARY.md), [`checks.csv`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/blob/main/suite_runs/headless_linux_2026-11-15/checks.csv), [`runs.csv`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/blob/main/suite_runs/headless_linux_2026-11-15/runs.csv) (columns `n_girders_input`, `n_girders_checked`, `M_sw_ratio`). Example run with full dicts and log: [`S01_baseline_three_runs/run1_*`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/tree/main/suite_runs/headless_linux_2026-11-15/S01_baseline_three_runs). GUI run of the same inputs on Windows: [`gui_runs/TC00_baseline`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/blob/main/gui_runs/TC00_baseline).

### Root cause
1. [`plategirderbridge.py#L1006`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py#L1006): `n_l = no_of_girders + 2` when overhang > 0 (fine). But [`L1113-L1118`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py#L1113-L1118) passes `edge_longitudinal=self._girder_section()`, so the edge lines are modelled as full steel girders.
2. [`plategirderbridge.py#L2296`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py#L2296) and [`L3765`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py#L3765) build `PlateGirderAnalysisResults(dataset=..., bridge=...)` without `edge_dist`. The default `edge_dist=0` ([`analysis_results.py#L148`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/analysis_results.py#L148)) makes the naming at [`L455-L460`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/analysis_results.py#L455-L460) call the edge lines G1/G6 instead of EB1/EB2. The results cache built at [`L3290-L3294`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py#L3290-L3294) already passes `edge_dist=self.get_edge_dist()`. That is why the per-girder deflections and plots show G1-G4 while the design check shows G1-G6 for the same run.
3. [`designer.py#L401`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/designer.py#L401): `n_girders = geom.n_l` (includes the edge lines; the comment at L407-L411 already notes that `_girder_count()` is the girder count). The exterior/interior classification at L412-L416 uses indices 0 and n_main-1 on the 6-line numbering, so it marks line G4 as "outer" and the real exterior girders (lines 2 and 5) as "inner".

### Suggested fix
```python
# plategirderbridge.py L1113-1118: model the deck-edge line as a slab strip, not as a girder
self.grillage_model.create_sections(
    girder_sections=girder_sections,
    edge_longitudinal=self._edge_slab_section(),   # new: deck strip of width = overhang, thickness = deck
    transverse=self._transverse_section(),
    end_transverse=self._end_transverse_section(),
)
# L2296 and L3765: tell the results object where the edge beams are
results = PlateGirderAnalysisResults(dataset=dataset, bridge=self.grillage_model,
                                     edge_dist=self.grillage_geometry.edge_dist)
# designer.py L401
n_girders = bridge._girder_count()
```
and iterate the per-girder checks over the `G1..Gn` members only (skip `EB1`/`EB2`). Regression test: TC00 must give `n_girders == 4`, per-girder M_SW close to wL²/8 (the slab-strip stiffness takes a little), and dock/report labels G1-G4 that match the per-girder results.

### Duplicate check
Checked all open/closed issues on 15 Nov 2026. #91 covers the zero-overhang case, where the outer **girders** are wrongly left without self-weight. This issue is the positive-overhang case, where the **deck edges** are wrongly modelled and designed as girders. Different trigger and different code path.

---
All scripts, inputs, outputs and logs: https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026 (suite: `scripts/run_test_suite.py`, GUI logger: `scripts/run_logged.py`).
