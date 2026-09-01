---
name: organize
description: >
  Audita e corrige a camada mecânica da wiki: estrutura, metadados,
  links internos, referências, índice, sources, tags, plano, insights
  e artefatos derivados. Aceita corpus inteiro ou um essay específico.
  Não reescreve prosa nem argumento.
allowed-tools: Bash Read Write Edit Glob Grep AskUserQuestion WebFetch WebSearch
---
# Organize

**[ambos]** Manutenção mecânica e de metadados. Regras editoriais e formato canônico vivem em `conventions/SKILL.md`.

Não reescreva prosa ou argumento. Para isso use `/sweep` ou `/review`.

## Modos

```text
/organize          → corpus inteiro
/organize <slug>   → apenas o essay nomeado
```

Use o modo de essay único quando o Usuário pedir uma auditoria completa daquele arquivo. Skills editoriais já executam o fechamento mecânico básico por conta própria.

## Corpus inteiro

### 1. Gerar baseline e aplicar fixes mecânicos

Execute nesta ordem:

```bash
python scripts/build_index.py
python scripts/build_references.py
python scripts/check_wiki.py --json
python scripts/check_references.py --json
python scripts/fix_lint.py
python scripts/build_index.py
python scripts/build_references.py
```

Guarde os relatórios anteriores ao fixer para explicar o que foi corrigido. `fix_lint.py` pode atuar em qualquer `status:` porque não altera argumento.

### 2. Auditar saúde estrutural

Execute:

```bash
python scripts/find_backlinks.py --orphans
python scripts/check_gaps.py --tags-only
python scripts/check_dedupe.py
```

Interprete assim:

- **Órfão total:** atenção; proponha destino, fusão ou remoção, mas não decida sozinho.
- **Página sem essay-pai, mas citada por outra página:** informativo; não é defeito por si só.
- **Tag rasa:** sinal de cobertura, não correção automática. Ofereça `/plan add` ou `/scout`.
- **Quase-duplicata:** nunca fundir/deletar automaticamente. Mostre os pares e peça decisão.

Para consolidação de tag aprovada:

```bash
python scripts/retag.py "tag-antiga" "tag-nova" --dry-run
python scripts/retag.py "tag-antiga" "tag-nova"
python scripts/build_index.py
```

### 3. Auditar sources, mapa, plano e insights

Verifique:

- todo arquivo em `wiki/sources/**` tem entrada no manifesto e vice-versa;
- `Tipo:` e subpasta obedecem `conventions/SKILL.md`;
- `Ensaio Completo Importado` aponta para essay existente;
- `Tags:` usa o vocabulário controlado;
- `wiki/sources/map.md` cobre todas as fontes processadas;
- estrutura canônica de pastas existe;
- `wiki/log.md` permanece append-only;
- `plan/plano.md` mantém as 5 seções e status válidos;
- insights têm `maturidade:` válida e conexões coerentes.

Aplique diretamente apenas correções inequívocas: pasta canônica ausente, path de source claramente errado, tag faltante inferível, typo evidente de wikilink, estrutura mecânica.

Peça decisão quando houver ambiguidade de tipo, fusão, renomeação conceitual, órfão sem destino ou contradição entre fontes.

### 4. Tratar achados que exigem conteúdo ou fonte

- `FM_NO_SUMMARY`: liste nominalmente; não escreva summary dentro de `/organize`.
- `FM_LONG_SUMMARY`: reporte.
- Bibliografia ausente/rasa: reporte; suficiência é julgamento editorial.
- Wikilink morto com alvo óbvio: corrija. Sem alvo claro: pergunte.
- Link externo quebrado: encaminhe para `/linkify`.
- Referência com título/autor/container incerto (`EMPTY_REFERENCIAS`, `REF_BOLD_AUTHOR`, `REF_TITLE_IS_AUTHOR`, `REF_MISSING_TITLE` e equivalentes): verifique a fonte com `WebFetch`/`WebSearch` antes de editar. Não complete de memória.

### 5. Fechamento do corpus

Chame o subagent `update` de `.agents/agents/update.md`.

Use o resultado de stats e `output/graph/graph.json` no resumo. Páginas `isolated` e `tag_gaps` entram em atenção e podem encaminhar para `/connect`.

Exports são opcionais e só rodam sob pedido explícito.

### 6. Relatório

Nunca cole JSON bruto. Apresente:

- **Corrigido automaticamente**
- **Crítico — precisa de decisão**
- **Atenção — vale revisar**
- **Informativo**

Liste caminhos/códigos apenas quando ajudam o Usuário a agir. Inclua nominalmente os essays com `FM_NO_SUMMARY`.

## Essay único (`/organize <slug>`)

1. Resolva o slug; pergunte apenas se houver ambiguidade real.
2. Execute:

```bash
python scripts/check_wiki.py <slug> --json
python scripts/check_references.py --file <slug> --json
python scripts/fix_lint.py <slug>
```

3. Aplique fixes mecânicos e reporte o restante.
4. Não rode auditorias de corpus: órfãos globais, manifesto, plano, insights, grafo ou stats.
5. Se referências mudaram, rode `python scripts/build_references.py`.
6. Se `summary` ou tags mudaram, rode `python scripts/build_index.py`.

Reporte também que as checagens de corpus foram puladas.

## Log

Quando houver mudança:

```markdown
## [YYYY-MM-DD] organize | Resumo
```

Para essay único, use o título do essay.

## Limites

- Formatação mecânica pode ser corrigida automaticamente.
- Decisão editorial exige o Usuário.
- Contradições seguem `## Regra de contradição entre fontes` em `conventions/SKILL.md`.
- `/organize` não substitui `/sweep`, `/review`, `/gaps` ou `/linkify`.
