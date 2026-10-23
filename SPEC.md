# SPEC — χ² testi, olumsallık tablosu (`chi2-contingency`)

Kaynak: G*Power 3.1.9.7 → *χ² tests – Goodness-of-fit tests: Contingency tables*.
Arayüz: [CONTRACT.md](CONTRACT.md) v1.0.0. Bu belge **davranışı** tanımlar.
Her kuralın yanında kanıt etiketi var; ayrıntı [LEDGER.md](LEDGER.md).

## 1. Model

| Büyüklük | Tanım | Kanıt |
|---|---|---|
| Merkezsizlik parametresi | λ = w² · N | [DOK] L-01 |
| Kritik değer | χ²_krit = merkezi χ²(df)'nin 1−α kantili | [DOK] L-02 |
| Güç | 1 − F_ncχ²(χ²_krit; df, λ) | [DOK] L-03 |
| df | Kullanıcı girer; motor türetmez ((r−1)(c−1) kullanıcı/ajan işidir) | [DOK] L-04 |

## 2. Modlar

| Mod | Çözülen | Yöntem |
|---|---|---|
| a-priori | N | güç(N) ≥ hedef olan **en küçük tam sayı** N (yukarı yuvarlama) — L-10 |
| post-hoc | güç | doğrudan formül |
| compromise | α, β | β(c) = q·α(c) olacak kritik c (kök bulma) — L-12 |
| criterion | α | c = ncχ²'nin (1−güç) kantili, α = 1 − F_χ²(c) |
| sensitivity | w | güç(λ) = hedef olan λ, w = √(λ/N) |

## 3. Kabul kriterleri (Gherkin)

```gherkin
Feature: chi2-contingency güç analizi

  Background:
    Given test kimliği "chi2-contingency"

  Scenario: A priori — kılavuz örneği
    When mode "a-priori", w 0.3, alpha 0.05, power 0.95, df 5 verilir
    Then n_total 220 olur
    And ncp 19.8 olur
    And critical_chi2 11.0704977 (±1e-6) olur
    And actual_power 0.9502155 (±1e-6) olur

  Scenario: A priori — N yukarı yuvarlanır
    Given kesirli çözüm N* = 219.x
    When a-priori hesaplanır
    Then n_total = en küçük tam sayı N, öyle ki güç(N) ≥ hedef güç
    And güç(n_total − 1) < hedef güç

  Scenario Outline: A priori — sınır değerleri
    When mode "a-priori", w <w>, alpha 0.05, power <p>, df <df> verilir
    Then sonuç <sonuç> olur
    Examples:
      | w     | p    | df | sonuç                              |
      | 0.3   | 0.80 | 1  | n_total 88                         |
      | 0.01  | 0.95 | 1  | n_total 129948                     |
      | 5     | 0.95 | 1  | n_total 1 (GUI g08)                |
      | 0.3   | 0.05 | 5  | n_total 1 (güç = α kabul, GUI g09) |

  Scenario: Post hoc — kılavuz örneği
    When mode "post-hoc", w 0.3, alpha 0.05, n_total 100, df 5 verilir
    Then ncp 9 olur
    And power 0.6235846 (±1e-6) olur

  Scenario: Compromise — β/α = 1
    When mode "compromise", w 0.3, beta_alpha_ratio 1, n_total 100, df 5 verilir
    Then critical_chi2 7.6804954, alpha 0.1747455, beta 0.1747455, power 0.8252545 olur

  Scenario: Criterion
    When mode "criterion", w 0.3, power 0.95, n_total 100, df 5 verilir
    Then critical_chi2 4.6618452 ve alpha 0.4585253 olur

  Scenario: Sensitivity
    When mode "sensitivity", alpha 0.05, power 0.95, n_total 100, df 5 verilir
    Then ncp 19.7801344 ve w 0.4447486 olur

  Scenario: Güç α'dan küçük
    When mode "a-priori", w 0.3, alpha 0.05, power 0.04, df 5 verilir
    Then {"code":"INCONSISTENT","field":"power"} döner ve çıkış kodu 2 olur

  Scenario: w alt sınırı
    When w 0.0000009 verilir
    Then {"code":"OUT_OF_RANGE","field":"w"} döner
    When w 0.000001 verilir
    Then hesap yapılır (GUI g32)

  Scenario Outline: Geçersiz girdi
    When <girdi> verilir
    Then code <kod>, field <alan> döner ve çıkış kodu 2 olur
    Examples:
      | girdi                                  | kod           | alan    |
      | w eksik                                | MISSING_PARAM | w       |
      | a-priori modunda --n_total             | UNKNOWN_PARAM | n_total |
      | --w abc                                | INVALID_VALUE | w       |
      | --df 2.5                               | INVALID_VALUE | df      |
      | --w 0                                  | OUT_OF_RANGE  | w       |
      | --df 0                                 | OUT_OF_RANGE  | df      |
      | --n_total 1 (post-hoc)                 | OUT_OF_RANGE  | n_total |
      | --test t2-indep                        | UNSUPPORTED   | test    |

  Scenario: Arama sınırı
    Given gerekli N 10 000 000'u aşıyor
    Then {"code":"NO_SOLUTION"} döner ve çıkış kodu 1 olur

  Scenario: Determinizm
    When aynı girdi iki kez verilir
    Then iki çıktı bayt bayt aynıdır
```

## 4. Açık sorular (G*Power'dan kanıtlanmalı)

Bunlar şu an [AJAN] varsayımıdır; [REA] veya GUI vektörüyle kapatılmalı:

1. ~~a-priori alt sınırı~~ → GUI ile kapandı: N = 1 (L-11)
2. ~~güç ≤ α~~ → GUI ile kapandı: güç = α kabul, güç < α hata (L-13)
3. Aramanın üst sınırı ve durma koşulu — L-14 ([REA] bekliyor)
4. ~~Hata metinleri~~ → GUI ile kapandı (L-15, L-16g)
5. Bilinçli fark: post-hoc N = 1'i G*Power kabul ediyor, sözleşme gereği biz reddediyoruz (L-17)
