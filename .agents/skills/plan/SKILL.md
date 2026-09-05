---
name: plan
description: >
  Gerencia plan/plano.md e encaminha itens para a skill correta. Use para
  adicionar, listar, retomar ou concluir tarefas, fontes, revisões, estudos e
  essays futuros de longo prazo.
metadata:
  second-brain-role: "task-router"
  second-brain-mode: "mixed"
  second-brain-scope: "plan"
  second-brain-approval: "none"
  second-brain-closure: "plan"
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch AskUserQuestion
---
# Plan

`plan/plano.md` guarda trabalho futuro. `wiki/status.md` guarda estado de curto prazo entre sessões.

## Estrutura

As cinco seções sempre existem, nesta ordem, precedidas por `# Plano` e `## Índice`.

| Seção | Campos do item | Routing típico em `/plan work` |
| --- | --- | --- |
| Tarefas | `Tópico`, `Status`, `Adicionado`, `Nota` | executar a tarefa |
| Fontes para Ingerir | `Tópico`, `Status`, `Adicionado`, `Fonte`, `Skill sugerida`, `Nota` | `/import`, `/digest`, `/absorb` |
| Revisões | `Alvo`, `Tópico`, `Status`, `Adicionado`, `Nota` | `/review`, `/continuity`, `/expand`, `/chapter` |
| Estudos | `Tópico`, `Status`, `Adicionado`, `Fonte`, `Nota` | `/study` |
| Essays Futuros | `Tópico`, `Status`, `Adicionado`, `Fonte`, `Nota` | `/outline` → `/essay` |

`Status:` é `Pendente | Em Andamento`. `Adicionado:` usa `YYYY-MM-DD`. `Tópico:` é livre, mas reuse um existente antes de criar variante equivalente.

## `/plan add`

1. Classifique o item: exploração → Estudo; tese formada → Essay Futuro; material identificado → Fonte para Ingerir; caso geral → Tarefa.
2. Preencha os campos da seção.
3. Para fonte, sugira `/import`, `/digest` ou `/absorb` quando for claro.
4. Adicione na seção correta.

Não escreva `wiki/log.md` apenas por adicionar pendência.

## `/plan work <item>`

1. Localize o item e marque `Em Andamento`.
2. Execute o routing da tabela na mesma conversa e siga a skill de destino.
3. Concluído → `/plan done`; parcial → mantenha `Em Andamento` e atualize `Nota:`.

Essay Futuro: draft em `plan/drafts/` → `/essay`; sem draft → `/outline`.

## `/plan done <item>`

Remova apenas o item; preserve a seção. Registre:

```markdown
## [YYYY-MM-DD] plano-concluído | Título
Resultado e destino, se aplicável.
```

## `/plan list`

Mostre itens por seção na ordem canônica, com título, tópico e status. Read-only. Aceite filtro por seção/tópico.

## Limites

- `/plan` gerencia e encaminha; a skill de destino produz conteúdo.
- Não use o plano para substituir `wiki/status.md`.
- Não duplique itens equivalentes.
