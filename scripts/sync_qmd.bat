@echo off
REM Reindexa a wiki na busca semantica do qmd (collection "secondbrain").
REM A collection precisa apontar para DATA_ROOT\wiki (repo privado second-brain-data).
REM Uso: so dar dois cliques neste arquivo, ou rodar `scripts\sync_qmd.bat` do terminal.
cd /d "%~dp0.."

where qmd >nul 2>nul
if errorlevel 1 (
    echo qmd nao encontrado no PATH. Instale-o antes de rodar este script.
    pause
    exit /b 1
)

for /f "tokens=1,* delims==" %%A in ('python scriptsepo_paths.py ^| findstr /b "WIKI_ROOT="') do set "DATA_WIKI=%%B"
if not exist "%DATA_WIKI%" (
    echo WIKI_ROOT nao existe: %DATA_WIKI%
    pause
    exit /b 1
)
echo Collection secondbrain deve apontar para: %DATA_WIKI%
echo.
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
