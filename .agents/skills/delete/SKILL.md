---
name: delete
description: >
  Apaga um essay, concept, entity ou insight. Simples e direto:
  confirma com o Usuário, apaga o arquivo, registra no log, e chama
  `/organize` para consertar o que a remoção quebrou (links órfãos,
  índice, manifesto) — cujo fechamento pode fazer commit e push. Use quando o Usuário disser "apaga esse
  essay", "deleta esse concept", "remove essa entity", "não preciso
  mais dessa nota", ou quiser tirar uma página da wiki de vez.
allowed-tools: Bash Read Write Edit Glob Grep AskUserQuestion
---
# Delete

Apaga uma página da wiki. Sem cerimônia: confirma, apaga, loga, e roda `/organize` para consertar os links que apontavam pra ela.

## Passo a passo

1. **Resolva a página** (`/delete <slug>`). Ambíguo → pergunte.
2. **Mostre o impacto antes de apagar**: `python scripts/find_backlinks.py "<Título>"` — se algo referencia a página, liste esses caminhos ao Usuário.
3. **Confirme explicitamente** (`AskUserQuestion`) antes de apagar — irreversível. Se houver backlinks, deixe claro que essas páginas vão ficar com wikilink quebrado até `/organize` rodar.
4. **Apague o arquivo.**
5. **Log**:

   ```
   ## [YYYY-MM-DD] delete | Título Apagado
   N backlinks quebrados a resolver via /organize.
   ```

6. **Regenere o que depender do tipo apagado**: essay → `python scripts/build_index.py` (e `build_references.py` se ele carregava referências únicas). Se tinha entrada em `wiki/sources/manifest.md`, atualize `Virou:` para refletir que a página não existe mais.
7. **Rode `/organize`** — é ele quem repara os wikilinks órfãos deixados pela remoção (relata cada um, pergunta se remove o link, aponta pra outra página, ou vira um essay novo). Avise que o fechamento de `/organize` pode fazer commit e push em `./` e em `data/`.

## Regras

- Nunca apaga sem confirmação explícita do Usuário.
- Não decide sozinho o que fazer com um link órfão resultante — isso é o passo de wikilinks mortos do `/organize`.
- Se a página apagada era `finalizado`/`revisao`, avise no log mesmo assim; `/delete` não olha status, é decisão do Usuário.

## Skills relacionadas

- `/organize` — chamado ao final, conserta os links quebrados pela remoção
- `/merge` — quando a página não deve simplesmente sumir, mas ter seu conteúdo absorvido por outra
