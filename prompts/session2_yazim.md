# Oturum 2 — Yazım (temiz oda)

Bu oturum yalnızca `cleanroom` dalında çalıştı. O dalda yalnızca şu dosyalar var:
`SPEC.md`, `CONTRACT.md`, `tests/public_vectors.jsonl`, `oracle/gpower_gui_vectors.csv`
(G*Power arayüzünden toplanmış girdi/çıktı çiftleri — kara kutu gözlem, decompile değil).
LEDGER.md, rea/ ve önceki kod bu dalda yok; oturum Ghidra/disassembly çıktısı görmedi.

Oturuma verilen ilk prompt (birebir):

```
You are SESSION 2 (clean-room writer) of a university reverse-engineering assignment.
You may read ONLY the files in this worktree: SPEC.md, CONTRACT.md, tests/public_vectors.jsonl,
oracle/gpower_gui_vectors.csv. Do not run git commands that read other branches (no git log --all,
git show <other-branch>, git checkout of other branches) and do not read anything outside this
worktree. You have never seen and must not look for decompiled or disassembled code.

Task: implement SPEC.md in Python (SciPy allowed for distribution functions) exactly per
CONTRACT.md for the test family chi2-contingency, all five modes.
Architecture (mandatory): one engine module that holds ALL calculation logic
(src/powerclone/engine.py, function run(params: dict) -> dict raising an error type with
code/field/exit_code); thin layers that only call it:
  - src/powerclone/cli.py  -> console script `gpower-clone` (CONTRACT section 2)
  - src/powerclone/mcp_server.py -> MCP stdio server with one tool `power_analysis`
    (CONTRACT section 7; support mcp>=2 `mcp.server.mcpserver.MCPServer` and mcp 1.x FastMCP)
  - src/powerclone/agent.py -> Turkish clinical agent using the Anthropic SDK that only picks
    parameters and calls the MCP tool; it never computes numbers; logs every tool call to
    logs/agent_calls.jsonl (CONTRACT section 8). Model id from env POWERCLONE_MODEL,
    default "claude-sonnet-5-5".
  - pyproject.toml with package name powerclone-chi2, scripts gpower-clone and powerclone-mcp.
Test-first: before writing the engine, write pytest tests from every Gherkin scenario in SPEC.md,
from the chi2 rows of tests/public_vectors.jsonl, and from every row of
oracle/gpower_gui_vectors.csv (exp_* columns are G*Power's displayed values; compare integers
exactly, decimals within 1e-6 abs or rel, error rows must produce an error; rows SPEC.md lists
as deliberate contract divergences must produce the contract error instead). Also a test that
the CLI and MCP outputs are byte-identical for the same inputs.
Done = all tests pass. Then write a short CLEANROOM_NOTES.md: what in SPEC.md was ambiguous,
what you had to decide, iterations and approximate tokens. Commit on this branch; do not push.
```
