"""
run_test_suite.py - automated, headless test suite for OsdagBridge (Plate Girder Bridge).

What it does
------------
It drives the *real* OsdagBridge code, with no edits to the source:
  * the real homepage InputDock widget (fields, combos, hard validation, custom
    material flow, populate_from_dict used by Load Input),
  * the real Additional Inputs dialog (its compute functions and its Save logic),
  * solve_extend_basic_input_dict(), validate_osi_inputs(), the YAML .osi save/load,
  * one PlateGirderBridge backend per simulated GUI session, reused across runs
    with backend.reset() in between (exactly what "unlock" does in the GUI).
The Qt windows are created off-screen. Only TemplatePage itself (main window,
CAD/plots) is not built; its small glue methods (Design pre-steps, Save/Load
Input, update_cad_from_inputs) are mirrored line-for-line in class GuiSim and
the source line each one mirrors is noted next to it.

For every Design run it saves the input dict, the full output dict (gzipped),
the console log, and ~15 automatic consistency checks (girder count, girder
spacing, self-weight density, slab density, SW moment vs wL^2/8, deflection
consistency, thermal load case, end-diaphragm design, cross-bracing spacing,
section-area consistency, ...). Multi-run sequences are diffed run-to-run.
"UI logic" tests (U*) need no design run and finish in seconds.

Usage (Anaconda Prompt, osdagbridge-env active):
    cd C:\\Users\\Aditya\\Projects\\OsdagBridge\\src
    python C:\\Users\\Aditya\\Projects\\OsdagBridge-Testing\\scripts\\run_test_suite.py
Options:
    --list            list the test cases and exit
    --only U1,S03     run only these case ids (comma separated)
    --ui-only         run only the fast U* (no-design) tests
    --out DIR         output folder (default: OsdagBridge-Testing/suite_runs/<timestamp>)

Results: suite_runs/<timestamp>/SUMMARY.md, checks.csv, runs.csv, and one
folder per case with *_input.json, *_output.json.gz, *_log.txt, *_checks.json.
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import csv
import datetime as _dt
import gzip
import io
import json
import math
import os
import re
import sys
import threading
import time
import traceback
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TESTING_ROOT = SCRIPT_DIR.parent
FIXTURES_DIR = TESTING_ROOT / "fixtures"
FIXTURE_TC00 = FIXTURES_DIR / "TC00_baseline_ui_input.json"
FIXTURE_TC01 = FIXTURES_DIR / "TC01_custom_materials_ui_input.json"


# ============================================================================
# Output capture (the app prints a lot; keep the console readable)
# ============================================================================
class _LogStream:
    """File-like stream for sys.stdout/sys.stderr replacement.

    Writes go to a log file only. fileno() points at the real console so code
    that needs a real descriptor (faulthandler, multiprocessing) keeps working,
    and reconfigure() is a no-op (core/utils/connect.py calls it on import)."""

    def __init__(self, fh, lock):
        self._fh, self._lock = fh, lock

    def write(self, s):
        if not isinstance(s, str):
            s = str(s)
        with self._lock:
            try:
                self._fh.write(s)
            except Exception:
                pass
        return len(s)

    def writelines(self, lines):
        for line in lines:
            self.write(line)

    def flush(self):
        try:
            self._fh.flush()
        except Exception:
            pass

    def reconfigure(self, *a, **k):
        return None

    def fileno(self):
        return (sys.__stdout__ or sys.__stderr__).fileno()

    def isatty(self):
        return False

    def writable(self):
        return True

    @property
    def encoding(self):
        return "utf-8"


@contextlib.contextmanager
def capture(fh):
    lock = threading.Lock()
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = _LogStream(fh, lock)
    try:
        yield
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def say(msg=""):
    out = sys.__stdout__
    enc = getattr(out, "encoding", None) or "utf-8"
    text = str(msg).encode(enc, errors="replace").decode(enc, errors="replace")   # Windows console safe
    print(text, file=out, flush=True)


# ============================================================================
# Small helpers
# ============================================================================
def fnum(v, default=None):
    try:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return default
        return float(v)
    except Exception:
        return default


def close(a, b, rel=0.005, abs_tol=1e-9):
    if a is None or b is None:
        return False
    return math.isclose(float(a), float(b), rel_tol=rel, abs_tol=abs_tol)


VOLATILE_KEY_RE = re.compile(r"time|elapsed|duration|path|figure|image|timestamp|_dir\b|tmp", re.I)
STAMP_RE = re.compile(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}")   # "Generated: 2026-11-14 20:33:40"


# ============================================================================
# Simulated GUI session
# ============================================================================
class GuiSim:
    """One GUI session: real InputDock + real AdditionalInputs + one backend.

    Mirrors osdagbridge/desktop/ui/template_page.py (commit d74f56d):
      design_prep()          -> common_design_func() L627-660
      _update_cad()          -> update_cad_from_inputs() L886-900 (CAD drawing omitted)
      open_additional_inputs -> common_design_func('Additional Inputs') + _show_additional_inputs()
                                + AdditionalInputs Save (additional_inputs.py L519)
      save_osi()             -> saveOSI_inputs() L793-812
      load_osi()             -> loadOSI_inputs() L827-870
      unlock()               -> input_dock.toggle_lock() L842-875 (backend.reset())
    """

    popups: list = []      # every CustomMessageBox the app tried to show
    _dialog_answer = None  # values the "user" types into the next custom-material dialog

    def __init__(self, ctx, name):
        self.ctx, self.name = ctx, name
        self.parent = ctx.Parent()
        self.backend = ctx.PlateGirderBridge()
        with capture(io.StringIO()):
            self.dock = ctx.InputDock(self.backend, self.parent)
            self.dlg = ctx.AdditionalInputs()
        self.parent.input_dock = self.dock
        self.dock.input_value_changed.connect(self._update_cad)
        self.pump()

    # -- plumbing ------------------------------------------------------------
    @property
    def d(self) -> dict:
        return self.parent.input_dict

    def pump(self):
        for _ in range(3):
            self.ctx.app.processEvents()

    def _update_cad(self):  # template_page.update_cad_from_inputs (minus the drawing)
        if self.dock.is_require_field_changed:
            try:
                with capture(io.StringIO()):
                    self.ctx.solve_extend(self.d)
                self.dock.is_require_field_changed = False
            except Exception:
                pass

    # -- user actions on the homepage -----------------------------------------
    def set_field(self, key, value):
        """Type into a homepage text box (then leave it) or pick a combo item."""
        QLineEdit, QComboBox, QWidget = self.ctx.QLineEdit, self.ctx.QComboBox, self.ctx.QWidget
        w = self.dock.input_widget.findChild(QWidget, key)
        n_pop = len(GuiSim.popups)
        with capture(io.StringIO()):
            if isinstance(w, QLineEdit):
                w.setText(str(value))
                self.dock._on_field_edited(key, w)          # what editingFinished does
            elif isinstance(w, QComboBox):
                if w.findText(str(value)) < 0:
                    raise ValueError(f"{key}: '{value}' is not an option")
                w.setCurrentText(str(value))
            else:                                            # e.g. project.location (dialog)
                if self.dock._is_require_field(key):
                    self.dock.is_require_field_changed = True
                self.dock._update_input_dict(key, value)
                self.dock.input_value_changed.emit()
            self.pump()
        return GuiSim.popups[n_pop:]

    def create_custom_material(self, member_key, values: dict):
        """Pick 'Custom' in a material combo, type `values` into the dialog, press Save."""
        GuiSim._dialog_answer = {k: str(v) for k, v in values.items()}
        try:
            n_pop = len(GuiSim.popups)
            with capture(io.StringIO()):
                self.dock._material_combo_map[member_key].setCurrentText(self.ctx.MATERIAL_CUSTOM_OPTION)
                self.pump()
            return GuiSim.popups[n_pop:]
        finally:
            GuiSim._dialog_answer = None

    def material_info_button(self, member_key):
        """The (i) button next to a material combo (input_dock._show_material_info)."""
        try:
            with capture(io.StringIO()):
                self.dock._show_material_info(member_key)
            return None
        except Exception as exc:
            return f"{type(exc).__name__}: {exc}"

    # -- template_page glue ---------------------------------------------------
    def design_prep(self):
        """common_design_func(): prime materials, check required, re-solve, compute values."""
        with capture(io.StringIO()):
            self.dock._prime_material_inputs()
            missing = []
            for key, label, *_rest, meta in self.backend.input_values():
                if meta.get("required", False):
                    w = self.dock.input_widget.findChild(self.ctx.QWidget, key)
                    if isinstance(w, self.ctx.QLineEdit):
                        if w.text().strip() == "":
                            missing.append(key)
                    elif not isinstance(w, self.ctx.QComboBox):
                        if self.d.get(key) in (None, "", [], {}):
                            missing.append(key)
            if missing:
                return missing
            if self.dock.is_require_field_changed:
                self.ctx.solve_extend(self.d)
                self.dock.is_require_field_changed = False
            for fn in self.dlg._compute_functions:
                f = getattr(self.dlg, fn, None)
                if f is None:
                    continue
                r = f(self.d)
                if isinstance(r, dict):
                    self.d.update(r)
        return []

    def open_additional_inputs(self, edits: dict):
        """Open Additional Inputs, change `edits`, press Save."""
        missing = self.design_prep()
        if missing:
            raise RuntimeError(f"required fields empty: {missing}")
        self.dlg.set_input_dictionary(self.d)
        self.dlg.working_input_dict.update(copy.deepcopy(edits))
        self.dlg.default_input_dict.update(self.dlg.working_input_dict)   # dialog Save

    def save_osi(self, path):
        with capture(io.StringIO()):
            try:
                self.ctx.solve_extend(self.d)
            except Exception:
                pass
        with open(path, "w") as fh:
            self.ctx.yaml.dump(self.d, fh)

    def load_osi(self, path):
        with open(path, "r") as fh:
            data = self.ctx.yaml.safe_load(fh)
        if not isinstance(data, dict):
            return False, ["File does not contain a valid input dictionary."]
        validation = self.ctx.validate_osi_inputs(data)
        if not validation.is_valid:
            return False, list(validation.errors)
        with capture(io.StringIO()):
            self.dock.populate_from_dict(data)
            self.pump()
            self.dlg.set_input_dictionary(self.d)
            try:
                self.ctx.solve_extend(self.d)
            except Exception:
                pass
        return True, []

    def unlock(self):
        with capture(io.StringIO()):
            self.backend.reset()


# ============================================================================
# Context: lazy imports (after the main guard; needed for spawn on Windows)
# ============================================================================
class Ctx:
    def __init__(self):
        if sys.platform != "win32":          # Windows: native platform plugin, windows are never shown
            os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        sink = io.StringIO()
        with capture(sink):
            from PySide6.QtWidgets import QApplication, QWidget, QLineEdit, QComboBox, QDialog
            self.app = QApplication.instance() or QApplication([])
            import yaml
            from osdagbridge.core.utils import common as C
            from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge
            from osdagbridge.core.bridge_types.plate_girder.defaults import (
                solve_extend_basic_input_dict, BASIC_INPUT_DICT)
            from osdagbridge.core.bridge_types.plate_girder.validator import BridgeInputValidator
            from osdagbridge.core.utils.osi_validator import validate_osi_inputs
            import osdagbridge.desktop.ui.docks.input_dock as input_dock_mod
            import osdagbridge.desktop.ui.dialogs.material_properties as matprop_mod
            from osdagbridge.desktop.ui.dialogs.additional_input.additional_inputs import AdditionalInputs
        self.QWidget, self.QLineEdit, self.QComboBox, self.QDialog = QWidget, QLineEdit, QComboBox, QDialog
        self.yaml, self.C = yaml, C
        self.PlateGirderBridge = PlateGirderBridge
        self.solve_extend = solve_extend_basic_input_dict
        self.BASIC_INPUT_DICT = BASIC_INPUT_DICT
        self.BridgeInputValidator = BridgeInputValidator
        self.validate_osi_inputs = validate_osi_inputs
        self.InputDock = input_dock_mod.InputDock
        self.MATERIAL_CUSTOM_OPTION = input_dock_mod.MATERIAL_CUSTOM_OPTION
        self.MaterialPropertiesDialog = matprop_mod.MaterialPropertiesDialog
        self.AdditionalInputs = AdditionalInputs
        self._patch_modals(input_dock_mod, matprop_mod)

        basic = BASIC_INPUT_DICT

        class Parent(QWidget):                 # stands in for TemplatePage
            def __init__(self):
                super().__init__()
                self.input_dict = dict(basic)  # template_page.py L121
        self.Parent = Parent

    def _patch_modals(self, input_dock_mod, matprop_mod):
        """Modal pop-ups would block a headless run: record them instead."""

        class RecordedMessageBox:
            def __init__(self, title="", text="", informativeText="", buttons=None, dialogType=None, **kw):
                self.rec = {"title": str(title), "text": str(text)}

            def exec(self):
                GuiSim.popups.append(self.rec)
                return "Continue"

        input_dock_mod.CustomMessageBox = RecordedMessageBox
        matprop_mod.CustomMessageBox = RecordedMessageBox
        Dlg = matprop_mod.MaterialPropertiesDialog
        QDialog = self.QDialog

        def fake_exec(dlg_self):
            answer = GuiSim._dialog_answer
            if dlg_self.read_only or answer is None:   # read-only info dialog: just "close" it
                return QDialog.Rejected
            for key, text in answer.items():
                w = dlg_self.field_inputs.get(key)
                if w is None:
                    raise KeyError(f"material dialog has no field {key}")
                w.setText(text)
            dlg_self._update_custom_material_name()
            dlg_self._validate_and_save()                  # real validation + save
            return dlg_self.result()

        Dlg.exec = fake_exec


# ============================================================================
# Evidence extraction + automatic checks for one design run
# ============================================================================
SW_RE = re.compile(r"Self weight line load @ z=([-\d.]+) m: ([-\d.]+) N/m \(A=([-\d.eE]+) m")
SLAB_RE = re.compile(r"Deck slab load magnitude: ([-\d.]+) N/m")
THERMAL_RE = re.compile(r"'thermal_load' load case not available")
DECK_MSLS_RE = re.compile(r"M<sub>SLS</sub>,char \(sagging\)\s*:\s*([-\d.]+)")


def extract(inp: dict, out: dict, log: str) -> dict:
    """Pull the numbers the checks need out of input dict, output dict and log."""
    C = None
    ev = {}
    g = lambda k: inp.get(k)
    ev["span_m"] = fnum(g("geometry.span"))
    ev["carriageway_m"] = fnum(g("geometry.carriageway_width"))
    ev["design_mode"] = g("geometry.design_mode")
    ev["n_girders_input"] = int(fnum(g("typical_section.no_of_girders"), 0) or 0)
    ev["girder_spacing_input_m"] = fnum(g("typical_section.girder_spacing"))
    ev["overall_width_input_m"] = fnum(g("typical_section.overall_bridge_width"))
    ev["deck_thickness_input_mm"] = fnum(g("typical_section.deck_thickness"))
    ev["girder_material"] = g("material.girder")
    ev["girder_density_input"] = fnum(g("material.girder.density"))
    ev["girder_fy_input"] = fnum(g("material.girder.fy"))
    ev["girder_E_input"] = fnum(g("material.girder.e"))
    ev["deck_material"] = g("material.deck")
    ev["deck_density_input"] = fnum(g("material.deck.density"))
    ev["deck_fck_input"] = fnum(g("material.deck.fck"))
    ev["cross_bracing_material"] = g("material.cross_bracing")
    cb_keys = sorted(k for k in inp if k.startswith("member_properties.cross_bracing_details.spacing."))
    ev["cb_spacing_input_m"] = fnum(inp[cb_keys[0]]) if cb_keys else None

    sw = SW_RE.findall(log)
    ev["sw_lines"] = len(sw)
    if sw:
        zs = sorted(float(z) for z, _, _ in sw)
        ev["sw_z_m"] = zs
        ev["girder_spacing_analysis_m"] = round(zs[1] - zs[0], 4) if len(zs) > 1 else None
        ev["sw_line_load_N_m"] = float(sw[0][1])
        ev["sw_area_m2"] = float(sw[0][2])
        ev["girder_density_used"] = round(float(sw[0][1]) / float(sw[0][2]) / 1000.0, 2)
    m = SLAB_RE.search(log)
    if m:
        ev["slab_load_N_m2"] = float(m.group(1))
        if ev["deck_thickness_input_mm"]:
            ev["deck_density_used"] = round(float(m.group(1)) / (ev["deck_thickness_input_mm"] / 1000.0) / 1000.0, 3)
    ev["thermal_missing_warnings"] = len(THERMAL_RE.findall(log))

    dr = out.get("design_results") or {}
    pg = dr.get("per_girder") or {}
    ev["n_girders_checked"] = dr.get("n_girders")
    ev["per_girder_ids"] = ",".join(pg.keys()) if isinstance(pg, dict) else ""
    msw = [fnum((v.get("demand") or {}).get("M_girder_sw_kNm")) for v in pg.values()] if isinstance(pg, dict) else []
    msw = [x for x in msw if x is not None]
    ev["M_sw_max_kNm"] = max(msw) if msw else None
    if ev.get("sw_line_load_N_m") and ev["span_m"]:
        ev["M_sw_expected_kNm"] = round(ev["sw_line_load_N_m"] / 1000.0 * ev["span_m"] ** 2 / 8.0, 2)
        if ev["M_sw_max_kNm"]:
            ev["M_sw_ratio"] = round(ev["M_sw_max_kNm"] / ev["M_sw_expected_kNm"], 3)
    ev["A_steel_check_m2"] = (fnum(dr.get("A_steel_mm2")) or 0) / 1e6 or None
    ev["delta_total_check_mm"] = fnum(dr.get("delta_total_mm"))
    per_def = [fnum(v) for k, v in out.items() if k.startswith("steeldesign.deflection.total_mm.G")]
    per_def = [x for x in per_def if x is not None]
    ev["delta_total_output_max_mm"] = max(per_def) if per_def else None
    ev["fy_used_MPa"] = fnum(dr.get("fy_MPa"))
    ev["tf_mm"] = fnum(dr.get("tf_top_mm"))
    ev["tw_mm"] = fnum(dr.get("tw_mm"))
    ev["D_mm"] = fnum(dr.get("D_mm"))
    ev["overall_status"] = dr.get("overall_status")
    ev["max_dcr"] = fnum(dr.get("max_dcr"))
    ev["controlling_girder"] = dr.get("controlling_girder")
    ev["Md_kNm"] = fnum(dr.get("Md_kNm"))
    ev["cb_spacing_check_m"] = fnum(dr.get("cross_bracing_spacing_m"))
    geom = (out.get("crossbracing_forces_dict") or {}).get("geometry") or {}
    ev["cb_spacing_analysis_m"] = fnum(geom.get("cb_spacing_m"))
    ed = out.get("end_diaphragm_design_results")
    if isinstance(ed, dict):
        ev["end_diaphragm_pairs"] = len(ed)
        ev["end_diaphragm_empty_pairs"] = sum(1 for v in ed.values() if not v)
    cbr = out.get("crossbracing_design_results") or {}
    sig = []
    for pair in sorted(cbr):
        for mem in sorted(cbr[pair] or {}):
            for ft in sorted(cbr[pair][mem] or {}):
                r = cbr[pair][mem][ft] or {}
                sig.append(f"{pair}/{mem}/{ft}:{r.get('section_size.designation')}:"
                           f"{r.get('Member.tension_capacity') or r.get('KEY_FCD')}")
    ev["bracing_signature"] = "|".join(sig)
    deck = out.get("deck_design_results") or {}
    m = DECK_MSLS_RE.search(str(deck.get("deck_design_check", "")))
    ev["deck_Msls_sag_kNm_m"] = float(m.group(1)) if m else None
    ev["deck_exposure"] = deck.get("deck_exposure")
    ev["deck_cover_required_mm"] = deck.get("min_cover_recommended")
    ev["output_keys"] = len(out)
    return ev


def run_checks(ev: dict) -> list:
    """Each check: (id, title, PASS/FAIL/INFO, expected, actual)."""
    res = []

    def add(cid, title, ok, expected, actual, info=False):
        res.append({"check": cid, "title": title,
                    "result": "INFO" if info else ("PASS" if ok else "FAIL"),
                    "expected": expected, "actual": actual})

    add("C01", "Design check uses the real number of girders",
        ev.get("n_girders_checked") == ev.get("n_girders_input"),
        ev.get("n_girders_input"), f"{ev.get('n_girders_checked')} ({ev.get('per_girder_ids')})")
    if ev.get("girder_spacing_analysis_m") is not None:
        add("C02", "Grillage girder spacing = input girder spacing",
            close(ev["girder_spacing_analysis_m"], ev["girder_spacing_input_m"], rel=0, abs_tol=0.0011),
            ev.get("girder_spacing_input_m"), ev["girder_spacing_analysis_m"])
    if ev.get("girder_density_used") is not None:
        add("C03", "Steel self-weight uses the girder material density",
            close(ev["girder_density_used"], ev["girder_density_input"]),
            ev.get("girder_density_input"), ev["girder_density_used"])
    if ev.get("deck_density_used") is not None:
        add("C04", "Deck slab load uses the deck material density",
            close(ev["deck_density_used"], ev["deck_density_input"]),
            ev.get("deck_density_input"), ev["deck_density_used"])
    if ev.get("M_sw_ratio") is not None:
        add("C05", "Girder self-weight moment ~ w*L^2/8 (simply supported)",
            0.95 <= ev["M_sw_ratio"] <= 1.05, ev.get("M_sw_expected_kNm"),
            f"{ev.get('M_sw_max_kNm')} (ratio {ev['M_sw_ratio']})")
    if ev.get("delta_total_check_mm") is not None and ev.get("delta_total_output_max_mm") is not None:
        add("C06", "Deflection in design check = deflection shown per girder",
            close(ev["delta_total_check_mm"], ev["delta_total_output_max_mm"], rel=0.05),
            ev["delta_total_check_mm"], ev["delta_total_output_max_mm"])
    add("C07", "Thermal load case exists (it is used in combinations)",
        ev.get("thermal_missing_warnings", 0) == 0, 0, ev.get("thermal_missing_warnings"))
    if ev.get("end_diaphragm_pairs"):
        add("C08", "End diaphragm members are designed",
            ev.get("end_diaphragm_empty_pairs") == 0, "0 empty pairs",
            f"{ev.get('end_diaphragm_empty_pairs')} of {ev.get('end_diaphragm_pairs')} empty")
    if ev.get("cb_spacing_input_m") is not None:
        used = ev.get("cb_spacing_analysis_m") or ev.get("cb_spacing_check_m")
        add("C09", "Cross-bracing spacing used = Additional Input spacing",
            close(used, ev["cb_spacing_input_m"], rel=0, abs_tol=0.01), ev["cb_spacing_input_m"], used)
    if ev.get("sw_area_m2") and ev.get("A_steel_check_m2"):
        add("C10", "Girder area in analysis/self-weight = area in design check",
            close(ev["sw_area_m2"], ev["A_steel_check_m2"], rel=0.005),
            f"{ev['A_steel_check_m2']:.5f} m2", f"{ev['sw_area_m2']:.5f} m2")
    if ev.get("fy_used_MPa") is not None:
        add("C11", "Design fy = girder material fy", close(ev["fy_used_MPa"], ev["girder_fy_input"]),
            ev.get("girder_fy_input"), f"{ev['fy_used_MPa']} (tf={ev.get('tf_mm')} mm)", info=True)
    add("C12", "Number of girder self-weight lines = number of girders",
        ev.get("sw_lines") == ev.get("n_girders_input"), ev.get("n_girders_input"), ev.get("sw_lines"))
    return res


def compare_runs(a: dict, b: dict) -> list:
    """Flattened diff between two output dicts, ignoring volatile keys."""
    fa, fb = FLATTEN(TO_JSONABLE(a)), FLATTEN(TO_JSONABLE(b))
    diffs = []
    for k in sorted(set(fa) | set(fb)):
        if VOLATILE_KEY_RE.search(k):
            continue
        va, vb = fa.get(k, "<missing>"), fb.get(k, "<missing>")
        if isinstance(va, str) and isinstance(vb, str):
            va, vb = STAMP_RE.sub("<time>", va), STAMP_RE.sub("<time>", vb)
        if va != vb:
            if isinstance(va, float) and isinstance(vb, float) and math.isclose(va, vb, rel_tol=1e-9, abs_tol=1e-12):
                continue
            diffs.append((k, va, vb))
    return diffs


# ============================================================================
# Suite runner
# ============================================================================
class Suite:
    def __init__(self, ctx, out_dir: Path):
        self.ctx, self.out = ctx, out_dir
        self.fx = json.load(open(FIXTURE_TC00, encoding="utf-8"))
        self.fx01 = json.load(open(FIXTURE_TC01, encoding="utf-8"))
        self.run_rows, self.check_rows = [], []
        self.case_notes = {}
        self.cur_case = None

    # -- bookkeeping ------------------------------------------------------------
    def case_dir(self):
        p = self.out / self.cur_case
        p.mkdir(parents=True, exist_ok=True)
        return p

    def check(self, cid, title, ok, expected, actual, info=False, step="-"):
        row = {"case": self.cur_case, "step": step, "check": cid, "title": title,
               "result": "INFO" if info else ("PASS" if ok else "FAIL"),
               "expected": expected, "actual": actual}
        self.check_rows.append(row)
        mark = {"PASS": "  ok ", "FAIL": "  FAIL", "INFO": "  info"}[row["result"]]
        say(f"   {mark} {cid} {title}: expected {expected!s:.60}  got {actual!s:.80}")
        return row

    def note(self, text):
        self.case_notes.setdefault(self.cur_case, []).append(text)
        say(f"   - {text}")

    # -- sessions -----------------------------------------------------------------
    def new_session(self, name="session") -> GuiSim:
        return GuiSim(self.ctx, name)

    def baseline_session(self) -> GuiSim:
        """Fresh GUI session with the TC00 homepage inputs typed in."""
        s = self.new_session()
        C = self.ctx.C
        s.set_field(C.KEY_PROJECT_LOCATION, copy.deepcopy(self.fx[C.KEY_PROJECT_LOCATION]))
        for key in (C.KEY_SPAN, C.KEY_CARRIAGEWAY_WIDTH, C.KEY_SKEW_ANGLE):
            s.set_field(key, self.fx[key])
        for key in (C.KEY_DESIGN_MODE, C.KEY_INCLUDE_MEDIAN, C.KEY_FOOTPATH,
                    C.KEY_GIRDER, C.KEY_CROSS_BRACING, C.KEY_END_DIAPHRAGM, C.KEY_DECK_CONCRETE_GRADE_BASIC):
            w = s.dock.input_widget.findChild(self.ctx.QWidget, key)
            if w is not None and w.currentText() != str(self.fx[key]):
                s.set_field(key, self.fx[key])
        return s

    def custom_materials_tc01(self, s: GuiSim):
        C = self.ctx.C
        s.create_custom_material(C.KEY_GIRDER, {
            C.KEY_MATERIAL_GIRDER_DENSITY: "80", C.KEY_MATERIAL_GIRDER_FY: "410", C.KEY_MATERIAL_GIRDER_FU: "540",
            C.KEY_MATERIAL_GIRDER_E: "210", C.KEY_MATERIAL_GIRDER_G: "80.8", C.KEY_MATERIAL_GIRDER_POISSON: "0.3",
            C.KEY_MATERIAL_GIRDER_THERMAL: "12"})
        s.create_custom_material(C.KEY_DECK_CONCRETE_GRADE_BASIC, {
            C.KEY_MATERIAL_DECK_DENSITY: "26", C.KEY_MATERIAL_DECK_FCK: "45", C.KEY_MATERIAL_DECK_FCTM: "3.8",
            C.KEY_MATERIAL_DECK_ECM: "34", C.KEY_MATERIAL_DECK_THERMAL: "10"})

    # -- one Design click -----------------------------------------------------------
    def design(self, s: GuiSim, step: str, prep=True):
        """Click Design in session `s`. Returns a record with evidence + checks."""
        d = self.case_dir()
        t0 = time.time()
        rec = {"case": self.cur_case, "step": step, "status": "?", "seconds": 0.0, "error": ""}
        if prep:
            missing = s.design_prep()
            if missing:
                rec.update(status="blocked", error=f"required fields empty: {missing}")
                self.run_rows.append(rec)
                return rec
        inp = copy.deepcopy(s.d)
        WRITE_JSON(d / f"{step}_input.json", inp)
        log_path = d / f"{step}_log.txt"
        say(f"   > Design [{self.cur_case} {step}] ...")
        tb = ""
        with open(log_path, "w", encoding="utf-8", errors="replace") as fh, capture(fh):
            try:
                s.backend.set_input(s.d)
                s.backend.design()
                rec["status"] = "ok"
            except Exception as exc:
                tb = traceback.format_exc()
                rec["status"], rec["error"] = "error", f"{type(exc).__name__}: {exc}"
                print(tb)
        rec["seconds"] = round(time.time() - t0, 1)
        out = dict(s.backend.output_dict or {})
        with gzip.open(d / f"{step}_output.json.gz", "wt", encoding="utf-8") as gz:
            json.dump(TO_JSONABLE(out), gz, indent=1, sort_keys=True, ensure_ascii=False)
        log = log_path.read_text(encoding="utf-8", errors="replace")
        ev = extract(inp, out, log) if rec["status"] == "ok" else {"output_keys": len(out)}
        checks = run_checks(ev) if rec["status"] == "ok" else []
        WRITE_JSON(d / f"{step}_checks.json", {"record": rec, "evidence": ev, "checks": checks, "traceback": tb})
        rec.update({k: v for k, v in ev.items() if not isinstance(v, list)})
        rec["_out"] = out
        self.run_rows.append(rec)
        fails = [c["check"] for c in checks if c["result"] == "FAIL"]
        say(f"     {rec['status']} in {rec['seconds']} s; girders in check={ev.get('n_girders_checked')}"
            f" status={ev.get('overall_status')} maxDCR={ev.get('max_dcr')}"
            f" failed checks={','.join(fails) or 'none'} {rec['error']}")
        for c in checks:
            row = dict(c, case=self.cur_case, step=step)
            self.check_rows.append(row)
        return rec

    # ======================================================================
    # UI-logic tests (no design run)
    # ======================================================================
    def U1_builder_matches_gui(self):
        """The simulated GUI produces exactly the dict the real GUI sent in TC00/TC01."""
        s = self.baseline_session()
        s.design_prep()
        diff = [k for k in sorted(set(s.d) | set(self.fx))
                if json.dumps(TO_JSONABLE(s.d.get(k)), sort_keys=True) != json.dumps(self.fx.get(k), sort_keys=True)]
        WRITE_JSON(self.case_dir() / "TC00_sim_vs_gui_diff.json", {k: [TO_JSONABLE(s.d.get(k)), self.fx.get(k)] for k in diff})
        self.check("U1a", "Simulated Design dict == real GUI TC00 dict (576 keys)", not diff, "0 differences",
                   f"{len(diff)} differences {diff[:5]}")
        s2 = self.baseline_session()
        self.custom_materials_tc01(s2)
        s2.design_prep()
        diff2 = [k for k in sorted(set(s2.d) | set(self.fx01))
                 if json.dumps(TO_JSONABLE(s2.d.get(k)), sort_keys=True) != json.dumps(self.fx01.get(k), sort_keys=True)]
        WRITE_JSON(self.case_dir() / "TC01_sim_vs_gui_diff.json", {k: [TO_JSONABLE(s2.d.get(k)), self.fx01.get(k)] for k in diff2})
        self.check("U1b", "Simulated custom-material dict == real GUI TC01 dict", not diff2, "0 differences",
                   f"{len(diff2)} differences {diff2[:5]}")

    def U2_girder_count_history(self):
        """Same homepage inputs, different girder count depending on what was typed before."""
        C = self.ctx.C
        k_n, k_s = C.KEY_TS_NO_OF_GIRDERS, C.KEY_TS_GIRDER_SPACING
        loc = copy.deepcopy(self.fx[C.KEY_PROJECT_LOCATION])

        def session(cw_sequence):
            s = self.new_session()
            s.set_field(C.KEY_PROJECT_LOCATION, copy.deepcopy(loc))
            s.set_field(C.KEY_SPAN, "40")
            for cw in cw_sequence:
                s.set_field(C.KEY_CARRIAGEWAY_WIDTH, cw)
            s.design_prep()
            return s

        fresh = session(["11"])
        variants = {"typed 11 directly (fresh)": fresh,
                    "typed 7.5, then corrected to 11": session(["7.5", "11"]),
                    "typed 5, then corrected to 11": session(["5", "11"]),
                    "typed 20, then corrected to 11": session(["20", "11"])}
        b = self.baseline_session(); b.design_prep()
        b.set_field(C.KEY_SPAN, "40"); b.set_field(C.KEY_CARRIAGEWAY_WIDTH, "11"); b.design_prep()
        variants["after a Design at TC00 (cw 7.5), changed to span 40/cw 11"] = b
        rows = []
        for label, s in variants.items():
            rows.append({"how": label, "girders": s.d[k_n], "spacing_m": s.d[k_s],
                         "overhang_m": s.d.get(C.KEY_TS_DECK_OVERHANG), "width_m": s.d.get(C.KEY_TS_OVERALL_WIDTH)})
            self.note(f"span 40 / cw 11, {label}: {s.d[k_n]} girders @ {s.d[k_s]} m, overhang {s.d.get(C.KEY_TS_DECK_OVERHANG)} m")
        WRITE_JSON(self.case_dir() / "U2_girder_count_table.json", rows)
        counts = {r["girders"] for r in rows}
        self.check("U2", "Girder layout depends only on current inputs (not on typing history)",
                   len(counts) == 1, f"{fresh.d[k_n]} girders @ {fresh.d[k_s]} m every time",
                   "; ".join(f"{r['girders']}@{r['spacing_m']}" for r in rows))
        self.shared["U2"] = variants

    ADDITIONAL_EDITS = {
        "typical_section.deck_thickness": 300.0,
        "typical_section.wearing_course.thickness": 80.0,
        "design_options_cont.partial_factor.yielding_and_buckling.gamma_m0": "1.15",
        "loading.wind_load.avg_exposed_height": "15",
        "support_conditions.left_support": "Fixed",
        "design_options.shear_studs.diameter": "22",
    }

    def _kept(self, s: GuiSim, edits):
        return {k: (v, s.d.get(k)) for k, v in edits.items()}

    def _report_kept(self, cid, title, s, edits):
        kept = self._kept(s, edits)
        lost = {k: f"{a}->{b}" for k, (a, b) in kept.items() if str(a) != str(b)}
        self.check(cid, title, not lost, "all edits kept", f"{len(lost)} reset: {lost}" if lost else "all kept")
        return lost

    def U3_additional_inputs_reset(self):
        """Additional Inputs edits vs (a) basic-field change, (b) Save Input, (c) Load Input."""
        C = self.ctx.C
        e = self.ADDITIONAL_EDITS
        # (a) change a homepage field after editing Additional Inputs
        s = self.baseline_session()
        s.open_additional_inputs(e)
        self._report_kept("U3a0", "Edits present right after Additional Inputs > Save", s, e)
        s.set_field(C.KEY_SPAN, "32")
        s.design_prep()
        self._report_kept("U3a", "Additional Inputs kept after changing span 30->32", s, e)
        # (b) Save Input in the same session, then Design without changing anything
        s = self.baseline_session()
        s.open_additional_inputs(e)
        osi = self.case_dir() / "U3_saved.osi"
        s.save_osi(osi)
        saved = self.ctx.yaml.safe_load(open(osi))
        lost_file = {k: f"{v}->{saved.get(k)}" for k, v in e.items() if str(saved.get(k)) != str(v)}
        self.check("U3b1", "Save Input writes the edited Additional Inputs to the .osi", not lost_file,
                   "all edits in file", f"{len(lost_file)} reset in file: {lost_file}" if lost_file else "all kept")
        s.design_prep()
        self._report_kept("U3b2", "Session still has the edits after clicking Save Input", s, e)
        # (c) Load that .osi in a new session (use a file that DOES contain the edits)
        good = self.case_dir() / "U3_with_edits.osi"
        d_edit = copy.deepcopy(self.fx); d_edit.update(e)
        with open(good, "w") as fh:
            self.ctx.yaml.dump(d_edit, fh)
        s2 = self.new_session()
        ok, errs = s2.load_osi(good)
        self.check("U3c0", "Hand-checked .osi with edits loads", ok, "loaded", errs or "loaded")
        s2.design_prep()
        self._report_kept("U3c", "Additional Inputs kept after Load Input (file contains them)", s2, e)

    def U4_custom_material_reload(self):
        """Custom materials after Save/Load: values, re-selection, (i) info button."""
        C = self.ctx.C
        s = self.baseline_session()
        self.custom_materials_tc01(s)
        osi = self.case_dir() / "U4_custom.osi"
        s.save_osi(osi)
        s2 = self.new_session()
        ok, errs = s2.load_osi(osi)
        self.check("U4a", "Custom-material .osi loads", ok, "loaded", errs or "loaded")
        keys = [C.KEY_MATERIAL_GIRDER_FY, C.KEY_MATERIAL_GIRDER_E, C.KEY_MATERIAL_GIRDER_DENSITY,
                C.KEY_MATERIAL_DECK_FCK, C.KEY_MATERIAL_DECK_FCTM, C.KEY_MATERIAL_DECK_ECM, C.KEY_MATERIAL_DECK_DENSITY]
        before = {k: s.d.get(k) for k in keys}
        s2.design_prep()
        after = {k: s2.d.get(k) for k in keys}
        lost = {k: f"{before[k]}->{after[k]}" for k in keys if str(before[k]) != str(after[k])}
        self.check("U4b", "Custom material values survive Save > Load > Design", not lost,
                   json.dumps(before), f"changed: {lost}" if lost else "all kept")
        self.shared["U4_session"] = s2
        err = s2.material_info_button(C.KEY_GIRDER)
        self.check("U4c", "(i) info button works for a loaded custom steel", err is None, "dialog opens",
                   err or "dialog opens")
        combo = s2.dock._material_combo_map[C.KEY_GIRDER]
        name = combo.currentText()
        s2.set_field(C.KEY_GIRDER, "E 250A")
        s2.set_field(C.KEY_GIRDER, name)
        s2.design_prep()
        self.check("U4d", "Re-selecting the custom steel restores its fy/E",
                   str(s2.d.get(C.KEY_MATERIAL_GIRDER_FY)) in ("410", "410.0"),
                   f"{name}: fy 410, E 210",
                   f"combo={combo.currentText()} fy={s2.d.get(C.KEY_MATERIAL_GIRDER_FY)} E={s2.d.get(C.KEY_MATERIAL_GIRDER_E)}")
        self.shared["U4d_session"] = s2

    def U5_homepage_validation(self):
        """Hard validation of homepage fields (what the user sees when leaving a field)."""
        C = self.ctx.C
        cases = [
            (C.KEY_SPAN, "19.9", True), (C.KEY_SPAN, "45.1", True), (C.KEY_SPAN, "0", True),
            (C.KEY_SPAN, "-5", True), (C.KEY_SPAN, "abc", True), (C.KEY_SPAN, "20", False),
            (C.KEY_SPAN, "45", False),
            (C.KEY_CARRIAGEWAY_WIDTH, "4.2", True), (C.KEY_CARRIAGEWAY_WIDTH, "23.7", True),
            (C.KEY_CARRIAGEWAY_WIDTH, "4.25", False), (C.KEY_CARRIAGEWAY_WIDTH, "23.6", False),
            (C.KEY_SKEW_ANGLE, "16", True), (C.KEY_SKEW_ANGLE, "-16", True), (C.KEY_SKEW_ANGLE, "15", False),
            (C.KEY_SKEW_ANGLE, "-15", False),
        ]
        rows = []
        for key, val, should_reject in cases:
            s = self.baseline_session()
            pops = s.set_field(key, val)
            w = s.dock.input_widget.findChild(self.ctx.QWidget, key)
            shown = w.text() if isinstance(w, self.ctx.QLineEdit) else None
            rejected = bool(pops) or str(s.d.get(key)) != val
            rows.append({"field": key, "typed": val, "popup": pops[0]["text"] if pops else "",
                         "field_now": shown, "dict_now": s.d.get(key)})
            self.check("U5", f"{key} = {val!r} {'rejected' if should_reject else 'accepted'}",
                       rejected == should_reject, "reject" if should_reject else "accept",
                       (f"rejected -> {shown} ({pops[0]['text'][:50] if pops else 'no popup'})" if rejected else "accepted"),
                       step=f"{key.split('.')[-1]}={val}")
        WRITE_JSON(self.case_dir() / "U5_validation_table.json", rows)

    def U6_osi_validation(self):
        """Load Input validation for hand-edited .osi files."""
        C = self.ctx.C
        custom_bad = {C.KEY_GIRDER: "custom_steel_5000_6000", C.KEY_MATERIAL_GIRDER_FY: "5000",
                      C.KEY_MATERIAL_GIRDER_FU: "6000"}
        cases = [
            ("span abc", {C.KEY_SPAN: "abc"}, True),
            ("span 19.9", {C.KEY_SPAN: 19.9}, True),
            ("span 100", {C.KEY_SPAN: 100}, True),
            ("carriageway 30", {C.KEY_CARRIAGEWAY_WIDTH: 30}, True),
            ("skew 30", {C.KEY_SKEW_ANGLE: 30}, True),
            ("no_of_girders 1", {C.KEY_TS_NO_OF_GIRDERS: 1}, True),
            ("girder_spacing 0", {C.KEY_TS_GIRDER_SPACING: 0}, True),
            ("deck_thickness 20 mm", {C.KEY_TS_DECK_THICKNESS: 20}, True),
            ("design_mode Foo", {C.KEY_DESIGN_MODE: "Foo"}, True),
            ("custom steel fy 5000 MPa", custom_bad, True),
            ("girder density 999 (custom)", {C.KEY_GIRDER: "custom_steel_410_540", C.KEY_MATERIAL_GIRDER_FY: "410",
                                             C.KEY_MATERIAL_GIRDER_FU: "540", C.KEY_MATERIAL_GIRDER_DENSITY: "999"}, True),
            ("deck fck 500 (custom)", {C.KEY_DECK_CONCRETE_GRADE_BASIC: "custom_concrete_500_3.8",
                                       C.KEY_MATERIAL_DECK_FCK: "500"}, True),
            ("girder grade 'E 999X'", {C.KEY_GIRDER: "E 999X"}, True),
            ("valid file (TC00)", {}, False),
        ]
        rows = []
        for label, mods, should_reject in cases:
            data = copy.deepcopy(self.fx); data.update(mods)
            p = self.case_dir() / f"U6_{re.sub(r'[^A-Za-z0-9]+', '_', label)}.osi"
            with open(p, "w") as fh:
                self.ctx.yaml.dump(data, fh)
            s = self.new_session()
            ok, errs = s.load_osi(p)
            rows.append({"case": label, "loaded": ok, "errors": errs})
            self.check("U6", f".osi with {label} {'rejected' if should_reject else 'loaded'}",
                       (not ok) == should_reject, "reject" if should_reject else "load",
                       "rejected: " + "; ".join(errs)[:90] if not ok else "LOADED", step=label)
            if label == "custom steel fy 5000 MPa" and ok:
                self.shared["U6_fy5000_session"] = s
        WRITE_JSON(self.case_dir() / "U6_osi_validation_table.json", rows)

    def U7_custom_material_dialog(self):
        """Custom-material dialog validation (Custom... in a material combo)."""
        C = self.ctx.C
        base = {C.KEY_MATERIAL_GIRDER_DENSITY: "78.5", C.KEY_MATERIAL_GIRDER_FY: "410", C.KEY_MATERIAL_GIRDER_FU: "540",
                C.KEY_MATERIAL_GIRDER_E: "200", C.KEY_MATERIAL_GIRDER_G: "76.9", C.KEY_MATERIAL_GIRDER_POISSON: "0.3",
                C.KEY_MATERIAL_GIRDER_THERMAL: "12"}
        cases = [("normal fy410/fu540", {}, False), ("fu < fy (450/400)", {C.KEY_MATERIAL_GIRDER_FY: "450", C.KEY_MATERIAL_GIRDER_FU: "400"}, True),
                 ("density 130", {C.KEY_MATERIAL_GIRDER_DENSITY: "130"}, True),
                 ("E 50 GPa", {C.KEY_MATERIAL_GIRDER_E: "50"}, True),
                 ("G inconsistent with E,nu (E200, nu0.3, G 120)", {C.KEY_MATERIAL_GIRDER_G: "120"}, True)]
        for label, mods, should_reject in cases:
            s = self.baseline_session()
            vals = dict(base); vals.update(mods)
            pops = s.create_custom_material(C.KEY_GIRDER, vals)
            name = s.dock._material_combo_map[C.KEY_GIRDER].currentText()
            accepted = name.startswith("custom_steel_")
            self.check("U7", f"Custom steel {label} {'rejected' if should_reject else 'accepted'}",
                       accepted != should_reject, "reject" if should_reject else "accept",
                       f"accepted as {name} (fy={s.d.get(C.KEY_MATERIAL_GIRDER_FY)}, fu={s.d.get(C.KEY_MATERIAL_GIRDER_FU)},"
                       f" G={s.d.get(C.KEY_MATERIAL_GIRDER_G)})" if accepted else f"rejected: {pops[:1]}", step=label)

    def U8_backend_validation(self):
        """Backend's own validation (used by .osi loads, scripts, any future CLI)."""
        C = self.ctx.C
        for label, mods in [("span 100 m", {C.KEY_SPAN: 100}), ("carriageway 40 m", {C.KEY_CARRIAGEWAY_WIDTH: 40}),
                            ("skew 60 deg", {C.KEY_SKEW_ANGLE: 60}), ("girder fy 5000", {C.KEY_MATERIAL_GIRDER_FY: 5000})]:
            b = self.ctx.PlateGirderBridge()
            d = copy.deepcopy(self.fx); d.update(mods)
            with capture(io.StringIO()):
                b.set_input(d)
                try:
                    b._validate_inputs()
                    msg = None
                except Exception as exc:
                    msg = str(exc)
            self.check("U8", f"Backend rejects {label}", msg is not None, "ValueError", msg or "accepted (no range check)",
                       step=label)

    # ======================================================================
    # Design-run tests
    # ======================================================================
    def S01_baseline_three_runs(self):
        """TC00 inputs; Design -> unlock -> Design -> unlock -> Design (no changes)."""
        s = self.baseline_session()
        r = []
        for i in (1, 2, 3):
            if i > 1:
                s.unlock()
            r.append(self.design(s, f"run{i}"))
        self.repeat_check(r[0], r[1], "R1", "Run 2 output identical to run 1")
        self.repeat_check(r[0], r[2], "R2", "Run 3 output identical to run 1")
        self.shared["baseline"] = r[0]

    def repeat_check(self, a, b, cid, title):
        if a.get("status") != "ok" or b.get("status") != "ok":
            self.check(cid, title, False, "both runs ok", f"{a.get('status')}/{b.get('status')}")
            return
        diffs = compare_runs(a["_out"], b["_out"])
        WRITE_JSON(self.case_dir() / f"{cid}_diff_{a['step']}_vs_{b['step']}.json",
                   [{"key": k, "first": va, "second": vb} for k, va, vb in diffs[:2000]])
        self.check(cid, title, not diffs, "0 differences",
                   f"{len(diffs)} differences, e.g. {[d[0] for d in diffs[:3]]}")

    def S02_A_B_A(self):
        """A (span30/cw7.5) -> B (span40/cw11) -> A again, in one session; plus B in a fresh session."""
        C = self.ctx.C
        s = self.baseline_session()
        ra = self.design(s, "run1_A")
        s.unlock(); s.set_field(C.KEY_SPAN, "40"); s.set_field(C.KEY_CARRIAGEWAY_WIDTH, "11")
        rb = self.design(s, "run2_B")
        s.unlock(); s.set_field(C.KEY_SPAN, "30"); s.set_field(C.KEY_CARRIAGEWAY_WIDTH, "7.5")
        ra2 = self.design(s, "run3_A")
        self.repeat_check(ra, ra2, "R3", "A after B identical to first A")
        f = self.typed_session("40", ["11"])               # fresh session, B typed directly
        rbf = self.design(f, "fresh_B")
        self.check("R4", "B after A (same session) == B typed in a fresh session (girders)",
                   rb.get("n_girders_input") == rbf.get("n_girders_input"),
                   f"{rbf.get('n_girders_input')} girders @ {rbf.get('girder_spacing_input_m')} m (fresh)",
                   f"{rb.get('n_girders_input')} girders @ {rb.get('girder_spacing_input_m')} m (after A)")
        self.check("R5", "B after A (same session) == B typed in a fresh session (max DCR / status)",
                   close(rb.get("max_dcr"), rbf.get("max_dcr"), rel=1e-6),
                   f"{rbf.get('max_dcr')} {rbf.get('overall_status')}", f"{rb.get('max_dcr')} {rb.get('overall_status')}")
        t = self.typed_session("40", ["20", "11"])          # typo: 20 first, corrected to 11
        rt = self.design(t, "typo_B_cw20_then_11")
        self.check("R6", "B with a corrected typo (cw 20 -> 11) == B typed directly",
                   rt.get("n_girders_input") == rbf.get("n_girders_input") and close(rt.get("max_dcr"), rbf.get("max_dcr"), rel=1e-6),
                   f"{rbf.get('n_girders_input')} girders, max DCR {rbf.get('max_dcr')}",
                   f"{rt.get('n_girders_input')} girders, max DCR {rt.get('max_dcr')} {rt.get('overall_status')}")

    def typed_session(self, span, cw_sequence):
        """Fresh session; location + span typed, then the carriageway values in order."""
        C = self.ctx.C
        s = self.new_session()
        s.set_field(C.KEY_PROJECT_LOCATION, copy.deepcopy(self.fx[C.KEY_PROJECT_LOCATION]))
        s.set_field(C.KEY_SPAN, span)
        for cw in cw_sequence:
            s.set_field(C.KEY_CARRIAGEWAY_WIDTH, cw)
        s.set_field(C.KEY_SKEW_ANGLE, "0")
        return s

    def get_baseline(self):
        if "baseline" not in self.shared:
            self.shared["baseline"] = self.design(self.baseline_session(), "baseline_reference")
        return self.shared["baseline"]

    def S03_custom_materials(self):
        """TC01 custom girder steel + custom deck concrete, then back to defaults."""
        base = self.get_baseline()
        s = self.baseline_session()
        self.custom_materials_tc01(s)
        rc = self.design(s, "run1_custom")
        if base and rc.get("status") == "ok":
            self.check("M1", "Custom girder density 80 changes the girder self-weight",
                       not close(rc.get("sw_line_load_N_m"), base.get("sw_line_load_N_m"), rel=1e-6),
                       f"!= {base.get('sw_line_load_N_m')} N/m", rc.get("sw_line_load_N_m"))
            self.check("M2", "Custom deck density 26 changes the deck design moments",
                       not close(rc.get("deck_Msls_sag_kNm_m"), base.get("deck_Msls_sag_kNm_m"), rel=1e-6),
                       f"!= {base.get('deck_Msls_sag_kNm_m')} kNm/m", rc.get("deck_Msls_sag_kNm_m"))
            self.check("M3", "Custom fy 410 reaches the design (Md changes)",
                       not close(rc.get("Md_kNm"), base.get("Md_kNm"), rel=1e-6),
                       f"!= {base.get('Md_kNm')}", rc.get("Md_kNm"))
            self.check("M4", "Deck exposure/cover with custom M45-equivalent concrete",
                       rc.get("deck_exposure") == base.get("deck_exposure"),
                       f"{base.get('deck_exposure')} (same environment as baseline)",
                       f"{rc.get('deck_exposure')}, cover {rc.get('deck_cover_required_mm')} mm")
        C = self.ctx.C
        s.unlock()
        s.set_field(C.KEY_GIRDER, self.fx[C.KEY_GIRDER]); s.set_field(C.KEY_DECK_CONCRETE_GRADE_BASIC, self.fx[C.KEY_DECK_CONCRETE_GRADE_BASIC])
        rb = self.design(s, "run2_back_to_default")
        if base:
            self.repeat_check(base, rb, "R7", "Back to default materials == baseline")

    def S04_custom_after_reload(self):
        """U4 session: custom materials saved, re-loaded, girder re-selected E250A -> custom. Design."""
        s = self.shared.get("U4d_session")
        if s is None:
            self.U4_custom_material_reload(); s = self.shared["U4d_session"]
        r = self.design(s, "run1_reloaded_custom")
        C = self.ctx.C
        if r.get("status") == "ok":
            self.check("M5", "Design fy for loaded+reselected custom_steel_410_540",
                       close(r.get("fy_used_MPa"), 410), 410, r.get("fy_used_MPa"))

    def S05_additional_inputs(self):
        """Additional Inputs (deck 300, WC 80, ...) reach the design; then change span and Design again."""
        C = self.ctx.C
        s = self.baseline_session()
        s.open_additional_inputs(self.ADDITIONAL_EDITS)
        r1 = self.design(s, "run1_edits")
        if r1.get("status") == "ok":
            self.check("A1", "Deck thickness 300 mm used in the slab load",
                       close(r1.get("slab_load_N_m2"), 0.300 * 25000, rel=1e-3) or close(r1.get("deck_thickness_input_mm"), 300),
                       "300 mm", f"input {r1.get('deck_thickness_input_mm')} mm, slab load {r1.get('slab_load_N_m2')} N/m2")
        s.unlock(); s.set_field(C.KEY_SPAN, "32")
        r2 = self.design(s, "run2_span32")
        self.check("A2", "Deck thickness after changing span (user never re-edited it)",
                   close(r2.get("deck_thickness_input_mm"), 300), 300, r2.get("deck_thickness_input_mm"))

    def S06_girders_and_bracing(self):
        """Additional Inputs: 5 girders; cross-bracing spacing 5 m; cross-bracing steel E 450A."""
        C = self.ctx.C
        s = self.baseline_session()
        s.design_prep()
        s.d[C.KEY_TS_NO_OF_GIRDERS] = 5          # Typical Section tab: girders 4 -> 5 (layout re-solved)
        with capture(io.StringIO()):
            self.ctx.solve_extend(s.d)
        self.design(s, "run1_5_girders", prep=True)
        s = self.baseline_session()
        s.design_prep()
        edits = {k: 5.0 for k in s.d if k.startswith("member_properties.cross_bracing_details.spacing.")}
        s.open_additional_inputs(edits)
        self.design(s, "run2_cb_spacing_5m")
        s = self.baseline_session()
        s.set_field(C.KEY_CROSS_BRACING, "E 450A")
        r3 = self.design(s, "run3_bracing_E450A")
        base = self.get_baseline()
        if base and r3.get("status") == "ok":
            self.check("M6", "Cross-bracing steel E 350A -> E 450A changes bracing design",
                       r3.get("bracing_signature") != base.get("bracing_signature"),
                       "different capacities", "identical sections and capacities" if
                       r3.get("bracing_signature") == base.get("bracing_signature") else "changed")

    def S07_boundaries(self):
        """Valid boundary values, each typed into a fresh session (so the girder count is the fresh-session one)."""
        C = self.ctx.C
        cases = [("span20", "20", "7.5", "0", {}), ("span45", "45", "7.5", "0", {}),
                 ("cw4.25", "30", "4.25", "0", {}), ("cw23.6", "30", "23.6", "0", {}),
                 ("skew+15", "30", "7.5", "15", {}), ("skew-15", "30", "7.5", "-15", {}),
                 ("median_yes_cw15", "30", "15", "0", {C.KEY_INCLUDE_MEDIAN: "Yes"}),
                 ("footpath_both", "30", "7.5", "0", {C.KEY_FOOTPATH: "__both__"})]
        for step, span, cw, skew, combos in cases:
            s = self.new_session()
            try:
                s.set_field(C.KEY_PROJECT_LOCATION, copy.deepcopy(self.fx[C.KEY_PROJECT_LOCATION]))
                for k, v in combos.items():          # combos first: the layout is fixed at the first carriageway value
                    if v == "__both__":
                        w = s.dock.input_widget.findChild(self.ctx.QComboBox, k)
                        v = next(w.itemText(i) for i in range(w.count()) if "both" in w.itemText(i).lower())
                    s.set_field(k, v)
                for k, v in ((C.KEY_SPAN, span), (C.KEY_CARRIAGEWAY_WIDTH, cw), (C.KEY_SKEW_ANGLE, skew)):
                    pops = s.set_field(k, v)
                    if pops:
                        self.note(f"{step}: popup on {k}={v}: {pops[0]['text'][:90]}")
            except Exception as exc:
                self.note(f"{step}: could not set inputs ({exc})")
                continue
            self.design(s, step)

    def S08_stale_after_failure(self):
        """A -> failing run -> what is left in the backend -> A again."""
        C = self.ctx.C
        s = self.baseline_session()
        ra = self.design(s, "run1_A")
        s.unlock()
        s.design_prep()
        s.d[C.KEY_TS_GIRDER_SPACING] = 0              # a value the backend rejects
        rf = self.design(s, "run2_fail", prep=False)
        left = len(s.backend.output_dict or {})
        self.check("R8", "After a failed design no results from the previous run remain",
                   left == 0 or rf.get("status") == "ok", "output_dict empty",
                   f"status={rf.get('status')} ({rf.get('error')[:60]}), output_dict still has {left} keys"
                   f" (previous run had {ra.get('output_keys')})")
        s.unlock()
        with capture(io.StringIO()):
            self.ctx.solve_extend(s.d)
        ra2 = self.design(s, "run3_A")
        self.repeat_check(ra, ra2, "R9", "A after a failed run identical to first A")

    def S09_osi_bad_material(self):
        """The fy=5000 custom steel .osi that Load Input accepted (U6): what does Design do?"""
        if "U6_fy5000_session" not in self.shared:
            self.U6_osi_validation()
        s = self.shared.get("U6_fy5000_session")
        if s is None:
            self.note("U6 did not accept the fy=5000 file (nothing to run)")
            return
        r = self.design(s, "run1_fy5000")
        if r.get("status") == "ok":
            self.check("V1", "Design refuses fy = 5000 MPa loaded from .osi", False, "error / refused",
                       f"designed with fy={r.get('fy_used_MPa')} MPa, status {r.get('overall_status')}")
        else:
            self.check("V1", "Design refuses fy = 5000 MPa loaded from .osi", True, "error / refused", r.get("error"))

    def S10_deck_grade(self):
        """Deck concrete M40 -> M45 -> M50 (standard grades): exposure class and cover the deck design assumes."""
        C = self.ctx.C
        base = self.get_baseline()
        rows = [("M40", base)]
        for grade in ("M45", "M50"):
            s = self.baseline_session()
            s.set_field(C.KEY_DECK_CONCRETE_GRADE_BASIC, grade)
            rows.append((grade, self.design(s, f"deck_{grade}")))
        self.note("deck grade -> exposure / required cover / deck check: " + "; ".join(
            f"{g}: {r.get('deck_exposure')} / {r.get('deck_cover_required_mm')} mm" for g, r in rows))
        same = len({r.get("deck_exposure") for _, r in rows}) == 1
        self.check("D1", "Exposure class does not change when only the concrete grade changes", same,
                   f"{base.get('deck_exposure')} for every grade",
                   ", ".join(f"{g}->{r.get('deck_exposure')} ({r.get('deck_cover_required_mm')} mm)" for g, r in rows))

    def S11_open_additional_inputs_no_edit(self):
        """Open Additional Inputs and press Save WITHOUT changing anything: does the design change?"""
        C = self.ctx.C
        base = self.get_baseline()
        s = self.baseline_session()
        s.open_additional_inputs({})
        r = self.design(s, "opened_and_saved_no_edits")
        WRITE_JSON(self.case_dir() / "input_keys_changed_by_opening_dialog.json",
                   {k: [self.fx.get(k), s.d.get(k)] for k in sorted(set(self.fx) | set(s.d))
                    if json.dumps(TO_JSONABLE(self.fx.get(k))) != json.dumps(TO_JSONABLE(s.d.get(k)))})
        if r.get("status") == "ok":
            ob, orr = base["_out"]["design_results"], r["_out"]["design_results"]
            fields = ["cross_bracing_spacing_m", "chi_LT", "Mb_kNm", "max_dcr", "overall_status"]
            self.check("A3", "Design unchanged after opening Additional Inputs and saving with no edits",
                       all(str(ob.get(f)) == str(orr.get(f)) for f in fields),
                       ", ".join(f"{f}={ob.get(f)}" for f in fields), ", ".join(f"{f}={orr.get(f)}" for f in fields))
            self.check("A4", "Girder area unchanged after opening Additional Inputs (no edits)",
                       close(r.get("sw_area_m2"), base.get("sw_area_m2"), rel=1e-6),
                       base.get("sw_area_m2"), r.get("sw_area_m2"))

    CASES = [
        ("U1", "U1_builder_matches_gui"), ("U2", "U2_girder_count_history"),
        ("U3", "U3_additional_inputs_reset"), ("U4", "U4_custom_material_reload"),
        ("U5", "U5_homepage_validation"), ("U6", "U6_osi_validation"),
        ("U7", "U7_custom_material_dialog"), ("U8", "U8_backend_validation"),
        ("S01", "S01_baseline_three_runs"), ("S02", "S02_A_B_A"), ("S03", "S03_custom_materials"),
        ("S04", "S04_custom_after_reload"), ("S05", "S05_additional_inputs"),
        ("S06", "S06_girders_and_bracing"), ("S07", "S07_boundaries"),
        ("S08", "S08_stale_after_failure"), ("S09", "S09_osi_bad_material"),
        ("S10", "S10_deck_grade"), ("S11", "S11_open_additional_inputs_no_edit"),
    ]

    def run(self, only=None, ui_only=False):
        self.shared = {}
        for cid, meth in self.CASES:
            if only and cid not in only:
                continue
            if ui_only and not cid.startswith("U"):
                continue
            self.cur_case = f"{cid}_{meth.split('_', 1)[1]}"
            doc = (getattr(self, meth).__doc__ or "").strip().splitlines()[0]
            say(f"\n== {cid}: {doc}")
            t0 = time.time()
            try:
                getattr(self, meth)()
            except Exception as exc:
                tb = traceback.format_exc()
                (self.case_dir() / "case_error.txt").write_text(tb, encoding="utf-8")
                self.check("ERR", "test case crashed", False, "no exception", f"{type(exc).__name__}: {exc}")
            say(f"   ({time.time() - t0:.0f} s)")
        part = self.out / "partials"
        part.mkdir(exist_ok=True)
        cases = sorted({r["case"] for r in self.check_rows} | {r["case"] for r in self.run_rows})
        WRITE_JSON(part / f"{os.getpid()}_{int(time.time())}.json",
                   {"cases": cases, "runs": [{k: v for k, v in r.items() if k != "_out"} for r in self.run_rows],
                    "checks": self.check_rows, "notes": self.case_notes})
        self.write_reports()

    # -- reports -------------------------------------------------------------------
    def write_reports(self):
        """Merge every partial result in <out>/partials (later runs of a case replace earlier ones)."""
        by_case_runs, by_case_checks, notes = {}, {}, {}
        for f in sorted((self.out / "partials").glob("*.json"), key=lambda p: p.stat().st_mtime):
            part = json.load(open(f, encoding="utf-8"))
            for c in part["cases"]:
                by_case_runs[c] = [r for r in part["runs"] if r["case"] == c]
                by_case_checks[c] = [r for r in part["checks"] if r["case"] == c]
                notes[c] = part["notes"].get(c, [])
        order = [f"{cid}_{m.split('_', 1)[1]}" for cid, m in self.CASES]
        keyf = lambda c: order.index(c) if c in order else 999
        self.run_rows = [r for c in sorted(by_case_runs, key=keyf) for r in by_case_runs[c]]
        self.check_rows = [r for c in sorted(by_case_checks, key=keyf) for r in by_case_checks[c]]
        self.case_notes = {c: notes[c] for c in sorted(notes, key=keyf) if notes[c]}
        run_fields = ["case", "step", "status", "seconds", "error", "design_mode", "span_m", "carriageway_m",
                      "n_girders_input", "n_girders_checked", "per_girder_ids", "girder_spacing_input_m",
                      "girder_spacing_analysis_m", "overall_width_input_m", "girder_material", "girder_density_input",
                      "girder_density_used", "girder_fy_input", "fy_used_MPa", "deck_material", "deck_density_input",
                      "deck_density_used", "deck_thickness_input_mm", "sw_line_load_N_m", "sw_area_m2",
                      "A_steel_check_m2", "M_sw_max_kNm", "M_sw_expected_kNm", "M_sw_ratio", "delta_total_check_mm",
                      "delta_total_output_max_mm", "thermal_missing_warnings", "end_diaphragm_empty_pairs",
                      "cb_spacing_input_m", "cb_spacing_analysis_m", "tf_mm", "tw_mm", "D_mm", "Md_kNm",
                      "overall_status", "max_dcr", "controlling_girder", "deck_Msls_sag_kNm_m", "deck_exposure",
                      "deck_cover_required_mm", "output_keys"]
        with open(self.out / "runs.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=run_fields, extrasaction="ignore")
            w.writeheader()
            for r in self.run_rows:
                w.writerow({k: r.get(k) for k in run_fields})
        with open(self.out / "checks.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["case", "step", "check", "result", "title", "expected", "actual"])
            w.writeheader()
            for r in self.check_rows:
                w.writerow({k: r.get(k) for k in w.fieldnames})
        n = {"PASS": 0, "FAIL": 0, "INFO": 0}
        for r in self.check_rows:
            n[r["result"]] = n.get(r["result"], 0) + 1
        lines = [f"# OsdagBridge automated test suite - {self.out.name}", "",
                 f"Design runs: {len(self.run_rows)} "
                 f"(ok {sum(r['status'] == 'ok' for r in self.run_rows)}, "
                 f"error {sum(r['status'] == 'error' for r in self.run_rows)}); "
                 f"checks: {n['PASS']} pass, {n['FAIL']} fail, {n['INFO']} info", ""]
        lines += ["## Design runs", "", "| case | step | status | s | girders in/checked | spacing in/used (m) | "
                  "steel dens in/used | deck dens in/used | M_sw ratio | defl check/shown (mm) | status | max DCR |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in self.run_rows:
            lines.append(f"| {r['case']} | {r['step']} | {r['status']} | {r['seconds']} | "
                         f"{r.get('n_girders_input')}/{r.get('n_girders_checked')} | "
                         f"{r.get('girder_spacing_input_m')}/{r.get('girder_spacing_analysis_m')} | "
                         f"{r.get('girder_density_input')}/{r.get('girder_density_used')} | "
                         f"{r.get('deck_density_input')}/{r.get('deck_density_used')} | {r.get('M_sw_ratio')} | "
                         f"{r.get('delta_total_check_mm')}/{r.get('delta_total_output_max_mm')} | "
                         f"{r.get('overall_status')} | {r.get('max_dcr')} |")
        lines += ["", "## Failed checks", "", "| case | step | check | title | expected | actual |", "|---|---|---|---|---|---|"]
        for r in self.check_rows:
            if r["result"] == "FAIL":
                lines.append(f"| {r['case']} | {r['step']} | {r['check']} | {r['title']} | "
                             f"{str(r['expected'])[:80]} | {str(r['actual'])[:140]} |")
        if self.case_notes:
            lines += ["", "## Notes", ""]
            for c, notes in self.case_notes.items():
                for t in notes:
                    lines.append(f"- **{c}**: {t}")
        (self.out / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        say(f"\nDone. {len(self.run_rows)} design runs, {n['PASS']} pass / {n['FAIL']} fail / {n['INFO']} info checks.")
        say(f"Results: {self.out}")


# ============================================================================
def main():
    global TO_JSONABLE, WRITE_JSON, FLATTEN
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--ui-only", action="store_true")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    if args.list:
        for cid, meth in Suite.CASES:
            print(f"{cid:4} {(getattr(Suite, meth).__doc__ or '').strip().splitlines()[0]}")
        return

    sys.path.insert(1, os.getcwd())          # run from OsdagBridge/src, like run_logged.py
    sys.path.insert(0, str(SCRIPT_DIR))
    import run_logged                        # reuse the JSON / git helpers
    TO_JSONABLE, WRITE_JSON, FLATTEN = run_logged.to_jsonable, run_logged.write_json, run_logged._flatten

    stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = Path(args.out) if args.out else TESTING_ROOT / "suite_runs" / stamp
    out.mkdir(parents=True, exist_ok=True)
    info = run_logged.session_info("run_test_suite")
    WRITE_JSON(out / "session_info.json", info)
    say(f"OsdagBridge test suite -> {out}")
    say(f"OsdagBridge commit {info.get('git_commit', '?')[:10]}  status '{info.get('git_status_short', '')}'")
    t0 = time.time()
    ctx = Ctx()
    suite = Suite(ctx, out)
    only = {x.strip() for x in args.only.split(",") if x.strip()} or None
    suite.run(only=only, ui_only=args.ui_only)
    say(f"Total time {time.time() - t0:.0f} s")


TO_JSONABLE = WRITE_JSON = FLATTEN = None

if __name__ == "__main__":
    main()
