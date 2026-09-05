---
name: polish
description: >
  Melhora clareza, concisão, tom e naturalidade sem mudar conteúdo ou argumento.
  Use para revisão de estilo; as regras normativas de prosa vivem em
  conventions/SKILL.md e devem prevalecer sobre heurísticas desta passada.
metadata:
  second-brain-role: "style-editor"
  second-brain-mode: "write"
  second-brain-scope: "essay"
  second-brain-approval: "none"
  second-brain-closure: "single-essay"
allowed-tools: Bash Read Write Edit Glob Grep
---
# Polish

Revisa estilo sem alterar conteúdo, tese ou ordem lógica. A definição normativa do que constitui boa prosa está em `## Estilo de prosa` de `conventions/SKILL.md`; **não replique esse checklist aqui**.

## Fluxo

1. Leia o essay inteiro antes da primeira edição.
2. Aplique `## Estilo de prosa` de `conventions/SKILL.md` ao documento no contexto, não por substituição cega de palavras.
3. Procure padrões recorrentes que prejudiquem clareza, coesão, naturalidade ou precisão técnica.
4. Preserve voz do autor, terminologia técnica, cautela epistemológica, repetição deliberada e ritmo intencional.
5. Uma ocorrência isolada de um termo que aparece como gatilho em `conventions` não é erro por si só; avalie função e contexto.
6. Não adicione nem remova ideias. Se a correção necessária mudar argumento, evidência ou estrutura, reporte e encaminhe para `/expand`, `/chapter` ou `/review` em vez de fazê-la silenciosamente.

## Relatório

Resuma as categorias de ajuste e qualquer item substantivo que tenha ficado fora do escopo. Não liste cada troca salvo se o Usuário pedir diff.

## Fechamento

Use o `## Fechamento padrão de essay único` de `conventions/SKILL.md`.

Não altere `updated:` por revisão apenas estilística. Registre em `wiki/log.md` somente quando a passada for extensa:

```markdown
## [YYYY-MM-DD] polish | Título do Essay
Resumo do ajuste de estilo.
```

## Limites

- `conventions/SKILL.md` é a única fonte normativa das regras de prosa.
- `/proofread` corrige língua; `/polish` corrige estilo.
- `/review` trata argumento e evidência; `/chapter` trata estrutura.
