---
name: doctor
description: >
  Diagnóstico read-only do repositório, skills, corpus e exports. Executa
  scripts/check_repo.py sem argumentos (full) e reporta PASS/WARN/FAIL/SKIP.
  Nunca corrige, edita, commita ou faz push.
allowed-tools: Bash Read
---
# Doctor

**[script]** Diagnóstico do sistema, não manutenção editorial.

Execute:

```bash
python scripts/check_repo.py
```

Sem argumentos, `check_repo.py` executa o diagnóstico completo. Em um clone skeleton, ausência de essays/HTML/PDF é `SKIP`, não erro.

Reporte por grupo: Repository, Skills, Script defaults, Wiki, References, HTML, PDF, Environment. Não faça correções automaticamente. Se houver falha, informe o código e o caminho; encaminhe correções de conteúdo para `/organize` e falhas de infraestrutura para manutenção do repo.

Não chame o subagent `update`, não altere `wiki/`, não rode fixers, não faça commit/push.
