# AGENT_COST — Ajan maliyet ve süreç günlüğü

| Oturum | Ajan / model | Yaklaşık token | İterasyon | Not |
|---|---|---|---|---|
| Yazım (motor, CLI, MCP, ajan, testler, belgeler) | Claude Code, Opus 5.5 | ~140 000 (bağlam) | 3 test turu (45/45 yeşil) | 2 hata testlerle yakalandı (HALLUCINATIONS H-1, H-2) |
| İnceleme (statik analiz) | Claude Code, Opus 5.5 (ayrı oturum) | ~190 000 | ~45 araç çağrısı, ≈ 15–20 dk | 22 [REA] bulgu; 1 yanlış sınıf hatası g08 ile yakalandı. Ghidra 12.2 JDK 25 istediği için objdump kullanıldı (rea/SESSION_LOG.md) |
| GUI kâhini (44 vektör) | Claude Code + oracle/collect_gui.py | ~30 000 | 4 toplama turu | Ekran görüntüsü hatası (öndeki pencere sızdı) PrintWindow ile düzeltildi |
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
