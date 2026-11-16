# Video script (silent screen recording, about 8 minutes)

The task asks for: a custom-material run, 3 consecutive runs, and the 3D CAD and plots.
This script also captures GUI proof for issues 01 and 05.

Recorder: **Win + Alt + R** starts and stops Xbox Game Bar recording of the active window. If Game Bar is off, use the
Windows Snipping Tool's "Record" mode and drag over the whole screen. The file goes to `Videos\Captures`.

Before recording: close other windows, set the screen to 100% zoom if possible, and start the app with logging:
```
cd C:\Users\Aditya\Projects\OsdagBridge\src
python C:\Users\Aditya\Projects\OsdagBridge-Testing-Winter2026\scripts\run_logged.py VIDEO
```

| # | Do this | Hold for |
|---|---|---|
| 1 | Start recording. Fill the homepage: location Mumbai, span 30, carriageway 7.5, skew 0, Optimized, default materials. | - |
| 2 | Click **Design**. When done, show the output dock (scroll it slowly). | 5 s |
| 3 | 3D CAD view: rotate the model with the mouse, zoom in on the girders and cross-frames. | 15 s |
| 4 | Open the plots (bending moment, shear force) for one girder; switch girder G1 -> G2. | 15 s |
| 5 | Unlock (Continue), click **Design** again (run 2). Show the same output values. | 5 s |
| 6 | Unlock, **Design** again (run 3). Show the same output values. | 5 s |
| 7 | Unlock. Girder material -> **Custom**: density 80, fy 410, fu 540, E 210, nu 0.3, thermal 12 -> Save. | - |
| 8 | Deck concrete -> **Custom**: density 26, fck 45, fctm 3.8, Ecm 34, thermal 10 -> Save. **Design** (run 4). Show the output dock and the 3D CAD. | 10 s |
| 9 | Unlock. Set girder material back to E 350A and deck concrete to **M45**. **Design** (run 5). Generate the report, scroll to "Cover and Detailing": the Clear Cover row says 75 mm ... FAIL (issue 05). | 10 s |
| 10 | Unlock. Deck back to M40. Open **Additional Inputs**, change nothing, press **Save**. **Design** (run 6). | 5 s |
| 11 | Stop recording. | - |

Afterwards: upload the video to YouTube (Unlisted) or Google Drive (anyone with the link can view) and send me the link.
Also send the `runs\..._VIDEO` folder. Runs 1-3 prove repeatability, run 4 covers the custom materials, run 5 is the
deck-cover issue, and run 6 vs run 1 is issue 01 (LTB spacing 3 m -> 15 m) in the real GUI.
