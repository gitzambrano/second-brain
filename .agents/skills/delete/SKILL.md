---
name: delete
description: >
  Apaga um essay, concept, entity ou insight. Levanta a página e todos os
  backlinks antes de escrever, confirma o conjunto inteiro com o Usuário, e
  então repara os links e remove o arquivo numa unidade só, terminando com
  `check_wiki.py` limpo. Use quando o Usuário disser "apaga esse essay",
  "deleta esse concept", "remove essa entity", "não preciso mais dessa nota",
  ou quiser tirar uma página da wiki de vez.
allowed-tools: Bash Read Write Edit Glob Grep AskUserQuestion
---
# Delete

Apaga uma página da wiki. A decisão do Usuário acontece antes da primeira escrita: levanta tudo que a remoção afeta, confirma o conjunto inteiro, e só então repara os links e apaga o arquivo, sem parar no meio.

## 1. Pré-flight — levantar antes de escrever

Nada é escrito nesta fase.

1. **Resolva a página** (`/delete <slug>`). Ambíguo → pergunte.
2. **Leia a página inteira** — é a última chance de ver o que se perde.
3. **Levante os backlinks**: `python scripts/find_backlinks.py "<Título>"`. Cada resultado é um wikilink que vai apontar para o vazio depois da remoção.
4. **Levante o resto do rastro**: entrada em `wiki/sources/manifest.md` com `Virou: [[slug|...]]`, e os derivados a regenerar pelo tipo (essay → `build_index.py`; se carregava referências únicas, `build_references.py`).

## 2. Confirmação — o conjunto completo, de uma vez

Apresente ao Usuário, numa lista só (`AskUserQuestion`): o arquivo a apagar, cada backlink com caminho e a ação proposta para ele (remover o link, deixando o texto visível como prosa, ou reapontar para outra página), e a entrada de manifesto a corrigir. Deixe claro que a remoção é irreversível.

Só siga com um "sim" explícito ao conjunto. Divergiu em algum item, ajuste o plano e reconfirme — ainda sem escrever.

## 3. Aplicação — uma unidade, sem pausa

Nesta ordem, sem voltar a perguntar:

1. Aplique a ação combinada em cada backlink.
2. Apague o arquivo.
3. Atualize `wiki/sources/manifest.md` se havia entrada.
4. Regenere os derivados levantados no pré-flight.
5. **Log**:

   ```
   ## [YYYY-MM-DD] delete | Título Apagado
   N backlinks reparados no mesmo fluxo.
   ```

Se aparecer um caso não previsto no pré-flight, termine a unidade mesmo assim — parar no meio é o que deixa a wiki quebrada — e relate o caso ao final.

## 4. Verificação

```bash
python scripts/check_wiki.py
```

A operação só está concluída quando este comando passa. Wikilink morto apontando para a página apagada é **falha deste fluxo**: corrija agora e relate como falha. Não encaminhe para `/organize` nem deixe a wiki quebrada com uma sugestão de rodar outra skill depois.

## Regras

- Nunca apaga sem confirmação explícita do Usuário, e nunca escreve antes dela.
- Toda decisão sobre link órfão é tomada no pré-flight, não depois da remoção.
- Se a página apagada era `finalizado`/`revisao`, avise no log mesmo assim; `/delete` não olha status, é decisão do Usuário.

## Skills relacionadas

- `/organize` — passada mecânica ampla do corpus, sob pedido separado; não é o reparo desta remoção
- `/merge` — quando a página não deve simplesmente sumir, mas ter seu conteúdo absorvido por outra
