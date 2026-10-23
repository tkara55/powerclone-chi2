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

## H-6: Hata mesajı, kontrolü doğru anlatır (G*Power'ın kendi metni)

- **Varsayım:** "Effect size w must be greater 1e-06." mesajı w = 1e-6'nın reddedildiğini söyler.
- **Gerçek:** w = 1e-6 tam değeri kabul ediliyor (g32); yalnızca daha küçükleri reddediliyor (g19). Mesaj ile kontrol uyuşmuyor; motor GUI'yi izliyor.
