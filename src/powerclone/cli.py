"""`gpower-clone` command-line entry point (thin layer over engine.run)."""

from __future__ import annotations

import json
import platform
import sys

from . import engine

TEAM_NAME = "powerclone-chi2"


def parse_args(argv: list[str]) -> dict:
    """Parse `--field value` pairs. Raises EngineError on malformed input."""
    params: dict = {}
    i = 0
    while i < len(argv):
        token = argv[i]
        if not token.startswith("--") or len(token) == 2:
            raise engine.EngineError(f"unexpected argument: {token}", "INVALID_VALUE", None)
        key = token[2:]
        if "=" in key:
            key, value = key.split("=", 1)
            i += 1
        else:
            if i + 1 >= len(argv):
                raise engine.EngineError(f"missing value for --{key}", "MISSING_PARAM", key)
            value = argv[i + 1]
            i += 2
        # unknown fields are rejected by engine.run, after test/mode are checked
        if key in params:
            raise engine.EngineError(f"duplicate field: {key}", "INVALID_VALUE", key)
        params[key] = value
    return params


def execute(argv: list[str]) -> tuple[dict, int]:
    """Return (json_payload, exit_code). Shared by the CLI and its tests."""
    if argv == ["--version"]:
        return ({"contract_version": engine.CONTRACT_VERSION, "name": TEAM_NAME,
                 "engine": f"Python {platform.python_version()} + SciPy"}, 0)
    try:
        return engine.run(parse_args(argv)), 0
    except engine.EngineError as err:
        return err.to_dict(), err.exit_code
    except Exception as exc:  # internal failure, never a traceback on stdout
        print(repr(exc), file=sys.stderr)
        return {"error": f"internal error: {exc}", "code": "NO_SOLUTION", "field": None}, 1


def main() -> None:
    payload, code = execute(sys.argv[1:])
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.exit(code)


if __name__ == "__main__":
    main()
