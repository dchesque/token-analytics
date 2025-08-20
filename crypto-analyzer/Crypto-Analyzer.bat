@echo off
:: ====================================
:: Crypto Analyzer v2.0 - Launcher
:: ====================================

title 🚀 Crypto Analyzer v2.0
color 0B
cls

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║                                                          ║
echo  ║              CRYPTO ANALYZER v2.0                       ║
echo  ║           Analise Inteligente de Tokens                 ║
echo  ║                                                          ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.
echo  Inicializando...
echo.

:: Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERRO] Python nao foi encontrado!
    echo.
    echo  Por favor, instale Python 3.8 ou superior:
    echo  https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: Mostra versão do Python
echo  [OK] Python instalado:
python --version
echo.

:: Verifica e instala dependências se necessário
echo  Verificando dependencias...
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo  Instalando dependencias necessarias...
    pip install -r requirements.txt
    echo.
)

:: Carrega variáveis de ambiente do .env se existir
if exist .env (
    echo  [OK] Arquivo .env encontrado
) else (
    echo  [INFO] Arquivo .env nao encontrado - usando modo basico
    echo  Para habilitar todas as funcionalidades, copie .env.example para .env
)
echo.

:: Inicia a aplicação
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║             INICIANDO APLICACAO...                      ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"
python src\main.py %*

:: Se o programa fechar com erro, mantém a janela aberta
if errorlevel 1 (
    echo.
    echo  ╔══════════════════════════════════════════════════════════╗
    echo  ║                      ERRO!                              ║
    echo  ║   O programa encontrou um problema e foi fechado        ║
    echo  ╚══════════════════════════════════════════════════════════╝
    echo.
    echo  Pressione qualquer tecla para fechar...
    pause >nul
)