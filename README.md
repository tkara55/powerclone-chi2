# powerclone-chi2 — χ² olumsallık tablosu güç analizi (YZM301 Teardown Sprint)

**Yapılan katmanlar:** ✅ Temel (CLI) · ✅ MCP sunucusu · ✅ AI ajanı (kod hazır; değerlendirme `ANTHROPIC_API_KEY` ile çalıştırılmalı)

**Test ailesi:** 4) χ² testi, olumsallık tablosu (yanıt oranları) — `chi2-contingency`, 5 modun hepsi.

> Bu araç G*Power **değildir** ve onun yerine sunulmaz. G*Power'ın davranışını referans alan,
> yayımlanmış yöntemlerden bağımsız olarak yazılmış bir eğitim çalışmasıdır.

## Atıf

G*Power: Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007). G*Power 3: A flexible statistical
power analysis program for the social, behavioral, and biomedical sciences. *Behavior Research Methods, 39*, 175–191.
Faul, F., Erdfelder, E., Buchner, A., & Lang, A.-G. (2009). Statistical power analyses using G*Power 3.1:
Tests for correlation and regression analyses. *Behavior Research Methods, 41*, 1149–1160.

## Sürüm bilgisi

| | |
|---|---|
| Referans | G*Power 3.1.9.7 (Windows), psychologie.hhu.de |
| GPowerNT.exe SHA-256 | `C63E6A133EB6372932F810C08CC33DC35A06D1DDB658F897BD6C34A754EFC812` |
| GPowerWin_3.1.9.7.zip SHA-256 | `3BB7F1F2478D74EE5BA701AE7F849373CF2B8A11F6B6216C7C6B236DB7861199` |
| Sözleşme | CONTRACT.md 1.0.0 |
| Motor | Python ≥ 3.10, SciPy |
| Demo videosu | `<doldurulacak: 60 sn CLI videosu linki>` |

## Kurulum ve çalıştırma

```bash
pip install -e ".[dev,agent]"
```

```bash
gpower-clone --test chi2-contingency --mode a-priori --w 0.3 --alpha 0.05 --power 0.95 --df 5
```

```json
{"ncp": 19.8, "critical_chi2": 11.070497693516355, "n_total": 220, "actual_power": 0.9502155018970162}
```

Diğer modlar:

```bash
gpower-clone --test chi2-contingency --mode post-hoc --w 0.3 --alpha 0.05 --n_total 100 --df 5
```

## Mimari

```
src/powerclone/engine.py      ← TÜM hesap burada (tek motor)
src/powerclone/cli.py         ← ince katman: argüman → engine.run → JSON
src/powerclone/mcp_server.py  ← ince katman: MCP aracı → engine.run → aynı JSON
src/powerclone/agent.py       ← LLM yalnızca parametre seçer, MCP aracını çağırır; sayı üretmez
```

## Testler

```bash
python -m pytest -q
```

```bash
python -I tests/differential.py
```

- `tests/test_public_vectors.py` — CONTRACT §9'daki 5 χ² vektörü (5/5 eşleşiyor), diğer aileler `UNSUPPORTED`.
- `tests/test_boundaries.py` — geçersiz girdiler, güç ≤ α, çok küçük/büyük w, N'nin minimal olması.
- `tests/test_mcp_equivalence.py` — 25 açık vektör + hata vakaları için CLI çıktısı == MCP çıktısı.
- `tests/differential.py` → `tests/REPORT.md` — statsmodels ile 799 vektör (N: 799/799 ceil eşleşmesi) ve G*Power GUI vektörleri.

## Kâhin (oracle/)

- `oracle/gpower_gui_vectors.csv` — G*Power 3.1.9.7 arayüzünden toplanmış 34 vektör (sınır değerler ve
  hata mesajları dahil); her satırın ekran görüntüsü `oracle/screenshots/<id>.png`. Uyum: **33/34**
  (tek fark sözleşmeden kaynaklı, LEDGER L-17).
- `oracle/collect_gui.py` — vektörleri toplayan betik: açık G*Power penceresini Win32 mesajlarıyla sürer
  (fare yok), çıktıları ekranda gösterildiği gibi okur, pencereyi PrintWindow ile yakalar.
- `oracle/statsmodels_vectors.csv` — ölçek için 799 vektör.

## MCP sunucusu

```bash
powerclone-mcp
```

Claude Desktop / Claude Code yapılandırması:

```json
{"mcpServers": {"powerclone": {"command": "python", "args": ["-m", "powerclone.mcp_server"]}}}
```

### Araç şeması: `power_analysis`

| Alan | Tür | Zorunlu | Not |
|---|---|---|---|
| `test` | string | evet | `"chi2-contingency"` |
| `mode` | string | evet | `a-priori`, `post-hoc`, `compromise`, `criterion`, `sensitivity` |
| `w` | number | moda göre | etki büyüklüğü (> 0) |
| `alpha` | number | moda göre | 0 < α < 1 |
| `power` | number | moda göre | 0 < güç < 1 |
| `df` | integer | evet | ≥ 1, (satır−1)(sütun−1) |
| `n_total` | integer | moda göre | ≥ 2 |
| `beta_alpha_ratio` | number | compromise | > 0 |

Çıktı: CLI stdout'u ile aynı tek satırlık JSON (metin içeriği). Hata: `{"error","code","field"}`.

## AI ajanı

```bash
python -m powerclone.agent "İki tedavide iyileşme oranlarını karşılaştıracağım, w=0.3, güç %80. Kaç hasta?"
```

```bash
python -I agent_eval/run_eval.py
```

- Model: `claude-sonnet-5-5` (`POWERCLONE_MODEL` ile değiştirilebilir). Jev kullanılmadı; aile seçimi
  sistem prompt'uyla `chi2-contingency` / desteklenmeyen / belirsiz ile sınırlı bir LLM'e yaptırıldı.
- 10 soruluk set: `agent_eval/questions.jsonl` · sonuç: `agent_eval/RESULTS.md` · log: `logs/agent_calls.jsonl`.
- Yalnızca kurgusal araştırma senaryoları kullanılır.

## Kurulum kontrolü

`<doldurulacak: "REA araçları ve Ghidra sağlayıcısı bu oturumda kullanılabilir mi?" yanıtının ekran görüntüsü>`

## Teslim dosyaları

SPEC.md · LEDGER.md · HALLUCINATIONS.md · AGENT_COST.md · prompts/ · oracle/ · src/ · tests/
