**Title:** [Bug] Two different girder deflections for the same run: design check 22.87 mm (PASS) vs per-girder output/report 51.23 mm (FAIL vs L/600 = 50 mm)

### What happens
Every run produces two sets of deflections that differ by the composite stiffness ratio (about 2.2x). The DCR/design check uses one set and the per-girder results (Generate Results dialog, output dictionary, report Table 5.10 and chapter 4) use the other. For the default bridge, the design check reports SLS total deflection **PASS** while the report's per-girder table shows **FAIL** for the same girders.

### Environment
Windows 11, Python 3.12, `dev` @ `d74f56dd7f22925fb8148cabf5740ed8d1e39ff3` (unmodified). Also reproduced headlessly on Linux.

### Steps to reproduce
Homepage: span 30 m, carriageway 7.5 m, skew 0, Optimized, defaults. **Design** and generate the report. Compare the DCR panel / report "SLS Deflection" check with report Table 5.10 (per-girder deflections), or compare these output-dictionary keys.

### Expected / actual (TC00, same run)
| Quantity | Design check (`design_results`, DCR panel, summary) | Per-girder output (`steeldesign.deflection.*.G1..G4`, report Table 5.10) | Limit |
|---|---|---|---|
| Total (DL + LL) | `delta_total_mm` = **22.871** -> PASS | G1 51.09, G2 **51.225**, G3 51.225, G4 51.09 -> **FAIL** | L/600 = 50.0 |
| Live load | `delta_live_mm` = 9.631 | 19.252 / 19.385 / 19.385 / 19.252 | L/800 = 37.5 |

The difference appears in every run of the automated suite (check C06). Two examples: span 20 m gives 21.52 vs 60.41 mm, and median + cw 15 m gives 50.82 vs 130.96 mm. The two values agree only in the skew cases, where the per-girder values are missing (see #89).

### Evidence
* TC00 GUI run on Windows: [`gui_runs/TC00_baseline/run01_output.json`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/blob/main/gui_runs/TC00_baseline/run01_output.json) (keys above) and the generated report [`report/TC00_report.pdf`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/blob/main/gui_runs/TC00_baseline/report/TC00_report.pdf) (deflection check PASS in the summary, FAIL in the per-girder table).
* Suite: [`runs.csv`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/blob/main/suite_runs/headless_linux_2026-11-15/runs.csv) columns `delta_total_check_mm` / `delta_total_output_max_mm` for 30 designs.

### Root cause
* The design check divides the grillage displacement by `stiffness_ratio = I_composite / I_steel` ([`designer.py#L2889`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/designer.py#L2889), applied at [`L2955`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/designer.py#L2955) and [`L2966`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/designer.py#L2966)).
* The per-girder values come from `build_deflections_cache()` ([`results_data.py#L768`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/results_data.py#L768)): raw grillage displacements, no correction. They are written to `steeldesign.deflection.total_mm.G*` in [`plategirderbridge.py#L779-L785`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py#L779-L785), and the report reads exactly those keys ([`chap5.py#L466-L468`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/reports/chap5.py#L466-L468), [`chap4.py#L66`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/reports/chap4.py#L66)) and assigns PASS/FAIL against the limits.

So the same physical quantity goes through two different stiffness assumptions and reaches two different verdicts. (A single ratio for DL + LL is also questionable: steel + wet-concrete dead load acts on the bare steel section, and only superimposed dead load and live load act on the composite section.)

### Suggested fix
Compute the deflection once, per girder, in the designer, and write that same value everywhere:
```python
# designer.py, after computing per-girder values with the proper stiffness per load stage
dl_mm  = dy_dl_bare_steel_mm                      # stage 1: steel + wet concrete on I_steel
sdl_ll_mm = dy_sdl_ll_mm / stiffness_ratio        # stage 2: composite (short-term n for LL)
results.delta_total_mm = dl_mm + sdl_ll_mm
# plategirderbridge.py L779-785: write the designer's per-girder values, not the raw cache
for gi, r in design_results["per_girder"].items():
    self.output_dict[f"{KEY_SD_DEFL_TOTAL}.{gi}"] = r["demand"]["delta_total_mm"]
    self.output_dict[f"{KEY_SD_DEFL_LIVE}.{gi}"]  = r["demand"]["delta_live_mm"]
```
Alternatively, give the grillage longitudinal members the composite section for the SDL/LL cases, and drop the post-hoc division. Either way the DCR panel, the Generate Results dialog and both report tables must show one number. Regression test: assert `design_results["delta_total_mm"] == max(output["steeldesign.deflection.total_mm.G*"])` for TC00.

### Duplicate check
Checked all open/closed issues on 15 Nov 2026. #94 (check-card count) and #89 (skewed per-girder results) are different. No issue on the deflection mismatch.
