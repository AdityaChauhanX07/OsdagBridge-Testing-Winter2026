**Title:** [Bug] Opening Additional Inputs and pressing Save (no edits) changes the design: LTB length jumps from 3 m to 15 m (Mb 7986 -> 2621 kNm)

### What happens
With identical inputs, the girder LTB check, deck design and cross-bracing forces depend on whether the user ever opened the **Additional Inputs** dialog and pressed **Save**:

* Never opened (the normal "fill the homepage and click Design" path): the backend uses a hidden fallback cross-bracing spacing of **3.0 m**.
* Opened and saved with **no edits**: it uses **15.0 m**. This is the value the dialog shows (span / (No. of Cross Bracings + 1) = 30/(1+1)), and the value the design report prints in Table 2.7 in **both** cases.

So in the default path the design report says 15 m, but the LTB check assumed 3 m. That makes the Stage-2 LTB capacity 3x higher than for the spacing shown to the user (unconservative).

### Environment
Found with my automated suite, which drives the real `InputDock`, Additional Inputs dialog and backend with no source changes (headless, Linux, env from `environment.yml`, Python 3.12), on `dev` @ `d74f56dd7f22925fb8148cabf5740ed8d1e39ff3`. The suite's dict matches the dict the real GUI sent on my Windows 11 machine key for key (576 keys). Windows 11 re-run results will be added below.

### Steps to reproduce (GUI)
1. Homepage: Mumbai, span 30 m, carriageway 7.5 m, skew 0, no median/footpath, Optimized, default materials. Click **Design**. Note the Stage 2 LTB result (DCR panel / report "Lateral-torsional buckling").
2. Unlock. Open **Additional Inputs**. Change nothing and press **Save**. Click **Design** again.
3. Compare the two runs.

### Expected / actual (same inputs, both runs)
| Output | Dialog never opened | Dialog opened + Save, no edits |
|---|---|---|
| `design_results.cross_bracing_spacing_m` | **3.0** | **15.0** |
| LTB note (check 6) | `LLT=cb_spacing=3.0m; lambda_LT=0.2992, chi_LT=1.0000` | `LLT=cb_spacing=15.0m; lambda_LT=1.4590, chi_LT=0.3282` |
| Stage 2 LTB capacity `Mb_kNm` | **7986.44** | **2621.07** |
| Stage 2 LTB DCR | 0.1505 | 0.4584 |
| Deck design "Cross-bracing spacing" / bottom bars | 3.000 m / Ø12 @ 175 | 15.000 m / Ø12 @ 185 |
| Report Table 2.7 "Spacing" | 15.0 m | 15.0 m |
| `member_properties.cross_bracing_details.spacing` (input dict) | `None` | `15.0` |

Works correctly only when the user happens to open and save the dialog. Fails (silently uses 3 m) in every session where the dialog is not saved, including after **Load Input** of an `.osi` saved without opening it.

### Evidence
* Suite case S11 (two designs, same inputs): [`S11_open_additional_inputs_no_edit/`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/tree/main/suite_runs/headless_linux_2026-11-15/S11_open_additional_inputs_no_edit). `*_input.json` = exact dict sent to `set_input()`; `*_output.json.gz` = full output dict; `input_keys_changed_by_opening_dialog.json` = every key the dialog Save changed.
* Every baseline run in [`SUMMARY.md`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/blob/main/suite_runs/headless_linux_2026-11-15/SUMMARY.md) shows the 3 m fallback ([`checks.csv`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/blob/main/suite_runs/headless_linux_2026-11-15/checks.csv), check C09).

### Root cause
Every consumer reads only the un-suffixed key `KEY_MP_CB_SPACING` and falls back to 3.0 m when it is empty:
* [`designer.py#L404-L406`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/designer.py#L404-L406): LTB unbraced length (`LLT = cross_bracing_spacing_m`, used at L1805).
* [`crossbracingforces.py#L247-L251`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/crossbracingforces.py#L247-L251): `ai.get(KEY_MP_CB_SPACING) or 3.0  # TODO: remove fallback once UI always sets spacing`.
* [`deckdesign.py#L472`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/deckdesign.py#L472): `float(inp.get(KEY_MP_CB_SPACING) or 3.0)`.

The un-suffixed key is written **only** by the Additional Inputs dialog when it saves (it is the form field of the currently selected girder pair). `solve_extend_basic_input_dict()` writes the per-pair keys `...spacing.G1G2.B1M1` = span/(n+1) = 15 m ([`defaults.py#L405-L432`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/defaults.py#L405-L432)), and the report prints those ([`chap2.py#L365`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/reports/chap2.py#L365)), but nothing in the analysis reads them. Separately, the grillage transverse lines ignore spacing altogether: `n_t = round(span / DEFAULT_CROSS_BRACING_SPACING * 2) + 1` ([`plategirderbridge.py#L1001`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py#L1001)).

Side effect of the same dialog Save: girder section properties are written back as 3-significant-figure strings (`section_properties.area.G1.M1`: `0.03491878` -> `"3.49e-02"`, [`additional_inputs.py#L1441`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/desktop/ui/dialogs/additional_input/additional_inputs.py#L1441)), so the self-weight area also changes (0.03492 -> 0.0349 m²).

### Suggested fix
1. Resolve spacing from one source that always exists, the per-pair keys `solve_extend_basic_input_dict()` already maintains, and remove the silent 3.0 fallbacks:
```python
# plategirderbridge.py (new helper)
def _cross_bracing_spacing(self, pair: str | None = None) -> float:
    """Spacing (m) for a girder pair 'G1G2'; governing (max) spacing if pair is None."""
    prefix = KEY_MP_CB_SPACING + "."
    vals = {k[len(prefix):].split(".")[0]: float(v) for k, v in self.input_dict.items()
            if k.startswith(prefix) and v not in (None, "")}
    if not vals:
        raise ValueError("Cross-bracing spacing missing: run solve_extend_basic_input_dict() first")
    return vals[pair] if pair else max(vals.values())
```
   Then `designer.py` L405: `cb_spacing = bridge._cross_bracing_spacing()` (the largest unbraced length governs LTB); `crossbracingforces.py` L250 and `deckdesign.py` L472 call the same helper instead of `... or 3.0`.
2. Build `n_t` in `_build_dtos()` from the resolved spacing (e.g. `n_t = max(3, round(span / spacing) * 2 + 1)`), so the grillage cross-frames are where the design assumes them.
3. In `AdditionalInputs`, keep full precision in the dict and format only the displayed text.
4. Regression test: TC00 inputs, `design()` with the dialog never opened vs opened and saved, must give identical `design_results`.

### Duplicate check
Checked all open/closed issues on 15 Nov 2026. #93 covers the **CAD** using the 3 m constant and says it has no effect on solver forces. This issue is about the **design/analysis** (LTB, deck, bracing forces) depending on dialog state. Not covered by #43, #71 or #86.

---
All scripts, inputs, outputs and logs: https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026 (suite: `scripts/run_test_suite.py`, GUI logger: `scripts/run_logged.py`).
