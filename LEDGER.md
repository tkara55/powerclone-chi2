# LEDGER — Kanıt defteri

Etiketler: **[DOK]** kılavuz/makale · **[REA]** binary'den kanıt (adres / dize referansı) · **[AJAN]** kanıtsız çıkarım.

> ⚠️ **Durum:** [REA] satırları henüz doldurulmadı. Bunlar G*Power 3.1.9.7 üzerinde REA + Ghidra
> oturumu (prompts/session1_inceleme.md) çalıştırılarak, **gerçek fonksiyon adresi ve dize
> referansıyla** doldurulmalı. Kanıtı olmayan satır [AJAN] olarak kalır. Adres uydurmayın.

| ID | Etiket | İddia | Kanıt | Doğrulayan test |
|---|---|---|---|---|
| L-01 | [DOK] | λ = w² · N | Faul vd. (2007) Behav Res Methods 39(2); G*Power kılavuzu, "Goodness-of-fit tests: Contingency tables" | test_public_vectors (ncp=19.8, 9.0) |
| L-02 | [DOK] | Kritik χ² merkezi χ²(df)'nin 1−α kantili | Kılavuz, aynı bölüm | public a-priori: 11.0704977 |
| L-03 | [DOK] | Güç = 1 − F_ncχ²(krit; df, λ) | Kılavuz; Cohen (1988) bölüm 7 | public post-hoc: 0.6235846 |
| L-04 | [DOK] | df kullanıcı tarafından girilir | GUI'de "Df" giriş alanı; CONTRACT §4.4 | — |
| L-10 | [AJAN] | a-priori N = güç ≥ hedef olan en küçük tam sayı (ceil) | statsmodels kesirli N ile 799/799 ceil eşleşmesi (tests/REPORT.md); 220 ve 88 GUI değerleriyle uyumlu | test_a_priori_n_is_minimal, differential.py |
| L-10r | [REA] | _TODO:_ Yuvarlama/arama döngüsünün bulunduğu fonksiyon | `FUN_????????` @ `0x????????` — doldurulacak | — |
| L-11 | [AJAN] | a-priori aramanın alt sınırı N = 2 | CONTRACT §5 "n_total ≥ 2" aralığından çıkarım | test_huge_effect_hits_minimum_n; GUI g07/g08 ile doğrulanmalı |
| L-11r | [REA] | _TODO:_ Alt sınır sabiti | — | — |
| L-12 | [AJAN] | Compromise: β(c) − q·α(c) = 0 kökü | public compromise vektörü 1e-6 içinde | test_public_chi2[compromise] |
| L-13 | [AJAN] | güç ≤ α → INCONSISTENT hatası | CONTRACT §2.4 örnek hata mesajı "Power, alpha değerinden büyük olmalı" | test_invalid; GUI g09/g10 ile doğrulanmalı |
| L-13r | [REA] | _TODO:_ GUI'de güç ≤ α'da çıkan mesaj dizesi ve onu referanslayan fonksiyon | — | — |
| L-14 | [AJAN] | Arama üst sınırı 10⁷, aşılırsa NO_SOLUTION | Kendi tasarım kararımız; G*Power'ın sınırı bilinmiyor | GUI g06 (w=0.001) ile karşılaştırılmalı |
| L-14r | [REA] | _TODO:_ İterasyon durma koşulu / maksimum N | — | — |
| L-15 | [REA] | _TODO:_ w ≤ 0, df < 1, N < 2 için GUI mesajları (dize tablosu) | — | GUI g19, g20, g25 |
| L-16 | [DOK] | Cohen eşikleri w: 0.1 / 0.3 / 0.5 | Cohen (1988); CONTRACT §10 | ajan sistem prompt'u |

## REA oturumu için arama ipuçları

- Dize araması: `"Contingency"`, `"Goodness-of-fit"`, `"Effect size w"`, `"Noncentrality parameter"`, `"Total sample size"`, hata/uyarı metinleri.
- Bu dizelere referans veren fonksiyonlardan hesap çağrısına (ncχ² CDF) inin.
- Her bulguda: fonksiyon adresi + kısa (≤ 2 satır) alıntı. Decompile çıktısı repoya **konmaz**.
