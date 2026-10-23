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
    (BASE + ["--w", "0.3", "--alpha", "0.05", "--power", "0.04", "--df", "5"], "INCONSISTENT", "power"),
    (BASE + ["--w", "0.3", "--alpha", "0.05", "--power", "0.01", "--df", "5"], "INCONSISTENT", "power"),
    (BASE + ["--w", "0.0000009", "--alpha", "0.05", "--power", "0.8", "--df", "1"], "OUT_OF_RANGE", "w"),
    (["--test", "t2-indep", "--mode", "a-priori"], "UNSUPPORTED", "test"),
    (["--test", "chi2-contingency", "--mode", "magic"], "UNSUPPORTED", "mode"),
    (["--test", "chi2-contingency", "--mode", "post-hoc", "--w", "0.3", "--alpha", "0.05", "--n_total", "1", "--df", "1"], "OUT_OF_RANGE", "n_total"),
])
def test_invalid(argv, code, field):
    payload, exit_code = run(argv)
    assert exit_code == 2
    assert payload["code"] == code and payload["field"] == field and payload["error"]


PH = ["--test", "chi2-contingency", "--mode", "post-hoc"]
CP = ["--test", "chi2-contingency", "--mode", "compromise"]


@pytest.mark.parametrize("argv, field", [
    # REA R-06/R-07 + GUI g39, g41: alpha and power must lie in [1e-7, 0.9999999]
    (PH + ["--w", "0.3", "--alpha", "0.00000001", "--n_total", "100", "--df", "1"], "alpha"),
    (BASE + ["--w", "0.3", "--alpha", "0.05", "--power", "0.99999995", "--df", "1"], "power"),
    # REA R-09 + GUI g42: beta/alpha ratio in [0.01, 100]
    (CP + ["--w", "0.3", "--beta_alpha_ratio", "0.005", "--n_total", "100", "--df", "5"], "beta_alpha_ratio"),
    # REA R-10 + GUI g44: df is checked before w
    (BASE + ["--w", "0", "--alpha", "0.05", "--power", "0.8", "--df", "0"], "df"),
])
def test_gpower_admissible_ranges(argv, field):
    payload, code = run(argv)
    assert code == 2 and payload["code"] == "OUT_OF_RANGE" and payload["field"] == field


@pytest.mark.parametrize("argv", [
    PH + ["--w", "0.3", "--alpha", "0.0000001", "--n_total", "100", "--df", "1"],      # g40
    CP + ["--w", "0.3", "--beta_alpha_ratio", "100", "--n_total", "100", "--df", "5"],  # g43
    PH + ["--w", "0.0000005", "--alpha", "0.05", "--n_total", "100", "--df", "1"],     # g37: no 1e-6 floor in post-hoc
])
def test_gpower_admissible_edges_accepted(argv):
    assert run(argv)[1] == 0


def test_no_n_ceiling():
    # GUI g35: w = 1e-6 -> N = 7.8489e+12
    payload, code = run(BASE + ["--w", "0.000001", "--alpha", "0.05", "--power", "0.8", "--df", "1"])
    assert code == 0 and abs(payload["n_total"] - 7.8489e12) <= 5e-5 * 7.8489e12


def test_tiny_effect_is_large_but_finite():
    payload, code = run(BASE + ["--w", "0.01", "--alpha", "0.05", "--power", "0.95", "--df", "1"])
    assert code == 0 and payload["n_total"] > 100_000
    assert payload["actual_power"] >= 0.95


def test_huge_effect_hits_minimum_n():
    # G*Power GUI vector g08: w=5 -> N=1
    payload, code = run(BASE + ["--w", "5", "--alpha", "0.05", "--power", "0.95", "--df", "1"])
    assert code == 0 and payload["n_total"] == 1


def test_power_equal_alpha_is_accepted():
    # G*Power GUI vector g09: power == alpha -> N=1, no error
    payload, code = run(BASE + ["--w", "0.3", "--alpha", "0.05", "--power", "0.05", "--df", "5"])
    assert code == 0 and payload["n_total"] == 1


def test_w_exactly_1e6_is_accepted():
    # G*Power GUI vector g32
    payload, code = run(["--test", "chi2-contingency", "--mode", "post-hoc", "--w", "0.000001",
                         "--alpha", "0.05", "--n_total", "100", "--df", "1"])
    assert code == 0


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
