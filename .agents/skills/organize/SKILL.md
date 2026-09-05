---
name: organize
description: >
  Audita e corrige estrutura, metadados, links internos, referências e derivados
  sem reescrever argumento. Use em um essay ou no corpus; commit/push só ocorre
  se o Usuário autorizar explicitamente o subagent update.
metadata:
  second-brain-role: "maintenance-orchestrator"
  second-brain-mode: "mixed"
  second-brain-scope: "essay-or-corpus"
  second-brain-approval: "before-remote"
  second-brain-closure: "mechanical"
allowed-tools: Bash Read Write Edit Glob Grep AskUserQuestion WebFetch WebSearch
---
# Organize

Manutenção mecânica e de metadados. Estrutura, estilo e formato canônico vivem em `conventions/SKILL.md`.

Não reescreva argumento ou prosa substantiva. Para isso use `/sweep`, `/review`, `/expand` ou `/chapter`.

## Escopo

```text
/organize          → corpus inteiro
/organize <slug>   → essay específico
```

## Essay específico

1. Resolva o slug; pergunte somente se houver ambiguidade real.
2. Execute:

```bash
python scripts/check_wiki.py <slug> --json
python scripts/check_references.py --file <slug> --json
python scripts/fix_lint.py <slug>
```

3. Aplique correções mecânicas inequívocas e reporte o que exigir julgamento.
4. Não rode auditorias globais de órfãos, manifesto, plano, insights, grafo ou stats.
5. Regenere `build_references.py` somente se referências mudarem e `build_index.py` somente se campos do índice mudarem.

## Corpus inteiro

### Baseline e fixer

```bash
python scripts/build_index.py
python scripts/build_references.py
python scripts/check_wiki.py --json
python scripts/check_references.py --json
python scripts/fix_lint.py
python scripts/build_index.py
python scripts/build_references.py
```

Preserve o baseline anterior ao fixer para explicar o que mudou.

### Saúde estrutural

```bash
python scripts/find_backlinks.py --orphans
python scripts/check_gaps.py --tags-only
python scripts/check_dedupe.py
```

Interprete os achados sem transformar heurística em decisão editorial:

- órfão total → proponha destino/fusão/remoção;
- tag rasa → sinal de cobertura, não correção automática;
- quase-duplicata → proponha `/merge`, nunca funda sozinho;
- link externo quebrado → encaminhe para `/linkify`;
- referência incerta → verifique a fonte antes de editar.

### Sources, plano e insights

Confira manifesto/mapa, tipo e subpasta de source, vocabulário de tags, estrutura de `plan/plano.md`, `wiki/log.md` append-only e maturidade/conexões de insights.

Aplique diretamente apenas correções inequívocas. Ambiguidade de tipo, fusão, renomeação conceitual, órfão sem destino ou contradição exige decisão do Usuário.

`FM_NO_SUMMARY` e suficiência bibliográfica são achados editoriais: reporte, não escreva summary nem invente referência dentro de `/organize`.

## Fechamento e remoto

`/organize` pode deixar derivados locais em dia, mas **não faz push por conta própria**.

No corpus, depois do relatório, ofereça o subagent `.agents/agents/update.md`. Só execute `update` após autorização explícita; ele valida, reconstrói derivados, commita e faz push em `./` e `data/`.

## Relatório

Agrupe em:

- corrigido automaticamente;
- crítico — decisão necessária;
- atenção;
- informativo.

Não cole JSON bruto. Liste nominalmente arquivos quando isso for necessário para agir.

## Log

Quando houver mudança:

```markdown
## [YYYY-MM-DD] organize | Resumo
```

Não altere `updated:` por manutenção mecânica.
