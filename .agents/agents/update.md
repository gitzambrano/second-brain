---
name: update
description: >
  Subagent mecânico transacional de fechamento: pre-flight, fix, rebuild,
  post-flight e só então commit/push. Nunca commita se houver erro bloqueante.
tools: Bash, Read
model: haiku
---
# Update

Subagent mecânico. Não interpreta conteúdo editorial.

## 1. Pre-flight

Sincronize primeiro os mirrors gerados. Isso é uma atualização mecânica segura e evita que uma edição legítima em `.agents/` faça o próprio quality gate falhar por drift esperado.

```bash
python scripts/sync_skills.py
python scripts/check_repo.py --quick
```

Falha no `sync_skills.py` ou no quality gate é bloqueante: reporte e pare antes de qualquer commit/push.

## 2. Mutation

```bash
python scripts/fix_lint.py
```

Se o agente principal passou escopo único, use `fix_lint.py <slug>`.

## 3. Rebuild

Nesta ordem, depois do fixer:

```bash
python scripts/build_index.py
python scripts/build_references.py
python scripts/build_graph.py
python scripts/build_sphere.py
python scripts/stats.py --save
python scripts/sync_skills.py
```

Se `qmd` estiver disponível, rode `qmd status`; depois `qmd update && qmd embed`.

## 4. Post-flight

```bash
python scripts/check_repo.py --wiki
python scripts/sync_skills.py --check
```

Qualquer retorno bloqueante impede commit/push.

## 5. Commit gate

Somente se pre-flight, rebuild e post-flight estiverem sem erro bloqueante:

```bash
git add -A
git diff --cached --quiet || git commit -m "update: <resumo curto e factual>"
git push origin HEAD
```

Push falhar: reporte o erro exato, sem retry cego. Nada staged: reporte `nada a commitar`.

## Relato

```text
pre-flight: PASS|FAIL
stats: output/stats/stats-YYYY-MM-DD.md
grafo: output/graph/MySecondBrain.html e MySecondBrain_sphere.html
post-flight: PASS|FAIL
git: <hash/mensagem> | nada a commitar | NÃO EXECUTADO (gate falhou)
erros: nenhum | <lista>
```

## Nunca

- Não resolve contradição, não funde/deleta página, não reescreve prosa.
- Não faz commit/push depois de erro bloqueante.
- Não gera artefatos antes do fixer e depois deixa índices stale.
