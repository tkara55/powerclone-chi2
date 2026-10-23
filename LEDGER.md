# LEDGER — Kanıt defteri

Etiketler: **[DOK]** kılavuz/makale · **[REA]** binary'den kanıt (adres / dize referansı) · **[GUI]** G*Power arayüzünde gözlendi (oracle/ ekran görüntüsü) · **[AJAN]** kanıtsız çıkarım.

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
| L-11 | [GUI] | a-priori aramanın alt sınırı **N = 1** (ilk varsayım N = 2 yanlıştı, HALLUCINATIONS H-4) | GUI g08 (w=5 → N=1), g34 (power 0.051 → N=1), ekran görüntüleri | test_huge_effect_hits_minimum_n |
| L-11r | [REA] | _rea/FINDINGS.md'den eklenecek_ | — | — |
| L-12 | [AJAN] | Compromise: β(c) − q·α(c) = 0 kökü | public + GUI g27, g28 1e-6 içinde | test_public_chi2[compromise] |
| L-13 | [GUI] | **güç = α kabul edilir** (N=1); yalnızca güç < α reddedilir: "Power must be greater than or equal to alpha." (ilk varsayım yanlıştı, H-5) | GUI g09, g10, g11 | test_power_equal_alpha_is_accepted |
| L-13r | [REA] | _rea/FINDINGS.md'den eklenecek_ | — | — |
| L-14 | [AJAN] | Arama üst sınırı 10⁷, aşılırsa NO_SOLUTION | Kendi kararımız; GUI g06 (N = 7 848 861) bu sınırın altında eşleşiyor | differential.py |
| L-14r | [REA] | _rea/FINDINGS.md'den eklenecek_ | — | — |
| L-15 | [GUI] | w < 1e-6 reddedilir ("Effect size w must be greater 1e-06."), ama **w = 1e-6 tam kabul edilir** — mesaj ile kontrol uyuşmuyor | GUI g19, g32, g33 | test_w_exactly_1e6_is_accepted |
| L-16g | [GUI] | df < 1 reddedilir: "Degrees of Freedom must be greater or equal one." | GUI g20 | test_invalid |
| L-17 | [GUI] | Post-hoc'ta N = 1 G*Power'da kabul edilir; **sözleşme `n_total ≥ 2` dediği için biz OUT_OF_RANGE veriyoruz** (bilinçli fark) | GUI g25 | tests/REPORT.md'deki tek uyuşmazlık |
| L-16 | [DOK] | Cohen eşikleri w: 0.1 / 0.3 / 0.5 | Cohen (1988); CONTRACT §10 | ajan sistem prompt'u |

## REA oturumu için arama ipuçları

- Dize araması: `"Contingency"`, `"Goodness-of-fit"`, `"Effect size w"`, `"Noncentrality parameter"`, `"Total sample size"`, hata/uyarı metinleri.
- Bu dizelere referans veren fonksiyonlardan hesap çağrısına (ncχ² CDF) inin.
- Her bulguda: fonksiyon adresi + kısa (≤ 2 satır) alıntı. Decompile çıktısı repoya **konmaz**.
