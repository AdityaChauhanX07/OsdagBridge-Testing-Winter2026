**Title:** [Bug] Material properties are never validated on Load Input (fy = 5000 MPa loads and is designed with), and the custom-material dialog accepts fu < fy and an inconsistent G

### What happens
1. **Load Input** checks span, carriageway, skew, design mode and about 50 Additional Inputs, but **no material key at all**. A hand-edited `.osi` with impossible material values loads without a warning, and Design runs with them.
2. The **Custom material dialog** checks each field against its own range only. It accepts physically inconsistent combinations: ultimate strength below yield strength, and a shear modulus that contradicts E and nu.

### Environment
Found with my automated suite, which drives the real `InputDock`, Additional Inputs dialog and backend with no source changes (headless, Linux, env from `environment.yml`, Python 3.12), on `dev` @ `d74f56dd7f22925fb8148cabf5740ed8d1e39ff3`. The suite's dict matches the dict the real GUI sent on my Windows 11 machine key for key (576 keys). Windows 11 re-run results will be added below.

### Steps to reproduce
**A. Load Input.** Save any design (File > Save Input). Edit the `.osi` in a text editor and change:
```yaml
material.girder: custom_steel_5000_6000
material.girder.fy: '5000'
material.girder.fu: '6000'
```
Load it (File > Load Input): "Loaded OSI Successfully!". Design: it completes, and `design_results.fy_MPa = 5000.0`.

**B. Custom dialog.** Girder material > Custom: enter fy 450, fu **400** (other fields default) > Save. It is accepted as `custom_steel_450_400`. Or enter E 200, nu 0.3, G **120** > Save: accepted (G should be E / (2(1+nu)) = 76.9 GPa).

### Expected / actual
| Input | Range enforced in the dialog | Load Input | Design |
|---|---|---|---|
| custom steel fy 5000 / fu 6000 MPa | fy 100-1200, fu 100-1500 | **loaded** | **runs with fy = 5000** |
| custom girder density 999 kN/m³ | 50-120 | **loaded** | - |
| custom deck fck 500 MPa | 10-80 | **loaded** | - |
| girder grade `E 999X` (not in the database) | combo list only | **loaded** | - |
| span `abc` / 19.9 / 100 m, skew 30, girders 1, spacing 0, deck 20 mm | (homepage / Additional Inputs) | rejected (correct) | - |

| Custom dialog entry | Expected | Actual |
|---|---|---|
| fy 450, fu 400 | rejected (fu must be at least fy) | accepted |
| E 200, nu 0.3, G 120 | rejected or G recomputed | accepted, G = 120 stored |
| density 130 / E 50 | rejected | rejected (correct) |

### Evidence
* Suite case U6 (14 hand-edited `.osi` files and the loader's verdict): [`U6_osi_validation/`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/tree/main/suite_runs/headless_linux_2026-11-15/U6_osi_validation) (`U6_osi_validation_table.json`, every `.osi` used).
* Suite case S09 (Design after loading the fy = 5000 file): [`S09_osi_bad_material/`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/tree/main/suite_runs/headless_linux_2026-11-15/S09_osi_bad_material) (`run1_fy5000_input.json`, `run1_fy5000_output.json.gz`: `design_results.fy_MPa = 5000.0`).
* Suite case U7 (custom dialog, driven through the real `MaterialPropertiesDialog._validate_and_save()`): [`checks.csv`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/blob/main/suite_runs/headless_linux_2026-11-15/checks.csv) rows U7.

### Root cause
* [`osi_validator.py#L81-L111`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/utils/osi_validator.py#L81-L111): `_BASIC_KEYS` / `_ADDITIONAL_KEYS` contain no `material.*` key, and `validate()` never calls `BridgeInputValidator.validate_material_inputs()`, although that method exists ([`validator.py#L78`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/validator.py#L78)). The material grade strings are not checked against the database either.
* [`validator.py#L78-L172`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/validator.py#L78-L172): every material field is checked in isolation. [`material_properties.py#L319-L355`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/desktop/ui/dialogs/material_properties.py#L319-L355) (`_validate_and_save`) passes `{key: val}` for one field at a time, so no cross-field rule can be applied.

### Suggested fix
```python
# osi_validator.py, in OsiInputValidator.validate(), after the additional-input loop
_MATERIAL_PREFIXES = ("material.girder.", "material.cross_bracing.", "material.end_diaphragm.", "material.deck.")
for key, value in flat.items():
    if key.startswith(_MATERIAL_PREFIXES) and not self._is_missing(value):
        # cross-bracing / end-diaphragm steel use the same rules as girder steel
        canonical = re.sub(r"^material\.(cross_bracing|end_diaphragm)\.", "material.girder.", key)
        self._run(self._bridge_validator.validate_material_inputs, canonical, {canonical: value}, result)
for member in (KEY_GIRDER, KEY_CROSS_BRACING, KEY_END_DIAPHRAGM, KEY_DECK_CONCRETE_GRADE_BASIC):
    grade = str(flat.get(member) or "")
    if grade and not grade.startswith(("custom_steel_", "custom_concrete_")) and grade not in KNOWN_GRADES:
        result.errors.append(f"{member}: '{grade}' is not in the material database.")   # KNOWN_GRADES from connectdb()

# validator.py: cross-field rules used by both the dialog and the loader
def validate_material_consistency(self, values: dict) -> list[str]:
    errs = []
    fy, fu = self._to_float(values.get(KEY_MATERIAL_GIRDER_FY)), self._to_float(values.get(KEY_MATERIAL_GIRDER_FU))
    if fy and fu and fu < fy:
        errs.append("Ultimate strength fu must not be less than yield strength fy.")
    E, G, nu = (self._to_float(values.get(k)) for k in (KEY_MATERIAL_GIRDER_E, KEY_MATERIAL_GIRDER_G, KEY_MATERIAL_GIRDER_POISSON))
    if E and G and nu is not None and abs(G - E / (2 * (1 + nu))) > 0.02 * G:
        errs.append(f"G must equal E / (2(1+nu)) = {E / (2 * (1 + nu)):.1f} GPa.")
    return errs
```
and call `validate_material_consistency()` at the end of `MaterialPropertiesDialog._validate_and_save()` with all field values. Regression tests: the four `.osi` files above are rejected; fy 450 / fu 400 and G = 120 are rejected in the dialog.

### Duplicate check
Checked all open/closed issues on 15 Nov 2026. #88 (NaN values pass OSI validation) and #67 (empty span) concern geometry keys. #76 concerns the number of decimals in the dialog. No issue about material keys being skipped by the loader, or about cross-field material checks.

---
All scripts, inputs, outputs and logs: https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026 (suite: `scripts/run_test_suite.py`, GUI logger: `scripts/run_logged.py`).
