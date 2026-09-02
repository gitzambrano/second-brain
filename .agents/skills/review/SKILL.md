---
name: review
description: >
  Faz peer review crítico de um essay: força da tese, lógica, validade
  física/matemática, profundidade, citações, gaps e oportunidades de
  enriquecimento. Invoca /continuity para coerência estrutural e só
  edita após aprovação explícita de um plano de modificação.
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch AskUserQuestion
---
# Review

Revisa conteúdo e argumento, não estilo. `/continuity` cobre coerência estrutural; `/organize` cobre metadados/formatação; `/proofread` e `/polish` cobrem linguagem.

`/review` é interativo e não roda em batch.

## 1. Preparar

1. Resolva o essay alvo; pergunte apenas se houver ambiguidade.
2. Leia o essay inteiro.
3. Rode `/continuity` primeiro e reutilize os achados. Não refaça o mesmo checklist.
4. Busque na wiki antes de sugerir material externo.

## 2. Avaliar

Analise seis dimensões.

### Força argumentativa

- A tese depende de premissa frágil ou implícita?
- Qual é a objeção mais forte de um leitor informado?
- O essay responde essa objeção?
- Qual elo mais enfraquece a conclusão?

### Validade lógica e filosófica

- Há falácia, falsa dicotomia, generalização ou apelo indevido à autoridade?
- Conceitos importantes estão definidos e usados de forma consistente?
- Em tema filosófico, objeções clássicas relevantes estão representadas?

### Validade física e matemática

- Afirmações quantitativas têm fonte, derivação ou ordem de grandeza?
- Unidades, hipóteses e limites de validade estão corretos?
- Há conflito com princípios físicos estabelecidos?

Para essay técnico, duas exigências são obrigatórias:

1. **Insight físico de first principles:** mecanismo, causa e resposta a parâmetros.
2. **Desenvolvimento matemático:** equações centrais apresentadas ou derivadas com os passos que carregam a física.

Falta de qualquer uma é **Crítico**.

### Profundidade e completude

- Há descrição sem mecanismo?
- Algum conceito ficou apenas no nível de definição?
- Falta exemplo, consequência concreta ou caso numérico onde seria útil?

### Citações e cobertura

- Claims históricos, empíricos ou atribuídos têm fonte?
- Falta autor, obra, corrente ou perspectiva indispensável ao tema?
- Há seção relevante praticamente sem sustentação externa?

### Enriquecimento

Sugira somente quando agregar valor real:
- fonte ou obra específica;
- experimento mental;
- exemplo concreto ou numérico;
- analogia útil;
- conexão com outra página da wiki.

## 3. Priorizar e reportar

Classifique:

- **🔴 Crítico:** enfraquece ou invalida a tese; resolver antes de `revisao`.
- **🟡 Moderado:** reduz rigor, clareza ou profundidade.
- **🟢 Sugestão:** enriquecimento opcional.

Reporte antes de editar:

```markdown
## Relatório de Revisão — Título

### Visão geral
...

### 🔴 Críticos
1. Problema — localização — impacto.

### 🟡 Moderados
1. ...

### 🟢 Sugestões
1. ...

### Fontes / exemplos candidatos
- ...
```

Inclua os achados relevantes de `/continuity` na visão geral e na prioridade apropriada.

## 4. Plano de modificação

Pergunte quais achados o Usuário quer resolver. Para os selecionados, proponha um plano numerado com:

- localização;
- mudança concreta;
- evidência/fonte necessária;
- efeito esperado no argumento.

Aguarde aprovação explícita. Não edite antes dela.

## 5. Executar o plano aprovado

Para cada item aprovado:

1. releia o trecho em contexto;
2. aplique somente a mudança aprovada;
3. preserve o estilo do essay e siga `conventions/SKILL.md`;
4. atualize Sumário/Referências quando a estrutura ou fontes mudarem;
5. marque o item como concluído.

Não amplie o escopo silenciosamente.

## 6. Fechar

Após mudanças:

- atualize `updated:`;
- rode o fechamento mecânico de essay único em `conventions/SKILL.md`;
- se referências mudaram, rode `python scripts/build_references.py`;
- se summary/tags mudaram, rode `python scripts/build_index.py`;
- registre:

```markdown
## [YYYY-MM-DD] review | Título
Revisão: N críticos, M moderados, K sugestões. X modificações aplicadas.
```

Se o essay era `draft` e não restar crítico, pergunte se o Usuário quer promover para `revisao`. Não altere status automaticamente.

Se a edição mudou estrutura ou tese, ofereça repetir `/continuity`.

## Limites

- Não edite sem aprovação do plano.
- Não transforme review em reescrita de estilo.
- Não invente citações; verifique fontes antes de integrá-las.
- Contradições seguem `## Regra de contradição entre fontes` em `conventions/SKILL.md`.
