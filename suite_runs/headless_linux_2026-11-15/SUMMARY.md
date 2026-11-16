# OsdagBridge automated test suite - full2

Design runs: 34 (ok 32, error 2); checks: 88 pass, 351 fail, 32 info

## Design runs

| case | step | status | s | girders in/checked | spacing in/used (m) | steel dens in/used | deck dens in/used | M_sw ratio | defl check/shown (mm) | status | max DCR |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01_baseline_three_runs | run1 | ok | 21.1 | 4/6 | 2.1/2.133 | 76.4/78.5 | 24.5/25.0 | 0.669 | 22.871/51.225 | FAIL | 1.577 |
| S01_baseline_three_runs | run2 | ok | 16.4 | 4/6 | 2.1/2.133 | 76.4/78.5 | 24.5/25.0 | 0.669 | 22.871/51.225 | FAIL | 1.577 |
| S01_baseline_three_runs | run3 | ok | 17.6 | 4/6 | 2.1/2.133 | 76.4/78.5 | 24.5/25.0 | 0.669 | 22.871/51.225 | FAIL | 1.577 |
| S02_A_B_A | run1_A | ok | 17.7 | 4/6 | 2.1/2.133 | 76.4/78.5 | 24.5/25.0 | 0.669 | 22.871/51.225 | FAIL | 1.577 |
| S02_A_B_A | run2_B | ok | 26.8 | 4/6 | 2.975/3.008 | 76.4/78.5 | 24.5/25.0 | 0.667 | 32.445/67.295 | FAIL | 1.686 |
| S02_A_B_A | run3_A | ok | 16.8 | 4/6 | 2.1/2.133 | 76.4/78.5 | 24.5/25.0 | 0.669 | 22.871/51.225 | FAIL | 1.577 |
| S02_A_B_A | fresh_B | ok | 35.5 | 5/7 | 2.38/2.405 | 76.4/78.5 | 24.5/25.0 | 0.714 | 30.207/59.754 | FAIL | 1.5115 |
| S02_A_B_A | typo_B_cw20_then_11 | ok | 89.8 | 9/11 | 1.3222/1.335 | 76.4/78.5 | 24.5/25.0 | 0.818 | 25.317/43.729 | FAIL | 1.1301 |
| S03_custom_materials | baseline_reference | ok | 17.7 | 4/6 | 2.1/2.133 | 76.4/78.5 | 24.5/25.0 | 0.669 | 22.871/51.225 | FAIL | 1.577 |
| S03_custom_materials | run1_custom | ok | 17.5 | 4/6 | 2.1/2.133 | 80.0/78.5 | 26.0/25.0 | 0.669 | 21.781/48.786 | FAIL | 1.577 |
| S03_custom_materials | run2_back_to_default | ok | 16.9 | 4/6 | 2.1/2.133 | 76.4/78.5 | 24.5/25.0 | 0.669 | 22.871/51.225 | FAIL | 1.577 |
| S04_custom_after_reload | run1_reloaded_custom | error | 12.7 | None/None | None/None | None/None | None/None | None | None/None | None | None |
| S05_additional_inputs | run1_edits | ok | 18.7 | 4/6 | 2.1/2.133 | 76.4/78.5 | 24.5/25.0 | 0.669 | 23.553/56.513 | FAIL | 1.7567 |
| S05_additional_inputs | run2_span32 | ok | 18.8 | 4/6 | 2.1/2.133 | 76.4/78.5 | 24.5/25.0 | 0.666 | 23.881/50.814 | FAIL | 1.4358 |
| S06_girders_and_bracing | run1_5_girders | ok | 22.6 | 5/7 | 1.68/1.705 | 76.4/78.5 | 24.5/25.0 | 0.716 | 21.09/45.052 | FAIL | 1.4022 |
| S06_girders_and_bracing | run2_cb_spacing_5m | ok | 16.8 | 4/6 | 2.1/2.133 | 76.4/78.5 | 24.5/25.0 | 0.669 | 22.863/51.209 | FAIL | 1.5765 |
| S06_girders_and_bracing | run3_bracing_E450A | ok | 17.8 | 4/6 | 2.1/2.133 | 76.4/78.5 | 24.5/25.0 | 0.669 | 22.871/51.225 | FAIL | 1.577 |
| S06_girders_and_bracing | baseline_reference | ok | 17.1 | 4/6 | 2.1/2.133 | 76.4/78.5 | 24.5/25.0 | 0.669 | 22.871/51.225 | FAIL | 1.577 |
| S07_boundaries | span20 | ok | 10.6 | 4/6 | 2.1/2.133 | 76.4/78.51 | 24.5/25.0 | 0.663 | 21.516/60.408 | FAIL | 2.2152 |
| S07_boundaries | span45 | ok | 28.5 | 4/6 | 2.1/2.133 | 76.4/78.5 | 24.5/25.0 | 0.667 | 27.709/49.842 | FAIL | 1.1355 |
| S07_boundaries | cw4.25 | ok | 11.4 | 3/5 | 1.7167/1.767 | 76.4/78.5 | 24.5/25.0 | 0.601 | 16.91/36.297 | FAIL | 1.0856 |
| S07_boundaries | cw23.6 | ok | 91.7 | 10/12 | 2.45/2.461 | 76.4/78.5 | 24.5/25.0 | 0.859 | 35.486/81.952 | FAIL | 2.5041 |
| S07_boundaries | skew+15 | ok | 14.1 | 4/6 | 2.1/2.133 | 76.4/78.5 | 24.5/25.0 | 0.664 | 23.336/None | FAIL | 1.5795 |
| S07_boundaries | skew-15 | ok | 14.4 | 4/6 | 2.1/2.133 | 76.4/78.5 | 24.5/25.0 | 0.664 | 21.75/None | FAIL | 1.4679 |
| S07_boundaries | median_yes_cw15 | ok | 60.4 | 7/9 | 4.5857/4.602 | 76.4/78.5 | 24.5/25.0 | 0.846 | 50.815/130.958 | FAIL | 3.8903 |
| S07_boundaries | footpath_both | ok | 28.7 | 5/7 | 2.43/2.405 | 76.4/78.5 | 24.5/25.0 | 0.717 | 26.511/61.103 | FAIL | 1.8512 |
| S08_stale_after_failure | run1_A | ok | 17.0 | 4/6 | 2.1/2.133 | 76.4/78.5 | 24.5/25.0 | 0.669 | 22.871/51.225 | FAIL | 1.577 |
| S08_stale_after_failure | run2_fail | error | 0.4 | None/None | None/None | None/None | None/None | None | None/None | None | None |
| S08_stale_after_failure | run3_A | ok | 17.1 | 4/6 | 2.1/2.133 | 76.4/78.5 | 24.5/25.0 | 0.669 | 22.871/51.225 | FAIL | 1.577 |
| S09_osi_bad_material | run1_fy5000 | ok | 18.0 | 4/6 | 2.1/2.133 | 76.4/78.5 | 24.5/25.0 | 0.669 | 22.871/51.225 | FAIL | 1.577 |
| S10_deck_grade | deck_M45 | ok | 18.9 | 4/6 | 2.1/2.133 | 76.4/78.5 | 24.5/25.0 | 0.669 | 22.871/51.225 | FAIL | 1.577 |
| S10_deck_grade | deck_M50 | ok | 18.9 | 4/6 | 2.1/2.133 | 76.4/78.5 | 24.5/25.0 | 0.669 | 22.871/51.225 | FAIL | 1.577 |
| S11_open_additional_inputs_no_edit | baseline_reference | ok | 17.4 | 4/6 | 2.1/2.133 | 76.4/78.5 | 24.5/25.0 | 0.669 | 22.871/51.225 | FAIL | 1.577 |
| S11_open_additional_inputs_no_edit | opened_and_saved_no_edits | ok | 17.2 | 4/6 | 2.1/2.133 | 76.4/78.5 | 24.5/25.0 | 0.669 | 22.863/51.209 | FAIL | 1.5765 |

## Failed checks

| case | step | check | title | expected | actual |
|---|---|---|---|---|---|
| U2_girder_count_history | - | U2 | Girder layout depends only on current inputs (not on typing history) | 5 girders @ 2.38 m every time | 5@2.38; 4@2.975; 3@3.9667; 9@1.3222; 4@2.975 |
| U3_additional_inputs_reset | - | U3a | Additional Inputs kept after changing span 30->32 | all edits kept | 6 reset: {'typical_section.deck_thickness': '300.0->250.0', 'typical_section.wearing_course.thickness': '80.0->50.0', 'design_options_cont.p |
| U3_additional_inputs_reset | - | U3b1 | Save Input writes the edited Additional Inputs to the .osi | all edits in file | 6 reset in file: {'typical_section.deck_thickness': '300.0->250.0', 'typical_section.wearing_course.thickness': '80.0->50.0', 'design_option |
| U3_additional_inputs_reset | - | U3b2 | Session still has the edits after clicking Save Input | all edits kept | 6 reset: {'typical_section.deck_thickness': '300.0->250.0', 'typical_section.wearing_course.thickness': '80.0->50.0', 'design_options_cont.p |
| U3_additional_inputs_reset | - | U3c | Additional Inputs kept after Load Input (file contains them) | all edits kept | 6 reset: {'typical_section.deck_thickness': '300.0->250.0', 'typical_section.wearing_course.thickness': '80.0->50.0', 'design_options_cont.p |
| U4_custom_material_reload | - | U4b | Custom material values survive Save > Load > Design | {"material.girder.fy": "410", "material.girder.e": "210", "material.girder.densi | changed: {'material.deck.fck': '45->None', 'material.deck.fctm': '3.8->None', 'material.deck.ecm': '34->None', 'material.deck.density': '26- |
| U4_custom_material_reload | - | U4c | (i) info button works for a loaded custom steel | dialog opens | UnboundLocalError: cannot access local variable 'defaults' where it is not associated with a value |
| U4_custom_material_reload | - | U4d | Re-selecting the custom steel restores its fy/E | custom_steel_410_540: fy 410, E 210 | combo=custom_steel_410_540 fy=250.0 E=200.0 |
| U6_osi_validation | custom steel fy 5000 MPa | U6 | .osi with custom steel fy 5000 MPa rejected | reject | LOADED |
| U6_osi_validation | girder density 999 (custom) | U6 | .osi with girder density 999 (custom) rejected | reject | LOADED |
| U6_osi_validation | deck fck 500 (custom) | U6 | .osi with deck fck 500 (custom) rejected | reject | LOADED |
| U6_osi_validation | girder grade 'E 999X' | U6 | .osi with girder grade 'E 999X' rejected | reject | LOADED |
| U7_custom_material_dialog | fu < fy (450/400) | U7 | Custom steel fu < fy (450/400) rejected | reject | accepted as custom_steel_450_400 (fy=450, fu=400, G=76.9) |
| U7_custom_material_dialog | G inconsistent with E,nu (E200, nu0.3, G 120) | U7 | Custom steel G inconsistent with E,nu (E200, nu0.3, G 120) rejected | reject | accepted as custom_steel_410_540 (fy=410, fu=540, G=120) |
| U8_backend_validation | span 100 m | U8 | Backend rejects span 100 m | ValueError | accepted (no range check) |
| U8_backend_validation | carriageway 40 m | U8 | Backend rejects carriageway 40 m | ValueError | accepted (no range check) |
| U8_backend_validation | skew 60 deg | U8 | Backend rejects skew 60 deg | ValueError | accepted (no range check) |
| U8_backend_validation | girder fy 5000 | U8 | Backend rejects girder fy 5000 | ValueError | accepted (no range check) |
| S01_baseline_three_runs | run1 | C01 | Design check uses the real number of girders | 4 | 6 (G1,G2,G3,G4,G5,G6) |
| S01_baseline_three_runs | run1 | C02 | Grillage girder spacing = input girder spacing | 2.1 | 2.133 |
| S01_baseline_three_runs | run1 | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S01_baseline_three_runs | run1 | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S01_baseline_three_runs | run1 | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.38 | 206.16 (ratio 0.669) |
| S01_baseline_three_runs | run1 | C06 | Deflection in design check = deflection shown per girder | 22.871 | 51.225 |
| S01_baseline_three_runs | run1 | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S01_baseline_three_runs | run1 | C08 | End diaphragm members are designed | 0 empty pairs | 3 of 3 empty |
| S01_baseline_three_runs | run1 | C09 | Cross-bracing spacing used = Additional Input spacing | 15.0 | 3.0 |
| S01_baseline_three_runs | run1 | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03492 m2 |
| S01_baseline_three_runs | run2 | C01 | Design check uses the real number of girders | 4 | 6 (G1,G2,G3,G4,G5,G6) |
| S01_baseline_three_runs | run2 | C02 | Grillage girder spacing = input girder spacing | 2.1 | 2.133 |
| S01_baseline_three_runs | run2 | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S01_baseline_three_runs | run2 | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S01_baseline_three_runs | run2 | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.38 | 206.16 (ratio 0.669) |
| S01_baseline_three_runs | run2 | C06 | Deflection in design check = deflection shown per girder | 22.871 | 51.225 |
| S01_baseline_three_runs | run2 | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S01_baseline_three_runs | run2 | C08 | End diaphragm members are designed | 0 empty pairs | 3 of 3 empty |
| S01_baseline_three_runs | run2 | C09 | Cross-bracing spacing used = Additional Input spacing | 15.0 | 3.0 |
| S01_baseline_three_runs | run2 | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03492 m2 |
| S01_baseline_three_runs | run3 | C01 | Design check uses the real number of girders | 4 | 6 (G1,G2,G3,G4,G5,G6) |
| S01_baseline_three_runs | run3 | C02 | Grillage girder spacing = input girder spacing | 2.1 | 2.133 |
| S01_baseline_three_runs | run3 | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S01_baseline_three_runs | run3 | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S01_baseline_three_runs | run3 | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.38 | 206.16 (ratio 0.669) |
| S01_baseline_three_runs | run3 | C06 | Deflection in design check = deflection shown per girder | 22.871 | 51.225 |
| S01_baseline_three_runs | run3 | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S01_baseline_three_runs | run3 | C08 | End diaphragm members are designed | 0 empty pairs | 3 of 3 empty |
| S01_baseline_three_runs | run3 | C09 | Cross-bracing spacing used = Additional Input spacing | 15.0 | 3.0 |
| S01_baseline_three_runs | run3 | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03492 m2 |
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
| S02_A_B_A | run2_B | C01 | Design check uses the real number of girders | 4 | 6 (G1,G2,G3,G4,G5,G6) |
| S02_A_B_A | run2_B | C02 | Grillage girder spacing = input girder spacing | 2.975 | 3.008 |
| S02_A_B_A | run2_B | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S02_A_B_A | run2_B | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S02_A_B_A | run2_B | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 958.38 | 638.85 (ratio 0.667) |
| S02_A_B_A | run2_B | C06 | Deflection in design check = deflection shown per girder | 32.445 | 67.295 |
| S02_A_B_A | run2_B | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S02_A_B_A | run2_B | C08 | End diaphragm members are designed | 0 empty pairs | 3 of 3 empty |
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
| S02_A_B_A | - | R4 | B after A (same session) == B typed in a fresh session (girders) | 5 girders @ 2.38 m (fresh) | 4 girders @ 2.975 m (after A) |
| S02_A_B_A | - | R5 | B after A (same session) == B typed in a fresh session (max DCR / status) | 1.5115 FAIL | 1.686 FAIL |
| S02_A_B_A | typo_B_cw20_then_11 | C01 | Design check uses the real number of girders | 9 | 11 (G1,G2,G3,G4,G5,G6,G7,G8,G9,G10,G11) |
| S02_A_B_A | typo_B_cw20_then_11 | C02 | Grillage girder spacing = input girder spacing | 1.3222 | 1.335 |
| S02_A_B_A | typo_B_cw20_then_11 | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S02_A_B_A | typo_B_cw20_then_11 | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S02_A_B_A | typo_B_cw20_then_11 | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 958.38 | 783.99 (ratio 0.818) |
| S02_A_B_A | typo_B_cw20_then_11 | C06 | Deflection in design check = deflection shown per girder | 25.317 | 43.729 |
| S02_A_B_A | typo_B_cw20_then_11 | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S02_A_B_A | typo_B_cw20_then_11 | C08 | End diaphragm members are designed | 0 empty pairs | 8 of 8 empty |
| S02_A_B_A | typo_B_cw20_then_11 | C09 | Cross-bracing spacing used = Additional Input spacing | 20.0 | 3.0 |
| S02_A_B_A | typo_B_cw20_then_11 | C10 | Girder area in analysis/self-weight = area in design check | 0.06361 m2 | 0.06104 m2 |
| S02_A_B_A | - | R6 | B with a corrected typo (cw 20 -> 11) == B typed directly | 5 girders, max DCR 1.5115 | 9 girders, max DCR 1.1301 FAIL |
| S03_custom_materials | baseline_reference | C01 | Design check uses the real number of girders | 4 | 6 (G1,G2,G3,G4,G5,G6) |
| S03_custom_materials | baseline_reference | C02 | Grillage girder spacing = input girder spacing | 2.1 | 2.133 |
| S03_custom_materials | baseline_reference | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S03_custom_materials | baseline_reference | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S03_custom_materials | baseline_reference | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.38 | 206.16 (ratio 0.669) |
| S03_custom_materials | baseline_reference | C06 | Deflection in design check = deflection shown per girder | 22.871 | 51.225 |
| S03_custom_materials | baseline_reference | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S03_custom_materials | baseline_reference | C08 | End diaphragm members are designed | 0 empty pairs | 3 of 3 empty |
| S03_custom_materials | baseline_reference | C09 | Cross-bracing spacing used = Additional Input spacing | 15.0 | 3.0 |
| S03_custom_materials | baseline_reference | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03492 m2 |
| S03_custom_materials | run1_custom | C01 | Design check uses the real number of girders | 4 | 6 (G1,G2,G3,G4,G5,G6) |
| S03_custom_materials | run1_custom | C02 | Grillage girder spacing = input girder spacing | 2.1 | 2.133 |
| S03_custom_materials | run1_custom | C03 | Steel self-weight uses the girder material density | 80.0 | 78.5 |
| S03_custom_materials | run1_custom | C04 | Deck slab load uses the deck material density | 26.0 | 25.0 |
| S03_custom_materials | run1_custom | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.38 | 206.16 (ratio 0.669) |
| S03_custom_materials | run1_custom | C06 | Deflection in design check = deflection shown per girder | 21.781 | 48.786 |
| S03_custom_materials | run1_custom | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S03_custom_materials | run1_custom | C08 | End diaphragm members are designed | 0 empty pairs | 3 of 3 empty |
| S03_custom_materials | run1_custom | C09 | Cross-bracing spacing used = Additional Input spacing | 15.0 | 3.0 |
| S03_custom_materials | run1_custom | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03492 m2 |
| S03_custom_materials | - | M1 | Custom girder density 80 changes the girder self-weight | != 2741.12 N/m | 2741.12 |
| S03_custom_materials | - | M2 | Custom deck density 26 changes the deck design moments | != 30.898 kNm/m | 30.898 |
| S03_custom_materials | - | M4 | Deck exposure/cover with custom M45-equivalent concrete | Very Severe (same environment as baseline) | Extreme, cover 75 mm |
| S03_custom_materials | run2_back_to_default | C01 | Design check uses the real number of girders | 4 | 6 (G1,G2,G3,G4,G5,G6) |
| S03_custom_materials | run2_back_to_default | C02 | Grillage girder spacing = input girder spacing | 2.1 | 2.133 |
| S03_custom_materials | run2_back_to_default | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S03_custom_materials | run2_back_to_default | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S03_custom_materials | run2_back_to_default | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.38 | 206.16 (ratio 0.669) |
| S03_custom_materials | run2_back_to_default | C06 | Deflection in design check = deflection shown per girder | 22.871 | 51.225 |
| S03_custom_materials | run2_back_to_default | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S03_custom_materials | run2_back_to_default | C08 | End diaphragm members are designed | 0 empty pairs | 3 of 3 empty |
| S03_custom_materials | run2_back_to_default | C09 | Cross-bracing spacing used = Additional Input spacing | 15.0 | 3.0 |
| S03_custom_materials | run2_back_to_default | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03492 m2 |
| S04_custom_after_reload | - | U4b | Custom material values survive Save > Load > Design | {"material.girder.fy": "410", "material.girder.e": "210", "material.girder.densi | changed: {'material.deck.fck': '45->None', 'material.deck.fctm': '3.8->None', 'material.deck.ecm': '34->None', 'material.deck.density': '26- |
| S04_custom_after_reload | - | U4c | (i) info button works for a loaded custom steel | dialog opens | UnboundLocalError: cannot access local variable 'defaults' where it is not associated with a value |
| S04_custom_after_reload | - | U4d | Re-selecting the custom steel restores its fy/E | custom_steel_410_540: fy 410, E 210 | combo=custom_steel_410_540 fy=250.0 E=200.0 |
| S05_additional_inputs | run1_edits | C01 | Design check uses the real number of girders | 4 | 6 (G1,G2,G3,G4,G5,G6) |
| S05_additional_inputs | run1_edits | C02 | Grillage girder spacing = input girder spacing | 2.1 | 2.133 |
| S05_additional_inputs | run1_edits | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S05_additional_inputs | run1_edits | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S05_additional_inputs | run1_edits | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.21 | 206.21 (ratio 0.669) |
| S05_additional_inputs | run1_edits | C06 | Deflection in design check = deflection shown per girder | 23.553 | 56.513 |
| S05_additional_inputs | run1_edits | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S05_additional_inputs | run1_edits | C08 | End diaphragm members are designed | 0 empty pairs | 3 of 3 empty |
| S05_additional_inputs | run1_edits | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03490 m2 |
| S05_additional_inputs | run2_span32 | C01 | Design check uses the real number of girders | 4 | 6 (G1,G2,G3,G4,G5,G6) |
| S05_additional_inputs | run2_span32 | C02 | Grillage girder spacing = input girder spacing | 2.1 | 2.133 |
| S05_additional_inputs | run2_span32 | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S05_additional_inputs | run2_span32 | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S05_additional_inputs | run2_span32 | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 395.4 | 263.18 (ratio 0.666) |
| S05_additional_inputs | run2_span32 | C06 | Deflection in design check = deflection shown per girder | 23.881 | 50.814 |
| S05_additional_inputs | run2_span32 | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S05_additional_inputs | run2_span32 | C08 | End diaphragm members are designed | 0 empty pairs | 3 of 3 empty |
| S05_additional_inputs | run2_span32 | C09 | Cross-bracing spacing used = Additional Input spacing | 16.0 | 15.0 |
| S05_additional_inputs | run2_span32 | C10 | Girder area in analysis/self-weight = area in design check | 0.04430 m2 | 0.03935 m2 |
| S05_additional_inputs | - | A2 | Deck thickness after changing span (user never re-edited it) | 300 | 250.0 |
| S06_girders_and_bracing | run1_5_girders | C01 | Design check uses the real number of girders | 5 | 7 (G1,G2,G3,G4,G5,G6,G7) |
| S06_girders_and_bracing | run1_5_girders | C02 | Grillage girder spacing = input girder spacing | 1.68 | 1.705 |
| S06_girders_and_bracing | run1_5_girders | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S06_girders_and_bracing | run1_5_girders | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S06_girders_and_bracing | run1_5_girders | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.38 | 220.89 (ratio 0.716) |
| S06_girders_and_bracing | run1_5_girders | C06 | Deflection in design check = deflection shown per girder | 21.09 | 45.052 |
| S06_girders_and_bracing | run1_5_girders | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S06_girders_and_bracing | run1_5_girders | C08 | End diaphragm members are designed | 0 empty pairs | 4 of 4 empty |
| S06_girders_and_bracing | run1_5_girders | C09 | Cross-bracing spacing used = Additional Input spacing | 15.0 | 3.0 |
| S06_girders_and_bracing | run1_5_girders | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03492 m2 |
| S06_girders_and_bracing | run2_cb_spacing_5m | C01 | Design check uses the real number of girders | 4 | 6 (G1,G2,G3,G4,G5,G6) |
| S06_girders_and_bracing | run2_cb_spacing_5m | C02 | Grillage girder spacing = input girder spacing | 2.1 | 2.133 |
| S06_girders_and_bracing | run2_cb_spacing_5m | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S06_girders_and_bracing | run2_cb_spacing_5m | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S06_girders_and_bracing | run2_cb_spacing_5m | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.21 | 206.21 (ratio 0.669) |
| S06_girders_and_bracing | run2_cb_spacing_5m | C06 | Deflection in design check = deflection shown per girder | 22.863 | 51.209 |
| S06_girders_and_bracing | run2_cb_spacing_5m | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S06_girders_and_bracing | run2_cb_spacing_5m | C08 | End diaphragm members are designed | 0 empty pairs | 3 of 3 empty |
| S06_girders_and_bracing | run2_cb_spacing_5m | C09 | Cross-bracing spacing used = Additional Input spacing | 5.0 | 15.0 |
| S06_girders_and_bracing | run2_cb_spacing_5m | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03490 m2 |
| S06_girders_and_bracing | run3_bracing_E450A | C01 | Design check uses the real number of girders | 4 | 6 (G1,G2,G3,G4,G5,G6) |
| S06_girders_and_bracing | run3_bracing_E450A | C02 | Grillage girder spacing = input girder spacing | 2.1 | 2.133 |
| S06_girders_and_bracing | run3_bracing_E450A | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S06_girders_and_bracing | run3_bracing_E450A | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S06_girders_and_bracing | run3_bracing_E450A | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.38 | 206.16 (ratio 0.669) |
| S06_girders_and_bracing | run3_bracing_E450A | C06 | Deflection in design check = deflection shown per girder | 22.871 | 51.225 |
| S06_girders_and_bracing | run3_bracing_E450A | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S06_girders_and_bracing | run3_bracing_E450A | C08 | End diaphragm members are designed | 0 empty pairs | 3 of 3 empty |
| S06_girders_and_bracing | run3_bracing_E450A | C09 | Cross-bracing spacing used = Additional Input spacing | 15.0 | 3.0 |
| S06_girders_and_bracing | run3_bracing_E450A | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03492 m2 |
| S06_girders_and_bracing | baseline_reference | C01 | Design check uses the real number of girders | 4 | 6 (G1,G2,G3,G4,G5,G6) |
| S06_girders_and_bracing | baseline_reference | C02 | Grillage girder spacing = input girder spacing | 2.1 | 2.133 |
| S06_girders_and_bracing | baseline_reference | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S06_girders_and_bracing | baseline_reference | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S06_girders_and_bracing | baseline_reference | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.38 | 206.16 (ratio 0.669) |
| S06_girders_and_bracing | baseline_reference | C06 | Deflection in design check = deflection shown per girder | 22.871 | 51.225 |
| S06_girders_and_bracing | baseline_reference | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S06_girders_and_bracing | baseline_reference | C08 | End diaphragm members are designed | 0 empty pairs | 3 of 3 empty |
| S06_girders_and_bracing | baseline_reference | C09 | Cross-bracing spacing used = Additional Input spacing | 15.0 | 3.0 |
| S06_girders_and_bracing | baseline_reference | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03492 m2 |
| S06_girders_and_bracing | - | M6 | Cross-bracing steel E 350A -> E 450A changes bracing design | different capacities | identical sections and capacities |
| S07_boundaries | span20 | C01 | Design check uses the real number of girders | 4 | 6 (G1,G2,G3,G4,G5,G6) |
| S07_boundaries | span20 | C02 | Grillage girder spacing = input girder spacing | 2.1 | 2.133 |
| S07_boundaries | span20 | C03 | Steel self-weight uses the girder material density | 76.4 | 78.51 |
| S07_boundaries | span20 | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S07_boundaries | span20 | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 61.2 | 40.6 (ratio 0.663) |
| S07_boundaries | span20 | C06 | Deflection in design check = deflection shown per girder | 21.516 | 60.408 |
| S07_boundaries | span20 | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S07_boundaries | span20 | C08 | End diaphragm members are designed | 0 empty pairs | 3 of 3 empty |
| S07_boundaries | span20 | C09 | Cross-bracing spacing used = Additional Input spacing | 10.0 | 3.0 |
| S07_boundaries | span20 | C10 | Girder area in analysis/self-weight = area in design check | 0.01958 m2 | 0.01559 m2 |
| S07_boundaries | span45 | C01 | Design check uses the real number of girders | 4 | 6 (G1,G2,G3,G4,G5,G6) |
| S07_boundaries | span45 | C02 | Grillage girder spacing = input girder spacing | 2.1 | 2.133 |
| S07_boundaries | span45 | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S07_boundaries | span45 | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S07_boundaries | span45 | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 1521.71 | 1014.64 (ratio 0.667) |
| S07_boundaries | span45 | C06 | Deflection in design check = deflection shown per girder | 27.709 | 49.842 |
| S07_boundaries | span45 | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S07_boundaries | span45 | C08 | End diaphragm members are designed | 0 empty pairs | 3 of 3 empty |
| S07_boundaries | span45 | C09 | Cross-bracing spacing used = Additional Input spacing | 22.5 | 3.0 |
| S07_boundaries | span45 | C10 | Girder area in analysis/self-weight = area in design check | 0.08210 m2 | 0.07658 m2 |
| S07_boundaries | cw4.25 | C01 | Design check uses the real number of girders | 3 | 5 (G1,G2,G3,G4,G5) |
| S07_boundaries | cw4.25 | C02 | Grillage girder spacing = input girder spacing | 1.7167 | 1.767 |
| S07_boundaries | cw4.25 | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S07_boundaries | cw4.25 | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S07_boundaries | cw4.25 | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.38 | 185.33 (ratio 0.601) |
| S07_boundaries | cw4.25 | C06 | Deflection in design check = deflection shown per girder | 16.91 | 36.297 |
| S07_boundaries | cw4.25 | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S07_boundaries | cw4.25 | C08 | End diaphragm members are designed | 0 empty pairs | 2 of 2 empty |
| S07_boundaries | cw4.25 | C09 | Cross-bracing spacing used = Additional Input spacing | 15.0 | 3.0 |
| S07_boundaries | cw4.25 | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03492 m2 |
| S07_boundaries | cw23.6 | C01 | Design check uses the real number of girders | 10 | 12 (G1,G2,G3,G4,G5,G6,G7,G8,G9,G10,G11,G12) |
| S07_boundaries | cw23.6 | C02 | Grillage girder spacing = input girder spacing | 2.45 | 2.461 |
| S07_boundaries | cw23.6 | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S07_boundaries | cw23.6 | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S07_boundaries | cw23.6 | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.38 | 264.99 (ratio 0.859) |
| S07_boundaries | cw23.6 | C06 | Deflection in design check = deflection shown per girder | 35.486 | 81.952 |
| S07_boundaries | cw23.6 | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S07_boundaries | cw23.6 | C08 | End diaphragm members are designed | 0 empty pairs | 9 of 9 empty |
| S07_boundaries | cw23.6 | C09 | Cross-bracing spacing used = Additional Input spacing | 15.0 | 3.0 |
| S07_boundaries | cw23.6 | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03492 m2 |
| S07_boundaries | skew+15 | C01 | Design check uses the real number of girders | 4 | 6 (G1) |
| S07_boundaries | skew+15 | C02 | Grillage girder spacing = input girder spacing | 2.1 | 2.133 |
| S07_boundaries | skew+15 | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S07_boundaries | skew+15 | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S07_boundaries | skew+15 | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.38 | 204.73 (ratio 0.664) |
| S07_boundaries | skew+15 | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S07_boundaries | skew+15 | C09 | Cross-bracing spacing used = Additional Input spacing | 15.0 | 3.0 |
| S07_boundaries | skew+15 | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03492 m2 |
| S07_boundaries | skew-15 | C01 | Design check uses the real number of girders | 4 | 6 (G1) |
| S07_boundaries | skew-15 | C02 | Grillage girder spacing = input girder spacing | 2.1 | 2.133 |
| S07_boundaries | skew-15 | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S07_boundaries | skew-15 | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S07_boundaries | skew-15 | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.38 | 204.73 (ratio 0.664) |
| S07_boundaries | skew-15 | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S07_boundaries | skew-15 | C09 | Cross-bracing spacing used = Additional Input spacing | 15.0 | 3.0 |
| S07_boundaries | skew-15 | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03492 m2 |
| S07_boundaries | median_yes_cw15 | C01 | Design check uses the real number of girders | 7 | 9 (G1,G2,G3,G4,G5,G6,G7,G8,G9) |
| S07_boundaries | median_yes_cw15 | C02 | Grillage girder spacing = input girder spacing | 4.5857 | 4.602 |
| S07_boundaries | median_yes_cw15 | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S07_boundaries | median_yes_cw15 | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S07_boundaries | median_yes_cw15 | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.38 | 260.74 (ratio 0.846) |
| S07_boundaries | median_yes_cw15 | C06 | Deflection in design check = deflection shown per girder | 50.815 | 130.958 |
| S07_boundaries | median_yes_cw15 | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S07_boundaries | median_yes_cw15 | C08 | End diaphragm members are designed | 0 empty pairs | 6 of 6 empty |
| S07_boundaries | median_yes_cw15 | C09 | Cross-bracing spacing used = Additional Input spacing | 15.0 | 3.0 |
| S07_boundaries | median_yes_cw15 | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03492 m2 |
| S07_boundaries | footpath_both | C01 | Design check uses the real number of girders | 5 | 7 (G1,G2,G3,G4,G5,G6,G7) |
| S07_boundaries | footpath_both | C02 | Grillage girder spacing = input girder spacing | 2.43 | 2.405 |
| S07_boundaries | footpath_both | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S07_boundaries | footpath_both | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S07_boundaries | footpath_both | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.38 | 221.11 (ratio 0.717) |
| S07_boundaries | footpath_both | C06 | Deflection in design check = deflection shown per girder | 26.511 | 61.103 |
| S07_boundaries | footpath_both | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S07_boundaries | footpath_both | C08 | End diaphragm members are designed | 0 empty pairs | 4 of 4 empty |
| S07_boundaries | footpath_both | C09 | Cross-bracing spacing used = Additional Input spacing | 15.0 | 3.0 |
| S07_boundaries | footpath_both | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03492 m2 |
| S08_stale_after_failure | run1_A | C01 | Design check uses the real number of girders | 4 | 6 (G1,G2,G3,G4,G5,G6) |
| S08_stale_after_failure | run1_A | C02 | Grillage girder spacing = input girder spacing | 2.1 | 2.133 |
| S08_stale_after_failure | run1_A | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S08_stale_after_failure | run1_A | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S08_stale_after_failure | run1_A | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.38 | 206.16 (ratio 0.669) |
| S08_stale_after_failure | run1_A | C06 | Deflection in design check = deflection shown per girder | 22.871 | 51.225 |
| S08_stale_after_failure | run1_A | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S08_stale_after_failure | run1_A | C08 | End diaphragm members are designed | 0 empty pairs | 3 of 3 empty |
| S08_stale_after_failure | run1_A | C09 | Cross-bracing spacing used = Additional Input spacing | 15.0 | 3.0 |
| S08_stale_after_failure | run1_A | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03492 m2 |
| S08_stale_after_failure | run3_A | C01 | Design check uses the real number of girders | 4 | 6 (G1,G2,G3,G4,G5,G6) |
| S08_stale_after_failure | run3_A | C02 | Grillage girder spacing = input girder spacing | 2.1 | 2.133 |
| S08_stale_after_failure | run3_A | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S08_stale_after_failure | run3_A | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S08_stale_after_failure | run3_A | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.38 | 206.16 (ratio 0.669) |
| S08_stale_after_failure | run3_A | C06 | Deflection in design check = deflection shown per girder | 22.871 | 51.225 |
| S08_stale_after_failure | run3_A | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S08_stale_after_failure | run3_A | C08 | End diaphragm members are designed | 0 empty pairs | 3 of 3 empty |
| S08_stale_after_failure | run3_A | C09 | Cross-bracing spacing used = Additional Input spacing | 15.0 | 3.0 |
| S08_stale_after_failure | run3_A | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03492 m2 |
| S09_osi_bad_material | custom steel fy 5000 MPa | U6 | .osi with custom steel fy 5000 MPa rejected | reject | LOADED |
| S09_osi_bad_material | girder density 999 (custom) | U6 | .osi with girder density 999 (custom) rejected | reject | LOADED |
| S09_osi_bad_material | deck fck 500 (custom) | U6 | .osi with deck fck 500 (custom) rejected | reject | LOADED |
| S09_osi_bad_material | girder grade 'E 999X' | U6 | .osi with girder grade 'E 999X' rejected | reject | LOADED |
| S09_osi_bad_material | run1_fy5000 | C01 | Design check uses the real number of girders | 4 | 6 (G1,G2,G3,G4,G5,G6) |
| S09_osi_bad_material | run1_fy5000 | C02 | Grillage girder spacing = input girder spacing | 2.1 | 2.133 |
| S09_osi_bad_material | run1_fy5000 | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S09_osi_bad_material | run1_fy5000 | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S09_osi_bad_material | run1_fy5000 | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.38 | 206.16 (ratio 0.669) |
| S09_osi_bad_material | run1_fy5000 | C06 | Deflection in design check = deflection shown per girder | 22.871 | 51.225 |
| S09_osi_bad_material | run1_fy5000 | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S09_osi_bad_material | run1_fy5000 | C08 | End diaphragm members are designed | 0 empty pairs | 3 of 3 empty |
| S09_osi_bad_material | run1_fy5000 | C09 | Cross-bracing spacing used = Additional Input spacing | 15.0 | 3.0 |
| S09_osi_bad_material | run1_fy5000 | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03492 m2 |
| S09_osi_bad_material | - | V1 | Design refuses fy = 5000 MPa loaded from .osi | error / refused | designed with fy=5000.0 MPa, status FAIL |
| S10_deck_grade | deck_M45 | C01 | Design check uses the real number of girders | 4 | 6 (G1,G2,G3,G4,G5,G6) |
| S10_deck_grade | deck_M45 | C02 | Grillage girder spacing = input girder spacing | 2.1 | 2.133 |
| S10_deck_grade | deck_M45 | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S10_deck_grade | deck_M45 | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S10_deck_grade | deck_M45 | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.38 | 206.16 (ratio 0.669) |
| S10_deck_grade | deck_M45 | C06 | Deflection in design check = deflection shown per girder | 22.871 | 51.225 |
| S10_deck_grade | deck_M45 | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S10_deck_grade | deck_M45 | C08 | End diaphragm members are designed | 0 empty pairs | 3 of 3 empty |
| S10_deck_grade | deck_M45 | C09 | Cross-bracing spacing used = Additional Input spacing | 15.0 | 3.0 |
| S10_deck_grade | deck_M45 | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03492 m2 |
| S10_deck_grade | deck_M50 | C01 | Design check uses the real number of girders | 4 | 6 (G1,G2,G3,G4,G5,G6) |
| S10_deck_grade | deck_M50 | C02 | Grillage girder spacing = input girder spacing | 2.1 | 2.133 |
| S10_deck_grade | deck_M50 | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S10_deck_grade | deck_M50 | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S10_deck_grade | deck_M50 | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.38 | 206.16 (ratio 0.669) |
| S10_deck_grade | deck_M50 | C06 | Deflection in design check = deflection shown per girder | 22.871 | 51.225 |
| S10_deck_grade | deck_M50 | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S10_deck_grade | deck_M50 | C08 | End diaphragm members are designed | 0 empty pairs | 3 of 3 empty |
| S10_deck_grade | deck_M50 | C09 | Cross-bracing spacing used = Additional Input spacing | 15.0 | 3.0 |
| S10_deck_grade | deck_M50 | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03492 m2 |
| S10_deck_grade | - | D1 | Exposure class does not change when only the concrete grade changes | Very Severe for every grade | M40->Very Severe (50 mm), M45->Extreme (75 mm), M50->Extreme (75 mm) |
| S11_open_additional_inputs_no_edit | baseline_reference | C01 | Design check uses the real number of girders | 4 | 6 (G1,G2,G3,G4,G5,G6) |
| S11_open_additional_inputs_no_edit | baseline_reference | C02 | Grillage girder spacing = input girder spacing | 2.1 | 2.133 |
| S11_open_additional_inputs_no_edit | baseline_reference | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S11_open_additional_inputs_no_edit | baseline_reference | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S11_open_additional_inputs_no_edit | baseline_reference | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.38 | 206.16 (ratio 0.669) |
| S11_open_additional_inputs_no_edit | baseline_reference | C06 | Deflection in design check = deflection shown per girder | 22.871 | 51.225 |
| S11_open_additional_inputs_no_edit | baseline_reference | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S11_open_additional_inputs_no_edit | baseline_reference | C08 | End diaphragm members are designed | 0 empty pairs | 3 of 3 empty |
| S11_open_additional_inputs_no_edit | baseline_reference | C09 | Cross-bracing spacing used = Additional Input spacing | 15.0 | 3.0 |
| S11_open_additional_inputs_no_edit | baseline_reference | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03492 m2 |
| S11_open_additional_inputs_no_edit | opened_and_saved_no_edits | C01 | Design check uses the real number of girders | 4 | 6 (G1,G2,G3,G4,G5,G6) |
| S11_open_additional_inputs_no_edit | opened_and_saved_no_edits | C02 | Grillage girder spacing = input girder spacing | 2.1 | 2.133 |
| S11_open_additional_inputs_no_edit | opened_and_saved_no_edits | C03 | Steel self-weight uses the girder material density | 76.4 | 78.5 |
| S11_open_additional_inputs_no_edit | opened_and_saved_no_edits | C04 | Deck slab load uses the deck material density | 24.5 | 25.0 |
| S11_open_additional_inputs_no_edit | opened_and_saved_no_edits | C05 | Girder self-weight moment ~ w*L^2/8 (simply supported) | 308.21 | 206.21 (ratio 0.669) |
| S11_open_additional_inputs_no_edit | opened_and_saved_no_edits | C06 | Deflection in design check = deflection shown per girder | 22.863 | 51.209 |
| S11_open_additional_inputs_no_edit | opened_and_saved_no_edits | C07 | Thermal load case exists (it is used in combinations) | 0 | 27 |
| S11_open_additional_inputs_no_edit | opened_and_saved_no_edits | C08 | End diaphragm members are designed | 0 empty pairs | 3 of 3 empty |
| S11_open_additional_inputs_no_edit | opened_and_saved_no_edits | C10 | Girder area in analysis/self-weight = area in design check | 0.03870 m2 | 0.03490 m2 |
| S11_open_additional_inputs_no_edit | - | A3 | Design unchanged after opening Additional Inputs and saving with no edits | cross_bracing_spacing_m=3.0, chi_LT=1.0, Mb_kNm=7986.443, max_dcr=1.577, overall | cross_bracing_spacing_m=15.0, chi_LT=0.3282, Mb_kNm=2621.07, max_dcr=1.5765, overall_status=FAIL |
| S11_open_additional_inputs_no_edit | - | A4 | Girder area unchanged after opening Additional Inputs (no edits) | 0.03492 | 0.0349 |

## Notes

- **U2_girder_count_history**: span 40 / cw 11, typed 11 directly (fresh): 5 girders @ 2.38 m, overhang 1.19 m
- **U2_girder_count_history**: span 40 / cw 11, typed 7.5, then corrected to 11: 4 girders @ 2.975 m, overhang 1.4875 m
- **U2_girder_count_history**: span 40 / cw 11, typed 5, then corrected to 11: 3 girders @ 3.9667 m, overhang 1.9833 m
- **U2_girder_count_history**: span 40 / cw 11, typed 20, then corrected to 11: 9 girders @ 1.3222 m, overhang 0.6611 m
- **U2_girder_count_history**: span 40 / cw 11, after a Design at TC00 (cw 7.5), changed to span 40/cw 11: 4 girders @ 2.975 m, overhang 1.4875 m
- **S10_deck_grade**: deck grade -> exposure / required cover / deck check: M40: Very Severe / 50 mm; M45: Extreme / 75 mm; M50: Extreme / 75 mm
