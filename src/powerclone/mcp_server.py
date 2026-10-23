"""MCP server exposing one tool, `power_analysis`, over stdio.

Thin adapter: it forwards the fields to engine.run() and returns the same
one-line JSON the CLI prints. No statistics here.
"""

from __future__ import annotations

import json

try:  # mcp >= 2
    from mcp.server.mcpserver import MCPServer as _Server
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _Server

from . import engine

mcp = _Server("powerclone")


def respond(params: dict) -> str:
    """Same payload as the CLI's stdout, minus the trailing newline."""
    clean = {k: v for k, v in params.items() if v is not None}
    try:
        payload = engine.run(clean)
    except engine.EngineError as err:
        payload = err.to_dict()
    return json.dumps(payload, ensure_ascii=False)


@mcp.tool()
def power_analysis(
    test: str,
    mode: str,
    w: float | None = None,
    alpha: float | None = None,
    power: float | None = None,
    df: int | None = None,
    n_total: int | None = None,
    beta_alpha_ratio: float | None = None,
) -> str:
    """Chi-square contingency-table power analysis (test="chi2-contingency").

    Modes and required fields:
      a-priori:    w, alpha, power, df       -> ncp, critical_chi2, n_total, actual_power
      post-hoc:    w, alpha, n_total, df     -> ncp, critical_chi2, power
      compromise:  w, beta_alpha_ratio, n_total, df -> ncp, critical_chi2, alpha, beta, power
      criterion:   w, power, n_total, df     -> ncp, critical_chi2, alpha
      sensitivity: alpha, power, n_total, df -> ncp, critical_chi2, w
    df = (rows-1)*(columns-1). w is Cohen's effect size (0.1 small, 0.3 medium, 0.5 large).
    Returns one-line JSON; on bad input {"error","code","field"}.
    """
    return respond({"test": test, "mode": mode, "w": w, "alpha": alpha, "power": power,
                    "df": df, "n_total": n_total, "beta_alpha_ratio": beta_alpha_ratio})


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
