#!/usr/bin/env bash
# Reindexa a wiki na busca semantica do qmd (collection "secondbrain").
# Uso: ./scripts/sync_qmd.sh (dar permissao de execucao uma vez: chmod +x scripts/sync_qmd.sh)
# Equivalente POSIX de sync_qmd.bat, para quem trabalha fora do Windows.
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v qmd >/dev/null 2>&1; then
    echo "qmd nao encontrado no PATH. Instale-o antes de rodar este script."
    exit 1
fi

echo "Atualizando indice do qmd..."
qmd update

echo
echo "Gerando/atualizando embeddings..."
qmd embed

echo
qmd status
echo
echo "Concluido."
