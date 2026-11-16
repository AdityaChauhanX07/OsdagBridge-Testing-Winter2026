# OsdagBridge - Software Testing & Issue Reporting (FOSSEE Winter Internship 2026)

Screening task submission by **Aditya Chauhan** ([@AdityaChauhanX07](https://github.com/AdityaChauhanX07)).

Software under test: [Nidhikhare12/OsdagBridge](https://github.com/Nidhikhare12/OsdagBridge), branch `dev`, commit
`d74f56dd7f22925fb8148cabf5740ed8d1e39ff3` (unmodified). Plate Girder Bridge module.

## What is in this repository

| Folder | Contents |
|---|---|
| `scripts/run_logged.py` | Launches the normal OsdagBridge GUI and records, for every **Design** click, the input dictionary the UI sent, the backend input after normalisation, the full output dictionary, a console log, run metadata and a diff against the previous run (multi-run / stale-state evidence). No source changes: it wraps `PlateGirderBridge.set_input()` / `design()` at runtime. |
| `scripts/run_test_suite.py` | Automated test suite. Drives the **real** homepage `InputDock`, the real Additional Inputs dialog, the real custom-material dialog, `.osi` save/load and the backend headlessly (off-screen Qt), runs ~35 designs and applies ~15 automatic consistency checks per run. See "Automated suite" below. |
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

The full list (pass and fail), with input/output tables, is in the PDF report. Issues posted to
Nidhikhare12/OsdagBridge are listed in `issues/`.
