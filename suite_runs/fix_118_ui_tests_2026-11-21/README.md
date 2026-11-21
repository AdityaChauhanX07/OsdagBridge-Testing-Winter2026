# UI tests with the #118 fix applied (headless Linux, 21 Nov 2026)

The fast UI tests (`run_test_suite.py --ui-only`) run against the fix for
[#118](https://github.com/Nidhikhare12/OsdagBridge/issues/118):
branch [`fix/material-dialog-cross-field-checks`](https://github.com/AdityaChauhanX07/OsdagBridge/tree/fix/material-dialog-cross-field-checks)
(commit `5088d19`, on top of `dev` @ `d74f56d`; `session_info.json` records the run before the commit, as uncommitted changes).

Compared with the run on the unmodified code ([`../20261116_011421/checks.csv`](../20261116_011421/checks.csv)), exactly two of the 51 UI checks change, both in U7:

| Check | Before the fix | After the fix |
|---|---|---|
| U7 custom steel fy 450 / fu 400 rejected | FAIL (accepted as `custom_steel_450_400`) | PASS (rejected: "Fu (400 MPa) must be greater than Fy (450 MPa)") |
| U7 custom steel E 200, nu 0.3, G 120 rejected | FAIL (accepted, `material.girder.g = 120`) | PASS (rejected: "G = E / (2(1 + ν)) = 76.9 GPa") |

All other 49 UI checks give the same result as before. The remaining failures are the other reported issues, which this fix does not touch.
