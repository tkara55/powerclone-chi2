# 60-second CLI demo: types each command, then runs it for real.
# Usage: powershell -ExecutionPolicy Bypass -File demo\demo.ps1
$Host.UI.RawUI.WindowTitle = "powerclone-demo"
$exe = python -c "import os, sys; print(os.path.join(sys.prefix, 'Scripts', 'gpower-clone.exe'))"
if (-not (Test-Path $exe)) { $exe = (Get-Command gpower-clone).Source }
Set-Location (Split-Path $PSScriptRoot)

function Show($text, $ms = 18) {
    foreach ($ch in $text.ToCharArray()) { Write-Host -NoNewline $ch -ForegroundColor Yellow; Start-Sleep -Milliseconds $ms }
    Write-Host ""
}

function Step($comment, $argsLine) {
    Write-Host ""
    Write-Host "# $comment" -ForegroundColor DarkGray
    Write-Host -NoNewline "PS> " -ForegroundColor Green
    Show "gpower-clone $argsLine"
    $out = & $exe ($argsLine -split ' ')
    Write-Host $out -ForegroundColor Cyan
    Write-Host "(exit code $LASTEXITCODE)" -ForegroundColor DarkGray
    Start-Sleep -Seconds 2
}

Clear-Host
Write-Host "powerclone-chi2  |  YZM301 Teardown Sprint  |  chi2 contingency power analysis" -ForegroundColor White
Write-Host "Clean-room rewrite; reference: G*Power 3.1.9.7 (Faul, Erdfelder, Lang & Buchner)" -ForegroundColor DarkGray
Start-Sleep -Seconds 3

Step "Version / contract" "--version"
Step "A priori: how many patients? (manual example, G*Power: N = 220)" "--test chi2-contingency --mode a-priori --w 0.3 --alpha 0.05 --power 0.95 --df 5"
Step "2x2 table, medium effect (G*Power: N = 88)" "--test chi2-contingency --mode a-priori --w 0.3 --alpha 0.05 --power 0.80 --df 1"
Step "Post hoc: power with 100 patients (G*Power: 0.6235846)" "--test chi2-contingency --mode post-hoc --w 0.3 --alpha 0.05 --n_total 100 --df 5"
Step "Compromise: beta/alpha = 1" "--test chi2-contingency --mode compromise --w 0.3 --beta_alpha_ratio 1 --n_total 100 --df 5"
Step "Boundary: huge effect -> N = 1 (found in G*Power GUI + binary)" "--test chi2-contingency --mode a-priori --w 5 --alpha 0.05 --power 0.95 --df 1"
Step "Invalid: power < alpha -> error JSON, non-zero exit" "--test chi2-contingency --mode a-priori --w 0.3 --alpha 0.05 --power 0.04 --df 5"

Write-Host ""
Write-Host "# Differential report vs G*Power GUI (44 vectors) and statsmodels (799 vectors)" -ForegroundColor DarkGray
Write-Host -NoNewline "PS> " -ForegroundColor Green
Show "Select-String tests/REPORT.md -Pattern 'match'"
Select-String -Path tests\REPORT.md -Pattern "N exact match|Full match|Unexplained" | ForEach-Object { Write-Host $_.Line -ForegroundColor Cyan }
Start-Sleep -Seconds 5
