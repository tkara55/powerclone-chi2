"""Turkish-language clinical agent that answers sample-size questions via MCP.

The LLM only maps the researcher's words to tool parameters. Every number
(N, power, critical value) comes from the `power_analysis` MCP tool, which
calls the engine. Each tool call is appended to logs/agent_calls.jsonl.

Usage:
    set ANTHROPIC_API_KEY=...
    python -m powerclone.agent "Iki tedavi kolunda yanit orani farki icin kac hasta gerekir? ..."
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MODEL = os.environ.get("POWERCLONE_MODEL", "claude-sonnet-5-5")
LOG_PATH = Path(os.environ.get("POWERCLONE_LOG", "logs/agent_calls.jsonl"))

SYSTEM = """Sen klinik araştırmacılara örneklem büyüklüğü konusunda yardım eden bir asistansın.
Kurallar:
- Hiçbir sayıyı (N, güç, kritik değer, etki büyüklüğü) kendin HESAPLAMA. Her sayı power_analysis aracından gelir.
- Yalnızca χ² olumsallık tablosu / uyum iyiliği testlerini (test="chi2-contingency") destekliyorsun.
  t testi, ANOVA, regresyon gibi başka bir test gerekiyorsa bunu açıkça söyle ve aracı çağırma.
- df = (satır sayısı - 1) × (sütun sayısı - 1). Örn. 2 grup × 2 sonuç (yanıt var/yok) → df = 1; 3 kol × 2 sonuç → df = 2.
- Mod seçimi: "kaç hasta/denek gerekir" → a-priori; "elimde N hasta var, gücüm ne" → post-hoc.
- Etki büyüklüğü w: kullanıcı yalnızca "küçük/orta/büyük" derse Cohen eşiklerini (0.1/0.3/0.5) kullan ama
  bu varsayımı yanıtında AÇIKÇA belirt. Hiç etki büyüklüğü bilgisi yoksa uydurma; kullanıcıya sor.
- Kullanıcı alfa/güç belirtmezse alpha=0.05, power=0.80 varsay ve bunu açıkça söyle.
- Yanıtı Türkçe, kısa ver: kullanılan test, parametreler, aracın döndürdüğü sonuç ve varsayımlar.
"""


def _log(entry: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


async def ask(question: str, client: Anthropic | None = None) -> dict:
    """Answer one question. Returns {"answer", "tool_calls", "tokens_in", "tokens_out"}."""
    client = client or Anthropic()
    params = StdioServerParameters(command=sys.executable, args=["-m", "powerclone.mcp_server"])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as session:
            await session.initialize()
            listed = await session.list_tools()
            tools = [{"name": t.name, "description": t.description or "",
                      "input_schema": t.inputSchema} for t in listed.tools]

            messages = [{"role": "user", "content": question}]
            calls, tok_in, tok_out = [], 0, 0
            for _ in range(6):
                resp = client.messages.create(model=MODEL, max_tokens=1024, system=SYSTEM,
                                              tools=tools, messages=messages)
                tok_in += resp.usage.input_tokens
                tok_out += resp.usage.output_tokens
                messages.append({"role": "assistant", "content": resp.content})
                uses = [b for b in resp.content if b.type == "tool_use"]
                if not uses:
                    text = "".join(b.text for b in resp.content if b.type == "text")
                    return {"answer": text, "tool_calls": calls,
                            "tokens_in": tok_in, "tokens_out": tok_out}
                results = []
                for use in uses:
                    res = await session.call_tool(use.name, use.input)
                    out_text = res.content[0].text
                    try:
                        out = json.loads(out_text)
                    except json.JSONDecodeError:
                        out = {"raw": out_text}
                    calls.append({"tool_input": use.input, "tool_output": out})
                    _log({"ts": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
                          "question": question, "tool_input": use.input, "tool_output": out,
                          "tokens_in": resp.usage.input_tokens, "tokens_out": resp.usage.output_tokens})
                    results.append({"type": "tool_result", "tool_use_id": use.id, "content": out_text})
                messages.append({"role": "user", "content": results})
            return {"answer": "(durdu: çok fazla adım)", "tool_calls": calls,
                    "tokens_in": tok_in, "tokens_out": tok_out}


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: python -m powerclone.agent \"<soru>\"", file=sys.stderr)
        sys.exit(2)
    result = asyncio.run(ask(" ".join(sys.argv[1:])))
    print(result["answer"])
    print(f"\n[tokens in={result['tokens_in']} out={result['tokens_out']}, "
          f"tool calls={len(result['tool_calls'])}]", file=sys.stderr)


if __name__ == "__main__":
    main()
