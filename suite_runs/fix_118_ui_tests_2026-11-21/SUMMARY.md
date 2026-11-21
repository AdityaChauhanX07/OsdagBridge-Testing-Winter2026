# OsdagBridge automated test suite - fix_118_ui_tests_2026-11-21 (UI tests with the #118 fix)

Design runs: 0 (ok 0, error 0); checks: 35 pass, 16 fail, 0 info

## Design runs

| case | step | status | s | girders in/checked | spacing in/used (m) | steel dens in/used | deck dens in/used | M_sw ratio | defl check/shown (mm) | status | max DCR |
|---|---|---|---|---|---|---|---|---|---|---|---|

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
| U8_backend_validation | span 100 m | U8 | Backend rejects span 100 m | ValueError | accepted (no range check) |
| U8_backend_validation | carriageway 40 m | U8 | Backend rejects carriageway 40 m | ValueError | accepted (no range check) |
| U8_backend_validation | skew 60 deg | U8 | Backend rejects skew 60 deg | ValueError | accepted (no range check) |
| U8_backend_validation | girder fy 5000 | U8 | Backend rejects girder fy 5000 | ValueError | accepted (no range check) |

## Notes

- **U2_girder_count_history**: span 40 / cw 11, typed 11 directly (fresh): 5 girders @ 2.38 m, overhang 1.19 m
- **U2_girder_count_history**: span 40 / cw 11, typed 7.5, then corrected to 11: 4 girders @ 2.975 m, overhang 1.4875 m
- **U2_girder_count_history**: span 40 / cw 11, typed 5, then corrected to 11: 3 girders @ 3.9667 m, overhang 1.9833 m
- **U2_girder_count_history**: span 40 / cw 11, typed 20, then corrected to 11: 9 girders @ 1.3222 m, overhang 0.6611 m
- **U2_girder_count_history**: span 40 / cw 11, after a Design at TC00 (cw 7.5), changed to span 40/cw 11: 4 girders @ 2.975 m, overhang 1.4875 m
