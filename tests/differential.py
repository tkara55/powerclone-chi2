"""Differential test runner.

Two oracles:
  1. statsmodels GofChisquarePower (scale, >500 vectors). It returns a
     fractional N; G*Power-style N is the smallest integer reaching the
     target power, so we compare against ceil(N_statsmodels) and also check
     the post-hoc power at the same N.
  2. oracle/gpower_gui_vectors.csv: values read off the G*Power GUI
     (one screenshot per row in oracle/screenshots/). Rows with empty
     expected columns are skipped.

Writes tests/REPORT.md and oracle/statsmodels_vectors.csv.
Usage: python -I tests/differential.py   (from the repo root, package installed)
"""

from __future__ import annotations

import csv
import itertools
import math
from pathlib import Path

from statsmodels.stats.power import GofChisquarePower

from powerclone import engine

ROOT = Path(__file__).resolve().parent.parent
INT_FIELDS = {"n_total", "df"}


def close(a: float, b: float, tol: float = 1e-6) -> bool:
    return abs(a - b) <= tol or abs(a - b) <= tol * abs(b)


def statsmodels_grid():
    ws = [0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.7, 0.9, 1.2]
    alphas = [0.001, 0.01, 0.05, 0.10]
    powers = [0.5, 0.8, 0.9, 0.95, 0.99]
    dfs = [1, 2, 3, 5]
    return list(itertools.product(ws, alphas, powers, dfs))


def run_statsmodels():
    sm = GofChisquarePower()
    rows, n_match, p_match, mismatches, skipped = [], 0, 0, [], []
    for w, alpha, power, df in statsmodels_grid():
        frac = sm.solve_power(effect_size=w, nobs=None, alpha=alpha, power=power, n_bins=df + 1)
        if not math.isfinite(frac):
            # statsmodels' root finder fails when N is below its bracket (very large w)
            skipped.append((w, alpha, power, df))
            continue
        ref_n = max(engine.N_MIN, math.ceil(frac - 1e-9))
        ours = engine.run({"test": "chi2-contingency", "mode": "a-priori",
                           "w": w, "alpha": alpha, "power": power, "df": df})
        sm_power = sm.power(effect_size=w, nobs=ours["n_total"], alpha=alpha, n_bins=df + 1)
        ok_n = ours["n_total"] == ref_n
        ok_p = close(ours["actual_power"], sm_power)
        n_match += ok_n
        p_match += ok_p
        if not (ok_n and ok_p):
            mismatches.append((w, alpha, power, df, frac, ref_n, ours["n_total"]))
        rows.append({"w": w, "alpha": alpha, "power": power, "df": df,
                     "statsmodels_n_fractional": f"{frac:.6f}", "ceil_n": ref_n,
                     "our_n": ours["n_total"], "our_actual_power": ours["actual_power"],
                     "statsmodels_power_at_our_n": sm_power})
    with open(ROOT / "oracle" / "statsmodels_vectors.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return len(rows), n_match, p_match, mismatches, skipped


def run_gui():
    path = ROOT / "oracle" / "gpower_gui_vectors.csv"
    results = []
    if not path.exists():
        return results
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            expected = {k[4:]: v for k, v in row.items() if k.startswith("exp_") and v not in ("", None)}
            if not expected:
                continue
            inp = {k: v for k, v in row.items()
                   if k in engine.ALL_FIELDS | {"test", "mode"} and v not in ("", None)}
            try:
                got = engine.run(inp)
            except engine.EngineError as err:
                got = err.to_dict()
            ok = True
            for field, exp in expected.items():
                if field == "code":
                    ok &= got.get("code") == exp
                elif field in INT_FIELDS:
                    ok &= got.get(field) == int(exp)
                else:
                    ok &= field in got and close(got[field], float(exp))
            results.append((row["id"], ok, expected, got))
    return results


def main():
    total, n_match, p_match, mism, skipped = run_statsmodels()
    gui = run_gui()
    lines = ["# Differential test report", "",
             "## Oracle 1: statsmodels GofChisquarePower (a-priori)", "",
             f"- Vectors: **{total}** (w x alpha x power x df grid)",
             f"- N exact match vs ceil(statsmodels N): **{n_match}/{total}** ({100 * n_match / total:.1f}%)",
             f"- actual_power within 1e-6 of statsmodels power at our N: **{p_match}/{total}**",
             "", "statsmodels returns a fractional N (e.g. 219.4); a sample size must be an",
             "integer that *reaches* the target power, so the engine reports the smallest",
             "integer N with power >= target, i.e. ceil(). See LEDGER.md for the rounding rule.", "",
             f"- Skipped (statsmodels solver returned NaN, all very large w): **{len(skipped)}**", ""]
    if mism:
        lines += ["### Mismatches", "", "| w | alpha | power | df | sm N | ceil | ours |", "|---|---|---|---|---|---|---|"]
        lines += [f"| {w} | {a} | {p} | {d} | {f:.4f} | {c} | {o} |" for w, a, p, d, f, c, o in mism]
        lines.append("")
    lines += ["## Oracle 2: G*Power 3.1.9.7 GUI (oracle/gpower_gui_vectors.csv)", ""]
    if gui:
        ok = sum(r[1] for r in gui)
        lines += [f"- Vectors with recorded G*Power values: **{len(gui)}**",
                  f"- Full match: **{ok}/{len(gui)}** ({100 * ok / len(gui):.1f}%)", "",
                  "| id | match | expected | got |", "|---|---|---|---|"]
        lines += [f"| {i} | {'yes' if m else '**NO**'} | `{e}` | `{g}` |" for i, m, e, g in gui]
    else:
        lines.append("_No G*Power GUI values recorded yet. Fill the exp_* columns from the GUI._")
    (ROOT / "tests" / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"statsmodels: N {n_match}/{total}, power {p_match}/{total}; GUI rows: {len(gui)}")


if __name__ == "__main__":
    main()
