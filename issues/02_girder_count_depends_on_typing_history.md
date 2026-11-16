**Title:** [Bug] Number of girders depends on the first carriageway width typed: same inputs give 3, 4, 5 or 9 girders (max DCR 1.13 to 1.69)

### What happens
The girder layout (number of girders, spacing, overhang) is decided by the **first** carriageway width that triggers a layout solve in the session. It is never re-seeded when the carriageway width changes later. Two users who end up with identical homepage inputs therefore get different bridges and different design results. Typing a value, correcting it, unlocking and changing inputs after a run, or opening a file all lock in the old girder count.

### Environment
Found with my automated suite, which drives the real `InputDock`, Additional Inputs dialog and backend with no source changes (headless, Linux, env from `environment.yml`, Python 3.12), on `dev` @ `d74f56dd7f22925fb8148cabf5740ed8d1e39ff3`. The suite's dict matches the dict the real GUI sent on my Windows 11 machine key for key (576 keys). Windows 11 re-run results will be added below.

### Steps to reproduce (GUI)
1. Fresh start of the app. Location Mumbai, span 40, carriageway **11**. Open Additional Inputs > Typical Section: **5 girders @ 2.38 m**.
2. Restart the app. Location Mumbai, span 40, carriageway **20**, then change the carriageway to **11**. Open Additional Inputs > Typical Section: **9 girders @ 1.322 m**.
3. Restart. Carriageway 7.5 then 11 (or run Design at 7.5, unlock, change to 11): **4 girders @ 2.975 m**.

### Results (final homepage inputs identical: span 40 m, carriageway 11 m, skew 0, no median/footpath)
| How the value was entered | Girders | Spacing (m) | Overhang (m) | Design max DCR |
|---|---|---|---|---|
| 11 typed directly (fresh session) | **5** | 2.38 | 1.19 | **1.5115** |
| 7.5 typed first, corrected to 11 | 4 | 2.975 | 1.4875 | - |
| 5 typed first, corrected to 11 | 3 | 3.9667 | 1.9833 | - |
| 20 typed first, corrected to 11 | **9** | 1.3222 | 0.6611 | **1.1301** |
| Design at 7.5 m, unlock, change to span 40 / cw 11 | 4 | 2.975 | 1.4875 | **1.686** |

The layout works correctly only for the very first carriageway value of a session. Any later change keeps the old girder count and only re-spaces the girders.

### Evidence
* Suite case U2 (`U2_girder_count_table.json`) and design runs in S02 (`fresh_B`, `typo_B_cw20_then_11`, `run2_B`): [`suite_runs/.../S02_A_B_A`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/tree/main/suite_runs/headless_linux_2026-11-15/S02_A_B_A), with input/output dicts and logs. Summary in [`SUMMARY.md`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/blob/main/suite_runs/headless_linux_2026-11-15/SUMMARY.md), checks R4-R6.
* The suite drives the real `InputDock` widgets and `TemplatePage.update_cad_from_inputs()` logic, and its dict matches the real GUI dict key for key (check U1).

### Root cause
[`defaults.py#L915-L919`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/defaults.py#L915-L919):
```python
no_of_girders = int(
    basic_input_dict.get(KEY_TS_NO_OF_GIRDERS)
    or seed_no_of_girders(solver.calculate_overall_bridge_width())
)
sizing_result = solver._solve_layout(no_of_girders=no_of_girders, changed_field='girders')
```
`solve_extend_basic_input_dict()` runs after every required-field edit ([`template_page.py#L894-L897`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/desktop/ui/template_page.py#L894-L897), `update_cad_from_inputs`) and on Design / Load ([`L648`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/desktop/ui/template_page.py#L648), [`L867`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/desktop/ui/template_page.py#L867)). Once the first call has stored `KEY_TS_NO_OF_GIRDERS`, the seed from the new width is never used again, so the count reflects history, not the current inputs. (Many other keys are reset on the same call, see the Additional Inputs issue. The girder count is the opposite case: it is wrongly kept.)

### Suggested fix
Re-seed the count whenever the deck width changes, and keep a stored count only if the user set it explicitly in Typical Section:
```python
width = solver.calculate_overall_bridge_width()
user_n = basic_input_dict.get(KEY_TS_NO_OF_GIRDERS) if basic_input_dict.get("_ts_girders_user_set") else None
if user_n is None or basic_input_dict.get("_ts_layout_width") != width:
    user_n = seed_no_of_girders(width)
basic_input_dict["_ts_layout_width"] = width
no_of_girders = int(user_n)
```
(`_ts_girders_user_set` is set by the Typical Section girder-count handler and cleared when the carriageway/median/footpath changes.) Regression test: span 40 / cw 11 must give the same layout for the inputs "11", "7.5 then 11", "20 then 11", and after an unlock from a 7.5 m run.

### Duplicate check
Checked all open/closed issues on 15 Nov 2026. No issue on girder-count history. #71 and #86 concern values being **reset**; this one is a value being wrongly **kept**.

---
All scripts, inputs, outputs and logs: https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026 (suite: `scripts/run_test_suite.py`, GUI logger: `scripts/run_logged.py`).
