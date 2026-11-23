# OsdagBridge - Software Testing & Issue Reporting (FOSSEE Winter Internship 2026)

Screening task submission by **Aditya Chauhan** ([@AdityaChauhanX07](https://github.com/AdityaChauhanX07)).

Software under test: [Nidhikhare12/OsdagBridge](https://github.com/Nidhikhare12/OsdagBridge), branch `dev`, commit
`d74f56dd7f22925fb8148cabf5740ed8d1e39ff3` (unmodified). Plate Girder Bridge module.

**In short:** 8 new issues ([#111](https://github.com/Nidhikhare12/OsdagBridge/issues/111)-[#118](https://github.com/Nidhikhare12/OsdagBridge/issues/118)),
4 comments with new evidence on existing issues, 2 fix pull requests with regression tests
([#219](https://github.com/Nidhikhare12/OsdagBridge/pull/219), [#220](https://github.com/Nidhikhare12/OsdagBridge/pull/220)),
and an automated GUI-level test suite with identical results on Windows 11 and Linux.
Report: [`report/report.pdf`](report/report.pdf) (the page after the title page is a one-page summary).
Video of the test session (6 design runs, 3D CAD, plots, design report): https://youtu.be/G32tJCyJotU

## What is in this repository

| Folder | Contents |
|---|---|
| `scripts/run_logged.py` | Launches the normal OsdagBridge GUI and records, for every **Design** click, the input dictionary the UI sent, the backend input after normalisation, the full output dictionary, a console log, run metadata and a diff against the previous run (multi-run / stale-state evidence). No source changes: it wraps `PlateGirderBridge.set_input()` / `design()` at runtime. |
| `scripts/run_test_suite.py` | Automated test suite. Drives the **real** homepage `InputDock`, the real Additional Inputs dialog, the real custom-material dialog, `.osi` save/load and the backend headlessly (off-screen Qt), runs ~35 designs and applies ~15 automatic consistency checks per run. See "Automated suite" below. |
| `osi/` | Test input files for **File > Load Input**: TC00 baseline, TC01 custom materials, TC02 edited Additional Inputs, and 11 invalid files used to test Load Input validation. |
| `fixtures/` | The exact input dictionaries the GUI produced in the two manual runs (used by the suite's self-test). |
| `gui_runs/` | Evidence of the manual GUI runs on Windows 11 (`run_logged.py` output + generated design reports). |
| `suite_runs/` | Output of the automated suite (`SUMMARY.md`, `checks.csv`, `runs.csv`, and per-case input/output/log files). |
| `issues/` | The issue texts as posted to Nidhikhare12/OsdagBridge. |
| `notes/` | Working notes, environment details. |

## Test environment

* Windows 11 laptop, Miniconda, `conda env create -f environment.yml` from the OsdagBridge repo (Python 3.12, PySide6).
* The automated suite was also run headlessly on Linux (same environment.yml) to cross-check.

## How to reproduce

```bat
cd OsdagBridge\src
:: GUI with logging (one folder per session under OsdagBridge-Testing\runs)
python ..\..\OsdagBridge-Testing\scripts\run_logged.py MY_LABEL
:: automated suite (about 20 minutes), results under OsdagBridge-Testing\suite_runs
python ..\..\OsdagBridge-Testing\scripts\run_test_suite.py
python ..\..\OsdagBridge-Testing\scripts\run_test_suite.py --list      # list the cases
python ..\..\OsdagBridge-Testing\scripts\run_test_suite.py --ui-only   # 2-minute subset
```

## Automated suite

Self-test: the dictionary the suite builds by driving the real input dock is identical, key by key (576 keys), to the
dictionary the real GUI sent in the manual runs (`U1a`, `U1b`), so the suite reproduces what a user does.

| Group | Cases |
|---|---|
| UI logic (no design) | girder layout vs typing history; Additional Inputs vs homepage edits / Save Input / Load Input; custom materials after Save/Load; homepage hard validation (span, carriageway, skew; valid and invalid boundaries); `.osi` load validation; custom-material dialog validation; backend validation |
| Design runs | 3 identical consecutive runs; A -> B -> A in one session vs fresh session; custom girder steel + deck concrete and back; reloaded custom materials; Additional Inputs propagation; girder count / cross-bracing spacing / cross-bracing steel; boundary values (span 20/45, carriageway 4.25/23.6, skew +/-15, median, footpaths); run after a failed run; out-of-range material from `.osi`; deck concrete grade; opening Additional Inputs without edits |

Automatic checks per design run (C01-C12): design check girder count, grillage girder spacing, steel and deck density
actually used, girder self-weight moment vs wL^2/8, deflection consistency (design check vs per-girder output/report),
thermal load case presence, end-diaphragm design, cross-bracing spacing actually used, section area consistency
(analysis vs design check), fy used, self-weight lines.

## Findings and issues

The full list (pass and fail), with input/output tables, is in the PDF report (`report/report.pdf`).
Issues posted to Nidhikhare12/OsdagBridge (texts in `issues/`):

| Issue | File | Topic |
|---|---|---|
| [#111](https://github.com/Nidhikhare12/OsdagBridge/issues/111) | `01_cross_bracing_spacing_depends_on_opening_dialog.md` | LTB length 3 m vs 15 m depending on whether Additional Inputs was saved |
| [#112](https://github.com/Nidhikhare12/OsdagBridge/issues/112) | `02_girder_count_depends_on_typing_history.md` | girder count depends on the first carriageway width typed |
| [#113](https://github.com/Nidhikhare12/OsdagBridge/issues/113) | `03_deck_edge_lines_modelled_and_checked_as_girders.md` | deck-edge lines modelled and designed as girders |
| [#114](https://github.com/Nidhikhare12/OsdagBridge/issues/114) | `04_deflection_two_different_values.md` | two different deflections (design check vs report) |
| [#115](https://github.com/Nidhikhare12/OsdagBridge/issues/115) | `05_deck_exposure_inferred_from_concrete_grade.md` | deck exposure class derived from the concrete grade |
| [#116](https://github.com/Nidhikhare12/OsdagBridge/issues/116) | `06_optimized_mode_analysis_uses_stale_section.md` | Optimized mode uses the un-rounded section in the analysis |
| [#117](https://github.com/Nidhikhare12/OsdagBridge/issues/117) | `07_fy_not_reduced_for_plate_thickness.md` | fy not reduced for plates of 20 mm and more |
| [#118](https://github.com/Nidhikhare12/OsdagBridge/issues/118) | `08_custom_material_dialog_cross_field_checks.md` | custom material dialog accepts fu < fy and an inconsistent G |
| comments on [#71](https://github.com/Nidhikhare12/OsdagBridge/issues/71), [#19](https://github.com/Nidhikhare12/OsdagBridge/issues/19), [#43](https://github.com/Nidhikhare12/OsdagBridge/issues/43), [#96](https://github.com/Nidhikhare12/OsdagBridge/issues/96) | `comments_on_existing_issues.md` | additional evidence for existing issues #71, #19, #43, #96 |

## Fix pull requests

Both are one commit on top of `d74f56d` in my fork, with regression tests in the project's own `tests/unit` that fail
on the unmodified code and pass with the fix. The suite was rerun with each fix applied: only the targeted checks change
(FAIL -> PASS), every other check gives the same result as before.

| PR | Fixes | Tests added | Suite with the fix |
|---|---|---|---|
| [#219](https://github.com/Nidhikhare12/OsdagBridge/pull/219) | [#118](https://github.com/Nidhikhare12/OsdagBridge/issues/118): reject custom steel with fu <= fy or G inconsistent with E and nu | 13 (`tests/unit/test_material_consistency.py`) | [`suite_runs/fix_118_ui_tests_2026-11-21`](suite_runs/fix_118_ui_tests_2026-11-21) |
| [#220](https://github.com/Nidhikhare12/OsdagBridge/pull/220) | [#112](https://github.com/Nidhikhare12/OsdagBridge/issues/112): re-seed the girder count when the deck width changes | 10 (`tests/unit/test_girder_count_layout.py`) | [`suite_runs/fix_112_tests_2026-11-21`](suite_runs/fix_112_tests_2026-11-21) |
