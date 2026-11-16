**Title:** [Bug] Girder design uses the nominal yield strength for every plate thickness: 22 mm E 350 flanges designed with fy = 350 MPa instead of 330 MPa (IS 2062 Table 2)

### What happens
IS 2062:2011 Table 2 gives a **thickness-dependent** minimum yield stress (E 350: 350 MPa for t < 20 mm, 330 MPa for 20-40 mm, 320 MPa for t > 40 mm; similar steps for every grade). IS 800 / IRC 22 require the value for the actual element thickness. OsdagBridge looks up one fy per grade and uses it for all plates, so any girder with a plate of 20 mm or more is designed with an over-estimated fy. This includes the default Optimized result for a 30 m span.

### Environment
Windows 11, Python 3.12, `dev` @ `d74f56dd7f22925fb8148cabf5740ed8d1e39ff3` (unmodified). Also reproduced headlessly on Linux.

### Steps to reproduce
Homepage: span 30 m, carriageway 7.5 m, Optimized, girder steel **E 350A**. Design. `design_results.tf_top_mm = 22.0`, `tf_bot_mm = 22.0`, `fy_MPa = 350.0`.

### Expected / actual
| Plate | Thickness | fy used | fy per IS 2062 Table 2 |
|---|---|---|---|
| Top/bottom flange | 22 mm | 350 MPa | **330 MPa** |
| Web | 10 mm | 350 MPa | 350 MPa |

The flange-governed capacities (plastic moment, LTB, flange classification epsilon = sqrt(250/fy)) are therefore about 6% too high for this default design. It is correct only when every plate is under 20 mm. Thicker flanges, larger spans and custom thicknesses all get an un-reduced fy (a 45 m span, or a 40 mm flange, would need 320 MPa).

### Evidence
* GUI run on Windows: [`gui_runs/TC00_baseline/run01_output.json`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/blob/main/gui_runs/TC00_baseline/run01_output.json), keys `design_results.fy_MPa`, `tf_top_mm`, `tw_mm`.
* Suite: [`runs.csv`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/blob/main/suite_runs/headless_linux_2026-11-15/runs.csv) columns `fy_used_MPa`, `tf_mm` (check C11 "Design fy = girder material fy" is reported as INFO for every run, with flanges of 22 mm and more).
* Note that `osdag_core`, which OsdagBridge already depends on for the bracing member design, stores the three thickness bands in its `Material` table (`E 350 (Fe 490)`: 350 / 330 / 320). OsdagBridge's own `Steel_Grade_Properties` table has a single `Yield Strength` column.

### Root cause
* [`plategirderbridge.py#L1196-L1199`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py#L1196-L1199): `fy = self._lookup_material(steel_grade, "Yield Strength")`, one value per grade from `Steel_Grade_Properties`.
* [`designer.py#L281-L282`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/designer.py#L281-L282): `fy_struct = steel_prop.Fy / 1e6` is used for all girder checks, whatever the plate thickness.

### Suggested fix
Resolve fy from the governing plate thickness:
```python
# core/utils/codes/is2062_2011.py (new)
_FY_BANDS = {"E 250": (250, 240, 230), "E 275": (275, 265, 255), "E 300": (300, 290, 280),
             "E 350": (350, 330, 320), "E 410": (410, 390, 380), "E 450": (450, 430, 420),
             "E 550": (550, 530, 520), "E 600": (600, 580, 570), "E 650": (650, 630, 620)}

def fy_for_thickness(grade: str, t_mm: float) -> float:
    m = re.match(r"\s*E\s*(\d+)", grade)                   # "E 350A", "E 250B0" -> "E 350", "E 250"
    lt20, t20_40, gt40 = _FY_BANDS[f"E {m.group(1)}"]
    return lt20 if t_mm < 20 else (t20_40 if t_mm <= 40 else gt40)

# designer.py, after the section is resolved
fy_flange = fy_for_thickness(steel_grade, max(sec.tf_top, sec.tf_bot))
fy_web    = fy_for_thickness(steel_grade, sec.tw)
material.fy = min(fy_flange, fy_web)    # conservative single value; or pass fy_flange/fy_web separately
```
Custom grades keep the user's fy (and should ask for the thickness bands, or state that the value applies to all thicknesses). Regression test: E 350A with tf = 22 mm gives `fy_MPa == 330`, and with tf = 16 mm gives 350.

### Duplicate check
Checked all open/closed issues on 15 Nov 2026. #95 is about how the stress limit is displayed (0.9 fy vs fy/gamma_m0). #42 is about Gs for E 350A. No issue on thickness-dependent fy.
