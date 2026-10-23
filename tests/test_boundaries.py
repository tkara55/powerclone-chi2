"""Boundary values and invalid inputs (assignment section d)."""

import pytest

from powerclone import cli, engine


def run(argv):
    return cli.execute(argv)


BASE = ["--test", "chi2-contingency", "--mode", "a-priori"]


@pytest.mark.parametrize("argv, code, field", [
    (BASE + ["--alpha", "0.05", "--power", "0.95", "--df", "5"], "MISSING_PARAM", "w"),
    (BASE + ["--w", "0.3", "--alpha", "0.05", "--power", "0.95", "--df", "5", "--n_total", "50"], "UNKNOWN_PARAM", "n_total"),
    (BASE + ["--w", "0.3", "--alpha", "0.05", "--power", "0.95", "--df", "5", "--d", "0.5"], "UNKNOWN_PARAM", "d"),
    (BASE + ["--w", "abc", "--alpha", "0.05", "--power", "0.95", "--df", "5"], "INVALID_VALUE", "w"),
    (BASE + ["--w", "0.3", "--alpha", "0.05", "--power", "0.95", "--df", "2.5"], "INVALID_VALUE", "df"),
    (BASE + ["--w", "0", "--alpha", "0.05", "--power", "0.95", "--df", "5"], "OUT_OF_RANGE", "w"),
    (BASE + ["--w", "-0.3", "--alpha", "0.05", "--power", "0.95", "--df", "5"], "OUT_OF_RANGE", "w"),
    (BASE + ["--w", "0.3", "--alpha", "1", "--power", "0.95", "--df", "5"], "OUT_OF_RANGE", "alpha"),
    (BASE + ["--w", "0.3", "--alpha", "0.05", "--power", "0.95", "--df", "0"], "OUT_OF_RANGE", "df"),
    (BASE + ["--w", "0.3", "--alpha", "0.05", "--power", "0.05", "--df", "5"], "INCONSISTENT", "power"),
    (BASE + ["--w", "0.3", "--alpha", "0.05", "--power", "0.01", "--df", "5"], "INCONSISTENT", "power"),
    (["--test", "t2-indep", "--mode", "a-priori"], "UNSUPPORTED", "test"),
    (["--test", "chi2-contingency", "--mode", "magic"], "UNSUPPORTED", "mode"),
    (["--test", "chi2-contingency", "--mode", "post-hoc", "--w", "0.3", "--alpha", "0.05", "--n_total", "1", "--df", "1"], "OUT_OF_RANGE", "n_total"),
])
def test_invalid(argv, code, field):
    payload, exit_code = run(argv)
    assert exit_code == 2
    assert payload["code"] == code and payload["field"] == field and payload["error"]


def test_tiny_effect_is_large_but_finite():
    payload, code = run(BASE + ["--w", "0.01", "--alpha", "0.05", "--power", "0.95", "--df", "1"])
    assert code == 0 and payload["n_total"] > 100_000
    assert payload["actual_power"] >= 0.95


def test_huge_effect_hits_minimum_n():
    payload, code = run(BASE + ["--w", "5", "--alpha", "0.05", "--power", "0.8", "--df", "1"])
    assert code == 0 and payload["n_total"] == engine.N_MIN


def test_a_priori_n_is_minimal():
    payload, _ = run(BASE + ["--w", "0.3", "--alpha", "0.05", "--power", "0.95", "--df", "5"])
    n = payload["n_total"]
    assert engine.power_for_n(0.3, 0.05, 5, n - 1) < 0.95 <= engine.power_for_n(0.3, 0.05, 5, n)


def test_deterministic():
    argv = BASE + ["--w", "0.17", "--alpha", "0.01", "--power", "0.9", "--df", "3"]
    assert run(argv) == run(argv)


def test_integer_fields_are_json_ints():
    payload, _ = run(BASE + ["--w", "0.3", "--alpha", "0.05", "--power", "0.95", "--df", "5"])
    assert type(payload["n_total"]) is int
