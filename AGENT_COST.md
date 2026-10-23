# AGENT_COST — Ajan maliyet ve süreç günlüğü

| Oturum | Ajan / model | Yaklaşık token | İterasyon | Not |
|---|---|---|---|---|
| Yazım (motor, CLI, MCP, ajan, testler, belgeler) | Claude Code, Opus 5.5 | ~140 000 (bağlam) | 3 test turu (45/45 yeşil) | 2 hata testlerle yakalandı (HALLUCINATIONS H-1, H-2) |
| İnceleme (REA + Ghidra) | _doldurulacak_ | _doldurulacak_ | _doldurulacak_ | prompts/session1_inceleme.md |
| Ajan değerlendirmesi (10 soru) | claude-sonnet-5-5 | agent_eval/RESULTS.md | 1 | `ANTHROPIC_API_KEY` gerekli |

## Token karşılaştırması (MCP ve GUI yolu)

| Yol | Token | Süre | Doğruluk |
|---|---|---|---|
| MCP aracı | agent_eval/RESULTS.md | | |
| GUI (ekran görüntüsüyle) | _ölçülecek_ | | |

GUI yolunu ölçmek için aynı 10 soruyu bir computer-use ajanına G*Power penceresi üzerinden çözdürün
ve API'nin döndürdüğü `usage` değerlerini yazın.

## Neyi farklı yapardık

- İnceleme oturumunu önce çalıştırıp SPEC'i [REA] ile kapatmak, sonra yazmak.
- Kurulu kütüphane sürümünü (mcp 2.x) yazmadan önce kontrol etmek (H-1).
