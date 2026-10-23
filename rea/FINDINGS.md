# REA BULGULARI — G*Power 3.1.9.7, χ² "Goodness-of-fit tests: Contingency tables"

Oturum 1 (yalnızca inceleme). Hedef: `GPowerNT.exe`, SHA-256
`C63E6A133EB6372932F810C08CC33DC35A06D1DDB658F897BD6C34A754EFC812` (PE32 i386, MSVC/MFC140,
image base 0x400000). Binary repoya kopyalanmadı.

**Araç notu:** Ghidra 12.2 bu oturumda çalışmadı. `application.java.min=25` ama verilen JDK 21
(ayrıntı SESSION_LOG.md'de). Statik inceleme GNU objdump 2.47 (`-d -M intel`) ve dışarıda tutulan
küçük Python yardımcılarıyla (dize, sabit, vtable ve IAT okuyucu) yapıldı. Aşağıdaki **adresler
sanal adreslerdir (VA)**, yani Ghidra'nın göstereceği adreslerle aynıdır. Fonksiyonlar Ghidra
kuralıyla `FUN_00xxxxxx` diye adlandırıldı (giriş VA'sı). `DAT_` ile gösterilen adresler `.rdata`
sabitleridir. Alıntılar disassembly'dir (≤ 2 satır).

## Sınıf yerleşimi (bulguların dayanağı)

| Öğe | Adres | Kanıt |
|---|---|---|
| Contingency sınıfı vtable'ı | `0x5c6b14` | klonlayıcı `FUN_00498370` (vtable+0xc) içinde `498426: mov DWORD PTR [ebx],0x5c6b14` |
| Test adı dizesi | `0x5c6dd4` "Goodness-of-fit tests: Contingency tables" | `4989ca: movups xmm0,XMMWORD PTR ds:0x5c6dd4` |
| Varsayılanlar (w=.3, α=.05, güç=.95, N=100, df=5) | `FUN_00498a70` (vtable+0xb8) | `DAT_005bfab8`=0.3 → +0xd8, `DAT_005c6db0`={0.05,0.95} → +0xb0/+0xb8, `DAT_005c3b58`=100 → +0xe8, `DAT_005c19d8`=5 → +0x80 |
| Hesap dağıtıcısı (analiz türüne göre switch) | `FUN_00498ad0` (vtable+0xc8), atlama tablosu `0x499104` | case0 `0x498b2d` a-priori · case1 `0x498c6d` sensitivity · case2 `0x498d75` post-hoc · case3 `0x498e5a` criterion · case4 `0x498fa0` compromise |
| Mod çözücüleri (vtable 0x5c6b14) | +0x48 `FUN_00496aa0` a-priori · +0x28 `FUN_00496670` sensitivity · +0x30 `FUN_004981d0` post-hoc güç · +0x38 `FUN_004960b0` criterion · +0x40 `FUN_00496570` compromise | dağıtıcıdaki `call [eax+0x48]` vb. |

## Bulgular

| ID | Etiket | İddia | Kanıt (adres + ≤2 satır alıntı) | Güven | Açıkladığı GUI vektörü |
|---|---|---|---|---|---|
| R-01 | [REA] | "Effect size w must be greater 1e-06." tek bir dize **değil**. Dört parçadan kuruluyor: `"Effect size "` + ad `"w"` + `" must be greater "` + `ostream<<double(1e-6)` (varsayılan hassasiyet "1e-06" yazıyor) + `"."` | Dizeler: `0x5c61b4` "Effect size ", `0x5c6e4c` "w", `0x5c61c4` " must be greater ", `0x5c4ac8` ".". Kuran fonksiyon `FUN_00487880`: `4878cc: push 0x5c61b4` … `487903: push 0x5c61c4`. `<<double` = IAT `0x5be258` (MSVCP140 `basic_ostream::operator<<(double)`) | Yüksek | g19 (metin birebir) |
| R-02 | [REA] | A-priori modda w kontrolü **w ≥ 1e-6** (eşitlik kabul). Ret yalnızca `w < 1e-6` iken. Mesajdaki "greater" yanıltıcı | `FUN_00487880`: `4878b5: comisd xmm0,xmm1` / `4878c0: jb 0x4878c6` (jb → hata dalı). Çağrı yeri a-priori case'i: `498b5e: movsd xmm0,QWORD PTR ds:0x5c4970` (=1e-6), `498ba2: call 0x487880` | Yüksek | g19 (a-priori w=0 ret). **Dikkat:** g32/g33 post-hoc vektörleri, bu kontrolden değil R-03'ten geçiyor. A-priori w=1e-6 sınırı GUI'de henüz test edilmedi (önerilen vektör: a-priori w=1e-6 → kabul, w=9.99e-7 → ret) |
| R-03 | [REA] | **Belgelenmemiş:** post-hoc, criterion ve compromise modlarında w kontrolü farklı bir fonksiyonla yapılıyor ve yalnızca **w ≥ 0** isteniyor. Mesajı "Effect size w must be non-negative.". Yani post-hoc'ta **w = 0 kabul edilir** (güç = α beklenir). 1e-6 alt sınırı yalnızca a-priori'de var | `FUN_00487970`: `487998: comisd xmm0,QWORD PTR ds:0x5c29c0` (=0.0) / `4879a7: jb …`. Hata dizesi `0x5c6128` " must be non-negative." (`4879ce`). Çağrılar: `498ddc` (post-hoc), `498ec1` (criterion), `499007` (compromise) | Yüksek (statik); GUI'de **doğrulanmadı** | g32/g33 (post-hoc w=1e-6 ve 1.1e-6 kabul). Önerilen yeni vektör: post-hoc w=0 |
| R-04 | [REA] | df kontrolü **df ≥ 1.0**. df < 1 reddedilir ("Degrees of Freedom must be greater or equal one."). Kontrol switch'ten **önce**, tüm modlar için çalışıyor. Bu yüzden df hatası w/α/güç hatalarından önce gelir | `FUN_00487800`: `487806: comisd xmm0,QWORD PTR ds:0x5c19a0` (=1.0) / `48780e: jb 0x487815` → `48781b: push 0x5c615c`. Çağrı: `498b04: call 0x487800` (atlama tablosundan önce) | Yüksek | g20 |
| R-05 | [REA] | Güç ≥ α kontrolü **kapsayıcı**. Güç = α kabul, yalnızca güç < α ret. Dize `0x5c6220` | `FUN_004880e0`: `4880e6: comisd xmm0,QWORD PTR [esp+0x4]` (xmm0 = güç, [esp+4] = α) / `4880ec: jb 0x4880f3` → `4880f9: push 0x5c6220`. Çağrı a-priori'de `498c05` | Yüksek | g09 (güç=α → N=1), g10 (ret), g11 |
| R-06 | [REA] | **Belgelenmemiş:** α kabul aralığı **[1e-7, 0.9999999]** (iki uç dahil). Dışındaysa "Alpha is outside the admissible range (1e-07, 0.9999999)." | `FUN_00487530`: `487539: comisd xmm0,QWORD PTR ds:0x5c4398` (=1e-7) / `48754e: comisd xmm1,xmm0` (`DAT_005c6860`=0.9999999). Dize `0x5c6100` | Yüksek (statik) | — (yeni vektör önerisi: α=1e-8, α=0.99999995) |
| R-07 | [REA] | **Belgelenmemiş:** güç kabul aralığı da **[1e-7, 0.9999999]**. Mesaj: "Power is outside the admissible range (" | `FUN_00488110`: `488119: comisd xmm0,QWORD PTR ds:0x5c4398` / `48812e: comisd xmm1,xmm0` (0x5c6860). Dize `0x5c60d8` (`488194`) | Yüksek (statik) | g17 (güç=0.999 aralık içinde) |
| R-08 | [REA] | **Belgelenmemiş:** girdi olarak N (post-hoc/criterion/compromise/sensitivity) **tam sayı**, aralığı **[1, 2147483646]**. N = 1 kabul. Dışındaysa "Total sample size is outside the admissible range (" | `FUN_00488a10`: `488a18: cmp eax,DWORD PTR [esp+0x8]` / `488a1c: jl …`, `488a20: jg …`. Çağrı argümanları `498e0e: push 0x7ffffffe` / `498e13: push 0x1`. Dize `0x5c6524` | Yüksek | g25 (post-hoc N=1 kabul), g24 |
| R-09 | [REA] | **Belgelenmemiş:** compromise oranı q = β/α kabul aralığı **[0.01, 100]** (dahil). Mesaj: "$\beta$/$\alpha$ ratio is outside the admissible range (" | Çağrı yeri `49903b: movaps xmm0,XMMWORD PTR ds:0x5c6dc0` ({0.01, 100.0}) → `499057: call 0x4873e0`. `FUN_004873e0`: `4873ec: comisd xmm0,xmm2` / `4873f8: comisd xmm1,xmm0`. Dize `0x5c6558` | Yüksek (statik) | g27 (q=1), g28 (q=4) |
| R-10 | [REA] | A-priori sırası: df → w (≥1e-6) → α → güç → güç≥α → çözücü. Kontroller ilk hatada duruyor (her biri `je` ile çıkıyor). İlk hatanın mesajı gösterilir | `FUN_00498ad0` case0: `498ba2 call 0x487880` → `498bbf call 0x487530` → `498bdc call 0x488110` → `498c05 call 0x4880e0` → `498c5a call eax` ([vtable+0x48]) | Yüksek | g10, g19, g20 (her biri tek hata) |
| R-11 | [REA] | A-priori N araması: kök aranan fonksiyon **f(N) = güç(w, α, N) − hedef güç** (N sürekli). Kök **Brent** yöntemiyle bulunuyor (`FUN_004f9bb0`), maksimum **300 iterasyon** | Amaç `FUN_004968d0` (vtable+0x11c): `496902: call eax` ([vt+0x30] post-hoc güç) / `496904: fsub QWORD PTR [esi+0xb8]`. Çözücü `FUN_00496aa0`: `496aed: push 0x12c` / `496b03: call 0x4f9bb0` | Yüksek | g01–g05, g12–g18 |
| R-12 | [REA] | A-priori **başlangıç aralığı [1, 100]**. f(100) < 0 ise üst sınır **iterasyon sınırı olmadan ×1.6** büyütülüyor, alt sınır bir önceki üst sınır oluyor. f(100) ≥ 0 ise aralık 100'den aşağı daraltılıyor. Alt sınır en az 1'e sıkıştırılıyor | `FUN_00499150` (vtable+0x64): `499150: movaps xmm0,XMMWORD PTR ds:0x5c6e80` ({1.0, 100.0}) → `call 0x4962d0`. `FUN_004962d0` büyütme döngüsü: `49634f: mulsd xmm0,QWORD PTR ds:0x5c4ad8` (=1.6) / `496375: ja 0x496340` (sayaç yok). Sıkıştırma `49637c: comisd xmm1,QWORD PTR [esi+0x68]` | Yüksek | g06 (N=7 848 861: tavan yok), g08 |
| R-13 | [REA] | **N alt sınırı = 1.** Hedef güç N=1'de zaten aşılıyorsa (f(1) > 0) aralıkta işaret değişmez. Brent bu durumda **0.0 döndürür ve hata bayrağı koyar** (yakalanmıyor). Sonrasında `N < alt sınır` kontrolü N'yi 1'e çekiyor | Brent: `4f9c58: comisd xmm0,xmm1` (fa·fb > 0) / `4f9c5e: fldz` + `4f9c60: mov DWORD PTR [esi+0x54],0x1`. Sıkıştırma `FUN_00496aa0`: `496b3d: comisd xmm0,QWORD PTR [esi+0xe8]` / `496b47: movsd QWORD PTR [esi+0xe8],xmm0` | Yüksek | g08 (w=5 → N=1), g09, g11, g34 |
| R-14 | [REA] | **Yuvarlama:** N = ceil( floor(N*·1e10 + 0.5) / 1e10 ). Önce 10 ondalığa yuvarlanıyor, sonra yukarı. Güç N'de monoton olduğundan sonuç **güç ≥ hedef olan en küçük tam sayı**. Ayrıca 88.00000000001 gibi kayan nokta gürültüsü 89'a çıkmıyor. Yuvarlama, alt sınıra sıkıştırmadan önce ve sonra iki kez uygulanıyor | `FUN_00496a20` (vtable+0x74): `496a32: mulsd xmm0,QWORD PTR ds:0x5c4328` (=1e10) / `496a3e: addsd xmm0,QWORD PTR ds:0x5c29a8` (0.5). Thunk'lar: `0x5ac023`→`floor`, `0x5ac047`→`ceil` (api-ms-win-crt-math IAT `0x5be5b8`, `0x5be590`). Ara `modf` (`0x5be5a8`) çağrısının sonucu atılıyor (`496a73: fstp st(0)`) | Yüksek | g01 (220), g02 (88), g03 (785), g05 (129948) |
| R-15 | [REA] | Gösterilen "Actual power" **yuvarlanmış tam sayı N'de yeniden hesaplanıyor** (post-hoc fonksiyonu tekrar çağrılıyor) | `FUN_00496aa0`: `496b87: mov eax,DWORD PTR [eax+0x30]` / `496b9f: fstp QWORD PTR [esi+0x108]` | Yüksek | g01–g18 exp_actual_power |
| R-16 | [REA] | **Brent'in durma koşulu:** `tol` argümanı (1e-10, `DAT_005c3f48`) `this+0x8`'e yazılıyor ama döngüde **hiç okunmuyor**. Etkin yakınsama: \|xm\| ≤ 2⁻⁵³·\|b\| (`DAT_005c4390` = 1.11e-16) ya da f(b) == 0. Aksi halde maksimum iterasyonda durup son b'yi döndürüyor (durum bayrağı 2) | `4f9c33: movsd QWORD PTR [esi+0x8],xmm0` (tek yazma, okuma yok). `4f9d91: mulsd xmm7,QWORD PTR [esp+0x60]` (=2⁻⁵³) / `4f9db1: jae 0x4f9f73`. Maks iterasyon `4f9f3c: cmp edi,DWORD PTR [esi+0x50]` → `4f9f83: mov DWORD PTR [esi+0x54],0x2` | Orta-yüksek (fonksiyonun tamamı okundu; tol'a başka okuma bulunamadı) | g06 (aşırı küçük w'de tam N) |
| R-17 | [REA] | **Compromise çözücü:** α bilinmeyeni için f(α) = 1 − (1 − güç(α)) / (q·α) kökü aranıyor, yani β = q·α. Brent, **maks 100 iterasyon**, verilen tol 1e-10 (R-16'ya göre etkisiz, durma 2⁻⁵³ göreli). β = 1 − güç | `FUN_00496570`: `4965b6: push 0x64` / `4965c9: call 0x4f9bb0`. Amaç `FUN_00496770` (vtable+0x118): `4967b8: mulsd xmm2,QWORD PTR [esi+0xa8]` (q) / `4967cf: divsd xmm0,xmm2` | Yüksek | g27, g28 |
| R-18 | [REA] | Criterion ve compromise için α arama aralığı (`FUN_00496bc0`): f(0.5) > 0 ise [0.25, 0.5] ile başlayıp alt sınır yarıya iniyor. Değilse [0.5, 0.75] ile başlayıp üst sınır 1'e doğru yarılanıyor. Sınırlar [1e-99, 1] içine sıkıştırılıyor. Criterion maks 300 iterasyon | `496bf7: movsd xmm0,QWORD PTR ds:0x5c3f50` (0.25), `496c72: … ds:0x5c4228` (0.75), `496cd1: comisd xmm1,QWORD PTR [esi+0x68]` (`DAT_005c6848`=1e-99). Criterion `4960f6: push 0x12c` | Yüksek | g29 |
| R-19 | [REA] | Sensitivity: w için başlangıç aralığı **[1e-6, 0.5]**. güç(0.5) < hedef ise üst sınır ×1.6 büyütülüyor. Brent maks 100 iterasyon. Bu modda w girdisi olmadığı için w kontrolü yok | `FUN_00499130` (vtable+0x68): `499130: movaps xmm0,XMMWORD PTR ds:0x5c6e60` ({1e-6, 0.5}) → `call 0x4962d0`. `FUN_00496670`: `4966b6: push 0x64` | Yüksek | g30, g31 |
| R-20 | [REA] | λ = w²·N ve güç = 1 − F_ncχ²(krit; df, λ); krit = χ²(df) dağılımının (1−α) kantili (λ=0 iken). Belgelenmiş formülü binary düzeyinde doğruluyor | `FUN_00498770` (vtable+0x50): `498774: fmul st(0),st` / `498776: fmul QWORD PTR [ecx+0xe8]` (w²·N). `FUN_004981d0`: `498232: subsd xmm0,QWORD PTR [edi+0xb0]` (1−α) … `498290: fld1` / `498293: fsubrp st(1),st` | Yüksek | g21–g26 |
| R-21 | [REA] | Bilinçli bir "üst sınır N" yok. A-priori sonucu N, girdi aralığı [1, 2147483646] ile karşılaştırılmıyor. Pratikte tavan, ×1.6 büyütmenin sonlu bir değerde f ≥ 0 bulmasıdır. LEDGER L-14'teki "10⁷ tavanı" G*Power davranışı **değil**, bizim kararımız | R-12'deki sayaçsız döngü (`496340`…`496375`). `FUN_00496aa0` içinde N için `0x488a10` çağrısı yok | Orta (sayaç yok kesin; çok büyük N'de sayısal davranış test edilmedi) | g06 |
| R-22 | [REA] | Garip daraltma formülü: f(100) ≥ 0 iken yeni orta nokta `(m + lo)·0.5 − lo` (ortalama değil, ayrıca −lo). lo=1 için 50.5 → 24.75 → 11.875 → 5.4375 → 2.21875 → 0.61 (<1 → dur, 1'e sıkıştır). Sonucu etkilemiyor (Brent kökü yine bulur) ama aralık asimetrik | `FUN_004962d0`: `4963ec: addsd xmm0,xmm1` / `4963f8: subsd xmm0,xmm1` (xmm1 = lo, `4963c9`'da yeniden yüklenmiş) | Orta | g02, g04 (N<100 yolları) |

## Ghidra 12.2 doğrulaması

Ghidra 12.2 PUBLIC headless (JDK Temurin 25.0.4.1) ile otomatik analiz yapıldı (164 s, 9115 fonksiyon,
dil `x86:LE:32:default`). Ardından repo dışındaki `CheckGPower.java` post-script'i çalıştırıldı. Script yalnızca
adres ve ad yazdırıyor, decompile çıktısı yok. Log alıntısı: [ghidra_check.txt](ghidra_check.txt).

| Adres | Ghidra fonksiyon adı | Giriş noktası eşleşiyor mu | İlgili bulgular |
|---|---|---|---|
| `0x00498ad0` | `FUN_00498ad0` | evet | dağıtıcı, R-10 |
| `0x00487880` | `FUN_00487880` | evet | R-01, R-02 |
| `0x00487970` | `FUN_00487970` | evet | R-03 |
| `0x004880e0` | `FUN_004880e0` | evet | R-05 |
| `0x00496aa0` | `FUN_00496aa0` | evet | R-11, R-13, R-15 |
| `0x004962d0` | `FUN_004962d0` | evet | R-12, R-19, R-22 |
| `0x00496a20` | `FUN_00496a20` | evet | R-14 |
| `0x004f9bb0` | `FUN_004f9bb0` | evet | R-11, R-13, R-16 |
| `0x00496570` | `FUN_00496570` | evet | R-17 |

| Dize | Ghidra'nın bulduğu referanslar (adres → fonksiyon) | objdump bulgusuyla eşleşiyor mu |
|---|---|---|
| `0x5c6220` "Power must be greater than or equal to alpha." | `004880f9` → `FUN_004880e0` | evet (R-05) |
| `0x5c615c` "Degrees of Freedom must be greater or equal one." | `0048781b` → `FUN_00487800` | evet (R-04) |
| `0x5c61b4` "Effect size " | `004878cc` → `FUN_00487880`, `004879b3` → `FUN_00487970`, `00487aa0` → `FUN_00487a40`, `00487bcf` → `FUN_00487b70` | evet. İlk ikisi R-01/R-03. Son ikisi başka testlerin etki büyüklüğü kontrolleri, χ² contingency'den çağrılmıyor |
| `0x5c6128` " must be non-negative." | `004879ce` → `FUN_00487970`, `00487e5e` → `FUN_00487e00` | evet (R-03). `FUN_00487e00` noncentrality kontrolü, kapsam dışı |
| `0x5c6100` "Alpha is outside the admissible range (" | `004874ec` → `FUN_00487460`, `004875b4` → `FUN_00487530` | evet (R-06). `FUN_00487460` vtable+0x108'deki genel α kontrolü, contingency dağıtıcısı `FUN_00487530`'u çağırıyor |

Sonuç: objdump ile bulunan 9 fonksiyon girişinin tamamı ve 5 dizenin tüm referansları Ghidra'nın
analiziyle **birebir** örtüşüyor. Ghidra'nın bulduğu ek referanslar (`FUN_00487a40`, `FUN_00487b70`,
`FUN_00487e00`, `FUN_00487460`) objdump çıktısında da vardı. Bu oturumda contingency yoluna bağlı
olmadıkları için bulgu olarak yazılmamışlardı.

## Bağlanamayan / [AJAN] kalanlar

| ID | Etiket | İddia | Not |
|---|---|---|---|
| A-01 | [AJAN] | Brent'in `[esi+0x54]` durum bayrağı (1 = aralık işaret değiştirmiyor, 2 = iterasyon tükendi) GUI'de bir uyarıya bağlanıyor mu? | `FUN_00496aa0` bayrağı okumuyor. GUI katmanında okuyan olup olmadığı izlenmedi |
| A-02 | [AJAN] | Ncχ² CDF ve χ² kantil fonksiyonlarının iç algoritması (seri/yaklaşım, tolerans) | Dağılım nesnesinin (`this+0x58`) vtable'ı +0x4 (cdf), +0x8 (quantile), +0x2c (λ set). İç uygulama incelenmedi |

## Yanlış çıkan ilk inançlar (HALLUCINATIONS.md için)

1. **"A-priori alt sınır N = 2" (REA tarafında da tekrarlandı).** İlk olarak `0x5c6db0`/`0x5c6e50` varsayılanlarını kullanan ve
   `FUN_004991a0` ile klonlanan **vtable 0x5c6c40**'ı contingency sınıfı sandım. Onun aralık metodu
   `FUN_0049a210` `DAT_005c6f00` = {2.0, 100.0} ile çağırıyor. Bu, N ≥ 2 sonucunu verirdi ve g08 (N=1) ile çelişti.
   Dağıtıcı `FUN_00498ad0`'ın hangi vtable'da olduğuna bakınca (`0x5c6bdc` → vtable **0x5c6b14**)
   doğru metodun `FUN_00499150` ve aralığın {1.0, 100.0} olduğu çıktı. 0x5c6c40 kardeş bir χ² sınıfı.
   **Ders:** aynı modüldeki benzer sınıflar aynı sabit havuzunu paylaşıyor. Sınıfı test adı dizesinden ve dağıtıcının vtable slotundan doğrula.
2. **"Hata metni tek bir dize literali olarak bulunur."** "Effect size w must be greater 1e-06." binary'de
   hiç geçmiyor. Generic `FUN_00487880` metni parçalardan ve `operator<<(double)` ile kuruyor. Bu yüzden "1e-06" yazımı
   MSVC iostream'in varsayılan biçiminden geliyor, sabit bir metinden değil.
3. **"Brent'e verilen tol=1e-10 durma ölçütüdür."** Argüman nesneye yazılıyor ama hiç okunmuyor. Gerçek
   ölçüt makine epsilonu düzeyinde göreli (2⁻⁵³·|b|) ya da iterasyon sınırı.
4. **"g32 (w = 1e-6 kabul) a-priori'deki 1e-6 sınırının kanıtıdır."** g32 ve g33 post-hoc modunda. Post-hoc
   w'yi yalnızca ≥ 0 diye kontrol ediyor (R-03), yani bu vektörler 1e-6 sınırını hiç sınamıyor. Sınırın
   kapsayıcı olduğu (≥) bilgisi yalnızca binary'den geliyor (R-02). LEDGER L-15 bu iki yolu karıştırıyor.
5. **"Ghidra 12.2 + JDK 21 çalışır."** Ghidra 12.2 JDK 25 istiyor (`application.java.min=25`), headless
   başlatma anında düştü.
