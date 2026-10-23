# SPEC — χ² testi, olumsallık tabloları (`chi2-contingency`)

**Kaynak davranış:** G*Power 3.1.9.7 → *χ² tests – Goodness-of-fit tests: Contingency tables*
**Arayüz:** [CONTRACT.md](CONTRACT.md) v1.0.0 (komut, alan adları, JSON biçimi, hata kodları)
**Yazan:** Oturum 1 (inceleme). Bu belge yazım oturumunun **tek davranış kaynağıdır**.

Bu belge yalnızca **davranışı** tanımlar. Kanıtlara yalnızca kimlikleriyle atıf yapılır:

- `L-xx`: [LEDGER.md](LEDGER.md) satırı (belge, GUI ya da çıkarım)
- `R-xx`: tersine mühendislik bulgusu (ayrıntısı LEDGER'da, burada yalnızca kimlik)
- `gNN`: [oracle/gpower_gui_vectors.csv](oracle/gpower_gui_vectors.csv) satırı (G*Power arayüzünde gözlenen değer)
- `P`: [tests/public_vectors.jsonl](tests/public_vectors.jsonl) içindeki `chi2-contingency/*` satırları

Anahtar kelimeler: **MUST** (zorunlu), **SHOULD** (önerilen), **MAY** (serbest).

---

## 1. Model

Girdi büyüklükleri: etki büyüklüğü `w`, I. tip hata `alpha` (α), güç `power` (1−β), toplam örneklem `n_total` (N), serbestlik derecesi `df`.

| Büyüklük | Tanım | Kanıt |
|---|---|---|
| Merkezsizlik parametresi | λ = w² · N | L-01, R-20, P |
| Kritik değer | c = merkezi χ²(df) dağılımının (1 − α) kantili | L-02, R-20, P |
| Güç | güç(w, α, N, df) = 1 − F_ncχ²(c; df, λ) (F_ncχ²: merkezsiz χ² dağılım fonksiyonu) | L-03, R-20, P |
| β | β = 1 − güç | R-17 |
| df | Kullanıcı girer, motor türetmez. (r−1)(c−1) hesabı kullanıcının ya da ajanın işidir | L-04 |

Sayısal gereksinimler:

- F_ncχ² ve χ² kantili, CONTRACT §6 toleransını (1e-6) karşılayacak doğrulukta **MUST** olmalı. λ = 0 durumunda merkezi χ² ile aynı sonucu vermeli (güç = α).
- güç, sabit α ve df için N'de (ya da w'de) **kesin artan** kabul edilir. Bütün çözücüler bu monotonluğa dayanır.
- Sonuçlar tam double hassasiyetle yazılır. Ara yuvarlama yapılmaz (CONTRACT §2.3).

---

## 2. Modlar ve çözücüler

Her mod dört büyüklükten (α, güç, N, w) birini çözer. Ortak çıktı: `ncp` = λ, `critical_chi2` = c. Alanlar CONTRACT §4.4'teki gibidir.

### 2.1 `post-hoc` (doğrudan hesap)

1. λ = w²·N, c = χ²_df kantili(1−α)
2. `power` = 1 − F_ncχ²(c; df, λ)

Çıktı: `ncp`, `critical_chi2`, `power`. Kanıt: R-20, P, g21–g24, g26, g32, g33, g37, g40.

### 2.2 `a-priori` (N çözülür)

Hedef: güç(N) ≥ `power` koşulunu sağlayan **en küçük tam sayı N ≥ 1**.

1. N'yi sürekli bir değişken kabul et. f(N) = güç(w, α, N, df) − power (R-11).
2. **Alt sınır 1:** f(1) ≥ 0 ise (N = 1'de hedef güç zaten tutuyorsa) sonuç **N = 1**. Bu güç = α durumunu da kapsar (R-13, L-11, g08, g09, g11, g34).
3. Aksi halde f(N*) = 0 kökünü bul. Önerilen yöntem (R-12): [1, 100] aralığından başla. f(100) < 0 ise üst sınırı ×1.6 büyüterek f ≥ 0 olana kadar ilerle; alt sınır bir önceki üst sınırdır. Sonra bir aralık kök bulucusu (Brent ya da ikiye bölme) kullan. Kök, göreli olarak ~1e-12 ya da daha sıkı bulunmalı (R-16: G*Power makine hassasiyetine kadar iniyor).
4. **Üst sınır YOK.** N büyütmesine yapay bir tavan **MUST NOT** konmalı. w = 1e-6 gibi girdilerde N ≈ 7.85·10¹² olur ve bu geçerli bir sonuçtur (R-12, R-21, g06, g35).
5. **Yuvarlama (R-14):** N = ceil( floor(N*·10¹⁰ + 0.5) / 10¹⁰ ). Önce 10 ondalığa yuvarla, sonra yukarı yuvarla. Sonra N = max(N, 1). Böylece 88.00000000001 gibi kayan nokta gürültüsü 89'a çıkmaz. N*·10¹⁰ değeri 2⁵³'ü aşarsa (N* ≳ 9·10⁵) ilk adım etkisizdir ve sonuç doğrudan ceil(N*) olur. Bu beklenen davranıştır.
6. `n_total` = N (JSON tam sayısı). `ncp` = w²·N (**tam sayı N ile**). `actual_power` = güç(w, α, N, df) (**tam sayı N'de yeniden hesaplanır**, R-15).

Sonuç kuralı (test edilebilir biçimi): N ≥ 1 ve güç(N) ≥ power. N > 1 ise güç(N−1) < power. Tek istisna, 10 ondalık yuvarlamasının çok küçük bir farkı yok saymasıdır (R-14). Kanıt: L-10, L-10r, R-11…R-15, P, g01–g09, g11–g18, g34, g35.

### 2.3 `compromise` (α ve β çözülür, oran q = β/α sabit)

1. Bilinmeyen α ∈ (0, 1). β(α) = 1 − güç(w, α, N, df).
2. **β(α) = q · α** denklemini sağlayan α'yı bul (R-17, L-12). Eşdeğeri: g(α) = 1 − β(α)/(q·α) = 0. g, α'da artan olduğundan kök tektir.
3. Önerilen arama aralığı (R-18): g(0.5) > 0 ise kök 0.5'in altındadır; [0.25, 0.5] ile başlayıp alt sınırı yarıya indir. Değilse kök 0.5'in üstündedir; [0.5, 0.75] ile başlayıp üst sınırı 1'e doğru yaklaştır. Aralık [1e-99, 1] içinde kalır. Kök, göreli ~1e-12 ya da daha sıkı bulunmalı.
4. Çıktı: `alpha` = α, `beta` = β(α), `power` = 1 − β, `critical_chi2` = χ²_df kantili(1−α), `ncp` = w²·N.

Kanıt: R-17, R-18, P, g27, g28, g43.

### 2.4 `criterion` (α çözülür)

1. güç(w, α, N, df) = `power` olacak α'yı bul. Eşdeğeri: c = merkezsiz χ²(df, λ = w²N)'nin `(1 − power)` kantili, sonra α = 1 − F_χ²(c; df).
2. Kök arama yoluyla çözülürse aralık 2.3/3'teki gibidir (R-18).
3. Çıktı: `ncp` = w²·N, `critical_chi2` = c, `alpha` = α.

Kanıt: R-18, P, g29.

### 2.5 `sensitivity` (w çözülür)

1. güç(w, α, N, df) = `power` olacak **w > 0** değerini bul. Eşdeğeri: güç(λ) = power olacak λ*'ı bul, sonra w = √(λ*/N).
2. Önerilen arama aralığı (R-19): w ∈ [1e-6, 0.5] ile başla. güç(0.5) < power ise üst sınırı ×1.6 büyüt.
3. Çıktı: `ncp` = λ* = w²·N, `critical_chi2` = χ²_df kantili(1−α), `w`.
4. **power = α sınır durumu** (açık, bkz. §6/2): gerçek kök w = 0'dır. Bu durumda `w` = 0 ve `ncp` = 0 **SHOULD** döndürülmeli. Bu, a-priori'deki "kök aralıkta değilse alt uca düş" mekanizmasından çıkarılmıştır (R-13, R-19) ama GUI'de doğrulanmamıştır.

Kanıt: R-19, P, g30, g31.

---

## 3. Girdi doğrulama

### 3.1 Genel sıra (ilk hata kazanır, tek bir hata döner)

Bir çağrıda birden çok sorun varsa **yalnızca ilk** bulunan hata raporlanır. Aşamalar sırayla şöyledir:

| Aşama | Kontrol | Hata | `field` |
|---|---|---|---|
| 1 | `--test` yok | `MISSING_PARAM` | `test` |
| 1 | `--test` tanınmıyor (ya da bu motorda yok) | `UNSUPPORTED` | `test` |
| 2 | `--mode` yok | `MISSING_PARAM` | `mode` |
| 2 | `--mode` tanınmıyor | `UNSUPPORTED` | `mode` |
| 3 | Tanınmayan alan, ya da modla ilgisiz alan (ör. a-priori'de `--n_total`, ya da başka ailenin `--d` alanı). Komut satırındaki ilk sorunlu alan | `UNKNOWN_PARAM` | o alan |
| 4 | Modun gerektirdiği alan eksik. CONTRACT §4.4 tablosundaki sırayla ilk eksik alan | `MISSING_PARAM` | o alan |
| 5 | Değer sayı değil, sonlu değil (`nan`, `inf`) ya da tam sayı alanında tam sayı değil (`df 2.5`, `n_total 100.5`). Tam sayı alanında `5`, `5.0`, `5e0` gibi tam değerli sayılar kabul edilir. Alanlar CONTRACT tablo sırasıyla kontrol edilir | `INVALID_VALUE` | o alan |
| 6 | Aralık ve tutarlılık kontrolleri, **§3.2'deki mod sırasıyla** | `OUT_OF_RANGE` / `INCONSISTENT` | o alan |

Hata çıktısı CONTRACT §2.4 biçimindedir. Çıkış kodu **2**. `error` metni serbesttir. G*Power metinleri §3.4'te.

### 3.2 Aralık kontrollerinin mod bazında sırası (aşama 6)

G*Power'ın kontrol sırası budur (R-04, R-10). **df her modda ilk sırada.**

| Mod | Sıra |
|---|---|
| `a-priori` | df → w → alpha → power → (power ≥ alpha) |
| `post-hoc` | df → w → alpha → n_total |
| `criterion` | df → w → power → n_total |
| `compromise` | df → w → n_total → beta_alpha_ratio |
| `sensitivity` | df → alpha → power → (power ≥ alpha) → n_total |

### 3.3 Kurallar (G*Power ∩ CONTRACT §5)

Etkin kural, iki koşulun **ikisini de** sağlamaktır. CONTRACT §5'in reddettiği her değer G*Power kabul etse bile reddedilir (bkz. §4).

| Alan | Etkin kabul kuralı | Aksi halde | G*Power kuralı | Kanıt |
|---|---|---|---|---|
| `df` | tam sayı, df ≥ 1 | `OUT_OF_RANGE` / `df` | df ≥ 1 | R-04, L-16g, g20, g44 |
| `w` (a-priori) | w ≥ 1e-6 (**1e-6 dahil**) | `OUT_OF_RANGE` / `w` | w ≥ 1e-6 | R-01, R-02, L-15, g19, g35, g36 |
| `w` (post-hoc, criterion, compromise) | w > 0 | `OUT_OF_RANGE` / `w` | w ≥ 0 (**1e-6 alt sınırı yok**) | R-03, g32, g33, g37, g38 |
| `alpha` | 1e-7 ≤ α ≤ 0.9999999 | `OUT_OF_RANGE` / `alpha` | aynı | R-06, g39, g40 |
| `power` | 1e-7 ≤ güç ≤ 0.9999999 | `OUT_OF_RANGE` / `power` | aynı | R-07, g17, g41 |
| power ≥ alpha (a-priori, sensitivity) | güç ≥ α (**eşitlik kabul**) | `INCONSISTENT` / `power` | güç ≥ α | R-05, L-13, g09, g10, g11 |
| `n_total` (girdi) | tam sayı, 2 ≤ N ≤ 2147483646 | `OUT_OF_RANGE` / `n_total` | 1 ≤ N ≤ 2147483646 | R-08, L-17, g24, g25 |
| `beta_alpha_ratio` | 0.01 ≤ q ≤ 100 (iki uç dahil) | `OUT_OF_RANGE` / `beta_alpha_ratio` | aynı | R-09, g42, g43 |

Notlar:

- Negatif değerler de aynı kuralla `OUT_OF_RANGE` olur (ör. w = −0.3).
- 2147483646 üst sınırı yalnızca **girdi** olan `n_total` için geçerlidir. a-priori'nin **çıktısı** olan N bu sınırla karşılaştırılmaz (R-21, g35).
- a-priori ve sensitivity dışında power ≥ alpha kontrolü yoktur. Diğer modlarda bu iki alandan en çok biri girdidir.

### 3.4 Hata metinleri (`error` alanı için önerilen, G*Power ile aynı)

| Durum | G*Power metni | Kanıt |
|---|---|---|
| df < 1 | `Degrees of Freedom must be greater or equal one.` | R-04, g20 |
| a-priori w < 1e-6 | `Effect size w must be greater 1e-06.` (kontrol ≥ olduğu halde metin "greater" diyor) | R-01, g19, g36 |
| post-hoc vb. w < 0 | `Effect size w must be non-negative.` | R-03 |
| α aralık dışı | `Alpha is outside the admissible range (1e-07, 1).` | R-06, g39 |
| güç aralık dışı | `Power is outside the admissible range (1e-07, 1).` | R-07, g41 |
| güç < α | `Power must be greater than or equal to alpha.` | R-05, g10 |
| q aralık dışı | `β/α ratio is outside the admissible range (0.01, 100)` | R-09, g42 |
| N aralık dışı | `Total sample size is outside the admissible range (…)` | R-08 |

Aralık metinlerindeki üst uç "1" olarak görünür, ama kontrol 0.9999999 iledir. Bunun nedeni G*Power'ın sayıyı 6 anlamlı basamakla yazmasıdır. Kontrolü metne göre **değil**, §3.3'e göre yazın.

### 3.5 `NO_SOLUTION`

G*Power'da bu ailenin sayısal tavanı yoktur. §3.3'ü geçen her girdi için bir sonuç **MUST** üretilmeli. `NO_SOLUTION` (çıkış kodu 1) yalnızca hesap sonlu bir değer üretemezse (taşma, NaN) **MAY** döndürülür. Yapay bir N tavanı (ör. 10⁷) bu kodu tetiklememeli (R-21, g06, g35).

---

## 4. Sözleşmeyle bilinçli farklar

CONTRACT §5 aralığın **dışındaki** değerlerin reddedilmesini zorunlu kılar. G*Power'ın kabul ettiği iki değer bu yüzden reddedilir. Kural: **CONTRACT §5 kazanır.**

| # | Girdi | G*Power | Biz | Kanıt |
|---|---|---|---|---|
| D-1 | `post-hoc` (ve criterion, compromise, sensitivity) `n_total = 1` | kabul (g25: güç 0.0603726) | `OUT_OF_RANGE`, field `n_total` | L-17, R-08, g25 |
| D-2 | `post-hoc` (ve criterion, compromise) `w = 0` | kabul (g38: güç = α = 0.05) | `OUT_OF_RANGE`, field `w` | R-03, g38 |

Bu ikisi dışında GUI ile birebir uyum beklenir. a-priori'nin N = 1 **çıktısı** bir fark değildir: CONTRACT §5 yalnızca girdileri sınırlar (g08, g09).

---

## 5. Kabul kriterleri (Gherkin)

Toleranslar: ondalıklar CONTRACT §6'ya göre (mutlak ya da göreli 1e-6), tam sayılar tam eşleşme.

```gherkin
Feature: chi2-contingency güç analizi (G*Power 3.1.9.7 davranışı)

  Background:
    Given komut "gpower-clone --test chi2-contingency"

  # ---------- Model ve beş mod: açık vektörler ----------

  Scenario: A priori: kılavuz örneği (P, g01)
    When mode "a-priori", w 0.3, alpha 0.05, power 0.95, df 5
    Then n_total 220, ncp 19.8, critical_chi2 11.0704977, actual_power 0.9502155

  Scenario: Post hoc: kılavuz örneği (P, g21)
    When mode "post-hoc", w 0.3, alpha 0.05, n_total 100, df 5
    Then ncp 9, critical_chi2 11.0704977, power 0.6235846

  Scenario: Compromise q = 1 (P, g27)
    When mode "compromise", w 0.3, beta_alpha_ratio 1, n_total 100, df 5
    Then ncp 9, critical_chi2 7.6804954, alpha 0.1747455, beta 0.1747455, power 0.8252545

  Scenario: Compromise q = 4 (g28)
    When mode "compromise", w 0.3, beta_alpha_ratio 4, n_total 100, df 5
    Then critical_chi2 9.9516505, alpha 0.0766169, beta 0.3064674, power 0.6935326
    And beta = 4 · alpha (±1e-6)

  Scenario: Criterion (P, g29)
    When mode "criterion", w 0.3, power 0.95, n_total 100, df 5
    Then ncp 9, critical_chi2 4.6618452, alpha 0.4585253

  Scenario Outline: Sensitivity (P, g30, g31)
    When mode "sensitivity", alpha 0.05, power <p>, n_total <n>, df <df>
    Then ncp <ncp>, critical_chi2 <c>, w <w>
    Examples:
      | p    | n   | df | ncp        | c          | w         |
      | 0.95 | 100 | 5  | 19.7801344 | 11.0704977 | 0.4447486 |
      | 0.80 | 50  | 1  | 7.8488605  | 3.8414588  | 0.3962035 |

  # ---------- A priori: arama, yuvarlama, sınırlar ----------

  Scenario Outline: A priori: en küçük tam sayı N (g02–g07, g12–g18)
    When mode "a-priori", w <w>, alpha <a>, power <p>, df <df>
    Then n_total <N> ve actual_power <ap>
    And güç(n_total) ≥ <p> ve n_total > 1 ise güç(n_total − 1) < <p>
    Examples:
      | w     | a     | p     | df  | N       | ap        |
      | 0.3   | 0.05  | 0.80  | 1   | 88      | 0.8035275 |
      | 0.1   | 0.05  | 0.80  | 1   | 785     | 0.8000569 |
      | 0.5   | 0.05  | 0.80  | 1   | 32      | 0.8074304 |
      | 0.01  | 0.05  | 0.95  | 1   | 129948  | 0.9500013 |
      | 0.001 | 0.05  | 0.80  | 1   | 7848861 | 0.8000000 |
      | 2     | 0.05  | 0.80  | 1   | 2       | 0.8074304 |
      | 0.3   | 0.01  | 0.99  | 10  | 445     | 0.9900571 |
      | 0.3   | 0.001 | 0.9   | 3   | 289     | 0.9012598 |
      | 0.2   | 0.10  | 0.90  | 2   | 262     | 0.9005778 |
      | 0.25  | 0.05  | 0.90  | 2   | 203     | 0.9008030 |
      | 0.1   | 0.01  | 0.95  | 6   | 2705    | 0.9500639 |
      | 0.3   | 0.05  | 0.999 | 1   | 284     | 0.9990183 |
      | 0.3   | 0.05  | 0.95  | 100 | 632     | 0.9501569 |

  Scenario Outline: A priori: alt sınır N = 1 (R-13, g08, g09, g11, g34)
    When mode "a-priori", w <w>, alpha 0.05, power <p>, df <df>
    Then n_total 1, ncp <ncp>, actual_power <ap>
    Examples:
      | w   | p      | df | ncp  | ap        |
      | 5   | 0.95   | 1  | 25   | 0.9988173 |
      | 0.3 | 0.05   | 5  | 0.09 | 0.0539009 |
      | 0.3 | 0.0501 | 5  | 0.09 | 0.0539009 |
      | 0.5 | 0.051  | 1  | 0.25 | 0.0790975 |

  Scenario: A priori: N için tavan yok (R-12, R-21, g35)
    When mode "a-priori", w 0.000001, alpha 0.05, power 0.8, df 1
    Then hata dönmez ve çıkış kodu 0 olur
    And n_total bir JSON tam sayısıdır ve 2147483646'dan büyüktür
    And n_total, 7.8489e12'ye göreli 1e-4 içinde yakındır (GUI 5 anlamlı basamak gösteriyor)
    And ncp 7.8488605 ve actual_power 0.8 olur (±1e-6)

  Scenario: A priori: yuvarlama kuralı (R-14)
    Given sürekli kök N* = 88 + 1e-11 (kayan nokta gürültüsü)
    When a-priori yuvarlama kuralı uygulanır
    Then n_total 88 olur, 89 olmaz
    Given sürekli kök N* = 88 + 1e-9
    Then n_total 89 olur
    Given sürekli kök N* = 219.37
    Then n_total 220 olur

  Scenario: A priori: actual_power tam sayı N'de hesaplanır (R-15)
    When mode "a-priori", w 0.3, alpha 0.05, power 0.95, df 5
    Then actual_power = post-hoc(w 0.3, alpha 0.05, n_total 220, df 5).power

  # ---------- Doğrulama: sınır değerleri ----------

  Scenario Outline: w alt sınırı moda göre değişir (R-02, R-03)
    When mode "<mod>", w <w> ve diğer alanlar geçerli
    Then sonuç <sonuç>
    Examples:
      | mod        | w           | sonuç                                       |
      | a-priori   | 0.000001    | hesaplanır (g35)                            |
      | a-priori   | 0.000000999 | OUT_OF_RANGE, field w (g36)                 |
      | a-priori   | 0           | OUT_OF_RANGE, field w (g19)                 |
      | post-hoc   | 0.0000005   | hesaplanır, power 0.05, ncp 2.5e-11 (g37)   |
      | post-hoc   | 0.000001    | hesaplanır, power 0.05 (g32)                |
      | post-hoc   | 0           | OUT_OF_RANGE, field w (D-2; G*Power g38'de kabul) |
      | criterion  | 0           | OUT_OF_RANGE, field w (D-2)                 |
      | compromise | 0           | OUT_OF_RANGE, field w (D-2)                 |
      | post-hoc   | -0.3        | OUT_OF_RANGE, field w                       |

  Scenario Outline: alpha ve power kabul aralığı [1e-7, 0.9999999] (R-06, R-07)
    When <girdi>
    Then sonuç <sonuç>
    Examples:
      | girdi                                                      | sonuç                          |
      | post-hoc w 0.3, alpha 0.00000001, n_total 100, df 1        | OUT_OF_RANGE, field alpha (g39) |
      | post-hoc w 0.3, alpha 0.0000001, n_total 100, df 1         | power 0.009989983, critical_chi2 28.3739874 (g40) |
      | post-hoc w 0.3, alpha 0.9999999, n_total 100, df 1         | hesaplanır                     |
      | post-hoc w 0.3, alpha 0.99999995, n_total 100, df 1        | OUT_OF_RANGE, field alpha      |
      | post-hoc w 0.3, alpha 1, n_total 100, df 1                 | OUT_OF_RANGE, field alpha      |
      | a-priori w 0.3, alpha 0.05, power 0.99999995, df 1         | OUT_OF_RANGE, field power (g41) |
      | a-priori w 0.3, alpha 0.05, power 0.9999999, df 1          | hesaplanır                     |
      | criterion w 0.3, power 0.00000001, n_total 100, df 1       | OUT_OF_RANGE, field power      |

  Scenario Outline: güç ve α ilişkisi (R-05)
    When mode "<mod>", alpha 0.05, power <p> ve diğer alanlar geçerli
    Then sonuç <sonuç>
    Examples:
      | mod         | p      | sonuç                                       |
      | a-priori    | 0.04   | INCONSISTENT, field power, çıkış kodu 2 (g10) |
      | a-priori    | 0.05   | n_total 1 (g09)                             |
      | a-priori    | 0.0501 | n_total 1 (g11)                             |
      | sensitivity | 0.04   | INCONSISTENT, field power                   |

  Scenario Outline: β/α oranı [0.01, 100] (R-09)
    When mode "compromise", w 0.3, beta_alpha_ratio <q>, n_total 100, df 5
    Then sonuç <sonuç>
    Examples:
      | q     | sonuç                                                            |
      | 0.005 | OUT_OF_RANGE, field beta_alpha_ratio (g42)                       |
      | 0.01  | hesaplanır                                                       |
      | 100   | alpha 0.006654201, beta 0.6654201, power 0.3345799, critical_chi2 16.0674195 (g43) |
      | 100.5 | OUT_OF_RANGE, field beta_alpha_ratio                             |

  Scenario Outline: n_total girdisi (R-08, D-1)
    When mode "post-hoc", w 0.3, alpha 0.05, n_total <n>, df 1
    Then sonuç <sonuç>
    Examples:
      | n          | sonuç                                                |
      | 2          | power 0.0708635, ncp 0.18 (g24)                      |
      | 1          | OUT_OF_RANGE, field n_total (D-1; G*Power g25'te kabul) |
      | 2147483646 | hesaplanır                                           |
      | 2147483647 | OUT_OF_RANGE, field n_total                          |
      | 100.5      | INVALID_VALUE, field n_total                         |

  Scenario Outline: df (R-04)
    When mode "a-priori", w 0.3, alpha 0.05, power 0.95, df <df>
    Then sonuç <sonuç>
    Examples:
      | df  | sonuç                         |
      | 1   | hesaplanır                    |
      | 0   | OUT_OF_RANGE, field df (g20)  |
      | -1  | OUT_OF_RANGE, field df        |
      | 2.5 | INVALID_VALUE, field df       |
      | 5.0 | hesaplanır (df = 5 ile aynı)  |

  # ---------- Doğrulama: sıra ----------

  Scenario Outline: İlk hata kazanır (R-10, §3.1, §3.2)
    When <girdi>
    Then code <kod>, field <alan>
    Examples:
      | girdi                                                                 | kod           | alan    |
      | a-priori w 0, alpha 0.05, power 0.8, df 0                             | OUT_OF_RANGE  | df      |
      | a-priori w 0, alpha 2, power 0.04, df 5                               | OUT_OF_RANGE  | w       |
      | a-priori w 0.3, alpha 2, power 0.04, df 5                             | OUT_OF_RANGE  | alpha   |
      | a-priori w 0.3, alpha 0.05, power 2, df 5                             | OUT_OF_RANGE  | power   |
      | post-hoc w 0, alpha 0.05, n_total 1, df 1                             | OUT_OF_RANGE  | w       |
      | compromise w 0.3, beta_alpha_ratio 0.001, n_total 1, df 5             | OUT_OF_RANGE  | n_total |
      | sensitivity alpha 0.05, power 0.04, n_total 1, df 5                   | INCONSISTENT  | power   |
      | a-priori w abc, alpha 0.05, power 0.95, df 0                          | INVALID_VALUE | w       |
      | a-priori alpha 0.05, power 0.95, df 5 (w yok)                         | MISSING_PARAM | w       |
      | a-priori w 0.3, alpha 0.05, power 0.95, df 5, n_total 50              | UNKNOWN_PARAM | n_total |
      | a-priori w 0.3, alpha 0.05, power 0.95, df 5, d 0.5                   | UNKNOWN_PARAM | d       |
      | --test t9-unknown --mode a-priori                                     | UNSUPPORTED   | test    |
      | --test chi2-contingency --mode bogus                                  | UNSUPPORTED   | mode    |

  Scenario: Geçersiz girdilerde çıkış kodu
    When herhangi bir doğrulama hatası oluşur
    Then stdout'ta tek satır JSON {"error": ..., "code": ..., "field": ...} olur
    And çıkış kodu 2 olur

  # ---------- Genel ----------

  Scenario: Determinizm (CONTRACT §2.1)
    When aynı girdi iki kez verilir
    Then iki stdout bayt bayt aynıdır

  Scenario: Çıktı biçimi (CONTRACT §2.3)
    When herhangi bir başarılı hesap
    Then stdout tek satır JSON'dur
    And n_total JSON tam sayısıdır ("220", "220.0" değil)
    And ondalıklar yuvarlanmadan tam double olarak yazılır
```

---

## 6. Açık konular

1. **Sayısal hata bayrağı:** G*Power'ın kök bulucusu "aralıkta işaret değişimi yok" ya da "iterasyon tükendi" durumlarını kullanıcıya bildiriyor mu, bilinmiyor (LEDGER [AJAN] A-01). Bu belge, iki durumda da yukarıdaki sonuç kurallarını uygular.
2. **sensitivity, power = α:** w = 0 beklentisi çıkarımdır (§2.5/4). GUI vektörü yok. Önerilen yeni vektör: sensitivity, alpha 0.05, power 0.05, n_total 100, df 1.
3. **Ncχ² iç algoritması:** G*Power'ın kullandığı seri ya da yaklaşım incelenmedi (A-02). §1'deki doğruluk gereksinimi yeterli kabul edilir. Uyuşmazlık görülürse önce bu kontrol edilmeli.
