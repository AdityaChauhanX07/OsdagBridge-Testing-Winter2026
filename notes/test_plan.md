# Test plan and test cases

Two ways of testing were used:
1. **Manual GUI runs** with the run logger: TC00 baseline and TC01 custom materials (`gui_runs/`).
2. **The automated suite** `scripts/run_test_suite.py`, which drives the real input dock, dialogs and backend.

Every test case below has a pass/fail result in `suite_runs/<run>/checks.csv` and in the PDF report.

## Manual GUI test cases
| ID | Scenario | Inputs | Evidence |
|---|---|---|---|
| TC00 | Baseline design | Mumbai, span 30 m, carriageway 7.5 m, skew 0, no median/footpath, Optimized, E 350A, M40 | `gui_runs/TC00_baseline` (dicts, log, report) |
| TC01 | Custom girder steel + custom deck concrete | girder rho 80, fy 410, fu 540, E 210, nu 0.3; deck rho 26, fck 45, fctm 3.8, Ecm 34 | `gui_runs/TC01_custom_materials` |

## Automated test cases
| ID | Purpose | What is done | Expected |
|---|---|---|---|
| U1 | Self-test of the suite | build TC00/TC01 through the simulated GUI | identical to the dicts the real GUI sent (576 keys) |
| U2 | Layout vs typing history | span 40 / cw 11, typed in 5 different orders | same girder layout every time |
| U3 | Additional Inputs persistence | edit 6 Additional Inputs, then change span / Save Input / Load Input | edits kept |
| U4 | Custom materials after Save/Load | save custom materials, load in a new session, Design, use the (i) button, re-select | values kept, dialog opens |
| U5 | Homepage validation | span 19.9/45.1/0/-5/abc/20/45, cw 4.2/23.7/4.25/23.6, skew +/-16, +/-15 | invalid rejected, boundaries accepted |
| U6 | Load Input validation | 14 hand-edited .osi files (`osi/invalid_*.osi`) | invalid files rejected |
| U7 | Custom-material dialog validation | fu < fy, density 130, E 50, G inconsistent with E and nu | invalid entries rejected |
| U8 | Backend validation | span 100, cw 40, skew 60, fy 5000 passed straight to the backend | rejected |
| S01 | Repeatability | TC00 x 3 (Design, unlock, Design, unlock, Design) | identical outputs |
| S02 | Stale state | A -> B -> A, B in a fresh session, B after a typo | A repeats; B independent of history |
| S03 | Custom materials used | TC01 materials, then back to defaults | custom values change the results; back to defaults = baseline |
| S04 | Reloaded custom materials | design after Save/Load/re-select | design uses the custom values |
| S05 | Additional Inputs used | deck 300, wearing course 80, ...; then change span | values reach the design and survive |
| S06 | Girders / bracing | 5 girders; cross-bracing spacing; cross-bracing grade E 450A | design follows the inputs |
| S07 | Valid boundaries | span 20/45, cw 4.25/23.6, skew +/-15, median, footpaths | design completes |
| S08 | Run after a failed run | A -> invalid run -> A | no stale data; A repeats |
| S09 | Bad material from .osi | fy = 5000 loaded from file | design refuses |
| S10 | Deck grade | M40 / M45 / M50 | same exposure class |
| S11 | Opening a dialog | open Additional Inputs, Save without edits | design unchanged |

Automatic checks applied to every design run (C01-C12): girder count, grillage spacing, steel/deck density used,
SW moment vs wL^2/8, deflection consistency, thermal load case, end-diaphragm design, cross-bracing spacing,
section area consistency, fy, self-weight lines. See the report, Table 1.
