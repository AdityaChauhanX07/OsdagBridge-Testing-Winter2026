**Title:** [Bug] Optimized mode: analysis, self-weight and BOM use the un-rounded initial-sizing section (A = 34,919 mm²), while the design check uses the rounded plates (A = 38,700 mm², +10.8%)

### What happens
In Optimized mode with thickness "All" (the default), the plate thicknesses are rounded up to standard SAIL plates before design (tf 21.25 -> 22 mm, tw 8.137 -> 10 mm). The section **properties** (A, Iz, Iy, It, Iw, Z, mass) and the web depth are not recomputed. So the grillage stiffness, the girder self-weight load and the bill of materials describe one girder, while the IRC 22 checks and the CAD use a different, 10.8% heavier one.

### Environment
Windows 11, Python 3.12, `dev` @ `d74f56dd7f22925fb8148cabf5740ed8d1e39ff3` (unmodified). Also reproduced headlessly on Linux.

### Steps to reproduce
Homepage: span 30 m, carriageway 7.5 m, **Optimized**, defaults (thicknesses "All"). Design. Compare `design_results` with the girder section-property keys and the self-weight line in the log.

### Expected / actual (TC00, one run)
| Quantity | Used by analysis / self-weight / BOM (input dict) | Used by design check (`design_results`) |
|---|---|---|
| Top/bottom flange thickness | 21.25 mm (initial sizing) | **22 mm** |
| Web thickness | 8.137 mm | **10 mm** |
| Web depth | 1628 mm | 1626 mm (= 1670 - 2 x 22) |
| Area | `section_properties.area.G1.M1` = 0.03491878 m² | `A_steel_mm2` = **38,700** mm² (+10.8%) |
| Iz | 0.0176543 m⁴ | `Iz_steel_mm4` = 1.882e10 mm⁴ (+6.6%) |
| Girder self-weight | log: `2741.12 N/m (A=0.03492 m²)` | 38,700 mm² x 78.5 kN/m³ = 3038 N/m |

Expected: one section everywhere. The mismatch appears in every Optimized run of the suite (check C10 in [`checks.csv`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/blob/main/suite_runs/20261116_011421/checks.csv); every girder count and span tested). Manual mode is not affected, because there the entered thicknesses are used for both.

### Evidence
* GUI run on Windows: [`gui_runs/TC00_baseline/run01_output.json`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/blob/main/gui_runs/TC00_baseline/run01_output.json) and [`session.log`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/blob/main/gui_runs/TC00_baseline/session.log) (self-weight line). Suite: [`runs.csv`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/blob/main/suite_runs/20261116_011421/runs.csv) columns `sw_area_m2` vs `A_steel_check_m2`.
* The report's bill of materials for the steel girders uses the stale area (32.89 t for 4 x 30 m, against about 36.4 t for the designed plates).

### Root cause
`design()` calls [`_resolve_optimized_bounds_to_mm()`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py#L450) ([`L682`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py#L682)). It snaps the thickness keys `"All"` to the next SAIL plate but only rewrites the **dimension** keys. The **property** keys written earlier by the Additional Inputs compute functions from the initial-sizing dimensions are left untouched. `_girder_section()` then builds the grillage section (and the self-weight area) from those stale property keys ([`L1260-L1277`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py#L1260-L1277): `A=g(KEY_MP_GIRDER_SECTIONAL_AREA)`, `Iz=g(KEY_MP_GIRDER_SECTIONAL_IZ)`, ...). The designer recomputes A/I from the snapped dimensions.

### Suggested fix
After the dimensions are resolved, recompute the properties from them, once, per girder:
```python
# plategirderbridge.py, end of _resolve_optimized_bounds_to_mm() (or start of _build_dtos())
from osdagbridge.core.bridge_types.plate_girder.initial_sizing import BridgeConfigurationSolver
span = float(self.input_dict[KEY_SPAN])
solver = self._layout_solver()      # BridgeConfigurationSolver built as in solve_extend_basic_input_dict()
for i in range(self._girder_count()):
    sfx = f".G{i+1}.M1"
    v = lambda k: self._girder_value(k, i)          # metres after _convert_girder_dims_mm_to_m()
    p = solver.compute_section_properties(
            span=span, symmetry=v(KEY_MP_GIRDER_SYMMETRY),
            user_depth=v(KEY_MP_GIRDER_DEPTH),
            B_top=v(KEY_MP_GIRDER_TOP_FLANGE_WIDTH), B_bot=v(KEY_MP_GIRDER_BOTTOM_FLANGE_WIDTH),
            t_f_top=v(KEY_MP_GIRDER_TOP_FLANGE_THICKNESS), t_f_bot=v(KEY_MP_GIRDER_BOTTOM_FLANGE_THICKNESS),
            t_w=v(KEY_MP_GIRDER_WEB_THICKNESS))
    self.input_dict.update({
        KEY_MP_GIRDER_WEB_DEPTH + sfx:      p["d_web"],
        KEY_MP_GIRDER_SECTIONAL_AREA + sfx: p["Area"],
        KEY_MP_GIRDER_SECTIONAL_IZ + sfx:   p["I_z"],
        KEY_MP_GIRDER_SECTIONAL_IY + sfx:   p["I_y"],
        KEY_MP_GIRDER_MASS + sfx:           p["Mass"],
        # ... Z_ez / Z_pz / r_z / r_y / It / Iw keys likewise
    })
```
(`compute_section_properties()` in [`initial_sizing.py#L424`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/initial_sizing.py#L424) already returns these quantities in metres.) Regression test: Optimized TC00 must give `section_properties.area.G1.M1 * 1e6 == design_results["A_steel_mm2"]`, and a self-weight line load equal to A x density.

### Duplicate check
Checked all open/closed issues on 15 Nov 2026. #90 is about Optimized-mode **constraints** (allowed thickness lists and bounds) being ignored. This issue is about the **properties** not following the chosen plates. #20 covers the density value, not the area. #103 reports the Material Take-off using G1's area for every girder; the stale-area root cause here also explains part of that bill-of-materials mismatch, but the analysis/self-weight inconsistency is not covered there.

---
All scripts, inputs, outputs and logs: https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026 (suite: `scripts/run_test_suite.py`, GUI logger: `scripts/run_logged.py`).
