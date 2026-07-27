---
name: review
description: >
  Revisor de essay no estilo de peer review acadêmico: analisa validade
  argumentativa, lógica, física e matemática; detecta fenômenos mal
  explicados, ausência de citações de autores e filósofos, gaps
  conceituais e de profundidade. Além de apontar problemas, sugere fontes
  candidatas, experimentos mentais, exemplos concretos e conexões com
  ideias da wiki. Cria um plano de modificação para o Usuário aprovar
  antes de editar qualquer coisa. Use quando o Usuário disser "faz um
  review do essay X", "esse ensaio está profundo o suficiente?", "quais
  são os gaps argumentativos?", ou quiser o olhar de um revisor externo
  antes de marcar um essay como maduro ou finalizado.
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch AskUserQuestion
---
# Review

Funciona como um revisor de paper acadêmico: lê o essay com olhar crítico e construtivo, identifica problemas de argumentação, profundidade e rigor, e — diferente de um revisor puramente negativo — sugere ativamente o que enriqueceria o texto. Só edita após o Usuário aprovar um plano de modificação explícito.

## Passo a passo

### 1. Identificar o essay

Resolva o alvo:

- Com argumento (`/review meu-essay`): localize `wiki/essays/<slug>.md`. Se ambíguo, pergunte.
- Sem argumento: pergunte qual essay revisar — `/review` não roda em batch por design (o fluxo interativo não escala).

Leia o essay inteiro antes de qualquer análise.

### 2. Análise crítica — sete dimensões

Analise o essay em silêncio, gerando um relatório interno antes de qualquer saída. Use as sete dimensões abaixo como checklist:

#### 2.1 Tese e estrutura do argumento

- A tese central é explicitada no início?
- Cada capítulo avança o argumento, ou algum tangencia ou repete?
- A conclusão fecha o argumento aberto — não apenas resume, mas conclui?
- Há premissas implícitas que sustentam a tese sem nunca serem declaradas?

#### 2.2 Validade lógica e filosófica

- Há falácias detectáveis (post hoc ergo propter hoc, homem-palha, apelo à autoridade sem referência, generalização indevida, falsa dicotomia)?
- Se o essay toma posição filosófica, reconhece as objeções clássicas ao campo (ex: se defende determinismo, menciona o problema da agência; se defende emergência, menciona o argumento de Searle)?
- Conceitos-chave são definidos antes de serem usados?

#### 2.3 Validade física e matemática (quando aplicável)

- Afirmações quantitativas têm fonte ou estimativa de ordem de grandeza?
- Há contradições com leis ou princípios bem estabelecidos (termodinâmica, conservação, relatividade, etc.)?
- Modelos matemáticos são usados corretamente (unidades, limites de validade)?

#### 2.4 Profundidade e completude

- Algum fenômeno é descrito mas não explicado mecanisticamente (o "como" está ausente)?
- Algum conceito é introduzido mas nunca aprofundado além do nível de enciclopédia?
- Há seções que "pairiam" sobre o tema sem nunca aterrissar num exemplo ou consequência concreta?

#### 2.5 Citações e atribuições

- Ideias de filósofos, cientistas ou correntes são atribuídas sem nomear o autor/obra?
- Há afirmações de caráter histórico ou empírico sem nenhuma referência?
- Alguma seção inteira não cita nenhuma fonte externa?

#### 2.6 Gaps conceituais e de cobertura

- O essay menciona uma ideia conexa que deveria ser desenvolvida mas não é?
- Há uma perspectiva contrária relevante que está completamente ausente?
- O essay ignora um autor ou tradição que naturalmente deveria aparecer dado o tema?

#### 2.7 Oportunidades de enriquecimento

Esta dimensão é propositiva, não crítica. Liste ativamente o que tornaria o essay mais rico:

- **Experimentos mentais**: cenários hipotéticos que tornam o argumento mais palpável (ex: para um essay sobre identidade pessoal, o Teleporter de Parfit; para entropia, Maxwell's Demon)
- **Exemplos concretos e numéricos**: casos reais, dados, estimativas de ordem de grandeza que tiram o argumento da abstração
- **Fontes candidatas**: papers, livros ou autores que o essay deveria citar ou que ampliariam a argumentação — a buscar via `/scout` depois, se o Usuário quiser
- **Conexões com outros essays da wiki**: ideias que já foram desenvolvidas em outro lugar e que poderiam ser integradas (use os `[[wikilinks]]` conhecidos)
- **Analogias**: pontes entre domínios que clarificam o argumento sem simplificá-lo

### 3. Classificar e priorizar os achados

Organize os achados em três níveis de prioridade:

- **🔴 Crítico** — problema que enfraquece ou invalida a tese; deve ser resolvido antes de marcar o essay como `maduro`
- **🟡 Moderado** — lacuna ou imprecisão que reduz a credibilidade ou profundidade; vale resolver agora
- **🟢 Sugestão** — enriquecimento que tornaria o essay mais rico, mas que não é um problema atual

### 4. Apresentar o Relatório de Revisão

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

### 5. Criar o Plano de Modificação

Após apresentar o relatório, pergunte ao Usuário quais issues ele quer resolver nesta sessão. Para cada issue selecionado, proponha a modificação concreta:

- Para um gap filosófico: o parágrafo ou seção a adicionar, com rascunho
- Para uma citação ausente: o nome do autor/obra a referenciar, com sugestão de como integrá-la
- Para um fenômeno mal explicado: o mecanismo a detalhar, com sugestão de linguagem
- Para um experimento mental: onde no texto ele entraria e um rascunho da passagem

Agrupe as modificações em um **plano numerado**, apresente ao Usuário, e aguarde aprovação explícita antes de editar.

### 6. Executar o Plano Aprovado

Aplique **apenas** as modificações aprovadas, na ordem do plano. Para cada modificação:

1. Leia o trecho atual em contexto (parágrafo anterior e posterior)
2. Aplique a modificação preservando o estilo de prosa do essay
3. Confirme que o `## Sumário` ainda está correto (se uma seção nova foi adicionada, adicione o link)
4. Marque o item do plano como concluído antes de passar ao próximo

### 7. Registrar e fechar

Após aplicar as modificações:

- Atualize `updated:` no frontmatter do essay
- Registre em `wiki/log.md`:

  ```
  ## [YYYY-MM-DD] review | [Título do Essay]
  Revisão: N issues críticos, M moderados, K sugestões. X modificações aplicadas.
  ```

- Se o essay estava `draft` e todos os críticos foram resolvidos, **pergunte** ao Usuário se quer promovê-lo para `maduro` — não faça isso automaticamente.
- Oferença `/continuity` se detectar gaps que exigem a intervenção desse skill.
- Ofereça `/status update` se a sessão for encerrada após o review.

## Regras e limites

1. **Nunca edite sem aprovação explícita** — o plano de modificação é obrigatório.
2. **Não confunda review com reescrita** — o objetivo é melhorar o argumento e a profundidade, não mudar o estilo pessoal do Usuário. Em caso de dúvida, proponha e pergunte.
3. **Em contradição entre fontes**: siga a regra de `conventions/SKILL.md` — apresente as duas versões e aguarde o Usuário decidir qual prevalece.
4. **Não invente citações**: se uma citação parece necessária mas você não tem certeza da fonte exata, sinalize como "verificar" e deixe para o Usuário confirmar via `/scout` ou busca manual.
5. **Busque na wiki primeiro**: antes de sugerir uma fonte externa, verifique se a ideia já foi desenvolvida em outro essay ou concept da wiki — prefira uma conexão interna se ela existir.

## Skills relacionadas

- `/continuity` — fluxo narrativo (complementar ao review)
- `/expand` — aplicar uma adição específica decidida após o review
- `/scout` — buscar fontes candidatas sugeridas no relatório
- `/proofread`, `/polish` — revisão de língua e estilo após o review de conteúdo
- `/sweep` — sequência completa de revisões (inclui `/format`, continuity, proofread, polish, linkify)
