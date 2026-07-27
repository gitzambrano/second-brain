---
name: plan
description: >
  Orquestra plan/plano.md, o plano de longo prazo do Usuário: tarefas,
  fontes para ingerir, revisões, estudos e essays futuros — tudo que
  não é para agora, mas não pode ser esquecido entre sessões. Comandos:
  add (registrar um item novo em qualquer uma das 5 categorias), work
  (retomar um item e conduzir o fluxo certo, chamando /study, /essay,
  /import, /digest, /absorb, /continuity ou /expand conforme o caso),
  done (marcar concluído), list (mostrar o plano). Use quando o
  Usuário disser "anota isso para depois", "o que falta fazer",
  "retoma aquele item do plano", "tira isso do plano", ou trouxer
  qualquer pendência de longo prazo — de estudar algo a revisar um
  essay a uma tarefa qualquer que não seja sobre a wiki.
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch AskUserQuestion
---

# Plan

`plan/plano.md` é o único lugar para pendência de longo prazo do Usuário — a intenção de fazer algo, não o trabalho em si. `/plan` é quem gerencia esse arquivo e, quando o Usuário quer retomar um item, quem conduz para a skill certa. As skills que fazem o trabalho de fato (`/study`, `/essay`, `/import`, `/digest`, `/absorb`, `/continuity`, `/expand`, `/scout`) não sabem nada sobre o plano — só `/plan` sabe orquestrar.

Não confunda com `wiki/status.md` (skill `/status`): isso é pendência de **sessão para sessão** ("onde eu parei ontem"). `plan/plano.md` é pendência de **longo prazo**, sem prazo definido, que pode ficar meses esperando.

## As 5 categorias, e por que essa ordem

`plan/plano.md` é organizado em 5 seções fixas, sempre nesta ordem — do mais mecânico/concreto ao mais aberto/sem prazo:

1. **Tarefas** — qualquer pendência de longo prazo que não é sobre a wiki (um passo de projeto de engenharia, um lembrete). Mais parecida com um to-do direto.
2. **Fontes para Ingerir** — já existe material identificado (um PDF, um link, uma ideia com fonte clara), só falta processar. Trabalho mecânico: rodar `/import`, `/digest` ou `/absorb`.
3. **Revisões** — algo que **já existe** na wiki (essay, concept, entity) e precisa ser revisitado: a tese ainda se sustenta? um dado desatualizou? uma definição ficou rasa?
4. **Estudos** — algo que o Usuário quer aprender, ainda em fase de exploração, sem fonte fechada nem tese formada.
5. **Essays Futuros** — ideia de essay/white paper já suficientemente madura (tese em esboço), só falta escrever.

Essa ordem não é arbitrária: cada categoria pressupõe menos trabalho prévio de exploração e mais trabalho de execução do que a seguinte — Tarefas e Fontes para Ingerir são "só fazer", Revisões e Estudos ainda pedem leitura/reflexão, Essays Futuros é o que está mais perto de virar conteúdo.

Ao mostrar `/plan list`, respeite essa ordem — é ela que sugere por onde começar quando o Usuário não sabe o que priorizar.

## Formato de `plan/plano.md`

```markdown
# Plano

## Índice
- [Tarefas](#tarefas)
- [Fontes para Ingerir](#fontes-para-ingerir)
- [Revisões](#revisões)
- [Estudos](#estudos)
- [Essays Futuros](#essays-futuros)

## Tarefas

### Título da tarefa
- Tópico: zquoridor | BEMT | Psicometria | ... (livre, reuse antes de criar um novo)
- Status: Pendente | Em Andamento
- Adicionado: YYYY-MM-DD
- Nota: descrição breve.

## Fontes para Ingerir

### Título
- Tópico: ...
- Status: Pendente | Em Andamento
- Adicionado: YYYY-MM-DD
- Fonte: link ou descrição de onde/como conseguir o material
- Skill sugerida: /import | /digest | /absorb
- Nota: por que essa fonte importa.

## Revisões

### Título
- Alvo: [[Essay ou Concept/Entity a revisar]]
- Tópico: ...
- Status: Pendente | Em Andamento
- Adicionado: YYYY-MM-DD
- Nota: o que especificamente merece revisão — a tese inteira? um capítulo? um dado que pode ter mudado?

## Estudos

### Título
- Tópico: ...
- Status: Pendente | Em Andamento
- Adicionado: YYYY-MM-DD
- Fonte: [[wikilink]] | link externo | (sem fonte — ideia solta)
- Nota: o que se quer entender e por quê.

## Essays Futuros

### Título
- Tópico: ...
- Status: Pendente | Em Andamento
- Adicionado: YYYY-MM-DD
- Fonte: [[wikilink]] | link | (sem fonte)
- Nota: a tese/ideia central, já esboçada.
```

As 5 seções (`##`) sempre existem, mesmo vazias, para o Índice não quebrar. Dentro de cada seção, itens (`###`) não têm ordem obrigatória. `Tópico:` é livre, mas segue a mesma disciplina de reuso do vocabulário de tags (ver `conventions/SKILL.md`) — não crie um tópico novo se um existente já cobre a mesma área.

## `/plan add`

1. Pergunte (ou infira do que o Usuário disse) em qual das 5 categorias o item entra. Se ambíguo entre Estudo e Essay Futuro, pergunte: "já tem uma tese em mente, ou ainda é exploração?" — tese esboçada é Essay Futuro, exploração é Estudo. Se ambíguo entre Tarefa e Fonte para Ingerir, pergunte se já existe material identificado.
2. Colete os campos daquela categoria (ver formato acima).
3. Se `Fontes para Ingerir`, sugira `Skill sugerida:` com base no tipo de material (ensaio completo do autor → `/import`; artigo/vídeo/PDF para resumir → `/digest`; fonte que só embasa claims específicos → `/absorb`). Se não estiver claro, deixe em branco — `/plan work` decide na hora.
4. Adicione sob a seção certa. Não gera entrada em `wiki/log.md` — só `/plan done` e `/plan work` (quando resultam em algo concreto) geram.

## `/plan work <item>`

O comando que de fato conduz o trabalho, chamando a skill certa:

1. Localize o item (pergunte se houver ambiguidade entre seções/tópicos).
2. Marque `Status: Em Andamento`.
3. Dependendo da seção do item, siga o fluxo da skill correspondente **dentro da mesma conversa** (leia o `SKILL.md` dela e execute, não peça pro Usuário digitar outro comando):
   - **Tarefas** → normalmente não envolve a wiki. Pergunte o que o Usuário precisa (pode ser fora do escopo deste sistema — tudo bem, ajude do jeito que der).
   - **Fontes para Ingerir** → siga `/import`, `/digest` ou `/absorb` (o que estiver em `Skill sugerida:`, ou pergunte se estiver vazio).
   - **Revisões** → abra o `Alvo:`, leia por inteiro, e siga `/continuity` (reler e avaliar sem editar) ou `/expand` (se a revisão já revelar que precisa de conteúdo novo) — decida com base no que a `Nota:` do item pede.
   - **Estudos** → siga `/study`.
   - **Essays Futuros** → se já existe `plan/drafts/<slug>.md` referenciado na `Nota:`, siga direto `/essay` (ele lê o esboço). Se ainda não existe esqueleto, rode `/outline` primeiro — `/essay` não escreve prosa sem esboço aprovado, exceto quando a fonte é `/import`.
4. Ao final do trabalho, se o item foi de fato concluído, rode `/plan done` nele. Se só avançou parcialmente, deixe `Status: Em Andamento` e registre o progresso na `Nota:`.

## `/plan done <item>`

1. Localize o item pela seção/título.
2. Remova da seção (a seção `##` em si nunca é removida, mesmo vazia).
3. Registre em `wiki/log.md`:

   ```
   ## [YYYY-MM-DD] plano-concluído | Título do item
   Descrição breve do que foi feito e, se aplicável, para onde foi (essay/concept/entity resultante, ou fonte processada).
   ```

## `/plan list`

Leia `plan/plano.md` e mostre um resumo por seção, na ordem canônica (Tarefas → Fontes para Ingerir → Revisões → Estudos → Essays Futuros), com título + tópico + status de cada item. Read-only. Pode filtrar por seção ou por tópico se o Usuário pedir.

## Regras

1. **`/plan` nunca produz conteúdo de wiki sozinho** — só gerencia a lista e decide qual skill chamar. Quem escreve é sempre a skill de destino.
2. **Reuse tópicos antes de criar um novo.**
3. **Não duplique `wiki/status.md`** — pendência de sessão-a-sessão não é plano de longo prazo.
4. Se um item de `Fontes para Ingerir` ficar muito tempo parado, considere sugerir `/scout` para achar mais material antes de tentar ingerir com o que tem.

## Skills relacionadas

- `/study` — o trabalho de fato por trás de um item `Estudo`
- `/essay` — o trabalho de fato por trás de um item `Essay Futuro`
- `/import`, `/digest`, `/absorb` — o trabalho de fato por trás de um item `Fontes para Ingerir`
- `/continuity`, `/expand` — o trabalho de fato por trás de um item `Revisão`
- `/scout` — pesquisa fontes candidatas para qualquer item que precise
- `/status` — pendências agregadas do plano (contagem por seção) aparecem no snapshot de sessão
- `/organize` — audita a estrutura do plano (as 5 seções existem, `Status:` usa o vocabulário certo, tópicos não fragmentaram)
