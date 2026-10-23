"""Run the 10-question evaluation set through the agent and score it.

Expected N values come from the engine (and should be cross-checked in the
G*Power GUI). A question counts as correct when:
  - chi2 questions: the agent made a call whose test/mode/df match and whose
    numeric output N (or power) equals the expected engine result;
  - unsupported / ambiguous: the agent made no tool call.

Usage: python -I agent_eval/run_eval.py   (needs ANTHROPIC_API_KEY)
Writes agent_eval/RESULTS.md.
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

from powerclone import agent, engine

HERE = Path(__file__).resolve().parent


def expected_output(exp: dict) -> dict | None:
    if exp["label"] != "chi2-contingency":
        return None
    return engine.run({"test": "chi2-contingency", **exp["input"]})


def score(exp: dict, calls: list[dict]) -> bool:
    if exp["label"] != "chi2-contingency":
        return not calls
    want = expected_output(exp)
    for c in calls:
        inp, out = c["tool_input"], c["tool_output"]
        if inp.get("test") != "chi2-contingency" or inp.get("mode") != exp["input"]["mode"]:
            continue
        if int(inp.get("df", -1)) != exp["input"]["df"]:
            continue
        key = "n_total" if exp["input"]["mode"] == "a-priori" else "power"
        if key in out and abs(out[key] - want[key]) < 1e-9:
            return True
    return False


async def main():
    rows = [json.loads(l) for l in (HERE / "questions.jsonl").read_text(encoding="utf-8").splitlines() if l]
    results, tin, tout, secs = [], 0, 0, 0.0
    for row in rows:
        t0 = time.perf_counter()
        res = await agent.ask(row["question"])
        dt = time.perf_counter() - t0
        ok = score(row["expected"], res["tool_calls"])
        results.append((row, res, ok, dt))
        tin += res["tokens_in"]
        tout += res["tokens_out"]
        secs += dt
    correct = sum(r[2] for r in results)
    lines = ["# Agent evaluation (MCP path)", "",
             f"- Model: `{agent.MODEL}`",
             f"- Correct selection + result: **{correct}/{len(results)}**",
             f"- Tokens: in {tin}, out {tout}; wall time {secs:.1f} s", "",
             "| id | expected | ok | tool calls | tokens in/out | s |", "|---|---|---|---|---|---|"]
    for row, res, ok, dt in results:
        exp = row["expected"]
        lines.append(f"| {row['id']} | {exp['label']} {exp.get('input', '')} | {'yes' if ok else '**NO**'} "
                     f"| {len(res['tool_calls'])} | {res['tokens_in']}/{res['tokens_out']} | {dt:.1f} |")
    (HERE / "RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{correct}/{len(results)} correct")


if __name__ == "__main__":
    asyncio.run(main())
