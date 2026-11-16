**Title:** [Bug] Custom material dialog accepts physically impossible combinations: fu < fy, and a shear modulus G that contradicts E and nu

### What happens
The **Custom** material dialog (girder, cross-bracing or end-diaphragm steel) checks each field against its own range, one field at a time. It never checks the fields against each other, so it accepts and stores combinations that cannot exist. The custom steel then reaches the design.

### Environment
Windows 11 (Python 3.12.16, conda env from `environment.yml`), `dev` @ `d74f56dd7f22925fb8148cabf5740ed8d1e39ff3` (unmodified). Found and reproduced with my automated suite, which drives the real `MaterialPropertiesDialog._validate_and_save()` through the real `InputDock` material combo. Same results on a second, headless Linux run.

### Steps to reproduce (GUI)
1. Homepage > Girder material > **Custom...**
2. Enter fy **450**, fu **400**, leave the other fields at their defaults, press **Save**. It is accepted, and the combo now shows `custom_steel_450_400`.
3. Again **Custom...**: E 200, nu 0.3, G **120**, press **Save**. It is accepted with G = 120 GPa. With E = 200 and nu = 0.3, G must be E / (2(1 + nu)) = 76.9 GPa.

### Expected / actual
| Dialog entry | Expected | Actual |
|---|---|---|
| fy 450, fu 400 MPa | rejected (IS 2062: fu is always greater than fy) | **accepted** as `custom_steel_450_400` |
| E 200 GPa, nu 0.3, G 120 GPa | rejected, or G recomputed from E and nu | **accepted**, `material.girder.g = 120` |
| fy 410, fu 540 (normal) | accepted | accepted |
| density 130 kN/m³ / E 50 GPa | rejected (single-field range) | rejected |

It works for every single-field limit. It fails for any combination that is wrong only *relative to another field*. The stored values go into `input_dict` and reach the design: fy drives the girder checks, and fu drives rupture/connection checks.

### Evidence
Suite case U7, five dialog entries and the dialog's own verdict: [`checks.csv`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/blob/main/suite_runs/20261116_011421/checks.csv) (rows `U7`). From the run log on Windows 11:
```
FAIL U7 Custom steel fu < fy (450/400) rejected: expected reject  got accepted as custom_steel_450_400 (fy=450, fu=400, G=76.9)
FAIL U7 Custom steel G inconsistent with E,nu (E200, nu0.3, G 120) rejected: expected reject  got accepted as custom_steel_410_540 (fy=410, fu=540, G=120)
 ok  U7 Custom steel density 130 rejected
 ok  U7 Custom steel E 50 GPa rejected
```

### Root cause
* [`material_properties.py#L319-L355`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/desktop/ui/dialogs/material_properties.py#L319-L355) (`_validate_and_save`) loops over the fields and calls `self.validator.validate_material_inputs(key, {key: val})`, one field at a time.
* [`validator.py#L78-L172`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/validator.py#L78-L172) (`validate_material_inputs`) only has per-field range rules. There is no rule relating fu to fy, or G to E and nu.

### Suggested fix
Add one cross-field check to `BridgeInputValidator` and call it with all values at the end of `_validate_and_save()`. The `.osi` loader can reuse the same function.
```python
# validator.py (BridgeInputValidator)
def validate_material_consistency(self, v: dict) -> list[str]:
    errs = []
    fy, fu = self._to_float(v.get(KEY_MATERIAL_GIRDER_FY)), self._to_float(v.get(KEY_MATERIAL_GIRDER_FU))
    if fy is not None and fu is not None and fu <= fy:
        errs.append(f"Ultimate strength fu ({fu:g} MPa) must be greater than yield strength fy ({fy:g} MPa).")
    E, G, nu = (self._to_float(v.get(k)) for k in (KEY_MATERIAL_GIRDER_E, KEY_MATERIAL_GIRDER_G,
                                                    KEY_MATERIAL_GIRDER_POISSON))
    if None not in (E, G, nu) and abs(G - E / (2 * (1 + nu))) > 0.02 * G:
        errs.append(f"G must equal E / (2(1+nu)) = {E / (2 * (1 + nu)):.1f} GPa for E = {E:g} GPa, nu = {nu:g}.")
    return errs

# material_properties.py, end of _validate_and_save(), before self.accept()
values = {k: w.text().strip() for k, w in self.field_inputs.items()}
errors = self.validator.validate_material_consistency(values)
if errors:
    CustomMessageBox(title="Validation Error", text="\n".join(errors),
                     dialogType=MessageBoxType.Critical).exec()
    return
```
A simpler alternative for G is to make the field read-only and compute it from E and nu (the dialog's own defaults already follow that formula). Regression tests: fy 450 / fu 400, and G = 120 with E 200 / nu 0.3, are rejected; fy 410 / fu 540 / G 76.9 is accepted.

### Duplicate check
Checked all open/closed issues on 16 Nov 2026. #96 covers `.osi` **loading** skipping material validation; I add my design-run evidence there as a comment. #76 is about the number of decimals the dialog allows. Neither covers cross-field checks *inside the dialog*.

---
All scripts, inputs, outputs and logs: https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026 (suite: `scripts/run_test_suite.py`, GUI logger: `scripts/run_logged.py`).
