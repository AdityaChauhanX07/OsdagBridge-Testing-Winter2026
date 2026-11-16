# Comments to post on existing issues

---
## Comment on #71 (Save Input overwrites deck / wearing-course thickness)

The same reset also happens on two more triggers besides Save Input. It affects every Additional Input that `solve_extend_basic_input_dict()` defaults, not only the two thicknesses, and Save also changes the **live session**, not just the file.

Tested at `d74f56d` (Windows 11 + headless Linux). My suite drives the real `InputDock` and `AdditionalInputs` dialog code and replays `TemplatePage`'s glue methods line for line. Six Additional Inputs were edited and saved in the dialog: deck thickness 300, wearing course 80, gamma_m0 1.15, wind exposed height 15, left support Fixed, stud diameter 22.

| Trigger after the edits | Result (all six) |
|---|---|
| change a homepage required field (span 30 -> 32) and leave the box | reset to 250 / 50 / 1.10 / 10 / Pinned / 20 |
| Save Input: values written to the `.osi` | reset (as reported here) |
| Save Input: values left in the session, then Design | **reset too**: the next Design uses the defaults |
| Load Input of an `.osi` that *contains* the six edited values | reset right after loading |

Design-level effect: suite case S05. Deck 300 mm reaches the design (slab load 7500 N/m²). After changing only the span 30 -> 32 m, the next Design uses 250 mm, though the user never touched the thickness again.

Call sites: `template_page.py` [L894-L897](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/desktop/ui/template_page.py#L894-L897) (`update_cad_from_inputs`, runs on every required-field edit), [L648](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/desktop/ui/template_page.py#L648) (Design), [L797](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/desktop/ui/template_page.py#L797) (Save, mutates `self.input_dict` in place before the file dialog, so Cancel also resets the session), [L867](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/desktop/ui/template_page.py#L867) (Load). The "only fill if missing" `_update()` proposed above fixes all four. Derived values (crash-barrier load, layout) still need recomputing, so the fix has to separate *user* keys from *derived* keys.

Evidence (input dicts, the saved/loaded `.osi` files, checks U3a-U3c, A1-A2): [suite_runs/20261116_011421/U3_additional_inputs_reset](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/tree/main/suite_runs/20261116_011421/U3_additional_inputs_reset) and `.../S05_additional_inputs`.

---
## Comment on #19 (custom materials after OSI load)

One more symptom after a cold load: the custom grade can silently end up with **another grade's properties**. In a fresh session, load an `.osi` with `custom_steel_410_540` (fy 410, E 210). Select **E 250A** in the girder combo, then select `custom_steel_410_540` again. The combo shows the custom name, but `input_dict` keeps E 250A's values: `material.girder.fy = 250.0`, `e = 200.0`. The handler (`input_dock.py` L763-L779) builds `MaterialPropertiesDialog(..., custom_fields=None)`, hits the `UnboundLocalError` reported above at `material_properties.py:751`, and swallows it with `except Exception: pass`. So nothing is written back and the design runs as E 250A under a custom label. Reproduced through the real `InputDock` (suite case U4, check U4d). The fix for the missing-map branch should raise or show an error, not pass.

---
## Comment on #43 (cross-bracing / end-diaphragm grades unused)

I ran the sensitivity check suggested in the comment above. It also shows that the bracing design ignores the **standard** grades, not only custom ones: the bracing members are always designed as `E 250 (Fe 410 W)A` from the `connect.py` templates.

TC00 inputs (30 m / 7.5 m, Optimized), only `material.cross_bracing` changed from **E 350A** (default) to **E 450A**. Every cross-bracing design result is identical: the same sections, and the same tension/compression capacities (`crossbracing_design_results.*.Member.tension_capacity`, `KEY_FCD`) for all 3 pairs x diagonal/chord x tension/compression (suite check M6, case S06 `run3_bracing_E450A` vs S01 `run1`). So even the default E 350A bracing is designed as E 250. That is conservative for strength but wrong for the report, which prints "Cross Bracing Steel Grade: E 350A". `osdag_core`'s own material table uses names like `E 350 (Fe 490)` and `Cus_fy_fy_fy_fu`, so a mapping from OsdagBridge grade names is needed in the job payload:
```python
OSDAG_CORE_GRADE = {"E 250": "E 250 (Fe 410 W)A", "E 300": "E 300 (Fe 440)", "E 350": "E 350 (Fe 490)",
                    "E 410": "E 410 (Fe 540)", "E 450": "E 450 (Fe 570)D"}
d["Material"] = d["Connector.Material"] = OSDAG_CORE_GRADE.get(base_grade) or f"Cus_{fy}_{fy}_{fy}_{fu}"
```
Evidence: [suite_runs/20261116_011421/S06_girders_and_bracing](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/tree/main/suite_runs/20261116_011421/S06_girders_and_bracing).

---
## Comment on #96 (.osi load skips custom-material validation)

Confirmed on Windows 11 at `d74f56d`, with the effect on the **design** added. Hand-edited `.osi` files were loaded through the real `loadOSI_inputs` path (`validate_osi_inputs` then `populate_from_dict`):

| Value in the .osi | Load Input | Design |
|---|---|---|
| `material.girder: custom_steel_5000_6000`, fy 5000, fu 6000 | loaded | **completes with `design_results.fy_MPa = 5000.0`** |
| custom girder density 999 kN/m³ | loaded | - |
| custom deck fck 500 MPa | loaded | - |
| `material.girder: E 999X` (grade not in the database) | loaded | - |
| span abc / 19.9 / 100, skew 30, girders 1, spacing 0, deck 20 mm, design mode Foo | rejected (correct) | - |

The unknown-grade case is worth including in the fix: the grade string itself is never checked against the material database, not only the numeric sub-keys. Evidence (every `.osi` used, the loader's verdicts, and the fy = 5000 design input/output): [U6_osi_validation](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/tree/main/suite_runs/20261116_011421/U6_osi_validation) and [S09_osi_bad_material](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/tree/main/suite_runs/20261116_011421/S09_osi_bad_material).
