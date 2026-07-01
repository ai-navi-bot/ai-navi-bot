# Запускает AI NAVI Bot отдельным процессом (не зависит от терминала Cursor).
Set-Location $PSScriptRoot

if (Get-Command py -ErrorAction SilentlyContinue) {
    py -3 -c "from singleton import stop_running_instance; stop_running_instance()"
} else {
    python -c "from singleton import stop_running_instance; stop_running_instance()"
}

Start-Sleep -Seconds 2

$python = if (Get-Command py -ErrorAction SilentlyContinue) { "py" } else { "python" }
$args = if ($python -eq "py") { @("-3", "app.py", "--force") } else { @("app.py", "--force") }

Start-Process -FilePath $python -ArgumentList $args -WorkingDirectory $PSScriptRoot -WindowStyle Hidden

Start-Sleep -Seconds 3

if (Test-Path "$PSScriptRoot\data\bot.lock") {
    $pid = Get-Content "$PSScriptRoot\data\bot.lock"
    Write-Host "Бот запущен (PID $pid)."
} else {
    Write-Host "Не удалось запустить бота. Проверьте логи."
    exit 1
}
