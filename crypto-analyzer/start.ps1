# Crypto Analyzer v2.0 - PowerShell Launcher
# =============================================

# Define cores
$Host.UI.RawUI.BackgroundColor = "Black"
$Host.UI.RawUI.ForegroundColor = "Green"
Clear-Host

Write-Host ""
Write-Host "  ╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║                                                          ║" -ForegroundColor Cyan
Write-Host "  ║              CRYPTO ANALYZER v2.0                       ║" -ForegroundColor Cyan
Write-Host "  ║           Análise Inteligente de Tokens                 ║" -ForegroundColor Cyan
Write-Host "  ║                                                          ║" -ForegroundColor Cyan
Write-Host "  ╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Verifica Python
Write-Host "  Verificando ambiente..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python instalado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python não encontrado! Instale em: https://www.python.org" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit
}

# Verifica .env
if (Test-Path ".env") {
    Write-Host "  ✓ Arquivo .env encontrado" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Arquivo .env não encontrado - modo básico ativo" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  Iniciando aplicação..." -ForegroundColor Cyan
Write-Host ""

# Muda para o diretório do script
Set-Location $PSScriptRoot

# Executa a aplicação
python src\main.py $args

# Pausa se houver erro
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "  ✗ Erro durante execução!" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
}