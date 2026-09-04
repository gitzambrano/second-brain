---
name: merge
description: >
  Funde duas páginas do mesmo tipo (dois essays, dois concepts, duas
  entities, ou dois insights) numa só. Uma vira a sobrevivente, a
  outra é absorvida e apagada; todo wikilink que apontava para a
  absorvida passa a apontar para a sobrevivente. Simples e direto,
  sem reescrita de prosa. Use quando o Usuário disser "funde esses
  dois essays", "esses dois concepts são a mesma coisa, junta",
  "duplicou, junta os dois", ou `check_dedupe.py`/`/organize` tiver
  sinalizado um par quase-duplicata e o Usuário confirmar que é
  fusão.
allowed-tools: Bash Read Write Edit Glob Grep AskUserQuestion
---
# Merge

Funde duas páginas do mesmo tipo em uma só. Simples: lê as duas, junta o conteúdo sem perder nada, aponta os links de volta, apaga a absorvida.

## Passo a passo

1. **Resolva as duas páginas** (`/merge <slug-a> <slug-b>`). Mesma pasta obrigatoriamente — `essays` com `essays`, `concepts` com `concepts`, etc. Tipos diferentes não fundem; sugira `/chapter` (para incorporar um concept dentro de um essay) em vez disso.
2. **Leia as duas inteiras.**
3. **Escolha a sobrevivente**: se o Usuário já indicou qual título/slug fica, use esse. Se não, pergunte (`AskUserQuestion`) — normalmente a mais completa, mais antiga, ou mais bem linkada.
4. **Funda o conteúdo** na sobrevivente:
   - `tags`: união das duas listas, sem duplicar, sem passar de 5 — se passar, priorize as mais específicas ao tema combinado.
   - `sources`: união das duas listas.
   - `created`: mantém o mais antigo dos dois.
   - `updated`: hoje.
   - Corpo: incorpore o conteúdo da absorvida que a sobrevivente ainda não cobre. Não duplique parágrafos equivalentes — se as duas dizem a mesma coisa, fique com a versão mais bem escrita. Para essay, atualize `## Sumário` se seções novas entraram. Para concept/entity/insight, apenas funda o texto corrido.
   - Se as duas páginas se contradizem em algum ponto (não apenas se sobrepõem), pare e siga `## Regra de contradição entre fontes` em `conventions/SKILL.md` — não escolha um lado sozinho.
5. **Reaponte os links**: `python scripts/find_backlinks.py "<Título da Absorvida>"` lista quem referencia a absorvida. Em cada resultado, troque o wikilink `[[slug-absorvido|...]]` por `[[slug-sobrevivente|Título da Sobrevivente]]`.
6. **Apague a página absorvida** (o arquivo `.md` sai da pasta).
7. **Regenere o que depender do tipo fundido**:
   - Essay: `python scripts/build_index.py`. Se `## Referências` mudou, `python scripts/build_references.py`.
   - Qualquer tipo: se a página tinha entrada em `wiki/sources/manifest.md` apontando `Virou: [[slug-absorvido|...]]`, atualize para o slug sobrevivente.
8. **Log**:

   ```
   ## [YYYY-MM-DD] merge | Título Sobrevivente ← Título Absorvido
   Fundidos N links reapontados.
   ```

9. Ofereça `/organize` ao final — confirma que nenhum link ficou órfão e que a formatação da sobrevivente está correta. Diga ao oferecer que o fechamento de `/organize` pode fazer commit e push em `./` e em `data/`.

## Regras

- Nunca funde sem mostrar as duas páginas e confirmar a escolha de sobrevivente com o Usuário, a menos que ele já tenha dito explicitamente qual fica.
- Nunca funde tipos diferentes (essay com concept, etc.).
- Não reescreve estilo/prosa além do necessário para juntar sem redundância — isso é `/polish`, sob pedido separado.

## Skills relacionadas

- `/organize` — roda `check_dedupe.py`, que sinaliza candidatos a fusão
- `/delete` — quando uma das duas simplesmente não deveria existir, em vez de fundir
- `/chapter` — incorporar um concept/entity inteiro dentro de um essay (situação diferente de fundir duas páginas do mesmo tipo)
