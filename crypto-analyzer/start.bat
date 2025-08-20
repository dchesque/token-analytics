@echo off
title Crypto Analyzer v2.0
color 0A

echo ========================================
echo        CRYPTO ANALYZER v2.0
echo        Iniciando aplicacao...
echo ========================================
echo.

:: Ativa o ambiente virtual se existir
if exist venv\Scripts\activate.bat (
    echo Ativando ambiente virtual...
    call venv\Scripts\activate.bat
)

:: Executa o programa principal
python src\main.py

:: Pausa para ver erros caso o programa feche
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERRO: O programa encontrou um problema
    echo ========================================
    pause
)