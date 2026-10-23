"""The instructor's published chi2 vectors (CONTRACT.md section 9), run through the real CLI."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

VECTORS = [json.loads(l) for l in (Path(__file__).parent / "public_vectors.jsonl").read_text().splitlines() if l]
CHI2 = [v for v in VECTORS if v["input"]["test"] == "chi2-contingency"]
INT_FIELDS = {"n1", "n2", "n_total", "df", "df1", "df2"}


def cli(inp: dict) -> tuple[dict, int]:
    args = [sys.executable, "-m", "powerclone.cli"]
    for k, v in inp.items():
        args += [f"--{k}", str(v)]
    p = subprocess.run(args, capture_output=True, text=True, timeout=10)
    return json.loads(p.stdout), p.returncode


def assert_matches(got: dict, expected: dict) -> None:
    for field, exp in expected.items():
        assert field in got, f"missing {field}"
        if field in INT_FIELDS:
            assert got[field] == exp and isinstance(got[field], int), field
        else:
            # G*Power shows 7 decimals; contract tolerance is 1e-6 abs or rel
            assert abs(got[field] - exp) <= 1e-6 or abs(got[field] - exp) <= 1e-6 * abs(exp), field


@pytest.mark.parametrize("vec", CHI2, ids=[v["id"] for v in CHI2])
def test_public_chi2(vec):
    got, code = cli(vec["input"])
    assert code == 0, got
    assert_matches(got, vec["expected"])


@pytest.mark.parametrize("vec", [v for v in VECTORS if v not in CHI2], ids=lambda v: v["id"])
def test_other_families_unsupported(vec):
    got, code = cli(vec["input"])
    assert code == 2 and got["code"] == "UNSUPPORTED"
