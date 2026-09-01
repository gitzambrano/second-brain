---
name: plan
description: >
  Gerencia plan/plano.md, o plano de longo prazo: Tarefas, Fontes para
  Ingerir, Revisões, Estudos e Essays Futuros. Comandos: add, work,
  done e list. /plan work encaminha o item para a skill adequada.
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch AskUserQuestion
---
# Plan

`plan/plano.md` guarda intenção de trabalho futuro. `wiki/status.md` guarda estado de curto prazo entre sessões.

## Categorias

| Seção | Quando usar | Routing típico em `/plan work` |
| --- | --- | --- |
| Tarefas | pendência geral | executar a tarefa |
| Fontes para Ingerir | material já identificado | `/import`, `/digest`, `/absorb` |
| Revisões | conteúdo existente precisa revisão | `/review`, `/continuity`, `/expand`, `/chapter` |
| Estudos | tema ainda exploratório | `/study` |
| Essays Futuros | tese/ideia pronta para estruturar | `/outline` → `/essay` |

As cinco seções sempre existem e permanecem nesta ordem.

## Formato

```markdown
# Plano

## Índice
- [Tarefas](#tarefas)
- [Fontes para Ingerir](#fontes-para-ingerir)
- [Revisões](#revisões)
- [Estudos](#estudos)
- [Essays Futuros](#essays-futuros)

## Tarefas

### Título
- Tópico: ...
- Status: Pendente | Em Andamento
- Adicionado: YYYY-MM-DD
- Nota: ...

## Fontes para Ingerir

### Título
- Tópico: ...
- Status: Pendente | Em Andamento
- Adicionado: YYYY-MM-DD
- Fonte: ...
- Skill sugerida: /import | /digest | /absorb
- Nota: ...

## Revisões

### Título
- Alvo: [[slug|Página]]
- Tópico: ...
- Status: Pendente | Em Andamento
- Adicionado: YYYY-MM-DD
- Nota: ...

## Estudos

### Título
- Tópico: ...
- Status: Pendente | Em Andamento
- Adicionado: YYYY-MM-DD
- Fonte: ...
- Nota: ...

## Essays Futuros

### Título
- Tópico: ...
- Status: Pendente | Em Andamento
- Adicionado: YYYY-MM-DD
- Fonte: ...
- Nota: ...
```

`Tópico:` é livre, mas reuse um existente antes de criar variante equivalente.

## `/plan add`

1. Classifique o item.
   - Estudo vs Essay Futuro: exploração vs tese já formada.
   - Tarefa vs Fonte para Ingerir: existe ou não material identificado.
2. Preencha os campos da categoria.
3. Em Fonte para Ingerir, sugira `/import`, `/digest` ou `/absorb` quando for claro.
4. Adicione na seção correta.

Não escreva `wiki/log.md` apenas por adicionar uma pendência.

## `/plan work <item>`

1. Localize o item.
2. Marque `Status: Em Andamento`.
3. Execute o routing da tabela dentro da mesma conversa; leia a skill de destino e siga-a.
4. Se concluir, execute `/plan done`.
5. Se ficar parcial, mantenha `Em Andamento` e atualize `Nota:` com o progresso.

Para Essays Futuros:
- draft existente em `plan/drafts/` → `/essay`;
- sem draft → `/outline` primeiro.

## `/plan done <item>`

Remova apenas o item; preserve a seção.

Registre:

```markdown
## [YYYY-MM-DD] plano-concluído | Título
Resultado e destino, se aplicável.
```

## `/plan list`

Mostre itens por seção na ordem canônica, com título, tópico e status. Read-only. Aceite filtro por seção/tópico.

## Limites

- `/plan` gerencia e encaminha; conteúdo é produzido pela skill de destino.
- Não use o plano para substituir `wiki/status.md`.
- Não duplique itens equivalentes.
