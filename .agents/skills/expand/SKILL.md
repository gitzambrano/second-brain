---
name: expand
description: >
  Adiciona ou corrige conteúdo substantivo dentro da estrutura existente de um
  essay. Use para ideias, exemplos, derivações e correções factuais/conceituais;
  use /chapter quando o pedido exigir criar, mover, fundir ou dividir seções.
metadata:
  second-brain-role: "content-editor"
  second-brain-mode: "write"
  second-brain-scope: "essay"
  second-brain-approval: "conditional"
  second-brain-closure: "single-essay"
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch AskUserQuestion
---
# Expand

Edita **o que o essay diz** dentro da estrutura que já existe. `/chapter` é o dono de mudanças em H2/H3 e de reorganização estrutural.

## Fluxo

1. Resolva o essay e leia-o inteiro antes de editar.
2. Identifique o ponto exato de integração e preserve a progressão do texto.
3. Se o pedido estiver claro, execute. Pergunte apenas quando houver uma decisão substantiva que não possa ser inferida do contexto.
4. Para afirmação factual, técnica, histórica ou quantitativa nova, verifique a fonte com `WebSearch`/`WebFetch` antes de escrever.
5. Integre o conteúdo em prosa corrida; não acrescente um adendo solto ao fim.
6. Se o pedido exigir **nova seção, divisão, fusão, movimento ou renomeação de seção**, não edite aqui: encaminhe o brief já resolvido para `/chapter`. `/chapter` não devolve esse trabalho para `/expand`.

## Fontes e referências

Quando o conteúdo novo usa uma fonte externa:

- registre-a em `## Referências` quando ela sustentar o argumento;
- procure primeiro em `wiki/references.md` e reutilize a citação canônica quando existir;
- adicione ao campo `sources:` **somente** se o arquivo estiver arquivado em `wiki/sources/`;
- um link externo consultado na web não vira `sources:` apenas por ter sido usado na edição.

Se o conceito tiver página própria e a correção também se aplicar a ela, atualize-a para evitar contradição. Crie concept/entity novo apenas quando tiver valor próprio além deste essay, seguindo `conventions/SKILL.md`.

## Correção factual ou conceitual

Quando o Usuário apontar um erro:

1. verifique se o mesmo erro aparece em outros trechos do essay;
2. confirme externamente fatos que não sejam puramente editoriais;
3. corrija todas as ocorrências equivalentes dentro do escopo;
4. preserve o restante do texto.

Contradição entre uma fonte nova e o conteúdo existente segue a regra de contradição de `conventions/SKILL.md`; não escolha um lado silenciosamente.

## Fechamento

Use o `## Fechamento padrão de essay único` de `conventions/SKILL.md`.

Atualize `updated:` somente quando a prosa do corpo mudar de forma apreciável. Se `## Referências` mudou, rode `python scripts/build_references.py`. Se summary/tags mudaram, rode `python scripts/build_index.py`.

Para mudança substancial, registre:

```markdown
## [YYYY-MM-DD] expand | Título do Essay
Resumo do que foi adicionado ou corrigido.
```

Se houver handout e a tese central tiver mudado, informe que ele ficou stale e ofereça `/handout`.

## Limites

- Não cria nem reorganiza seções; isso é `/chapter`.
- Não inventa direção editorial quando falta uma decisão substantiva.
- Não inventa fatos, referências ou dados bibliográficos.
- Segue estrutura, prosa, links, status e datas de `conventions/SKILL.md`.
