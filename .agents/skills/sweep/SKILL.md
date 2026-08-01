---
name: sweep
description: >
  Orquestra a bateria completa de revisão num essay ou no corpus inteiro:
  /organize (passada mecânica) → /continuity → /proofread → /polish →
  /linkify, e produz um relatório consolidado. Aceita escopo corpus
  inteiro (/sweep) ou essay único (/sweep <slug>) — a lógica é idêntica,
  só o conjunto de arquivos processados muda. Use quando o Usuário disser
  "corrige todos os essays", "faz uma revisão geral", "passa o pente fino
  na wiki inteira", "passa o pente fino nesse essay", ou quiser a bateria
  completa de correções sem invocar cada skill manualmente. É um
  orquestrador: chama outros skills, não duplica a lógica deles.
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch AskUserQuestion
---

# Sweep

Roda a bateria completa de revisão — `/organize` (passada mecânica, no escopo correspondente) → `/continuity` → `/proofread` → `/polish` → `/linkify` — em qualquer escopo pedido pelo Usuário, e consolida os resultados num único relatório. É um **orquestrador**: toda a lógica de cada correção vive no skill correspondente.

## O que é e o que não é

- **É**: pente fino completo de um essay ou todos essays, cobrindo formatação, continuidade, português, estilo e links.
- **Não é**: `/organize` (saúde da wiki: índice, manifesto, orphans — rode antes para decidir se vale um sweep). Não é `/review` (validade argumentativa e profundidade de conteúdo).

## Escopo

```
/sweep              → corpus inteiro: todos os essays em wiki/essays/
/sweep <slug>       → um essay específico, identificado por slug, título parcial ou nome .md
```

A lógica é exatamente a mesma nos dois casos — apenas o conjunto de arquivos processados muda. O relatório final tem o mesmo formato. Se o argumento for ambíguo (ex: `/sweep física` poderia casar com dois essays), pergunte antes de prosseguir.

## Regras de status

Conforme `conventions/SKILL.md`:

- **Corpus inteiro**: pula essays com `status: finalizado` ou `maduro` — sem perguntar, sem avisar durante a execução. No resumo final, informa quantos foram pulados.
- **Essay específico**: executa normalmente, mesmo que `finalizado` ou `maduro`. Ao final, se o essay estava `finalizado`, avisa: "Este essay estava marcado como finalizado; executei porque você pediu diretamente."

## Passo a passo

**Execute os passos abaixo na ordem para cada essay do escopo** (um por vez; não paralelize).

### Passo 1 — Aviso de escala (corpus inteiro)

Se o escopo for corpus inteiro e a wiki tiver mais de 5 essays, avise o Usuário antes de começar: "são N essays, vou levar um tempo." Ofereça a opção de processar em lotes menores.

### Passo 2 — Passada mecânica: `/organize`

Para cada essay, chame `/organize <slug>` (escopo essay único — formatação mecânica, referências e wikilinks daquele arquivo só, sem as checagens de corpus). Se o escopo do sweep for o corpus inteiro, isso equivale a rodar `/organize <slug>` em sequência para cada essay; **não** chame `/organize` sem argumento aqui — isso repetiria as checagens de corpus (índice, manifesto, plano, órfãos, grafo) uma vez por essay, desperdício que o próprio design de `/organize` existe para evitar.

Aplique os fixes automáticos (sem interação com o Usuário). Acumule os issues restantes no relatório do essay.

### Passo 3 — `/continuity`

Rode `/continuity` no essay. Se encontrar um **problema grave** (contradição direta com a tese, conclusão que não fecha o argumento):

- Reporte e pergunte se a correção deve ser aplicada agora ou revisada depois.
- **Pause apenas este essay** — continue processando os demais do batch normalmente enquanto aguarda a decisão.
- Para achados estruturais menores (transição fraca, termo levemente antecipado), apenas registre no relatório sem interromper.

### Passo 4 — `/proofread`

Passada de português. Aplique as correções diretamente.

### Passo 5 — `/polish`

Passada de estilo: bullets, travessões, elegância de prosa. Aplique as correções diretamente.

### Passo 6 — `/linkify`

Checagem e adição de links externos. Aplique as adições diretamente.

### Passo 7 — Relatório consolidado

Ao final de **todos** os essays do escopo, apresente o relatório único:

```
## Sweep — [N essay(s) processado(s)]

### Resumo
- Essays processados: N
- Essays pulados por status (finalizado/maduro): K
- Issues de formato resolvidos automaticamente: X
- Issues de formato restantes (não-automáticos): Y
- Problemas de continuidade reportados: Z
- Correções de português: W
- Correções de estilo: V
- Links adicionados/corrigidos: U

### Por essay
**[Título]** (essays/slug.md)
- [resumo do que foi corrigido ou reportado]
```

Não exponha cada correção individual durante a execução — acumule e apresente só ao final.

### Passo 8 — Fechamento

Um sweep mexe em muita prosa de uma vez, então feche a sessão deixando os artefatos derivados em dia:

- Se algum essay foi tocado, rode `python scripts/build_index.py`; se `## Referências` mudou (Passo 6 quase sempre muda), rode também `python scripts/build_references.py`.
- **qmd**: se estiver disponível (`qmd status`), **ofereça** `qmd update && qmd embed` — sem isso a busca semântica continua vendo o texto anterior ao sweep. Não rode sozinho; sem qmd, pule sem avisar.
- **Espelho de skills**: rode `python scripts/sync_skills.py --check`. Se acusar drift, rode `python scripts/sync_skills.py` — é mecânico, aplique direto.
- Ofereça `/status update` (o sweep é trabalho substancial), e depois `/review`, `/expand` ou `/chapter` como próximos passos de conteúdo.

## Log

Uma única entrada consolidada no `wiki/log.md`:

**Corpus inteiro:**

```
## [YYYY-MM-DD] sweep | N essays revisados
Formato: X auto-corrigidos, Y issues restantes. Continuidade: Z reportados.
Português: W correções. Estilo: V correções. Links: U adicionados. K pulados por status.
```

**Essay único:**

```
## [YYYY-MM-DD] sweep | [Título do Essay]
Formato: X auto-corrigidos, Y issues restantes. Continuidade: Z reportados.
Português: W correções. Estilo: V correções. Links: U adicionados.
```

Atualize `updated:` no frontmatter de cada essay tocado.

## Convenções

Prosa segue `## Estilo de prosa` em `conventions/SKILL.md`.

## Skills relacionadas

- `/organize` — passada mecânica de formatação/metadados (chamada aqui no Passo 2, em escopo essay único); em modo corpus inteiro é o que decide se vale um sweep
- `/continuity`, `/proofread`, `/polish`, `/linkify` — skills chamados nos Passos 3–6
- `/review` — validade argumentativa e profundidade; complementar ao sweep, não substituto
- `/stats` — dashboard de saúde; rode antes para ter uma visão geral
