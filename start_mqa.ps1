Write-Host "🚀 Starting Market Quote Assistant..." -ForegroundColor Green

$venvPath = "C:\venvs\market_quote_assistant\Scripts\Activate.ps1"

if (Test-Path $venvPath) {
    . $venvPath
}
else {
    Write-Host "❌ Virtual environment not found at $venvPath" -ForegroundColor Red
    exit 1
}

python main.py