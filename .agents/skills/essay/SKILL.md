---
name: essay
description: >
  Escreve um essay, white paper ou estudo novo do zero, não derivado
  de uma fonte em raw/. Use quando o usuário quiser escrever um essay,
  rascunhar um white paper, desenvolver uma ideia num essay completo,
  disser "quero escrever sobre X", "cria um ensaio sobre", "vamos
  desenvolver essa ideia", ou quiser ajuda para autorar conteúdo
  original, profundo e extenso. Sempre comece perguntando a tese
  central do essay antes de qualquer outra coisa.
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch
---

# Essay

Parceiro de escrita e pesquisa para criar um essay novo, original, do zero. Diferente de `/import` e `/digest`, não há fonte bruta sendo processada: a ideia nasce da conversa com o usuário, e Claude pesquisa, estrutura e escreve no padrão da wiki. É coautoria: Claude é a extensão da mente do usuário para pesquisa, estruturação e redação, não um ghostwriter que decide sozinho o que o ensaio vai dizer.

O essay resultante deve ser **extenso, profundo e criativo**, não um resumo nem um esboço: o oposto de um artigo curto de blog, com desenvolvimento real de cada ideia.

## 1. Pergunte a tese central primeiro — sempre

Antes de qualquer outra coisa, pergunte qual é a **tese principal** do essay: a posição que ele vai defender, não só o tema. "Quero escrever sobre livre-arbítrio" é um tema; "quero argumentar que o compatibilismo dissolve o problema, não o resolve" é uma tese. Se o usuário só trouxer o tema, peça a tese antes de propor qualquer esboço: pesquisa, estrutura e argumentação seguem essa linha, não o contrário.

Depois da tese, confirme rapidamente (sem questionário formal se já vier na mensagem):

1. **Tipo**: `Ensaio`, `White Paper`, `Brainstorm`, `Estudo` ou `Análise`?
2. **Categoria temática** (ex: `Filosofia da Mente`, `Dinâmica de Aeronaves`) — usada na byline e no index.
3. **Domínio**: filosófico, técnico/engenharia, ou misto — isso muda o que a seção 4 exige (ver abaixo).

## 2. Pesquisar o terreno antes de escrever

1. **Busque na wiki existente** (`wiki/index.md`, `wiki/concepts/`, `wiki/entities/`) por temas relacionados. Um essay novo deve **linkar e construir sobre** essays/conceitos anteriores do usuário quando fizer sentido.
2. Use `WebSearch`/`WebFetch` para embasamento externo: dados, citações, referências acadêmicas, e — se o domínio for filosófico — as correntes e pensadores relevantes ao argumento. Parafraseie sempre, nunca reproduza trechos longos de fontes de terceiros.
3. Reporte ao usuário o que encontrou de relacionado na wiki: *"Isso conversa direto com [[Mente Aumentada]] e [[Second Brain]] — vou linkar os dois."*

## 3. Estruturar antes de redigir

Proponha um esboço de capítulos e espere aprovação antes do texto corrido. Estrutura mínima, sempre:

- **Introdução** — situa o problema e apresenta a tese, não só o tema
- **Capítulos de desenvolvimento** — sem teto artificial de quantidade. Um tema denso pode passar de 10 capítulos; o que importa é que cada um avance um passo real do argumento e prepare o seguinte. Prefira mais capítulos focados a poucos capítulos genéricos: divida quando um capítulo tenta cobrir mais de uma ideia central.
- **Conclusão** — fecha o argumento aberto na introdução, não introduz ideia nova não preparada antes

Cada capítulo deve se encadear logicamente com o anterior e com o seguinte — nunca uma sequência de seções independentes sob o mesmo título. Ao propor o esboço, mostre explicitamente essa cadeia (o que o capítulo N prepara para o capítulo N+1). Se o desenvolvimento crescer para muitos capítulos, rode `/continuity` ao final para confirmar que a progressão ainda se sustenta do início ao fim.

## 4. Redigir com profundidade real

Escreva em `wiki/essays/<slug>.md`, Português do Brasil, seguindo `## Estilo de Prosa dos Essays` do AGENTS.md (prosa corrida, travessões extremamente raros).

### Se o domínio é filosófico

- **Cite correntes, pensadores e obras específicas** — não fale de "algumas teorias éticas", nomeie o utilitarismo de Mill, o deontologismo kantiano, a ética das virtudes aristotélica, conforme o argumento pedir. Toda corrente/pensador citado leva **hyperlink** (Stanford Encyclopedia of Philosophy é a fonte preferencial, Wikipedia como alternativa) na primeira menção.
- **Mantenha uma tese do início ao fim** — o essay argumenta por uma posição, não apresenta "todos os lados" sem se comprometer. Apresentar objeções é bom argumentação; abandonar a tese no meio do caminho não é.
- **Use experimentos mentais quando o argumento pedir** — o quarto chinês, o cérebro de Boltzmann, o navio de Teseu, ou um experimento mental original construído para o argumento específico, sempre que ele ilumina a tese melhor que a exposição direta.
- Cite livros e artigos específicos que sustentam ou desafiam a tese, não apenas o nome do pensador solto.

### Se o domínio é técnico/engenharia

- **Extraia os princípios físicos do problema primeiro** — antes de qualquer equação, a exposição deve deixar claro *por que* o fenômeno acontece fisicamente, não só *como* calculá-lo.
- **Desenvolva matematicamente** — equações completas, não só o resultado final. Mostre a derivação quando ela ilumina o princípio físico por trás, não só o resultado.
- **Use exemplos de aplicação** — um caso numérico concreto aplicando o equacionamento desenvolvido, não deixar a matemática abstrata sem nunca tocar num número real.
- **Plots, gráficos, equações e diagramas**: gere plots/gráficos como artefatos (ex: matplotlib, salvos como imagem e referenciados no essay) sempre que uma relação quantitativa for mais clara visualmente que em prosa. Diagramas (esquemas, fluxos) da mesma forma. Ver skill `frontend-design`/ferramentas de visualização disponíveis para gerar essas figuras.
- Cite normas técnicas, papers e livros-texto específicos que sustentam o equacionamento, com link quando disponível.

### Se o domínio é misto

Aplique as duas seções acima na proporção que o argumento pedir — um essay sobre ética da automação aeronáutica, por exemplo, pode precisar tanto de correntes éticas quanto de equacionamento de sistemas de controle.

### Checklist obrigatório (todo domínio)

- **Frontmatter YAML**: `tags` (reuse do vocabulário controlado — só crie tag nova se nenhuma existente cobrir o tema), `sources`, `created`, `updated`
- **Título** `# Título do Essay`, linha em branco, byline (`> Tipo · Categoria`, `> Gustavo Zambrano · Mês de Ano`, sem `:`, sem `[[wikilinks]]`)
- **Sem resumo condensado dentro do essay** — vai direto da byline pro `## Sumário`; a introdução (primeira seção `##`) cumpre esse papel. Resumo de uma página é handout (`/handout`), nunca seção do essay.
- **`## Sumário`** logo após a byline, com links para cada seção `##` (exceto Referências e Conexões)
- **Corpo**: só links externos `[texto](url)` inline, nunca `[[wikilinks]]` fora de Conexões. **Mínimo 10 links externos**, cobrindo pensadores/correntes/obras (filosofia) ou normas/papers/conceitos técnicos (engenharia).
- **`## Referências`** (heading exato) com a bibliografia usada — cite a fonte sempre que possível, nunca afirme um dado ou claim sem verificação.
- **`## Conexões`** como última seção, só `[[wikilinks]]` para essays/conceitos/entidades relacionados

## 5. Criar/atualizar conceitos e entidades

Todo conceito, pensador, ou entidade central ao argumento que ainda não tem página própria ganha uma em `wiki/concepts/` ou `wiki/entities/`, linkada de volta ao essay. Nenhum conceito relevante fica sem página só porque "nasceu" num essay criado agora.

## 6. Indexar e logar

- `wiki/index.md`, categoria certa: `[[filename|Título do Essay]] — resumo de uma linha (sob 120 caracteres)`
- `wiki/log.md`:
  ```
  ## [YYYY-MM-DD] essay | Título do Essay
  Tese: uma frase com a posição central defendida.
  Tipo: X. Categoria: Y. Conecta com: [[Essay Relacionado]], [[Conceito]].
  ```

## 7. Oferecer exportação e handout

Depois de pronto, ofereça `/pdf` ou `/html` conforme o uso (imprimir/anexar vs. mandar link leve), e `/handout` se o usuário for compartilhar um resumo com terceiros. Não gere nenhum dos dois automaticamente.

## Diferença em relação a `/import` e `/digest`

| | `/import` | `/digest` | `/essay` |
|---|---|---|---|
| Ponto de partida | Arquivo em `raw/`, já pronto | Arquivo em `raw/`, de terceiro | Uma tese, conversa ou brainstorm |
| Papel do Claude | Arquivista — processa fielmente | Leitor — resume, nunca gera essay | Coautor — pesquisa, estrutura, escreve |
| Texto preservado? | Sim, intacto | N/A (não vira essay) | Não aplicável — texto é gerado |
| Pode expandir livremente depois? | Sim, via `/expand` etc. | N/A | Sim |

## Convenções

- Pergunte a tese antes do esboço, e negocie o esboço antes do texto corrido — ensaios longos são caros de refazer.
- Nunca invente citações, dados, ou referências — se não pesquisou, não afirme como fato.
- Toda a wiki é em Português do Brasil.

## Skills relacionadas

- **Iterar sobre este essay** com `/expand`, `/chapter`, `/proofread`, `/polish`, `/continuity`, `/linkify`
- **Processar novas fontes** com `/import`, `/digest`, ou `/absorb`
- **Perguntar sobre o que já existe** com `/query`
- **Organizar/auditar a wiki** com `/organize`, `/sweep`, `/stats`
