# Oturum 1 — İnceleme (REA + Ghidra)

İlk prompt:

> REA araçları ve Ghidra sağlayıcısı bu oturumda kullanılabilir mi? Önce bunu yanıtla.
>
> Hedef: G*Power 3.1.9.7 (Windows, resmi sayfadan indirilmiş, SHA-256: `<hash>`).
> Yalnızca "χ² tests – Goodness-of-fit tests: Contingency tables" hesabını incele.
>
> Bulman gerekenler (kılavuzda OLMAYAN davranışlar):
> 1. A priori modda N nasıl aranıyor ve nasıl yuvarlanıyor? Alt ve üst sınır nedir?
> 2. Aramanın durma koşulu nedir?
> 3. Güç ≤ α, w ≤ 0, df < 1, N < 2 girdilerinde ne oluyor? Hangi mesaj dizesi gösteriliyor?
> 4. Compromise modda β/α oranı nasıl çözülüyor?
>
> Kurallar:
> - Her iddiayı bir fonksiyon adresine ya da dize referansına bağla. Bağlayamıyorsan [AJAN] yaz.
> - Yalnızca SPEC.md ve LEDGER.md üret. Kod yazma. Decompile çıktısını dosyaya kopyalama;
>   en fazla 2 satırlık alıntı kullan.
