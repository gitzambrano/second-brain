@echo off
REM Reindexa a wiki na busca semantica do qmd (collection "secondbrain").
REM Uso: so dar dois cliques neste arquivo, ou rodar `scripts\sync_qmd.bat` do terminal.
cd /d "%~dp0.."

where qmd >nul 2>nul
if errorlevel 1 (
    echo qmd nao encontrado no PATH. Instale-o antes de rodar este script.
    pause
    exit /b 1
)

echo Atualizando indice do qmd...
qmd update
if errorlevel 1 goto :erro

echo.
echo Gerando/atualizando embeddings...
qmd embed
if errorlevel 1 goto :erro

echo.
qmd status
echo.
echo Concluido.
pause
exit /b 0

:erro
echo Falhou ao atualizar o indice do qmd.
pause
exit /b 1
