#!/usr/bin/env bash
# Reindexa a wiki na busca semantica do qmd (collection "secondbrain").
# A collection precisa apontar para DATA_ROOT/wiki (repo privado second-brain-data),
# nao para a raiz do engine.
# Uso: ./scripts/sync_qmd.sh (dar permissao de execucao uma vez: chmod +x scripts/sync_qmd.sh)
# Equivalente POSIX de sync_qmd.bat, para quem trabalha fora do Windows.
set -euo pipefail
cd "$(dirname "$0")/.."
DATA_WIKI="$(python scripts/repo_paths.py | sed -n 's/^WIKI_ROOT=//p')"
if [ -n "$DATA_WIKI" ] && [ ! -d "$DATA_WIKI" ]; then
    echo "WIKI_ROOT nao existe: $DATA_WIKI"
    exit 1
fi

if ! command -v qmd >/dev/null 2>&1; then
    echo "qmd nao encontrado no PATH. Instale-o antes de rodar este script."
    exit 1
fi

echo "Collection secondbrain deve apontar para: $DATA_WIKI"
echo
echo "Atualizando indice do qmd..."
qmd update

echo
echo "Gerando/atualizando embeddings..."
qmd embed

echo
qmd status
echo
echo "Concluido."
