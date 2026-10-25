# Oturum 2 — Yazım

## Gerçekte ne oldu

Yazım oturumu, Claude Code (Opus 5.5) içinde açılan ilk oturumdur. İlk prompt, öğrencinin ödev metnini
(yönerge dosyası) ekleyip şunu yazmasıydı:

> 4) χ² testi, olumsallık tablosu (yanıt oranları) benim konum — bu ödevi benim için yapar mısın

Bu oturum motoru, CLI'yi, MCP sunucusunu ve ajanı önce **yayımlanmış formüllerden** yazdı (CONTRACT.md ve
Cohen/G*Power makalesindeki λ = w²N modeli). Sonra davranışı iki kaynakla düzeltti:

1. G*Power GUI'sinden toplanan kara kutu vektörler (`oracle/`),
2. ayrı inceleme oturumunun (Oturum 1, `prompts/session1_inceleme.md`) bulgu düzeyindeki kuralları
   (sınırlar, kontrol sırası, yuvarlama).

Yazım oturumu decompile/disassembly çıktısını hiç açmadı. Ancak sıra yönergedekinin tersidir: kod,
SPEC.md'den önce yazıldı. README "Süreç notları"nda belirtildi.

## Hazırlanıp çalıştırılamayan temiz oda yeniden yazımı

Yönergeye tam uymak için, içinde yalnızca `SPEC.md`, `CONTRACT.md`, `tests/public_vectors.jsonl` ve
`oracle/gpower_gui_vectors.csv` bulunan bir `cleanroom` dalı oluşturuldu. Bu dalda yeni bir oturumun
aşağıdaki prompt ile kodu sıfırdan yazması planlandı. Oturum, ajan ortamının depo onayı adımı
tamamlanmadığı için başlamadı; bu yüzden teslim edilen kod bu oturumdan gelmiyor.

```
You are SESSION 2 (clean-room writer) of a university reverse-engineering assignment.
You may read ONLY the files in this worktree: SPEC.md, CONTRACT.md, tests/public_vectors.jsonl,
oracle/gpower_gui_vectors.csv. Do not run git commands that read other branches and do not read
anything outside this worktree. You have never seen and must not look for decompiled or
disassembled code.

Task: implement SPEC.md in Python (SciPy allowed for distribution functions) exactly per
CONTRACT.md for the test family chi2-contingency, all five modes. One engine module holds ALL
calculation logic; CLI, MCP server and agent are thin layers that only call it. Test-first: write
pytest tests from every Gherkin scenario in SPEC.md, the chi2 rows of tests/public_vectors.jsonl and
every row of oracle/gpower_gui_vectors.csv, plus a CLI == MCP equivalence test. Done = all tests pass.
Then write CLEANROOM_NOTES.md. Commit on this branch; do not push.
```
