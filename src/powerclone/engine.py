"""Calculation engine for the chi-square contingency-table family.

All statistics live here. The CLI, MCP server and agent are thin layers
that validate input, call `run()` and serialise the result.

Model (see SPEC.md):
    lambda (ncp)   = w^2 * N
    critical chi2  = chi2.ppf(1 - alpha, df)
    power          = 1 - ncx2.cdf(critical, df, lambda)
"""

from __future__ import annotations

import math

from scipy import optimize, stats

CONTRACT_VERSION = "1.0.0"
TEST_ID = "chi2-contingency"
N_MIN = 1           # smallest N searched in a-priori mode (GUI: w=5 gives N=1)
W_MIN = 1e-6        # GUI rejects w below 1e-6 but accepts exactly 1e-6
N_MAX = 10_000_000  # upper search bound; beyond this we report NO_SOLUTION

# Inputs required per mode (contract section 4.4). No defaults.
MODE_FIELDS = {
    "a-priori": ("w", "alpha", "power", "df"),
    "post-hoc": ("w", "alpha", "n_total", "df"),
    "compromise": ("w", "beta_alpha_ratio", "n_total", "df"),
    "criterion": ("w", "power", "n_total", "df"),
    "sensitivity": ("alpha", "power", "n_total", "df"),
}
INT_FIELDS = {"n_total", "df"}
FLOAT_FIELDS = {"w", "alpha", "power", "beta_alpha_ratio"}
ALL_FIELDS = INT_FIELDS | FLOAT_FIELDS


class EngineError(Exception):
    """Error in the contract's {"error","code","field"} shape."""

    def __init__(self, message: str, code: str, field: str | None = None, exit_code: int = 2):
        super().__init__(message)
        self.code = code
        self.field = field
        self.exit_code = exit_code

    def to_dict(self) -> dict:
        return {"error": str(self), "code": self.code, "field": self.field}


# --- primitives -------------------------------------------------------------

def critical_chi2(alpha: float, df: int) -> float:
    return float(stats.chi2.isf(alpha, df))


def power_at(crit: float, df: int, ncp: float) -> float:
    return float(stats.ncx2.sf(crit, df, ncp))


def power_for_n(w: float, alpha: float, df: int, n: int) -> float:
    return power_at(critical_chi2(alpha, df), df, w * w * n)


# --- modes ------------------------------------------------------------------

def a_priori(w: float, alpha: float, power: float, df: int) -> dict:
    """Smallest integer N whose power reaches the target (N is rounded UP)."""
    crit = critical_chi2(alpha, df)

    def reaches(n: int) -> bool:
        return power_at(crit, df, w * w * n) >= power

    lo, hi = N_MIN, N_MIN
    if not reaches(lo):
        while not reaches(hi):
            lo = hi
            hi *= 2
            if hi > N_MAX:
                raise EngineError("Required N exceeds search limit", "NO_SOLUTION", "power", 1)
        # invariant: reaches(hi) and not reaches(lo)
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if reaches(mid):
                hi = mid
            else:
                lo = mid
    n = hi
    ncp = w * w * n
    return {"ncp": ncp, "critical_chi2": crit, "n_total": n,
            "actual_power": power_at(crit, df, ncp)}


def post_hoc(w: float, alpha: float, n_total: int, df: int) -> dict:
    crit = critical_chi2(alpha, df)
    ncp = w * w * n_total
    return {"ncp": ncp, "critical_chi2": crit, "power": power_at(crit, df, ncp)}


def compromise(w: float, beta_alpha_ratio: float, n_total: int, df: int) -> dict:
    """Find critical c with beta(c) = q * alpha(c); beta - q*alpha is increasing in c."""
    ncp = w * w * n_total
    q = beta_alpha_ratio

    def g(c: float) -> float:
        return stats.ncx2.cdf(c, df, ncp) - q * stats.chi2.sf(c, df)

    hi = max(1.0, df + ncp)
    while g(hi) < 0:
        hi *= 2
    crit = optimize.brentq(g, 0.0, hi, xtol=1e-14, rtol=1e-15, maxiter=500)
    alpha = float(stats.chi2.sf(crit, df))
    beta = float(stats.ncx2.cdf(crit, df, ncp))
    return {"ncp": ncp, "critical_chi2": float(crit), "alpha": alpha,
            "beta": beta, "power": 1.0 - beta}


def criterion(w: float, power: float, n_total: int, df: int) -> dict:
    ncp = w * w * n_total
    crit = float(stats.ncx2.isf(power, df, ncp))
    return {"ncp": ncp, "critical_chi2": crit, "alpha": float(stats.chi2.sf(crit, df))}


def sensitivity(alpha: float, power: float, n_total: int, df: int) -> dict:
    crit = critical_chi2(alpha, df)

    def g(lam: float) -> float:
        return power_at(crit, df, lam) - power

    hi = 1.0
    while g(hi) < 0:
        hi *= 2
    ncp = optimize.brentq(g, 0.0, hi, xtol=1e-14, rtol=1e-15, maxiter=500)
    return {"ncp": float(ncp), "critical_chi2": crit, "w": math.sqrt(ncp / n_total)}


SOLVERS = {
    "a-priori": a_priori,
    "post-hoc": post_hoc,
    "compromise": compromise,
    "criterion": criterion,
    "sensitivity": sensitivity,
}


# --- validation + dispatch --------------------------------------------------

def _coerce(field: str, raw) -> float | int:
    if isinstance(raw, bool):
        raise EngineError(f"{field} must be a number", "INVALID_VALUE", field)
    if field in INT_FIELDS:
        if isinstance(raw, int):
            return raw
        if isinstance(raw, float):
            if raw.is_integer():
                return int(raw)
            raise EngineError(f"{field} must be an integer", "INVALID_VALUE", field)
        text = str(raw).strip()
        try:
            return int(text)
        except ValueError:
            raise EngineError(f"{field} must be an integer", "INVALID_VALUE", field) from None
    try:
        value = float(str(raw).strip()) if not isinstance(raw, (int, float)) else float(raw)
    except ValueError:
        raise EngineError(f"{field} must be a number", "INVALID_VALUE", field) from None
    if not math.isfinite(value):
        raise EngineError(f"{field} must be finite", "INVALID_VALUE", field)
    return value


def _check_range(field: str, v) -> None:
    ok = {
        "w": v > 0,
        "alpha": 0 < v < 1,
        "power": 0 < v < 1,
        "beta_alpha_ratio": v > 0,
        "n_total": v >= 2,
        "df": v >= 1,
    }[field]
    if not ok:
        raise EngineError(f"{field} out of range: {v}", "OUT_OF_RANGE", field)


def run(params: dict) -> dict:
    """Validate a contract-shaped dict and compute. Raises EngineError."""
    params = dict(params)
    test = params.pop("test", None)
    mode = params.pop("mode", None)
    if test is None:
        raise EngineError("test is required", "MISSING_PARAM", "test")
    if mode is None:
        raise EngineError("mode is required", "MISSING_PARAM", "mode")
    if test != TEST_ID:
        raise EngineError(f"unsupported test: {test}", "UNSUPPORTED", "test")
    if mode not in MODE_FIELDS:
        raise EngineError(f"unsupported mode: {mode}", "UNSUPPORTED", "mode")

    required = MODE_FIELDS[mode]
    for field in params:
        if field not in required:
            raise EngineError(f"unknown or irrelevant field for {mode}: {field}",
                              "UNKNOWN_PARAM", field)
    for field in required:
        if field not in params or params[field] is None:
            raise EngineError(f"{field} is required for {mode}", "MISSING_PARAM", field)

    values = {f: _coerce(f, params[f]) for f in required}
    for f, v in values.items():
        _check_range(f, v)

    if "w" in values and values["w"] < W_MIN:
        raise EngineError("Effect size w must be at least 1e-06", "OUT_OF_RANGE", "w")
    # GUI: power == alpha is accepted, only power < alpha is an input error
    if "alpha" in values and "power" in values and values["power"] < values["alpha"]:
        raise EngineError("Power must be greater than or equal to alpha", "INCONSISTENT", "power")

    try:
        return SOLVERS[mode](**values)
    except EngineError:
        raise
    except (ValueError, ArithmeticError, RuntimeError) as exc:
        raise EngineError(f"calculation failed: {exc}", "NO_SOLUTION", None, 1) from exc
