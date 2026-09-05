---
name: chapter
description: >
  Cria, move, funde, divide ou renomeia seções de um essay e escreve o conteúdo
  necessário para a nova estrutura. Use quando a mudança envolve H2/H3 ou a
  ordem do argumento; para conteúdo dentro de seção existente, use /expand.
metadata:
  second-brain-role: "structure-editor"
  second-brain-mode: "write"
  second-brain-scope: "essay"
  second-brain-approval: "conditional"
  second-brain-closure: "single-essay"
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch AskUserQuestion
---
# Chapter

Edita **a estrutura** de um essay. Esta skill é dona do trabalho quando a mudança cria, remove, move, funde, divide ou renomeia seções. Ela não devolve o conteúdo de uma seção nova para `/expand`.

## Abertura

Leia o essay inteiro antes da primeira edição. Determine o papel da seção afetada na cadeia argumentativa e confira `## Sumário`, referências e conexões que possam depender da estrutura.

## Mudança pedida diretamente

Se o Usuário já definiu a operação e o destino, execute exatamente esse brief. Para seção nova:

1. determine a posição coerente com o que vem antes e depois;
2. pesquise fatos, equações, normas ou referências necessários com `WebSearch`/`WebFetch`;
3. escreva a seção completa segundo `conventions/SKILL.md`;
4. atualize `## Sumário`;
5. releia as transições adjacentes e ajuste apenas o necessário para a nova ordem.

Se faltar detalhe operacional, derive o brief do contexto. Pergunte somente quando houver mais de uma direção substantiva plausível.

## Estrutura proposta pelo agente

Se o Usuário pedir que o agente decida como reorganizar o essay:

1. leia o documento inteiro;
2. proponha a nova sequência de seções e o papel de cada mudança;
3. espere aprovação antes de mover, fundir ou apagar texto;
4. depois da aprovação, aplique o plano sem ampliar o escopo.

## Concept ou entity associado

Quando uma seção introduzir um concept/entity que merece página própria:

```bash
python scripts/check_title.py "Título Candidato"
```

Crie a página somente se ela tiver valor independente. Use a pasta e o frontmatter de `conventions/SKILL.md` e registre a relação em `## Conexões` nos dois sentidos quando fizer sentido.

## Fechamento

Depois de qualquer mudança estrutural:

- atualize `## Sumário`;
- use o `## Fechamento padrão de essay único` de `conventions/SKILL.md`;
- atualize `updated:` porque a estrutura do corpo mudou;
- regenere referências/índice apenas quando os campos correspondentes mudarem.

Para mudança relevante, registre:

```markdown
## [YYYY-MM-DD] chapter | Título do Essay
Resumo da mudança estrutural.
```

Se houver handout e a reorganização alterar a tese ou o caminho argumentativo, informe que ele deve ser regenerado e ofereça `/handout`.

## Limites

- Não usa `/expand` como etapa intermediária de uma seção nova.
- Não reorganiza estrutura proposta pelo agente sem aprovação.
- Não inventa fatos ou referências; pesquise quando o conteúdo novo exigir evidência.
- Segue estrutura, prosa, links e status de `conventions/SKILL.md`.
