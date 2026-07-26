---
name: organize
description: >
  Organiza a base de conhecimento inteira na camada de metadados/
  grafo: atualiza stats, corrige links quebrados ou órfãos, atualiza
  wiki/index.md e confirma a integridade de wiki/log.md, atualiza
  wiki/sources/map.md, checa consistência do vocabulário de tags e de
  tipos de source. Use quando o usuário disser "organiza a wiki
  inteira", "atualiza o índice", "vê se tem link quebrado", "confere o
  mapa de sources", ou quiser manutenção da base inteira em vez de
  corrigir a prosa de um essay específico (isso é /sweep).
allowed-tools: Bash Read Write Edit Glob Grep
---

# Organize

Organiza a base inteira na camada de metadados: índice, log, mapa de sources, tags, consistência do manifesto. **Não reescreve prosa de essay** — isso é `/sweep`. Pense em `/organize` como a manutenção do grafo e do catálogo; `/sweep` como a manutenção do texto.

## Passo a passo

1. Rode `python wiki/scripts/stats.py` para ver o estado atual — números de essays/tags/órfãos/sources sem manifesto.
2. **Órfãos**: para cada concept/entity sem essay que o referencie, decida com o usuário se cria um essay novo, se anexa a um existente, ou se a página órfã deve ser removida por não servir a nada.
3. **Contradições e claims desatualizados**: ao ler os essays (via os achados do stats ou amostragem), sinalize contradições entre páginas e claims que fontes mais novas já superaram.
4. **`wiki/index.md`**: confirme que contém apenas essays, no formato `[[filename|Display Title]]`, sem dois-pontos no display text, organizados por categoria temática (ver `## Formato do Índice` no AGENTS.md). Adicione essays que faltarem, remova entradas de essays deletados.
5. **Tags quase-duplicadas**: verifique se alguma tag em uso é variante de grafia de outra (acento, plural, sinônimo). Proponha consolidação e liste os essays afetados antes de renomear em massa.
6. **`wiki/sources/manifest.md` e tipos de source — audite E corrija**: todo arquivo em `wiki/sources/**` tem entrada no manifesto? Todo `Tipo:` usa o vocabulário controlado? Para todo arquivo que **não** está na subpasta que seu `Tipo:` implica (ou que foi digerido direto na raiz de `wiki/sources/`, fora de qualquer subpasta): mova o arquivo para a subpasta correta agora, sem perguntar — é correção mecânica e inequívoca, a subpasta é sempre derivada do `Tipo:` (ver `## Tipos de Source — Vocabulário Controlado` no AGENTS.md). Atualize o campo `Pasta:` da entrada correspondente em `manifest.md` para refletir o novo caminho. A única exceção que exige pergunta ao usuário: um arquivo sem entrada no manifesto e sem `Tipo:` inferível com confiança — aí reporte e peça para classificar, não adivinhe o tipo.
7. **`wiki/sources/map.md`**: revise por inteiro (não só incremente) — toda fonte em `wiki/sources/` e todo item ainda pendente em `raw/` deve aparecer, com status correto e organizado por assunto. Se algum source foi movido no passo 6, confirme que o caminho/status aqui reflete a pasta nova.
8. **`wiki/log.md`**: confirme que é append-only (nenhuma entrada antiga foi editada) — só verifique, nunca reescreva o histórico.
9. **Links de toda a wiki — rode e corrija**: rode `python wiki/scripts/lint_all.py` (cobre wikilinks mortos em toda a wiki, órfãos, consistência de `index.md`, formatação mecânica). Aplique `python wiki/scripts/auto_fix_lint.py` para os achados mecânicos e inequívocos (espaçamento de heading, dois-pontos em display text de wikilink) — sem perguntar. Para cada **wikilink morto** reportado:
   - Se o alvo for claramente um erro de digitação de uma página que existe (nome quase idêntico ao de um título real), corrija o wikilink para o alvo certo agora, sem perguntar.
   - Se o alvo não corresponder a nenhuma página existente nem a um erro de digitação óbvio, **não invente ou apague o link silenciosamente** — reporte a lista completa (link morto → arquivo(s) que o referenciam) e pergunte se o usuário quer criar a página faltante, apontar para outra página existente, ou remover o link.
   Links **externos** (URLs que saíram do ar) não são responsabilidade do `/organize` — isso é `/linkify`, chamado por essay via `/sweep`.
10. **Exportação** (opcional, só se o usuário quiser uma checagem completa): rode `python wiki/scripts/export_essay.py --all` e `python wiki/scripts/export_essay_html.py --all`, confirme que PDFs têm hyperlinks clicáveis, imagens resolvem, `## Conexões` não aparece no PDF e `## Referências`/`## Sumário` aparecem.
11. Reporte um resumo consolidado do que foi corrigido e do que ainda precisa de decisão do usuário.

## Depois

Log:
```
## [YYYY-MM-DD] organize | Resumo do que foi corrigido
```
Se quiser um snapshot salvo da stats pós-organização, rode `python wiki/scripts/stats.py --save`.

## Convenções

Não corrija silenciosamente algo que depende de julgamento editorial (qual claim prevalece numa contradição, se um órfão vira essay ou é removido) — reporte e espere decisão. Correções mecânicas e inequívocas (índice desatualizado, entrada de manifesto faltando) podem ser aplicadas direto.

## Skills relacionadas

- `/sweep` — corrige prosa dentro de cada essay, não a camada de metadados
- `/stats` — o primeiro passo daqui, e também útil sozinho sem rodar o resto
- `/import`, `/digest`, `/absorb` — são quem alimenta `manifest.md` e `map.md` no dia a dia; `/organize` é a auditoria periódica, não o registro do dia a dia
