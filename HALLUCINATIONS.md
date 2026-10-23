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

## Eklenecek (REA oturumu)

En az bir tanesi G*Power davranışına dair olmalı; örneğin ajanın "a-priori aramanın alt sınırı 2" iddiası (L-11) GUI vektörü g07/g08 ile sınanınca doğru mu çıktı?
