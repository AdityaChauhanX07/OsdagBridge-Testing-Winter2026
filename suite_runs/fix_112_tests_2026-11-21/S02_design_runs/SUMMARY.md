# OsdagBridge automated test suite - fix_112_tests_2026-11-21 (S02 designs with the #112 fix)

Design runs: 5 (ok 5, error 0); checks: 9 pass, 50 fail, 5 info

## Design runs

| case | step | status | s | girders in/checked | spacing in/used (m) | steel dens in/used | deck dens in/used | M_sw ratio | defl check/shown (mm) | status | max DCR |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S02_A_B_A | run1_A | ok | 28.4 | 4/6 | 2.1/2.133 | 76.4/78.5 | 24.5/25.0 | 0.669 | 22.871/51.225 | FAIL | 1.577 |
| S02_A_B_A | run2_B | ok | 53.1 | 5/7 | 2.38/2.405 | 76.4/78.5 | 24.5/25.0 | 0.714 | 30.207/59.754 | FAIL | 1.5115 |
| S02_A_B_A | run3_A | ok | 24.9 | 4/6 | 2.1/2.133 | 76.4/78.5 | 24.5/25.0 | 0.669 | 22.871/51.225 | FAIL | 1.577 |
| S02_A_B_A | fresh_B | ok | 51.8 | 5/7 | 2.38/2.405 | 76.4/78.5 | 24.5/25.0 | 0.714 | 30.207/59.754 | FAIL | 1.5115 |
| S02_A_B_A | typo_B_cw20_then_11 | ok | 52.1 | 5/7 | 2.38/2.405 | 76.4/78.5 | 24.5/25.0 | 0.714 | 30.207/59.754 | FAIL | 1.5115 |

## Failed checks

| case | step | check | title | expected | actual |
|---|---|---|---|---|---|
| S02_A_B_A | run1_A | C01 | Design check uses the real number of girders | 4 | 6 (G1,G2,G3,G4,G5,G6) |
| S02_A_B_A | run1_A | C02 | Grillage girder spacing = input girder spacing | 2.1 | 2.133 |
| S02_A_B_A | run1_A | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S02_A_B_A | run1_A | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S02_A_B_A | run1_A | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.38 | 206.16 (ratio 0.669) |
| S02_A_B_A | run1_A | C06 | Deflection in design check = deflection shown per girder | 22.871 | 51.225 |
| S02_A_B_A | run1_A | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S02_A_B_A | run1_A | C08 | End diaphragm members are designed | 0 empty pairs | 3 of 3 empty |
| S02_A_B_A | run1_A | C09 | Cross-bracing spacing used = Additional Input spacing | 15.0 | 3.0 |
| S02_A_B_A | run1_A | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03492 m2 |
| S02_A_B_A | run2_B | C01 | Design check uses the real number of girders | 5 | 7 (G1,G2,G3,G4,G5,G6,G7) |
| S02_A_B_A | run2_B | C02 | Grillage girder spacing = input girder spacing | 2.38 | 2.405 |
| S02_A_B_A | run2_B | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S02_A_B_A | run2_B | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S02_A_B_A | run2_B | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 958.38 | 684.44 (ratio 0.714) |
| S02_A_B_A | run2_B | C06 | Deflection in design check = deflection shown per girder | 30.207 | 59.754 |
| S02_A_B_A | run2_B | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S02_A_B_A | run2_B | C08 | End diaphragm members are designed | 0 empty pairs | 4 of 4 empty |
| S02_A_B_A | run2_B | C09 | Cross-bracing spacing used = Additional Input spacing | 20.0 | 3.0 |
| S02_A_B_A | run2_B | C10 | Girder area in analysis/self-weight = area in design check | 0.06361 m2 | 0.06104 m2 |
| S02_A_B_A | run3_A | C01 | Design check uses the real number of girders | 4 | 6 (G1,G2,G3,G4,G5,G6) |
| S02_A_B_A | run3_A | C02 | Grillage girder spacing = input girder spacing | 2.1 | 2.133 |
| S02_A_B_A | run3_A | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S02_A_B_A | run3_A | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S02_A_B_A | run3_A | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.38 | 206.16 (ratio 0.669) |
| S02_A_B_A | run3_A | C06 | Deflection in design check = deflection shown per girder | 22.871 | 51.225 |
| S02_A_B_A | run3_A | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S02_A_B_A | run3_A | C08 | End diaphragm members are designed | 0 empty pairs | 3 of 3 empty |
| S02_A_B_A | run3_A | C09 | Cross-bracing spacing used = Additional Input spacing | 15.0 | 3.0 |
| S02_A_B_A | run3_A | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03492 m2 |
| S02_A_B_A | fresh_B | C01 | Design check uses the real number of girders | 5 | 7 (G1,G2,G3,G4,G5,G6,G7) |
| S02_A_B_A | fresh_B | C02 | Grillage girder spacing = input girder spacing | 2.38 | 2.405 |
| S02_A_B_A | fresh_B | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S02_A_B_A | fresh_B | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S02_A_B_A | fresh_B | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 958.38 | 684.44 (ratio 0.714) |
| S02_A_B_A | fresh_B | C06 | Deflection in design check = deflection shown per girder | 30.207 | 59.754 |
| S02_A_B_A | fresh_B | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S02_A_B_A | fresh_B | C08 | End diaphragm members are designed | 0 empty pairs | 4 of 4 empty |
| S02_A_B_A | fresh_B | C09 | Cross-bracing spacing used = Additional Input spacing | 20.0 | 3.0 |
| S02_A_B_A | fresh_B | C10 | Girder area in analysis/self-weight = area in design check | 0.06361 m2 | 0.06104 m2 |
| S02_A_B_A | typo_B_cw20_then_11 | C01 | Design check uses the real number of girders | 5 | 7 (G1,G2,G3,G4,G5,G6,G7) |
| S02_A_B_A | typo_B_cw20_then_11 | C02 | Grillage girder spacing = input girder spacing | 2.38 | 2.405 |
| S02_A_B_A | typo_B_cw20_then_11 | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S02_A_B_A | typo_B_cw20_then_11 | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S02_A_B_A | typo_B_cw20_then_11 | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 958.38 | 684.44 (ratio 0.714) |
| S02_A_B_A | typo_B_cw20_then_11 | C06 | Deflection in design check = deflection shown per girder | 30.207 | 59.754 |
| S02_A_B_A | typo_B_cw20_then_11 | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S02_A_B_A | typo_B_cw20_then_11 | C08 | End diaphragm members are designed | 0 empty pairs | 4 of 4 empty |
| S02_A_B_A | typo_B_cw20_then_11 | C09 | Cross-bracing spacing used = Additional Input spacing | 20.0 | 3.0 |
| S02_A_B_A | typo_B_cw20_then_11 | C10 | Girder area in analysis/self-weight = area in design check | 0.06361 m2 | 0.06104 m2 |
