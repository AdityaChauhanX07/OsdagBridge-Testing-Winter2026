# Tests with the #112 fix applied (headless Linux, 21 Nov 2026)

Runs of [`scripts/run_test_suite.py`](../../scripts/run_test_suite.py) against the fix for
[#112](https://github.com/Nidhikhare12/OsdagBridge/issues/112):
branch [`fix/girder-count-follows-deck-width`](https://github.com/AdityaChauhanX07/OsdagBridge/tree/fix/girder-count-follows-deck-width)
(commit `8d82ae9`, on top of `dev` @ `d74f56d`; `session_info.json` records the runs before the commit, as uncommitted changes).

Compared with the run on the unmodified code ([`../20261116_011421`](../20261116_011421)):

| Check | Before the fix | After the fix |
|---|---|---|
| U2 girder layout for span 40 / cw 11, whatever was typed first | FAIL: 5@2.38, 4@2.975, 3@3.9667, 9@1.3222, 4@2.975 | PASS: 5@2.38 every time |
| R4 design B (span 40 / cw 11) after design A in the same session: girders | FAIL: 4 girders @ 2.975 m | PASS: 5 girders @ 2.38 m |
| R5 same: max DCR | FAIL: 1.686 | PASS: 1.5115 (same as a fresh session) |
| R6 design B after a corrected typo (cw 20 -> 11) | FAIL: 9 girders, max DCR 1.1301 | PASS: 5 girders, max DCR 1.5115 |

All other checks are unchanged: 50 of the 51 UI checks ([`ui_tests`](ui_tests)) and 61 of the 64 S02 checks ([`S02_design_runs`](S02_design_runs)).
The checks that still fail belong to the other reported issues (for example the 7 lines checked for a 5-girder bridge, #113), which this fix does not touch.
