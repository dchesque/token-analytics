@echo off
echo 🚀 Crypto Analyzer - Script de Instalacao para Windows
echo.
echo Verificando Python...

REM Tentar diferentes comandos Python
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Python encontrado
    set PYTHON_CMD=python
    goto :install
)

python3 --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Python3 encontrado
    set PYTHON_CMD=python3
    goto :install
)

py --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Python Launcher encontrado
    set PYTHON_CMD=py
    goto :install
)

echo ❌ Python nao foi encontrado!
echo.
echo 📋 Para resolver:
echo 1. Instale Python de https://python.org
echo 2. Ou instale via Microsoft Store
echo 3. Certifique-se que Python esta no PATH
echo.
pause
exit /b 1

:install
echo.
echo 📦 Instalando dependencias...
%PYTHON_CMD% -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar dependencias
    pause
    exit /b 1
)

echo.
echo 🧪 Executando testes...
%PYTHON_CMD% setup_test.py

echo.
echo ✨ Instalacao concluida!
echo.
echo 💡 Para usar:
echo    %PYTHON_CMD% src/main.py
echo.
pause