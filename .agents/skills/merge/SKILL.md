---
name: merge
description: >
  Funde duas páginas do mesmo tipo, reaponta backlinks e remove a página
  absorvida. Use para duplicatas confirmadas; exige aprovação explícita do plano
  completo antes da primeira escrita.
metadata:
  second-brain-role: "destructive-maintenance"
  second-brain-mode: "write"
  second-brain-scope: "pages"
  second-brain-approval: "before-write"
  second-brain-closure: "multi-page"
allowed-tools: Bash Read Write Edit Glob Grep AskUserQuestion
---
# Merge

Funde duas páginas do mesmo tipo em uma só. A decisão do Usuário acontece antes da primeira escrita: lê as duas, levanta todos os backlinks da absorvida, confirma o plano inteiro, e só então escreve a sobrevivente, reaponta os links e apaga a absorvida numa unidade só.

## 1. Pré-flight — levantar antes de escrever

Nada é escrito nesta fase.

1. **Resolva as duas páginas** (`/merge <slug-a> <slug-b>`). Mesma pasta obrigatoriamente — `essays` com `essays`, `concepts` com `concepts`, etc. Tipos diferentes não fundem; sugira `/chapter` (para incorporar um concept dentro de um essay) em vez disso.
2. **Leia as duas inteiras.**
3. **Escolha a sobrevivente**: se o Usuário já indicou qual título/slug fica, use esse. Se não, pergunte (`AskUserQuestion`) — normalmente a mais completa, mais antiga, ou mais bem linkada.
4. **Levante os backlinks da absorvida**: `python scripts/find_backlinks.py "<Título da Absorvida>"`. Cada resultado vira um wikilink a reapontar para a sobrevivente.
5. **Levante o resto do rastro**: entrada em `wiki/sources/manifest.md` com `Virou: [[slug-absorvido|...]]`, e os derivados a regenerar (essay → `build_index.py`; se `## Referências` muda, `build_references.py`).
6. **Monte o plano de fusão** do conteúdo, sem gravar ainda:
   - `tags`: união das duas listas, sem duplicar, sem passar de 5 — se passar, priorize as mais específicas ao tema combinado.
   - `sources`: união das duas listas.
   - `created`: mantém o mais antigo dos dois.
   - `updated`: hoje.
   - Corpo: decida o que da absorvida entra — o que a sobrevivente ainda não cobre. Não duplique parágrafos equivalentes — se as duas dizem a mesma coisa, fique com a versão mais bem escrita. Para essay, atualize `## Sumário` se seções novas entraram. Para concept/entity/insight, apenas funda o texto corrido.
   - Se as duas páginas se contradizem em algum ponto (não apenas se sobrepõem), pare aqui — antes de qualquer escrita — e siga `## Regra de contradição entre fontes` em `conventions/SKILL.md`. Não escolha um lado sozinho.

## 2. Confirmação — o conjunto completo, de uma vez

Apresente ao Usuário, numa lista só (`AskUserQuestion`): a sobrevivente escolhida, o que entra do corpo da absorvida e o que fica de fora, cada backlink com caminho que será reapontado, o arquivo que será apagado e a entrada de manifesto a corrigir.

Só siga com um "sim" explícito ao conjunto. Divergiu em algum item, ajuste o plano e reconfirme — ainda sem escrever.

## 3. Aplicação — uma unidade, sem pausa

Nesta ordem, sem voltar a perguntar:

1. Grave a sobrevivente com o conteúdo fundido.
2. Em cada backlink, troque o wikilink `[[slug-absorvido|...]]` por `[[slug-sobrevivente|Título da Sobrevivente]]`.
3. Apague a página absorvida (o arquivo `.md` sai da pasta).
4. Atualize `wiki/sources/manifest.md` se havia entrada `Virou: [[slug-absorvido|...]]`.
5. Regenere os derivados levantados no pré-flight.
6. **Log**:

   ```
   ## [YYYY-MM-DD] merge | Título Sobrevivente ← Título Absorvido
   Fundidos N links reapontados.
   ```

Se aparecer um caso não previsto no pré-flight, termine a unidade mesmo assim — parar entre o reaponte e a remoção é o que deixa a wiki quebrada — e relate o caso ao final. A exceção é contradição de conteúdo: essa precisa aparecer no pré-flight, e se surgir só agora, grave o que já foi decidido, deixe o trecho contraditório fora e leve a decisão ao Usuário.

## 4. Verificação

```bash
python scripts/check_wiki.py
```

A fusão só está concluída quando este comando passa. Wikilink morto apontando para a absorvida é **falha deste fluxo**: corrija agora e relate como falha, em vez de sugerir `/organize` depois.

## Regras

- Nunca funde sem mostrar as duas páginas e confirmar a escolha de sobrevivente com o Usuário, a menos que ele já tenha dito explicitamente qual fica.
- Nunca escreve antes da confirmação do conjunto completo.
- Nunca funde tipos diferentes (essay com concept, etc.).
- Não reescreve estilo/prosa além do necessário para juntar sem redundância — isso é `/polish`, sob pedido separado.

## Skills relacionadas

- `/organize` — roda `check_dedupe.py`, que sinaliza candidatos a fusão
- `/delete` — quando uma das duas simplesmente não deveria existir, em vez de fundir
- `/chapter` — incorporar um concept/entity inteiro dentro de um essay (situação diferente de fundir duas páginas do mesmo tipo)
