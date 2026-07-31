---
name: format
description: >
  Audita formatação completa de essays: estrutura Markdown, byline,
  Sumário/Referências/Conexões, Obsidian-compat, espaçamentos, aspas,
  caracteres LaTeX perigosos, travessões, bullets fora do lugar, links
  externos, HTML residual e idioma PT-BR. Aplica correções mecânicas
  automáticas via auto_fix_lint.py e reporta o restante. Aceita escopo
  corpus inteiro (/format) ou essay único (/format <slug>). Sweep chama
  este skill na passada mecânica.
allowed-tools: Bash Read Write Edit Glob Grep AskUserQuestion
---

# Format

Executa uma auditoria completa de formatação em um ou todos os essays, cobrindo cada regra de `conventions/SKILL.md`. É **mecânico e não-interativo**: roda o script, aplica os fixes inequívocos automaticamente, e lista o restante para o Usuário resolver.

Não edita prosa nem argumento — isso é responsabilidade de `/proofread`, `/polish`, `/expand` e `/review`.

## Diferença em relação a skills vizinhos

- `/format` — formatação, estrutura, compatibilidade técnica (LaTeX, Obsidian, Markdown)
- `/proofread` — português: gramática, ortografia, concordância
- `/polish` — estilo de prosa: ritmo, elegância, travessões, bullets
- `/organize` — saúde da wiki inteira: índice, manifesto, plano, orphans
- `/review` — validade argumentativa, profundidade, gaps filosóficos/científicos

## Escopo

```
/format              → todos os essays em wiki/essays/
/format <slug>       → apenas o essay identificado por slug, título parcial ou nome .md
```

Em modo corpus inteiro, pula essays com `status: finalizado` ou `maduro` nos fixes automáticos (não altera a prosa deles), mas ainda os inclui no relatório de problemas encontrados.

## Passo a passo

1. **Leia `conventions/SKILL.md`** para verificar se as regras de formatação foram atualizadas desde a última execução.

2. **Resolva o escopo**:
   - Sem argumento: liste todos os `.md` em `wiki/essays/`.
   - Com `<slug>`: localize o arquivo exato em `wiki/essays/` (tente slug, nome `.md`, ou título parcial); se ambíguo, pergunte antes de prosseguir.

3. **Rode o script de formato**:

   ```bash
   python scripts/format_check.py [--file <slug>] --json
   ```

   O output JSON tem a estrutura:

   ```json
   {
     "essays": [
       {"name": "...", "issues": [{"severity": "ERROR|WARNING|INFO", "code": "...", "message": "..."}]}
     ]
   }
   ```

   **Rode também o script de referências**, com o mesmo escopo:

   ```bash
   python scripts/linkify_check.py [--file <slug>] --json
   ```

   Mesma estrutura de saída, com os códigos de `## Referências` (`REFERENCIA_FORMATO_INVALIDO`, `DUPLICATE_REFERENCIA`, `LINK_NOT_IN_REFERENCIAS`, `REFERENCIA_SEM_LINK`, `REFERENCIA_NAO_USADA`). `/format` só **reporta** esses achados: quem corrige é `/linkify`.

4. **Aplique os fixes automáticos** para achados mecânicos e inequívocos (sem interação com o Usuário):

   ```bash
   python scripts/auto_fix_lint.py
   ```

   O `auto_fix_lint.py` corrige:
   - Linha em branco faltando após heading
   - Dois-pontos em `[[wikilinks]]` → em dash
   - Espaços duplos no meio de parágrafos
   - Três ou mais linhas em branco consecutivas → duas

5. **Monte o relatório** agrupando os issues restantes (não auto-corrigíveis) por categoria:

   | Categoria | Códigos de issue |
   | --- | --- |
   | Estrutura obrigatória | `NO_FRONTMATTER`, `BAD_FRONTMATTER`, `FM_*`, `NO_H1`, `NO_SUMARIO`, `SUMARIO_NO_HR`, `SUMARIO_BROKEN_ANCHOR`, `NO_REFERENCIAS`, `NO_CONEXOES`, `CONEXOES_NOT_LAST` |
   | Resumo do índice | `FM_NO_SUMMARY`, `FM_BAD_SUMMARY`, `FM_LONG_SUMMARY` |
   | Byline | `BYLINE_*` |
   | Links | `WIKILINKS_IN_BODY`, `FEW_EXT_LINKS` |
   | LaTeX / aspas | `ASCII_QUOTES`, `BYLINE_LATEX_CHAR`, `TITLE_LATEX_CHAR` |
   | Espaçamento | `HEADING_SPACING`, `DOUBLE_SPACES`, `EXCESS_BLANK_LINES` |
   | Estilo | `TOO_MANY_EM_DASHES`, `BULLETS_IN_BODY` |
   | Residuais | `HTML_RESIDUAL`, `RESIDUAL_SYMBOL` |
   | Idioma | `ENGLISH_PARAGRAPH` |
   | Obsidian | `LOOSE_CHAPTER_LABEL` |
   | Referências | `REFERENCIA_FORMATO_INVALIDO`, `DUPLICATE_REFERENCIA`, `LINK_NOT_IN_REFERENCIAS`, `REFERENCIA_SEM_LINK`, `REFERENCIA_NAO_USADA` |

6. **Apresente o relatório final** com:
   - Contagem de essays limpos vs. com issues
   - Issues agrupados por categoria e por essay
   - Lista de fixes auto-aplicados
   - Se houver `REFERENCIA_FORMATO_INVALIDO`, sugira `python scripts/linkify_check.py --fix-format` — mas não rode: reformatar bibliografia é `/linkify`, não `/format`
   - **Liste nominalmente os essays com `FM_NO_SUMMARY`.** Sem `summary:` a entrada do essay em `wiki/index.md` sai sem resumo, e não existe outro lugar de onde um script possa tirar essa linha. Escrever o resumo é conteúdo, então não invente aqui: reporte quais essays estão sem, e ofereça preencher via `/expand` ou numa passada dedicada.

7. **Não pergunte ao Usuário** durante a execução — apenas reporte ao final. A única exceção é se o `--file <slug>` for ambíguo.

## O que este skill NÃO faz

- Não edita prosa ou argumento (só estrutura e metadados)
- Não faz auditoria de manifesto, índice ou plano — isso é `/organize`
- Não checa ortografia ou estilo de texto — isso é `/proofread` e `/polish`
- Não checa validade argumentativa — isso é `/review`

## Depois

Registre em `wiki/log.md`:

```
## [YYYY-MM-DD] format | N essays verificados
Auto-corrigidos: X arquivos. Issues restantes: Y (Z ERROR, W WARNING).
```

Atualize `updated:` no frontmatter de cada arquivo tocado pelo `auto_fix_lint.py`.

## Skills relacionadas

- `/organize` — auditoria de infra da wiki (índice, manifesto, orphans, plano)
- `/proofread`, `/polish` — correção de prosa
- `/sweep` — orquestrador que chama `/format` como primeira passada
- `/review` — validade argumentativa, filosófica e científica
