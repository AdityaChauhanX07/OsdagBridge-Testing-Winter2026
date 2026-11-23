"""
make_report_tables.py - turn a run_test_suite.py results folder into LaTeX tables for the report.

    python make_report_tables.py <suite_runs/folder> [<suite_runs/folder2> ...]

Writes report/generated/*.tex. When several folders are given, the first is
the "main" run (tables), the others are listed for comparison (run-time table).
"""
import ast
import csv
import json
import re
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parent / "generated"

CHECKS = OrderedDict([
    ("C01", ("Design check uses the real number of girders", "03")),
    ("C02", ("Grillage girder spacing = input girder spacing", "#74")),
    ("C03", ("Steel self-weight uses the girder material density", "#20")),
    ("C04", ("Deck slab load uses the deck material density", "#41")),
    ("C05", ("Girder SW moment = $wL^2/8$ (within 5\\%)", "03")),
    ("C06", ("Deflection: design check = per-girder output/report", "04")),
    ("C07", ("Thermal load case exists", "#92")),
    ("C08", ("End-diaphragm members designed", "#72")),
    ("C09", ("Cross-bracing spacing used = spacing shown", "01")),
    ("C10", ("Girder area: analysis = design check", "06")),
    ("C11", ("Design $f_y$ = material $f_y$ (info: thickness)", "07")),
    ("C12", ("One self-weight line per girder", "--")),
])


RUNS_CAPTION = (r"\caption{All design runs. ``in/chk'': girders in the input / girders in the design check. "
                r"$\gamma_s$, $\gamma_c$: steel and concrete densities, input / used by the analysis (kN/m$^3$). "
                r"$M_{SW}$ ratio: per-girder self-weight moment $/(wL^2/8)$. $\delta$: total deflection in the design "
                r"check / maximum per-girder value shown.}\label{tab:runs}\\")
UI_CAPTION = (r"\caption{Every UI-logic, multi-run and material check (U = UI logic, R = repeated runs, "
              r"A = Additional Inputs, M = materials, V = validation in design, D = deck grade), with the recorded result.}\label{tab:uichecks}\\")


def tex(s):
    s = "" if s is None else str(s)
    for a, b in (("\\", "\\textbackslash{}"), ("&", "\\&"), ("%", "\\%"), ("$", "\\$"), ("#", "\\#"),
                 ("_", "\\_"), ("{", "\\{"), ("}", "\\}"), ("~", "\\textasciitilde{}"), ("^", "\\^{}"),
                 ("°", "$^\\circ$"), ("²", "$^2$"), ("³", "$^3$"), ("≥", "$\\geq$"), ("≤", "$\\leq$"),
                 ("→", "$\\rightarrow$"), ("×", "$\\times$"), ("−", "$-$"), ("->", "$\\rightarrow$")):
        s = s.replace(a, b)
    return s


def changes(d):
    """{'a.b.key': 'x->y', ...} -> 'key x -> y; ...' (full, readable)."""
    parts = []
    for k, v in d.items():
        name = k.split(".")[-1]
        if name in ("thickness", "height", "diameter", "type") and "." in k:
            name = ".".join(k.split(".")[-2:])
        parts.append(f"{name} " + str(v).replace("->", " -> "))
    return "; ".join(parts)


def readable_actual(c, u5_popups, u6_errors):
    """The check's recorded result, complete. Text that the suite stored shortened
    is taken in full from the per-case evidence file of the same run."""
    a = c["actual"]
    a = re.sub(r"(\d+) differences(, e\.g\.)? \[\]$", r"\1 differences", a)
    m = re.match(r"^rejected: (\[\{.*\}\])$", a)
    if m:  # list of pop-ups shown by the dialog
        try:
            pops = ast.literal_eval(m.group(1))
            return "rejected. " + " ".join(f"Pop-up ({p.get('title', '')}): {p.get('text', '')}" for p in pops)
        except (ValueError, SyntaxError):
            pass
    m = re.match(r"^(.*?)(\{.*\})\s*$", a)
    if m:
        try:
            return f"{m.group(1).strip()} {changes(ast.literal_eval(m.group(2)))}".strip()
        except (ValueError, SyntaxError):
            pass
    if c["check"] == "U5" and "=" in c["step"]:
        field, typed = c["step"].split("=", 1)
        full = u5_popups.get((field, typed))
        if full and a.startswith("rejected -> "):
            shown = a[len("rejected -> "):].split("(", 1)[0].strip()
            return f"rejected, field set to {shown}. Pop-up: {full}"
    if c["check"] == "U6" and c["step"] in u6_errors and a.startswith("rejected"):
        return "rejected: " + " ".join(u6_errors[c["step"]])
    return a


def num(v, nd=3):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return "--"
    return f"{f:.{nd}f}".rstrip("0").rstrip(".") if "." in f"{f:.{nd}f}" else f"{f:.{nd}f}"


def issue_ref(code):
    if code.startswith("#"):
        return f"\\href{{https://github.com/Nidhikhare12/OsdagBridge/issues/{code[1:]}}}{{\\#{code[1:]}}}"
    if code == "--":
        return "--"
    return f"\\issue{{{code}}}"


def main(folders):
    OUT.mkdir(exist_ok=True)
    main_dir = Path(folders[0])
    runs = list(csv.DictReader(open(main_dir / "runs.csv", encoding="utf-8")))
    checks = list(csv.DictReader(open(main_dir / "checks.csv", encoding="utf-8")))

    # ---- design runs -------------------------------------------------------
    lines = [r"\begin{longtable}{@{}llrrrrrrrr@{}}", RUNS_CAPTION, r"\toprule",
             r"Case & Step & Girders & Spacing (m) & $\gamma_s$ & $\gamma_c$ & $M_{SW}$ & $\delta$ (mm) & max & \\",
             r" & & in/chk & in/used & in/used & in/used & ratio & chk/shown & DCR & Status\\", r"\midrule\endfirsthead",
             r"\multicolumn{10}{@{}l}{\emph{Table \thetable{} continued}}\\", r"\toprule",
             r"Case & Step & Girders & Spacing (m) & $\gamma_s$ & $\gamma_c$ & $M_{SW}$ & $\delta$ (mm) & max & \\",
             r" & & in/chk & in/used & in/used & in/used & ratio & chk/shown & DCR & Status\\", r"\midrule\endhead"]
    for r in runs:
        if r["status"] != "ok":
            lines.append(f"{tex(r['case'][:3])} & {tex(r['step'])} & \\multicolumn{{8}}{{@{{}}p{{0.6\\linewidth}}@{{}}}}{{\\raggedright\\emph{{{tex(r['status'])}: {tex(r['error'])}}}}}\\\\")
            continue
        lines.append(" & ".join([
            tex(r["case"][:3]), tex(r["step"]),
            f"{r['n_girders_input']}/{r['n_girders_checked']}",
            f"{num(r['girder_spacing_input_m'])}/{num(r['girder_spacing_analysis_m'])}",
            f"{num(r['girder_density_input'],1)}/{num(r['girder_density_used'],1)}",
            f"{num(r['deck_density_input'],1)}/{num(r['deck_density_used'],1)}",
            num(r["M_sw_ratio"]),
            f"{num(r['delta_total_check_mm'],1)}/{num(r['delta_total_output_max_mm'],1)}",
            num(r["max_dcr"]), tex(r["overall_status"])]) + r"\\")
    lines += [r"\bottomrule", r"\end{longtable}"]
    (OUT / "runs_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # ---- per-check summary ---------------------------------------------------
    cnt = defaultdict(lambda: defaultdict(int))
    for c in checks:
        cnt[c["check"]][c["result"]] += 1
    lines = [r"\begin{tabular}{@{}llrrrl@{}}", r"\toprule", r"ID & Check & Pass & Fail & Info & Issue\\", r"\midrule"]
    for cid, (title, iss) in CHECKS.items():
        d = cnt.get(cid, {})
        lines.append(f"{cid} & {title} & {d.get('PASS',0)} & {d.get('FAIL',0)} & {d.get('INFO',0)} & {issue_ref(iss)}\\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "check_summary.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # ---- every non-C check (UI logic, multi-run, materials) -------------------
    u5_popups, u6_errors = {}, {}
    u5 = main_dir / "U5_homepage_validation" / "U5_validation_table.json"
    if u5.exists():
        for r in json.load(open(u5, encoding="utf-8")):
            u5_popups[(r["field"].split(".")[-1], r["typed"])] = r["popup"]
    u6 = main_dir / "U6_osi_validation" / "U6_osi_validation_table.json"
    if u6.exists():
        for r in json.load(open(u6, encoding="utf-8")):
            u6_errors[r["case"]] = r["errors"]
    head = r"ID & Test & Actual & Result\\"
    lines = [r"\begin{longtable}{@{}>{\raggedright\arraybackslash}p{0.06\linewidth}>{\raggedright\arraybackslash}p{0.33\linewidth}>{\raggedright\arraybackslash}p{0.47\linewidth}l@{}}",
             UI_CAPTION, r"\toprule", head, r"\midrule\endfirsthead",
             r"\multicolumn{4}{@{}l}{\emph{Table \thetable{} continued}}\\", r"\toprule", head, r"\midrule\endhead"]
    seen = set()
    for c in checks:
        if c["check"].startswith("C"):
            continue
        key = (c["check"], c["title"], c["step"])
        if key in seen:
            continue
        seen.add(key)
        res = {"PASS": r"\pass", "FAIL": r"\fail", "INFO": r"\info"}[c["result"]]
        lines.append(f"{tex(c['check'])} & {tex(c['title'])} & {tex(readable_actual(c, u5_popups, u6_errors))} & {res}\\\\")
    lines += [r"\bottomrule", r"\end{longtable}"]
    (OUT / "ui_checks_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # ---- homepage validation table (U5) ---------------------------------------
    u5 = main_dir / "U5_homepage_validation" / "U5_validation_table.json"
    if u5.exists():
        rows = json.load(open(u5, encoding="utf-8"))
        lines = [r"\begin{tabular}{@{}ll>{\raggedright\arraybackslash}p{0.5\linewidth}l@{}}", r"\toprule",
                 r"Field & Typed & Pop-up shown & Field becomes\\", r"\midrule"]
        for r in rows:
            lines.append(f"{tex(r['field'].split('.')[-1])} & {tex(r['typed'])} & {tex(r['popup']) or '(none - accepted)'} & {tex(r['field_now'])}\\\\")
        lines += [r"\bottomrule", r"\end{tabular}"]
        (OUT / "u5_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # ---- .osi validation table (U6) --------------------------------------------
    u6 = main_dir / "U6_osi_validation" / "U6_osi_validation_table.json"
    if u6.exists():
        rows = json.load(open(u6, encoding="utf-8"))
        lines = [r"\begin{tabular}{@{}l>{\raggedright\arraybackslash}p{0.62\linewidth}@{}}", r"\toprule", r"Value changed in the .osi & Load Input result\\", r"\midrule"]
        for r in rows:
            res = ("rejected: " + tex(" ".join(r["errors"]))) if not r["loaded"] else r"\textbf{loaded}"
            lines.append(f"{tex(r['case'])} & {res}\\\\")
        lines += [r"\bottomrule", r"\end{tabular}"]
        (OUT / "u6_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # ---- environment / run-time comparison --------------------------------------
    lines = [r"\begin{tabular}{@{}lrrr>{\raggedright\arraybackslash}p{0.36\linewidth}@{}}", r"\toprule", r"Suite run & Designs & Pass & Fail & Platform\\", r"\midrule"]
    for f in folders:
        p = Path(f)
        rr = list(csv.DictReader(open(p / "runs.csv", encoding="utf-8")))
        cc = list(csv.DictReader(open(p / "checks.csv", encoding="utf-8")))
        info = json.load(open(p / "session_info.json", encoding="utf-8")) if (p / "session_info.json").exists() else {}
        plat = info.get("platform", "?")
        lines.append(f"{tex(p.name)} & {len(rr)} & {sum(c['result']=='PASS' for c in cc)} & "
                     f"{sum(c['result']=='FAIL' for c in cc)} & {tex(plat)}\\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "suite_runs_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT / "n_designs.tex").write_text(f"{len(runs)} ", encoding="utf-8")
    (OUT / "n_checks.tex").write_text(f"{len(checks)} ", encoding="utf-8")
    print("written:", sorted(x.name for x in OUT.iterdir()))


if __name__ == "__main__":
    main(sys.argv[1:])
