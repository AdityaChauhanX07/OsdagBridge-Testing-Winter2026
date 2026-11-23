# Video of the test session

**Video:** https://youtu.be/G32tJCyJotU (5 min)

One continuous screen recording on Windows 11 (OsdagBridge `dev` @ `d74f56d`, unmodified). Captions were added
underneath the picture; the waits while the analysis runs are shown at 4x speed and a few setup steps at 1.5x or 2x
(marked on screen). Nothing else was cut.

The app was started with the session logger, from `OsdagBridge\src`:

```bat
conda activate osdagbridge-env
python ..\..\OsdagBridge-Testing-Winter2026\scripts\run_logged.py VIDEO
```

All six runs use the baseline bridge: Mumbai, span 30 m, carriageway 7.5 m, skew 0, Optimized.

| Time | Run | What is shown |
|---|---|---|
| 0:00 | - | Title card |
| 0:05 | - | OsdagBridge started with the session logger |
| 0:14 | 1 | Inputs; default materials (girder, cross bracing and end diaphragm E 350A, deck M40) |
| 0:30 | 1 | Design (analysis in 14 stages) |
| 0:37 | 1 | 3D CAD: rotate, girders only, cross bracing only; tooltip on a brace (ANGLE 100 x 50 mm, spacing 3000 mm) |
| 1:05 | 1 | Output dock: Girder 1 section 1670 x 510 x 22 mm; bending moment, shear force and deflection diagrams |
| 1:29 | 2 | Unlock, change nothing, Design again; 3D model rebuilt |
| 1:42 | 3 | Unlock, change nothing, Design again |
| 1:49 | 3 | Same results as run 1 (Girder 1, self-weight case: flexure 2 %, shear 4 %, interaction 2 %, LTB 23 %, longitudinal shear 20 %) |
| 1:58 | 4 | Custom girder steel: fy 410, fu 540 MPa, E 210 GPa, G 80.8 GPa, nu 0.3, density 80 kN/m3, alpha 12e-6/C |
| 2:14 | 4 | Custom deck concrete: fck 45, fctm 3.8 MPa, Ecm 34 GPa, density 26 kN/m3, alpha 10e-6/C |
| 2:31 | 4 | Design with the custom materials |
| 2:38 | 4 | Output uses grade `custom_steel_410_540`; Girder 1 self-weight case LTB 22 %, longitudinal shear 21 % (runs 1-3: 23 %, 20 %) |
| 3:02 | 5 | Girder steel back to E 350A, deck concrete M40 -> M45 |
| 3:16 | 5 | Design |
| 3:23 | 5 | Generate Report |
| 3:34 | 5 | Design report, Table 5.22: Clear Cover needs >= 75 mm with M45 -> FAIL (with M40: >= 50 mm, pass). Issue [#115](https://github.com/Nidhikhare12/OsdagBridge/issues/115) |
| 3:59 | 6 | Deck back to M40 (inputs equal runs 1-3); Additional Inputs opened and saved with no edits |
| 4:21 | 6 | Design |
| 4:28 | 6 | Results: 3D model; girder diagrams with Member ID switched from Girder 1 to Girder 2 |
| 4:54 | - | Summary card |

What the recording covers for the task: three consecutive runs with the same inputs (runs 1-3), a run with custom
materials (run 4), the 3D CAD model and the girder plots, and the generated design report. Still frames from it are
in `report/figures/` and are discussed in the report section "3D CAD and plots".
