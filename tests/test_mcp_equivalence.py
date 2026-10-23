"""CLI and MCP must return identical JSON for the same input (contract section 7).

Runs the 25 public vectors plus error cases through the real CLI process and
through a real MCP stdio session.
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

VECTORS = [json.loads(l)["input"] for l in (Path(__file__).parent / "public_vectors.jsonl").read_text().splitlines() if l]
EXTRA = [
    {"test": "chi2-contingency", "mode": "a-priori", "w": 0.1, "alpha": 0.01, "power": 0.8, "df": 3},
    {"test": "chi2-contingency", "mode": "a-priori", "w": 0.3, "alpha": 0.05, "power": 0.05, "df": 5},
    {"test": "chi2-contingency", "mode": "post-hoc", "w": 0.3, "alpha": 0.05, "df": 5},
    {"test": "chi2-contingency", "mode": "post-hoc", "w": -1, "alpha": 0.05, "n_total": 50, "df": 5},
]
CASES = VECTORS + EXTRA


def cli_out(inp):
    args = [sys.executable, "-m", "powerclone.cli"]
    for k, v in inp.items():
        args += [f"--{k}", str(v)]
    return subprocess.run(args, capture_output=True, text=True, timeout=10).stdout.strip()


async def mcp_outs(cases):
    params = StdioServerParameters(command=sys.executable, args=["-m", "powerclone.mcp_server"])
    outs = []
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as session:
            await session.initialize()
            for inp in cases:
                # the MCP tool only declares chi2 fields; drop others like the agent would
                allowed = {"test", "mode", "w", "alpha", "power", "df", "n_total", "beta_alpha_ratio"}
                res = await session.call_tool("power_analysis", {k: v for k, v in inp.items() if k in allowed})
                outs.append(res.content[0].text)
    return outs


def test_cli_equals_mcp():
    mcp = asyncio.run(mcp_outs(CASES))
    for inp, m in zip(CASES, mcp):
        c = cli_out(inp)
        if inp["test"] != "chi2-contingency":
            # both must refuse the family the same way
            assert json.loads(c)["code"] == json.loads(m)["code"] == "UNSUPPORTED"
        else:
            assert c == m, (inp, c, m)
