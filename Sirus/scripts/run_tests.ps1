# run_tests.ps1

# --- Настройки ---
$ProjectPackage = "services"
$TestPath = "tests"
$CoverageReportPath = ".coverage_html"
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8' # (опционально, но полезно)

Write-Host "--- Inisialization среды тестирования ---"

# Переход в корневой каталог проекта
Set-Location (Join-Path $PSScriptRoot "..")

Write-Host "--- Start tests и сбор покрытия ---"

# Выполняем pytest. Захват кода выхода ($LASTEXITCODE) необходим для проверки успеха.
try {
    # Запускаем команду и подавляем стандартный вывод, чтобы захватить код выхода
    & python -m pytest $TestPath --cov=$ProjectPackage --cov-report=term --cov-report=html:$CoverageReportPath -v 
    
    $ExitCode = $LASTEXITCODE

} catch {
    Write-Host "Critical Error for pytest" -ForegroundColor Red
    $ExitCode = 1
}

# --- Анализ и отчет ---
Write-Host "--- Analis result ---"

if ($ExitCode -eq 0) {
    Write-Host "✅ ALL TESTS PASSED SUCCESSFULLY." -ForegroundColor Green
} else {
    Write-Host "❌ ERROR: Tests failed. Exit code: $ExitCode" -ForegroundColor Red
}

exit $ExitCode