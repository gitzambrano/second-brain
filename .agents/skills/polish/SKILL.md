---
name: polish
description: >
  Passada de estilo de prosa num essay: tom, ritmo, elegância, adesão
  às regras de prosa da wiki. Use quando o Usuário disser "melhora o
  estilo", "deixa a prosa mais elegante", "tira os bullets daqui",
  "conta os travessões", ou quiser que o texto leia melhor sem mudar
  o que ele argumenta.
allowed-tools: Bash Read Write Edit Glob Grep
---
# Polish

Ajusta tom, ritmo e elegância sem alterar conteúdo. Aplica `## Estilo de prosa` de `conventions/SKILL.md`.

## Regra de abertura

Leia o essay inteiro antes de reescrever qualquer trecho.

## O que corrigir

1. **Uma proposição principal por frase.**
2. **Conectores:** remova empilhamento ou transições desnecessárias.
3. **Bullets:** converta em prosa quando estiverem substituindo argumento corrido; preserve listas reais quando a estrutura justificar.
4. **Travessões:** respeite o limite de `conventions/SKILL.md`; reescreva excedentes.
5. **Ponto e vírgula:** elimine; prefira frases autônomas.
6. **Atalhos tipográficos:** evite barras, til, remissões abreviadas e intervalos com hífen na prosa quando prejudicarem clareza.
7. **Essays técnicos:** elimine antropomorfização, gerúndio ambíguo, nominalização pesada e superlativo vazio.

## O que preservar

Mantenha a voz do autor, o registro adequado ao domínio e o conteúdo argumentativo.

Não adicione nem remova ideias.

## Relatório

Resuma categorias de ajustes em vez de listar cada troca, salvo se o Usuário pedir diff.

## Depois

Feche com o `## Fechamento padrão de essay único` de `conventions/SKILL.md`.

Atualize `updated:`. Logue apenas quando a passada for extensa:

```markdown
## [YYYY-MM-DD] polish | Título do Essay
Resumo do ajuste de estilo.
```

## Convenções

Segue a regra de status de `conventions/SKILL.md`.

## Skills relacionadas

- `/proofread`
- `/sweep`
