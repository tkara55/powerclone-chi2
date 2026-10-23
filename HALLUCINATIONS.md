# HALLUCINATIONS — Ajanın yanlış çıkardığı şeyler

Yazım oturumundaki (Claude Code, Opus 5.5) gerçek hatalar. REA oturumundan çıkanlar da buraya eklenmeli.

## H-1: MCP SDK API'si "bilinen" sanıldı

- **Ne iddia etti:** MCP sunucusu `from mcp.server.fastmcp import FastMCP` ile kurulur.
- **Gerçek:** Kurulu sürüm `mcp 2.3.0`; bu sürümde sınıf `mcp.server.mcpserver.MCPServer` olarak yeniden adlandırılmış.
- **Nasıl fark edildi:** `tests/test_mcp_equivalence.py` gerçek bir stdio MCP oturumu açtığında sunucu `ModuleNotFoundError` ile düştü.
- **Ders:** Ajanın eğitim verisindeki API, kurulu sürümle aynı değildir. Düzeltme: iki sürümü de deneyen import.

## H-2: Hata kodunun önceliği yanlış kuruldu

- **Ne iddia etti:** CLI ayrıştırıcısı tanınmayan her alanı hemen `UNKNOWN_PARAM` ile reddedebilir.
- **Gerçek:** `--test t2-indep --tails 1 --d 0.5 ...` için doğru yanıt `UNSUPPORTED` (test ailesi desteklenmiyor); alan hatası değil. Kontrol sırası: test → mode → alanlar.
- **Nasıl fark edildi:** `tests/test_public_vectors.py::test_other_families_unsupported` 20 vektörde başarısız oldu.
- **Ders:** Gizli vektörlerde `code` eşleşmesi ek puan; sıralama bir davranış kuralıdır.

## H-3 (açık, [AJAN]): statsmodels her yerde kâhin olabilir

- **Varsayım:** statsmodels `GofChisquarePower.solve_power` her girdide kesirli N döndürür.
- **Gerçek:** w = 1.2 gibi çok büyük etkilerde kök bulucu yakınsamıyor ve `nan` döndürüyor.
- **Nasıl fark edildi:** `tests/differential.py` `ValueError: cannot convert float NaN to integer` ile durdu.
- **Ders:** İkinci kâhin de yanılabilir; bu satırlar raporda "atlandı" olarak sayılıyor, G*Power GUI vektörüyle (g07, g08) kapatılmalı.

## H-4: "a-priori aramanın alt sınırı N = 2" (G*Power davranışı)

- **Ne iddia etti:** Sözleşmedeki `n_total ≥ 2` girdi aralığından, G*Power'ın da N'yi 2'den aradığı çıkarıldı (eski L-11, [AJAN]).
- **Gerçek:** G*Power w = 5 için **N = 1** döndürüyor.
- **Nasıl fark edildi:** GUI vektörü g08 (ekran görüntüsü `oracle/screenshots/g08.png`); diferansiyel rapor uyuşmazlık gösterdi.
- **Yakalayan test:** `test_huge_effect_hits_minimum_n` (düzeltmeden sonra N=1 bekliyor).

## H-5: "güç = α ise hata" (G*Power davranışı)

- **Ne iddia etti:** Sözleşmedeki örnek hata ("Power, alpha değerinden büyük olmalı") yüzünden güç ≤ α'nın reddedildiği varsayıldı.
- **Gerçek:** G*Power güç = α'yı kabul ediyor (N = 1); mesajı "Power must be greater than or equal to alpha." — yalnızca güç < α reddediliyor.
- **Nasıl fark edildi:** GUI vektörleri g09 (güç = α → N=1) ve g10 (güç < α → hata penceresi).
- **Yakalayan test:** `test_power_equal_alpha_is_accepted`.

## H-7 (inceleme oturumu): yanlış sınıf, yanlış alt sınır

- **Ne iddia etti:** İnceleme ajanı ilk olarak vtable `0x5c6c40`'ı contingency sınıfı sandı. Onun aralık metodu `{2.0, 100.0}` kullanıyor → "alt sınır N = 2".
- **Gerçek:** Dağıtıcı `FUN_00498ad0` vtable `0x5c6b14`'te; doğru aralık `{1.0, 100.0}` (`FUN_00499150`). `0x5c6c40` kardeş bir χ² sınıfı.
- **Nasıl fark edildi:** GUI vektörü g08 (N = 1) statik çıkarımla çelişti.
- **Ders:** Aynı modüldeki sınıflar sabit havuzunu paylaşıyor; sınıfı dağıtıcının vtable slotundan doğrula.

## H-8 (inceleme oturumu): "Brent'e verilen tol = 1e-10 durma ölçütüdür"

- **Gerçek:** Argüman nesneye yazılıyor (`4f9c33`) ama döngüde hiç okunmuyor; durma ölçütü 2⁻⁵³·|b| ya da iterasyon sınırı (R-16).
- **Nasıl fark edildi:** Brent fonksiyonunun tamamı okunup `[esi+0x8]` için okuma bulunamadı.

## H-9 (yazım oturumu): post-hoc vektörü a-priori sınırının kanıtı sanıldı

- **Ne iddia etti:** LEDGER L-15'te g32 (post-hoc, w = 1e-6 kabul) "w ≥ 1e-6 sınırı kapsayıcı" kanıtı olarak yazıldı.
- **Gerçek:** Post-hoc w'yi yalnızca ≥ 0 diye kontrol ediyor (R-03, `FUN_00487970`); 1e-6 sınırı yalnızca a-priori'de. Motor da bu yüzden post-hoc'ta 0 < w < 1e-6'yı yanlışlıkla reddediyordu.
- **Nasıl fark edildi:** İnceleme oturumu işaret etti; yeni GUI vektörleri g35–g37 doğruladı.
- **Yakalayan test:** `test_gpower_admissible_edges_accepted`, `test_no_n_ceiling`.

## H-6: Hata mesajı, kontrolü doğru anlatır (G*Power'ın kendi metni)

- **Varsayım:** "Effect size w must be greater 1e-06." mesajı w = 1e-6'nın reddedildiğini söyler.
- **Gerçek:** w = 1e-6 tam değeri kabul ediliyor (g32); yalnızca daha küçükleri reddediliyor (g19). Mesaj ile kontrol uyuşmuyor; motor GUI'yi izliyor.
