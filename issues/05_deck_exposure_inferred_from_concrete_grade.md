**Title:** [Bug] Deck cover check infers the exposure class from the concrete grade: upgrading M40 -> M45/M50 switches to "Extreme" exposure, requires 75 mm cover and fails the deck

### What happens
The deck design never asks for the exposure condition. It **derives** the exposure from the concrete grade: it picks "the most severe exposure the grade satisfies". So a better concrete makes the software assume a harsher environment and demand more cover:

| Deck concrete | Exposure assumed | Min. cover required | Provided (default) | Report "Clear Cover" row |
|---|---|---|---|---|
| M40 (default) | Very Severe | 50 mm | 50 mm | PASS |
| M45 | **Extreme** | **75 mm** | 50 mm | **FAIL** |
| M50 | **Extreme** | **75 mm** | 50 mm | **FAIL** |
| custom `custom_concrete_45_3.8` (fck 45) | **Extreme** | **75 mm** | 50 mm | **FAIL** |

The same bridge at the same site passes with M40 and fails with M45. The opposite should happen: IRC 112 Table 14.2 gives the *minimum* grade and cover for a given exposure, so a higher grade can only help. The cover result is also not part of any deck status flag. Only the text and the report row show it, so the overall status ignores it. (The executive summary's "Deck design pass" text is the hard-coded summary already reported in #65.)

### Environment
Windows 11, Python 3.12, `dev` @ `d74f56dd7f22925fb8148cabf5740ed8d1e39ff3` (unmodified). Also reproduced headlessly on Linux.

### Steps to reproduce (GUI)
1. Homepage: span 30 m, carriageway 7.5 m, Optimized, deck concrete **M40**. Design, then generate the report: deck "Clear Cover (IRC 112 Cl. 15.2)" is `>= 50 mm (Table 14.2) ... PASS`.
2. Unlock, change only the deck concrete to **M45**, Design and generate the report: `>= 75 mm (Table 14.2) | Top 50 / Bottom 50 mm | FAIL`. The deck design text says `Concrete grade : M45 -> Exposure: Extreme ... Top cover provided : 50 mm -> BELOW RECOMMENDED`.

### Evidence
* Suite case S10 (M45, M50) vs baseline M40: [`S10_deck_grade/`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/tree/main/suite_runs/headless_linux_2026-11-15/S10_deck_grade) (`deck_design_results.deck_exposure`, `min_cover_recommended`, full deck text in the output dict). Check D1 in [`checks.csv`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/blob/main/suite_runs/headless_linux_2026-11-15/checks.csv).
* GUI run with custom fck 45 on Windows: [`gui_runs/TC01_custom_materials/report/TC01_report.tex`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/blob/main/gui_runs/TC01_custom_materials/report/TC01_report.tex) L1745 (`>= 75 mm ... FAIL`). The M40 run [`TC00_report.tex`](https://github.com/AdityaChauhanX07/OsdagBridge-Testing-Winter2026/blob/main/gui_runs/TC00_baseline/report/TC00_report.tex) L1745 shows `>= 50 mm ... PASS`.

### Root cause
[`irc112_2019.py#L108-L145`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/utils/codes/irc112_2019.py#L108-L145):
```python
chosen = IRC112_2019._TABLE_14_2[0]
for row in IRC112_2019._TABLE_14_2:      # Moderate(25,40) Severe(30,45) Very Severe(40,50) Extreme(45,75)
    if fck_val >= row[3]:                # row[3] = minimum grade for that exposure
        chosen = row                     # -> most severe exposure the grade "satisfies"
```
`deckdesign.py` calls it with the grade only ([`L493-L496`](https://github.com/Nidhikhare12/OsdagBridge/blob/d74f56dd7f22925fb8148cabf5740ed8d1e39ff3/src/osdagbridge/core/bridge_types/plate_girder/deckdesign.py#L493-L496)). `cover_top_ok / cover_bot_ok` only reach the text and report table, not any status flag that the summary uses.

### Suggested fix
Make exposure an input (Additional Inputs > Design Options > Deck, default "Severe" or "Very Severe" for bridge decks) and look the table up **by exposure**. Then check the chosen grade against that row:
```python
@staticmethod
def table_14_2_min_cover(exposure: str, concrete_grade: str) -> dict:
    row = next(r for r in IRC112_2019._TABLE_14_2 if r[0] == exposure)
    fck = int(re.findall(r"\d+", concrete_grade)[0])
    return {"exposure_condition": row[0], "min_cover_mm": row[4], "min_grade_MPa": row[3],
            "grade_ok": fck >= row[3], ...}
```
In `deckdesign.py`, add `cover_top_ok`, `cover_bot_ok` and `grade_ok` to the deck pass/fail status (for example a `deck_status` key next to `deck_exposure`), so that the overall status can use it. Regression test: with the same exposure, M40 -> M45 must not increase the required cover, and a cover shortfall must give a deck FAIL status.

### Duplicate check
Checked all open/closed issues on 15 Nov 2026. #65 covers the hard-coded "design pass" summary text. No issue on how the deck exposure/cover is chosen.
