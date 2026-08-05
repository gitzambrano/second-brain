---
name: review
description: >
  Revisor de essay no estilo de peer review acadêmico — o lado
  crítico do conteúdo: ataca a força dos argumentos, aponta falácias,
  premissas implícitas não sustentadas, erros de física/matemática,
  citações ausentes, e onde a tese fica vulnerável a uma objeção que
  ela não antecipou. Invoca /continuity internamente como primeiro
  passo para a coerência estrutural (progressão entre capítulos,
  conceito usado antes de explicado, fechamento do argumento) — nunca
  reimplementa esse checklist. Além de criticar, sugere ativamente
  fontes candidatas, experimentos mentais, exemplos concretos e
  conexões com ideias da wiki. Cria um plano de modificação para o
  Usuário aprovar antes de editar qualquer coisa. Use quando o
  Usuário disser "faz um review do essay X", "esse ensaio está
  profundo o suficiente?", "quais são os gaps argumentativos?",
  "ataca essa tese", "que objeções esse argumento não considerou?",
  ou quiser o olhar de um revisor externo antes de marcar um essay
  como maduro ou finalizado.
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch AskUserQuestion
---

# Review

Funciona como um revisor de paper acadêmico: lê o essay com olhar crítico e construtivo, ataca a validade dos argumentos, e — diferente de um revisor puramente negativo — sugere ativamente o que enriqueceria o texto. Só edita após o Usuário aprovar um plano de modificação explícito.

**Divisão de trabalho com `/continuity`**: coerência estrutural (a tese se sustenta do início ao fim sem contradizer a própria conclusão, conceito usado antes de explicado, transição abrupta entre seções) é domínio de `/continuity`, invocado aqui como passo 2. `/review` não reimplementa esse checklist — a dimensão 3.1 abaixo assume que a estrutura já foi checada e mira no que `/continuity` não cobre: se os argumentos usados para sustentar a tese são fortes, e que objeção um leitor cético levantaria.

## Passo a passo

### 1. Identificar o essay

Resolva o alvo:

- Com argumento (`/review meu-essay`): localize `wiki/essays/<slug>.md`. Se ambíguo, pergunte.
- Sem argumento: pergunte qual essay revisar — `/review` não roda em batch por design (o fluxo interativo não escala).

Leia o essay inteiro antes de qualquer análise.

### 2. Invocar /continuity

Chame `/continuity` no essay identificado antes de começar a análise crítica. Ele devolve os achados de coerência estrutural (conceito antes de explicado, salto entre seções, tese sustentada, fechamento) — incorpore esses achados diretamente na seção "Visão geral" e no nível 🔴/🟡/🟢 do relatório do passo 5, em vez de rechecar a mesma coisa na dimensão 3.1.

### 3. Análise crítica — sete dimensões

Analise o essay em silêncio, gerando um relatório interno antes de qualquer saída. Use as sete dimensões abaixo como checklist:

#### 3.1 Força argumentativa da tese

Assume que a estrutura já foi checada pelo passo 2 — o foco aqui é se o argumento convence, não se ele está bem organizado:

- Os argumentos usados para sustentar a tese são fortes, ou dependem de uma premissa frágil?
- Que objeção um leitor cético e bem informado levantaria contra a tese, e o essay a antecipa?
- Há premissas implícitas que sustentam a tese sem nunca serem declaradas ou justificadas?
- Onde a tese é mais vulnerável — o elo mais fraco da cadeia argumentativa?

#### 3.2 Validade lógica e filosófica

- Há falácias detectáveis (post hoc ergo propter hoc, homem-palha, apelo à autoridade sem referência, generalização indevida, falsa dicotomia)?
- Se o essay toma posição filosófica, reconhece as objeções clássicas ao campo (ex: se defende determinismo, menciona o problema da agência; se defende emergência, menciona o argumento de Searle)?
- Conceitos-chave são definidos antes de serem usados?

#### 3.3 Validade física e matemática (quando aplicável)

- Afirmações quantitativas têm fonte ou estimativa de ordem de grandeza?
- Há contradições com leis ou princípios bem estabelecidos (termodinâmica, conservação, relatividade, etc.)?
- Modelos matemáticos são usados corretamente (unidades, limites de validade)?

**Regra fixa para essay técnico** (física, engenharia, matemática aplicada como tema central, não menção de passagem): exigir sempre as duas coisas juntas, nunca uma no lugar da outra.

- **Insight físico a partir de first principles**: o essay precisa explicar o mecanismo em linguagem física direta antes ou junto da formalização — de onde vem o efeito, por que ele existe, o que aconteceria se o parâmetro variasse. Fórmula sem intuição por trás é sinal de 🔴.
- **Desenvolvimento matemático com equações**: a afirmação quantitativa central não fica só enunciada ou citada de fonte terceira — o essay deriva ou apresenta a equação relevante, passo a passo quando a derivação for o ponto, sem pular álgebra que carregue a física do argumento.

Falta de qualquer um dos dois num essay técnico é sempre 🔴, nunca 🟡 — ausência de intuição física deixa a matemática arbitrária; ausência de equação deixa a intuição não verificável.

#### 3.4 Profundidade e completude

- Algum fenômeno é descrito mas não explicado mecanisticamente (o "como" está ausente)?
- Algum conceito é introduzido mas nunca aprofundado além do nível de enciclopédia?
- Há seções que "pairiam" sobre o tema sem nunca aterrissar num exemplo ou consequência concreta?

#### 3.5 Citações e atribuições

- Ideias de filósofos, cientistas ou correntes são atribuídas sem nomear o autor/obra?
- Há afirmações de caráter histórico ou empírico sem nenhuma referência?
- Alguma seção inteira não cita nenhuma fonte externa?

#### 3.6 Gaps conceituais e de cobertura

- O essay menciona uma ideia conexa que deveria ser desenvolvida mas não é?
- Há uma perspectiva contrária relevante que está completamente ausente?
- O essay ignora um autor ou tradição que naturalmente deveria aparecer dado o tema?

#### 3.7 Oportunidades de enriquecimento

Esta dimensão é propositiva, não crítica. Liste ativamente o que tornaria o essay mais rico:

- **Experimentos mentais**: cenários hipotéticos que tornam o argumento mais palpável (ex: para um essay sobre identidade pessoal, o Teleporter de Parfit; para entropia, Maxwell's Demon)
- **Exemplos concretos e numéricos**: casos reais, dados, estimativas de ordem de grandeza que tiram o argumento da abstração
- **Fontes candidatas**: papers, livros ou autores que o essay deveria citar ou que ampliariam a argumentação — a buscar via `/scout` depois, se o Usuário quiser
- **Conexões com outros essays da wiki**: ideias que já foram desenvolvidas em outro lugar e que poderiam ser integradas (use os `[[wikilinks]]` conhecidos)
- **Analogias**: pontes entre domínios que clarificam o argumento sem simplificá-lo

### 4. Classificar e priorizar os achados

Organize os achados em três níveis de prioridade:

- **🔴 Crítico** — problema que enfraquece ou invalida a tese; deve ser resolvido antes de marcar o essay como `maduro`
- **🟡 Moderado** — lacuna ou imprecisão que reduz a credibilidade ou profundidade; vale resolver agora
- **🟢 Sugestão** — enriquecimento que tornaria o essay mais rico, mas que não é um problema atual

### 5. Apresentar o Relatório de Revisão

Apresente o relatório ao Usuário **antes de editar qualquer coisa**. Formato:

```
## Relatório de Revisão — [Título do Essay]

### Visão geral
[2-3 frases: o que está bem, o que precisa de atenção]

### 🔴 Críticos (N)
1. [descrição do problema, localização no essay, por que enfraquece a tese]

### 🟡 Moderados (N)
1. [descrição, localização, impacto]

### 🟢 Sugestões de enriquecimento (N)
1. [o que adicionar e por quê enriquece]

### Fontes candidatas sugeridas
- [Autor, obra, por que relevante]

### Experimentos mentais / exemplos aplicáveis
- [Descrição do experimento/exemplo e onde aplicar no essay]
```

### 6. Criar o Plano de Modificação

Após apresentar o relatório, pergunte ao Usuário quais issues ele quer resolver nesta sessão. Para cada issue selecionado, proponha a modificação concreta:

- Para um gap filosófico: o parágrafo ou seção a adicionar, com rascunho
- Para uma citação ausente: o nome do autor/obra a referenciar, com sugestão de como integrá-la
- Para um fenômeno mal explicado: o mecanismo a detalhar, com sugestão de linguagem
- Para um experimento mental: onde no texto ele entraria e um rascunho da passagem

Agrupe as modificações em um **plano numerado**, apresente ao Usuário, e aguarde aprovação explícita antes de editar.

### 7. Executar o Plano Aprovado

Aplique **apenas** as modificações aprovadas, na ordem do plano. Para cada modificação:

1. Leia o trecho atual em contexto (parágrafo anterior e posterior)
2. Aplique a modificação preservando o estilo de prosa do essay
3. Confirme que o `## Sumário` ainda está correto (se uma seção nova foi adicionada, adicione o link)
4. Marque o item do plano como concluído antes de passar ao próximo

### 8. Registrar e fechar

Após aplicar as modificações:

- Atualize `updated:` no frontmatter do essay
- Se alguma modificação aplicada tocou `## Referências` (citação nova ou corrigida), rode `python scripts/build_references.py` para regenerar `wiki/references.json`/`.md`.
- Registre em `wiki/log.md`:

  ```
  ## [YYYY-MM-DD] review | [Título do Essay]
  Revisão: N issues críticos, M moderados, K sugestões. X modificações aplicadas.
  ```

- Se o essay estava `draft` e todos os críticos foram resolvidos, **pergunte** ao Usuário se quer promovê-lo para `maduro` — não faça isso automaticamente.
- Se as modificações aplicadas mudaram a estrutura ou a tese, ofereça rodar `/continuity` de novo para confirmar que a coerência se manteve após a edição.
- Ofereça `/status update` se a sessão for encerrada após o review.

## Regras e limites

1. **Nunca edite sem aprovação explícita** — o plano de modificação é obrigatório.
2. **Não confunda review com reescrita** — o objetivo é melhorar o argumento e a profundidade, não mudar o estilo pessoal do Usuário. Em caso de dúvida, proponha e pergunte.
3. **Em contradição entre fontes**: siga a regra de `conventions/SKILL.md` — apresente as duas versões e aguarde o Usuário decidir qual prevalece.
4. **Não invente citações**: se uma citação parece necessária mas você não tem certeza da fonte exata, sinalize como "verificar" e deixe para o Usuário confirmar via `/scout` ou busca manual.
5. **Busque na wiki primeiro**: antes de sugerir uma fonte externa, verifique se a ideia já foi desenvolvida em outro essay ou concept da wiki (`qmd query "tema"`, ou `find_text.py` como fallback — ver `## Ferramentas` no AGENTS.md) — prefira uma conexão interna se ela existir.

## Skills relacionadas

- `/continuity` — coerência estrutural, invocado aqui como passo 2; `/review` nunca reimplementa esse checklist
- `/expand`, `/scout`, `/proofread`, `/polish`, `/sweep`
- `/organize` — saúde de metadados/formatação; `/review` é sobre validade do argumento, não sobre isso
