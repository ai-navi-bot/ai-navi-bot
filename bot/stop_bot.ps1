# Останавливает все запущенные экземпляры AI NAVI Bot.
Set-Location $PSScriptRoot

if (Get-Command py -ErrorAction SilentlyContinue) {
    py -3 -c "from singleton import stop_running_instance; stop_running_instance()"
} else {
    python -c "from singleton import stop_running_instance; stop_running_instance()"
}

Write-Host "Бот остановлен."
