@echo off
title Desinstalar Dependencias
echo Desinstalando dependencias...
echo.

for /f "tokens=1 delims=>=" %%a in (requirements.txt) do (
    echo Removendo %%a...
    pip uninstall -y %%a
)

echo.
echo Todas as dependencias foram removidas!
echo Pressione ENTER para sair...
pause >nul
