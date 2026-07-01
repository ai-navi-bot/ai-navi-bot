# Перезапускает AI NAVI Bot (остановка + запуск одного экземпляра).
Set-Location $PSScriptRoot

& "$PSScriptRoot\stop_bot.ps1"
Start-Sleep -Seconds 2

Write-Host "Запуск бота..."
if (Get-Command py -ErrorAction SilentlyContinue) {
    py -3 app.py --force
} else {
    python app.py --force
}
