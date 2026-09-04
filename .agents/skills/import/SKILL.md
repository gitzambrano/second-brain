---
name: import
description: >
  Ingere uma fonte que já é um essay/white paper completo escrito pelo
  próprio Usuário: arquiva o original inalterado em wiki/sources/ e
  empacota um essay derivado que preserva a prosa do autor, aplicando
  só as transformações autorizadas (frontmatter, Sumário, links,
  Referências, Conexões). Tradução não é uma delas por padrão: exige
  decisão explícita do Usuário e fica registrada. Use quando um arquivo
  em raw/ (ou texto colado) for um texto pronto do próprio autor, não
  material de terceiro a resumir. Se houver dúvida se a fonte é de fato
  obra completa do autor, pergunte antes de prosseguir: usar /import
  numa fonte de terceiro apresentaria incorretamente a escrita de outra
  pessoa como essay do autor.
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch AskUserQuestion
---
# Import

Processa uma fonte que **já é** um ensaio, white paper, ou artigo completo escrito pelo próprio Usuário. Claude aqui é arquivista, não coautor. Para qualquer fonte que não seja do próprio autor (paper de terceiro, livro, web clipping, transcrição), use `/digest`, não este skill.

Diferente de `/essay`, este skill **não passa por `/outline`**: não há tese a estruturar, porque não há autoria nova acontecendo — o texto já existe pronto, o trabalho aqui é fiel transformação em `.md`, não redação.

## Dois artefatos, dois contratos

O import produz **dois** arquivos, e eles não têm a mesma regra. Confundi-los é o
que faz "o texto é preservado intacto" soar como promessa quebrada assim que o
essay ganha um `## Sumário`.

| Artefato | Contrato |
| --- | --- |
| `wiki/sources/<tipo>/<nome-original>` | **O original, byte a byte.** Nunca é editado, nem para corrigir erro de digitação, nem para traduzir. É a regra geral 1 do `AGENTS.md`. |
| `wiki/essays/<slug>.md` | **Derivado.** Preserva a prosa do autor — frase, ordem, argumento e vocabulário — e recebe só as transformações listadas abaixo. |

### Transformações autorizadas no essay derivado

Estas são as únicas que este skill aplica sem perguntar:

- frontmatter YAML (`tags`, `sources`, `created`, `updated`, `summary`, `status`);
- H1 e byline, conforme `## Byline do essay` em `conventions/SKILL.md`;
- `## Sumário` gerado a partir dos H2 que já existem no texto;
- conversão de formatação para Markdown: headings, ênfase, listas, tabelas, notas de rodapé, equações, imagens extraídas para `wiki/assets/`;
- links externos inline na primeira ocorrência dos termos relevantes;
- `## Referências` reformatado no padrão AIAA a partir da bibliografia original;
- `## Conexões` com os wikilinks internos.

Fora desta lista, nada. Não reescreva frase, não corrija gramática, não condense,
não acrescente seção de conteúdo, não crie resumo dentro do corpo. Isso é trabalho
posterior e explícito, via `/expand`, `/proofread`, `/polish` ou `/chapter`.

### Tradução é decisão do Usuário, e fica registrada

Traduzir não é preservar: o essay resultante é uma **tradução**, e apresentá-lo
como o texto original engana o leitor sobre a autoria de cada frase. Por isso:

1. Se a fonte não estiver em Português do Brasil, **pergunte** antes de traduzir. Traduzir e importar, ou importar no idioma original, são as duas respostas válidas; nenhuma é padrão.
2. Traduzida, registre com o vocabulário que já existe — nenhum campo novo:
   - `sources:` no frontmatter aponta para o arquivo original arquivado;
   - a primeira entrada de `## Referências` é o texto original (título, container, ano), com a nota contextual dizendo que este essay é a tradução;
   - em `wiki/sources/manifest.md`, a linha `Virou:` aceita texto após o wikilink: `Virou: [[slug|Título]] — tradução para pt-BR`;
   - em `wiki/sources/map.md`, o `Status:` diz `Traduzido e importado como [[Essay]]`.

## Antes de começar: confirme a natureza da fonte

Se não estiver claro que o texto é do próprio Usuário e já está pronto (não um rascunho a desenvolver, não um material de terceiro), pergunte antes de prosseguir. É melhor uma pergunta rápida do que apresentar o trabalho de outra pessoa como um essay do autor.

## Passo a passo

1. Leia a fonte inteira em `raw/`.
2. Discuta com o Usuário os pontos-chave, se fizer sentido — mas a prosa em si não muda.
3. Se a fonte não estiver em Português do Brasil, pergunte se traduz; sem resposta explícita, não traduza. Ver `### Tradução é decisão do Usuário, e fica registrada`.
4. Classifique o `Tipo:` do source, normalmente `Ensaio Completo Importado`, conforme `## Tipos de Source — Vocabulário Controlado` em `conventions/SKILL.md`; isso determina a subpasta de destino em `wiki/sources/`.
5. Copie o conteúdo **integralmente** para `wiki/essays/` como arquivo `.md`, aplicando apenas o que está em `### Transformações autorizadas no essay derivado`. Sem resumo condensado dentro do essay. `status: finalizado` por padrão; use `draft` se ficar claro que é rascunho do próprio autor, conforme `## Status de essay` em `conventions/SKILL.md`.
6. Identifique conceitos e entidades mencionados. Para cada um: se já existe página, atualize com informação nova desta fonte; se não existe e a página tiver valor próprio, crie na subpasta apropriada.
7. Verifique se os concepts/entities criados ou atualizados têm relação com pelo menos um essay. Registre as relações em `## Conexões`; não crie um novo essay apenas para evitar órfão.
8. Adicione wikilinks entre páginas relacionadas na seção `## Conexões`, conforme `## Regra de links — Obsidian é o leitor primário` em `conventions/SKILL.md`.
9. Preencha `summary:` e rode `python scripts/build_index.py` para regenerar `wiki/index.json`/`wiki/index.md`; nunca edite o índice à mão.
10. Converta a bibliografia original para `## Referências` segundo `## Formato de ## Referências — padrão AIAA` em `conventions/SKILL.md`: título em itálico, container completo e `[Link](url)` no final da entrada. Valide com `python scripts/check_references.py --file <slug>` e rode `python scripts/build_references.py`.
11. Mova o arquivo original de `raw/` para `wiki/sources/<subpasta-do-tipo>/`, preservando o nome original. Registre em `wiki/sources/manifest.md` e `wiki/sources/map.md`. `Tags:` reutiliza o mesmo vocabulário controlado das páginas.
12. Feche com o `## Fechamento padrão de essay único` de `conventions/SKILL.md`.
13. Log: `## [YYYY-MM-DD] import | Título do Essay`.

Uma única fonte pode tocar muitas páginas. Isso é normal.

## Convenções

- **A source arquivada nunca é alterada**, em nenhum momento; o essay derivado só muda além das transformações autorizadas sob pedido explícito, via `/expand`, `/proofread`, `/polish` ou `/chapter`.
- Não invente dados bibliográficos. Confirme fonte, autores, título e container antes de criar referência.

## Skills relacionadas

- `/digest` — fonte de terceiro
- `/absorb`, `/expand`, `/proofread`, `/polish`
