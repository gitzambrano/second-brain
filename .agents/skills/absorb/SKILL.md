---
name: absorb
description: >
  Enriquece essays, conceitos ou entidades já existentes usando uma
  fonte já processada (importada, resumida via digest, ou apenas
  arquivada em wiki/sources/) — só quando pedido explicitamente pelo
  usuário. Use quando o usuário disser "usa essa fonte pra enriquecer
  o essay sobre X", "atualiza o conceito Y com o que tá nesse paper",
  ou apontar para uma fonte já em wiki/sources/ pedindo que ela seja
  incorporada ao conteúdo da wiki, em vez de só resumida (isso é
  /digest) ou virar um essay próprio (isso é /essay ou /import).
allowed-tools: Bash Read Write Edit Glob Grep
---

# Absorb

Incorpora o conteúdo de uma fonte já processada às páginas existentes da wiki — essays, conceitos, entidades. **Só roda quando pedido explicitamente.** `/digest` nunca chama isso sozinho; se o usuário só queria o resumo, a fonte fica arquivada e parada até ele pedir esse passo.

## Passo a passo

1. Confirme com o usuário quais essays/conceitos/entidades a fonte deve enriquecer. Se ele não especificar, releia o resumo (`wiki/sources/resumos/<slug>.md`, se houver) ou a fonte original e proponha candidatos antes de editar.
2. Leia a fonte: o original em `wiki/sources/<subpasta>/` se precisar do texto completo, ou o resumo em `wiki/sources/resumos/` se já for suficiente.
3. Atualize as páginas relevantes com o conteúdo novo — seja profundo, não superficial. Uma frase genérica não cumpre o propósito de absorver a fonte.
4. Ajuste `[[wikilinks]]` em `## Conexões` das páginas tocadas, nos dois sentidos quando fizer sentido.
5. Se a fonte revelar um conceito/entidade sem página própria e central o bastante, crie a página (mesma lógica de `/chapter`).
6. Atualize `wiki/sources/map.md` (status: "Absorvido em [[Página A]], [[Página B]]") e `manifest.md` se a fonte ainda não tiver entrada — raro, mas possível se foi arquivada manualmente.
7. Log: `## [YYYY-MM-DD] absorb | Fonte → páginas afetadas`

Uma única fonte pode tocar 10-15 páginas. Isso é normal.

## Convenções

Se a atualização de um essay for grande o bastante para mudar a tese central, avise o usuário e ofereça regenerar o handout (`/handout`) se um existir. Se o conteúdo absorvido contradiz o que já está escrito, não substitua silenciosamente — sinalize a contradição e cite as duas fontes, deixando a decisão editorial (qual prevalece, ou se ambas as visões devem conviver) para o usuário.

## Skills relacionadas

- `/digest` — passo anterior, quando a fonte ainda não foi lida/resumida
- `/chapter` — para criar página de conceito/entidade nova revelada pela fonte
- `/expand` — mesma lógica de adição de conteúdo, mas disparada por pedido direto do usuário em vez de por uma fonte
- `/atom` — se a fonte revelar uma ideia tangencial que não cabe no essay em edição, capture como nota atômica em vez de forçar ou descartar
