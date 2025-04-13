@echo off
title Resgatar Codigos Microsoft
cls

echo 1. Iniciar programa
echo 2. Desinstalar dependencias
echo 3. Sair
echo.

choice /C 123 /N /M "Escolha uma opcao: "

if errorlevel 3 exit
if errorlevel 2 (
    call uninstall.bat
    exit
)
if errorlevel 1 (
    cls
    echo Iniciando o programa...
    echo.
    python main.py
    echo.
    echo Pressione ENTER para sair...
    pause >nul
)
