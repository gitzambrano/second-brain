---
name: absorb
description: >
  Enriquece essays, conceitos ou entidades já existentes usando uma
  fonte já processada (importada, resumida via digest, ou apenas
  arquivada em wiki/sources/) — só quando pedido explicitamente pelo
  Usuário. Use quando o Usuário disser "usa essa fonte para enriquecer
  o essay sobre X", "atualiza o conceito Y com o que tá nesse paper",
  ou apontar para uma fonte já em wiki/sources/ pedindo que ela seja
  incorporada ao conteúdo da wiki, em vez de só resumida (isso é
  /digest) ou virar um essay próprio (isso é /essay ou /import).
allowed-tools: Bash Read Write Edit Glob Grep AskUserQuestion
---
# Absorb

Incorpora o conteúdo de uma fonte já processada às páginas existentes da wiki — essays, conceitos, entidades. **Só roda quando pedido explicitamente.** `/digest` nunca chama isso sozinho; se o Usuário só queria o resumo, a fonte fica arquivada e parada até ele pedir esse passo.

## Passo a passo

1. Confirme com o Usuário quais essays/conceitos/entidades a fonte deve enriquecer. Se ele não especificar, releia o resumo (`wiki/sources/resumos/<slug>.md`, se houver) ou a fonte original e proponha candidatos antes de editar — `qmd query` com os termos centrais da fonte acha candidatos mais rápido do que reler a wiki inteira (ver `## Ferramentas` no AGENTS.md).
2. Leia a fonte: o original em `wiki/sources/<subpasta>/` se precisar do texto completo, ou o resumo em `wiki/sources/resumos/` se já for suficiente.
3. Atualize as páginas relevantes com o conteúdo novo — seja profundo, não superficial. Uma frase genérica não cumpre o propósito de absorver a fonte. Adicione a fonte ao campo `sources:` do frontmatter de cada página tocada. Se isso acrescentar uma entrada em `## Referências` de algum essay, confira `wiki/references.md` primeiro: se a fonte já está catalogada, reuse a citação exata em vez de redigir uma nova.
4. Ajuste os wikilinks em `## Conexões` das páginas tocadas, nos dois sentidos quando fizer sentido, no formato de `## Regra de links` em `conventions/SKILL.md`.
5. Se a fonte revelar um conceito/entidade sem página própria e central o bastante, crie a página (mesma lógica de `/chapter`) — `tags:` reusa o vocabulário controlado (`## Reuso de vocabulário controlado` em `conventions/SKILL.md`).
6. Atualize `wiki/sources/map.md` (status: "Absorvido em [[slug-pagina-a|Página A]], [[slug-pagina-b|Página B]]") e `manifest.md` se a fonte ainda não tiver entrada — raro, mas possível se foi arquivada manualmente. Se `manifest.md` já tiver a entrada mas faltar `Tags:` (fonte antiga, de antes desse campo existir), aproveite e preencha (`## Reuso de vocabulário controlado` em `conventions/SKILL.md`).
7. Se o passo 3 acrescentou entrada em `## Referências` de algum essay, rode `python scripts/build_references.py` para regenerar `wiki/references.json`/`.md`.
8. Para cada essay tocado, feche com o `## Fechamento padrão de essay único` de `conventions/SKILL.md`.
9. Log: `## [YYYY-MM-DD] absorb | Fonte → páginas afetadas`

Uma única fonte pode tocar 10-15 páginas. Isso é normal.

## Convenções

Se a atualização de um essay for grande o bastante para mudar a tese central, avise o Usuário e ofereça regenerar o handout (`/handout`) se um existir.

Se o conteúdo absorvido contradiz o que já está escrito, não substitua silenciosamente — sinalize a contradição e cite as duas fontes, deixando a decisão editorial (qual prevalece, ou se ambas as visões devem conviver) para o Usuário.

Prosa segue `## Estilo de prosa` em `conventions/SKILL.md`.

## Skills relacionadas

- `/digest` — passo anterior, quando a fonte ainda não foi lida/resumida
- `/expand` — mesma lógica de conteúdo, mas por pedido direto, não por fonte
- `/chapter`, `/insight`
