"""
run_logged.py - launch the OsdagBridge desktop app with test logging.

Starts the normal OsdagBridge GUI, unchanged, but records evidence for every
design run without touching the OsdagBridge source code:

  runs/<timestamp>_<label>/
    session_info.json         Python/package versions, git commit, OS
    session.log               everything printed to the terminal (incl. the
                              @@input_dictionary prints and tracebacks)
    runNN_ui_input.json       dict exactly as the UI handed it to the backend
                              (PlateGirderBridge.set_input)
    runNN_backend_input.json  backend input_dict after normalisation and the
                              in-place mm -> m conversions done by design()
    runNN_output.json         backend output_dict (the "Output Dictionary")
    runNN_meta.json           status (ok / error / cancelled), duration, traceback
    runNN_diff_vs_prev.txt    what changed vs. the previous run in this session
                              (for the multi-run / stale-state tests)

How it works: it wraps PlateGirderBridge.set_input() and .design() at runtime
(monkeypatching), then calls the app's own main().

Usage (Anaconda Prompt, osdagbridge-env active):
    cd OsdagBridge\\src
    python ..\\..\\OsdagBridge-Testing-Winter2026\\scripts\\run_logged.py TC01_short_label
"""

from __future__ import annotations

import copy
import dataclasses
import datetime as _dt
import json
import math
import os
import platform
import re
import subprocess
import sys
import threading
import time
import traceback
from pathlib import Path

TESTING_ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = TESTING_ROOT / "runs"
TAG = "[run_logged]"


# --------------------------------------------------------------------------
# JSON conversion: turn anything in the dictionaries into something json can write
# --------------------------------------------------------------------------
MAX_DEPTH = 12
MAX_SEQ = 2000
_ADDR_RE = re.compile(r"at 0x[0-9A-Fa-f]+")


def to_jsonable(obj, _depth: int = 0):
    if _depth > MAX_DEPTH:
        return {"__truncated__": f"max depth {MAX_DEPTH}", "__type__": type(obj).__name__}

    if obj is None or isinstance(obj, (bool, int, str)):
        return obj
    if isinstance(obj, float):  # also catches numpy.float64 (a float subclass)
        obj = float(obj)
        return obj if math.isfinite(obj) else str(obj)  # NaN / inf -> "nan" / "inf"

    # numpy scalars / arrays (without importing numpy unless it is already loaded)
    np = sys.modules.get("numpy")
    if np is not None:
        if isinstance(obj, np.generic):
            return to_jsonable(obj.item(), _depth + 1)
        if isinstance(obj, np.ndarray):
            if obj.size > MAX_SEQ:
                flat = obj.ravel()
                return {"__ndarray__": True, "shape": list(obj.shape), "dtype": str(obj.dtype),
                        "first_20": to_jsonable(flat[:20].tolist(), _depth + 1)}
            return to_jsonable(obj.tolist(), _depth + 1)

    # mappings (dict, MappingProxyType, ...)
    if hasattr(obj, "items") and hasattr(obj, "keys"):
        try:
            return {str(k): to_jsonable(v, _depth + 1) for k, v in obj.items()}
        except Exception:
            pass

    if isinstance(obj, (list, tuple, set, frozenset)):
        seq = list(obj)
        if isinstance(obj, (set, frozenset)):
            seq = sorted(seq, key=repr)
        out = [to_jsonable(v, _depth + 1) for v in seq[:MAX_SEQ]]
        if len(seq) > MAX_SEQ:
            out.append({"__truncated__": f"{len(seq) - MAX_SEQ} more items"})
        return out

    if isinstance(obj, Path):
        return str(obj)

    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        d = {f.name: to_jsonable(getattr(obj, f.name, None), _depth + 1)
             for f in dataclasses.fields(obj)}
        d["__type__"] = type(obj).__name__
        return d

    if hasattr(obj, "model_dump"):  # pydantic v2 models
        try:
            d = to_jsonable(obj.model_dump(), _depth + 1)
            if isinstance(d, dict):
                d["__type__"] = type(obj).__name__
            return d
        except Exception:
            pass

    # Anything else (OCC shapes, xarray objects, Osdag design objects, ...):
    # record what it is without walking into it.
    try:
        r = repr(obj)
    except Exception as exc:  # repr itself can fail
        r = f"<repr failed: {exc}>"
    r = _ADDR_RE.sub("at 0x...", r)  # memory addresses differ every run -> noise in diffs
    return {"__type__": f"{type(obj).__module__}.{type(obj).__name__}", "repr": r[:300]}


def write_json(path: Path, data) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(to_jsonable(data), fh, indent=1, sort_keys=True, ensure_ascii=False)


# --------------------------------------------------------------------------
# Tee: keep printing to the console AND copy everything to session.log
# --------------------------------------------------------------------------
class Tee:
    """Console stream wrapper. Anything it doesn't implement itself (reconfigure,
    buffer, errors, ...) is passed through to the real console stream, so the app
    behaves exactly as without the logger (e.g. core/utils/connect.py calls
    sys.stderr.reconfigure(...) on import)."""

    def __init__(self, stream, logfile, lock):
        self._stream = stream
        self._log = logfile
        self._lock = lock

    def __getattr__(self, name):  # only called for attributes not defined here
        stream = self.__dict__.get("_stream")
        if stream is None:
            raise AttributeError(name)
        return getattr(stream, name)

    def reconfigure(self, *args, **kwargs):
        if self._stream is not None and hasattr(self._stream, "reconfigure"):
            return self._stream.reconfigure(*args, **kwargs)

    def write(self, s):
        if not isinstance(s, str):
            s = str(s)
        with self._lock:
            if self._stream is not None:
                try:
                    self._stream.write(s)
                except Exception:
                    pass
            try:
                self._log.write(s)
            except Exception:
                pass
        return len(s)

    def flush(self):
        with self._lock:
            for s in (self._stream, self._log):
                try:
                    if s is not None:
                        s.flush()
                except Exception:
                    pass

    def fileno(self):  # lets faulthandler keep writing to the real console
        return self._stream.fileno()

    def isatty(self):
        try:
            return self._stream.isatty()
        except Exception:
            return False

    @property
    def encoding(self):
        return getattr(self._stream, "encoding", "utf-8")

    def writable(self):
        return True

    def writelines(self, lines):
        for line in lines:
            self.write(line)


# --------------------------------------------------------------------------
# Session: numbering runs, writing files, diffing consecutive runs
# --------------------------------------------------------------------------
def _flatten(d, prefix=""):
    """Flatten nested dicts/lists to {"a.b[0].c": value} for diffing."""
    flat = {}
    if isinstance(d, dict):
        for k, v in d.items():
            flat.update(_flatten(v, f"{prefix}.{k}" if prefix else str(k)))
    elif isinstance(d, list):
        for i, v in enumerate(d):
            flat.update(_flatten(v, f"{prefix}[{i}]"))
    else:
        flat[prefix] = d
    return flat


def _diff_lines(title, old, new, limit=400):
    old_f, new_f = _flatten(old), _flatten(new)
    lines = []
    for k in sorted(set(old_f) | set(new_f)):
        a = old_f.get(k, "<missing>")
        b = new_f.get(k, "<missing>")
        if a != b:
            lines.append(f"  {k}: {a!r}  ->  {b!r}")
    out = [f"== {title}: {len(lines)} changed value(s) =="]
    out += lines[:limit]
    if len(lines) > limit:
        out.append(f"  ... {len(lines) - limit} more")
    return out


class Session:
    def __init__(self, label: str):
        stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", label).strip("_") or "session"
        self.dir = RUNS_DIR / f"{stamp}_{safe}"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.label = label
        self._n = 0
        self._lock = threading.Lock()
        self._prev = None  # (ui_input, output) of the previous run, as json-able data

    def next_run(self) -> int:
        with self._lock:
            self._n += 1
            return self._n

    def dump_run(self, n, backend, status, tb, started, seconds):
        p = self.dir
        ui_input = to_jsonable(getattr(backend, "_tc_ui_input_snapshot", {}))
        backend_input = to_jsonable(getattr(backend, "input_dict", {}))
        output = to_jsonable(dict(getattr(backend, "output_dict", {}) or {}))

        write_json(p / f"run{n:02d}_ui_input.json", ui_input)
        write_json(p / f"run{n:02d}_backend_input.json", backend_input)
        write_json(p / f"run{n:02d}_output.json", output)
        write_json(p / f"run{n:02d}_meta.json", {
            "session_label": self.label,
            "run": n,
            "status": status,
            "started": started,
            "duration_s": round(seconds, 2),
            "n_ui_input_keys": len(ui_input) if isinstance(ui_input, dict) else None,
            "n_output_keys": len(output) if isinstance(output, dict) else None,
            "traceback": tb,
        })

        if self._prev is not None:
            prev_in, prev_out = self._prev
            lines = [f"Run {n:02d} vs run {n - 1:02d}  (status this run: {status})", ""]
            lines += _diff_lines("UI input dictionary", prev_in, ui_input)
            lines.append("")
            lines += _diff_lines("Output dictionary", prev_out, output)
            (p / f"run{n:02d}_diff_vs_prev.txt").write_text("\n".join(lines), encoding="utf-8")
        self._prev = (ui_input, output)


# --------------------------------------------------------------------------
# Hooks around the backend
# --------------------------------------------------------------------------
def install_hooks(session: Session):
    from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge

    orig_set_input = PlateGirderBridge.set_input
    orig_design = PlateGirderBridge.design

    def set_input(self, input_dict, *args, **kwargs):
        try:
            self._tc_ui_input_snapshot = copy.deepcopy(dict(input_dict))
        except Exception:
            self._tc_ui_input_snapshot = to_jsonable(input_dict)
        return orig_set_input(self, input_dict, *args, **kwargs)

    def design(self, *args, **kwargs):
        n = session.next_run()
        started = _dt.datetime.now().isoformat(timespec="seconds")
        print(f"\n{TAG} ===== run {n:02d} started {started} =====", flush=True)
        t0 = time.perf_counter()
        status, tb = "ok", None
        try:
            return orig_design(self, *args, **kwargs)
        except BaseException as exc:
            cancelled = isinstance(exc, RuntimeError) and "cancel" in str(exc).lower()
            status = "cancelled" if cancelled else "error"
            tb = traceback.format_exc()
            raise
        finally:
            secs = time.perf_counter() - t0
            try:
                session.dump_run(n, self, status, tb, started, secs)
                print(f"{TAG} ===== run {n:02d} {status.upper()} in {secs:.1f} s -> "
                      f"saved to {session.dir} =====\n", flush=True)
            except Exception:
                print(f"{TAG} could not save run {n:02d}:\n{traceback.format_exc()}", flush=True)

    PlateGirderBridge.set_input = set_input
    PlateGirderBridge.design = design


# --------------------------------------------------------------------------
# Session info (for the report's "Test environment" section)
# --------------------------------------------------------------------------
def session_info(label: str) -> dict:
    info = {
        "label": label,
        "started": _dt.datetime.now().isoformat(timespec="seconds"),
        "cwd": os.getcwd(),
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "conda_env": os.environ.get("CONDA_DEFAULT_ENV"),
    }
    try:
        import importlib.util
        spec = importlib.util.find_spec("osdagbridge")  # namespace package: __file__ is None
        locs = list(spec.submodule_search_locations or []) if spec else []
        pkg_dir = Path(locs[0]).resolve()
        info["osdagbridge_path"] = str(pkg_dir)
        repo = pkg_dir.parents[1]
        for key, cmd in (("git_commit", ["rev-parse", "HEAD"]),
                         ("git_branch", ["rev-parse", "--abbrev-ref", "HEAD"]),
                         ("git_status_short", ["status", "--short"])):
            r = subprocess.run(["git", "-C", str(repo), *cmd],
                               capture_output=True, text=True, timeout=15)
            info[key] = r.stdout.strip()
    except Exception as exc:
        info["git_error"] = str(exc)
    try:
        from importlib.metadata import version, PackageNotFoundError
        for pkg in ("osdagbridge", "PySide6", "numpy", "scipy", "pandas", "matplotlib",
                    "pydantic", "openseespy", "opsvis", "shapely", "xarray"):
            try:
                info[f"pkg_{pkg}"] = version(pkg)
            except PackageNotFoundError:
                info[f"pkg_{pkg}"] = None
    except Exception:
        pass
    return info


def main():
    label = "_".join(sys.argv[1:]) if len(sys.argv) > 1 else "session"
    session = Session(label)

    logfile = open(session.dir / "session.log", "a", encoding="utf-8", errors="replace", buffering=1)
    lock = threading.RLock()
    sys.stdout = Tee(sys.stdout, logfile, lock)
    sys.stderr = Tee(sys.stderr, logfile, lock)

    # Same import behaviour as "python -m osdagbridge.desktop" run from src/
    if os.getcwd() not in sys.path:
        sys.path.insert(1, os.getcwd())

    write_json(session.dir / "session_info.json", session_info(label))
    print(f"{TAG} logging session '{label}' to {session.dir}", flush=True)

    install_hooks(session)

    import osdagbridge.desktop.__main__ as desktop_main  # runs the app's own startup code

    exit_code = 0
    try:
        desktop_main.main()
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else 0
    finally:
        print(f"{TAG} app closed (exit code {exit_code}). Evidence is in {session.dir}", flush=True)
        sys.stdout.flush()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
