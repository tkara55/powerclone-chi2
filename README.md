# powerclone-chi2 — χ² olumsallık tablosu güç analizi (YZM301 Teardown Sprint)

**Yapılan katmanlar:**

| Katman | Durum |
|---|---|
| Temel (CLI) | ✅ Tamam: 5 modun hepsi; G*Power GUI'ye karşı 42/44 (2 fark sözleşmeden), statsmodels'e karşı 799/799 |
| MCP sunucusu (+15) | ✅ Tamam: tek araç `power_analysis`, aynı motoru çağırır; CLI = MCP eşdeğerlik testi geçiyor |
| AI ajanı (+10) | ⚠️ **Kısmi:** ajan kodu, 10 soruluk set ve değerlendirme betiği hazır; **değerlendirme çalıştırılmadı** (API anahtarı yoktu), MCP–GUI token karşılaştırması yapılmadı. Bu katman için puan beklemiyoruz |

**Test ailesi:** 4) χ² testi, olumsallık tablosu (yanıt oranları) — `chi2-contingency`, 5 modun hepsi.

## Süreç notları ve yönergeden sapmalar

Dürüstlük için, yönergeden ayrıldığımız yerler:

1. **Temiz oda sırası ters.** Yönerge önce inceleme (Oturum 1 → SPEC.md), sonra yalnızca SPEC.md ile yazım
   (Oturum 2) istiyor. Bizde ilk motor, inceleme yapılmadan **yayımlanmış formüllerden** (Cohen 1988, G*Power
   makalesi) yazıldı; sonra G*Power GUI vektörleri ve ayrı inceleme oturumunun bulguları ile düzeltildi.
   Yazım oturumu hiçbir zaman decompile/disassembly çıktısı görmedi, yalnızca bulgu düzeyindeki kuralları
   (sınırlar, sıralar) kullandı. SPEC.md'nin son halini inceleme oturumu yazdı. Yalnızca SPEC.md'yi gören yeni
   bir oturumla sıfırdan yeniden yazım hazırlandı (`cleanroom` dalı, `prompts/session2_yazim.md`) ama
   çalıştırılamadı.
2. **REA aracı (`rea-agents`) kurulamadı.** Paket resmi kaynaktan doğrulandı (github.com/morluto/rea, npm 6.7.0),
   ancak kullandığımız ajan ortamının güvenlik denetimi kurulumu engelledi. Bu yüzden "REA araçları kullanılabilir
   mi?" ekran görüntüsü yok. [REA] etiketli bulgular, REA olmadan Ghidra 12.2 ve objdump ile **binary'den,
   adresleriyle** çıkarıldı (rea/).
3. **AI ajanı değerlendirmesi** yukarıdaki tabloda açıklandığı gibi çalıştırılmadı.

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
| Demo videosu | [demo/demo.mp4](demo/demo.mp4) (56 sn; `demo/demo.ps1` komutları canlı çalıştırır, ffmpeg ile kaydedildi) |

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

- `oracle/gpower_gui_vectors.csv` — G*Power 3.1.9.7 arayüzünden toplanmış 44 vektör (sınır değerler ve
  hata mesajları dahil); her satırın ekran görüntüsü `oracle/screenshots/<id>.png`. Uyum: **42/44**;
  iki fark da sözleşme aralığından kaynaklı (LEDGER L-17, L-18), açıklanamayan uyuşmazlık **0**.
- `oracle/collect_gui.py` — vektörleri toplayan betik: açık G*Power penceresini Win32 mesajlarıyla sürer
  (fare yok), çıktıları ekranda gösterildiği gibi okur, pencereyi PrintWindow ile yakalar.
- `oracle/statsmodels_vectors.csv` — ölçek için 799 vektör. statsmodels kesirli N verir (ör. 219.4);
  G*Power gücü hedefe ulaştıran en küçük tam sayıyı verir (yukarı yuvarlama, LEDGER R-14).

## Tersine mühendislik (rea/)

- `rea/FINDINGS.md` — ayrı inceleme oturumunun 22 [REA] bulgusu (fonksiyon/dize adresi + ≤ 2 satır alıntı);
  LEDGER.md'ye aktarıldı. 10 tanesi ayrıca yeni GUI vektörleriyle (g35–g44) arayüzde doğrulandı.
- `rea/SESSION_LOG.md` — inceleme oturumunun komutları ve maliyeti.
- **Araçlar:** İlk analiz GNU objdump disassembly'si ve küçük okuyucu betiklerle yapıldı (Ghidra 12.2 JDK 25
  istiyordu). JDK 25 kurulduktan sonra **Ghidra 12.2 headless** otomatik analizi çalıştırıldı ve bir post-script
  ile 9 anahtar fonksiyon girişinin ve 5 hata dizesi referansının tamamı doğrulandı: `rea/ghidra_check.txt`.
  Disassembly/decompile dökümü repoya konmadı.

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
| `w` | number | moda göre | etki büyüklüğü, > 0 (a-priori'de ≥ 1e-6) |
| `alpha` | number | moda göre | 1e-7 ≤ α ≤ 0.9999999 |
| `power` | number | moda göre | 1e-7 ≤ güç ≤ 0.9999999, güç ≥ α |
| `df` | integer | evet | ≥ 1, (satır−1)(sütun−1) |
| `n_total` | integer | moda göre | ≥ 2 |
| `beta_alpha_ratio` | number | compromise | 0.01 ≤ q ≤ 100 |

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
- 10 soruluk set: `agent_eval/questions.jsonl`. Değerlendirme çalıştırıldığında sonuç `agent_eval/RESULTS.md`,
  log `logs/agent_calls.jsonl` dosyasına yazılır. **Henüz çalıştırılmadı** (bkz. Süreç notları).
- Yalnızca kurgusal araştırma senaryoları kullanılır.

## Kurulum kontrolü

REA kurulamadığı için "REA araçları ve Ghidra sağlayıcısı bu oturumda kullanılabilir mi?" ekran görüntüsü
yok (bkz. Süreç notları, madde 2). Kullanılan araçlar: Ghidra 12.2 PUBLIC (JDK Temurin 25.0.4.1) headless,
GNU objdump 2.47; çalışmanın kaydı `rea/ghidra_check.txt` ve `rea/SESSION_LOG.md`.

## Teslim dosyaları

SPEC.md · LEDGER.md · HALLUCINATIONS.md · AGENT_COST.md · prompts/ · oracle/ · src/ · tests/
