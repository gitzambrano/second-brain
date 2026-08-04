---
name: essay
description: >
  Escreve um essay, white paper ou estudo novo do zero, não derivado
  de uma fonte em raw/. Use quando o Usuário quiser escrever um essay,
  rascunhar um white paper, desenvolver uma ideia num essay completo,
  disser "quero escrever sobre X", "cria um ensaio sobre", "vamos
  desenvolver essa ideia", ou quiser ajuda para autorar conteúdo
  original, profundo e extenso. Sempre exige um esboço aprovado via
  /outline antes de escrever qualquer prosa — se não existir, aciona
  /outline primeiro e só volta aqui depois de aprovado. Única exceção:
  essay que já chega pronto, escrito pelo próprio autor — isso é
  /import, não /essay, e não passa por /outline.
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch AskUserQuestion
---
# Essay

Parceiro de escrita e pesquisa para criar um essay novo, original, do zero. Diferente de `/import` e `/digest`, não há fonte bruta sendo processada: a ideia nasce da conversa com o Usuário, e Claude pesquisa, estrutura e escreve no padrão da wiki.

É coautoria: Claude é a extensão da mente do Usuário para pesquisa, estruturação e redação, não um ghostwriter que decide sozinho o que o ensaio vai dizer.

O essay resultante deve ser **extenso, profundo e criativo**, não um resumo nem um esboço: o oposto de um artigo curto de blog, com desenvolvimento real de cada ideia.

## 0. Exija um esboço aprovado — sem exceção

`/essay` nunca escreve prosa sem um esboço aprovado em `plan/drafts/<slug>.md`. Isso é regra, não sugestão:

- **Já existe o draft** (Usuário veio de `/outline`, ou citou um esboço já pronto): leia `plan/drafts/<slug>.md`. Tese (`tese:`), tipo e domínio já estão no frontmatter; a estrutura de capítulos e bullets é o brief de escrita — não proponha esboço novo, desenvolva o que já foi aprovado. Só apague `plan/drafts/<slug>.md` quando **todos** os capítulos do esboço estiverem escritos no essay. Se a sessão terminar com o essay parcialmente escrito, mantenha o draft e marque nele quais capítulos já foram escritos (`escritos: [Capítulo 1, Capítulo 2]` no frontmatter) — isso permite retomar depois, inclusive reestruturando só a parte pendente via `/outline` (ver `## Retomar um esboço em andamento` em `outline/SKILL.md`).
- **Não existe draft ainda**: não pergunte tese nem proponha esboço aqui dentro. Rode `/outline` primeiro (mesma conversa, sem exigir que o Usuário digite o comando à parte) e só volte a este skill depois que o esboço estiver aprovado. Se o próprio pedido do Usuário já trouxer tese e capítulos detalhados o bastante, `/outline` pode tratar o esboço como implicitamente aprovado e seguir direto para escrita (ver `## Esboço implicitamente aprovado` em `outline/SKILL.md`).
- **Única exceção**: essay que já é texto pronto do próprio autor não passa por aqui — isso é `/import`, que transforma o texto em `.md` preservando-o intacto, sem tese a estruturar porque não há autoria nova acontecendo.

## 1. Pesquisar o terreno antes de escrever

1. **Busque na wiki existente** por temas relacionados — prefira `qmd query "tema"` (busca semântica, ver `## Ferramentas` no AGENTS.md); sem qmd disponível/indexado, use `python scripts/find_text.py "tema" --ignore-case` (cobre essays, `wiki/concepts/`, `wiki/entities/` de uma vez). Um essay novo deve **linkar e construir sobre** essays/conceitos anteriores do Usuário quando fizer sentido — o esboço aprovado já deve ter listado candidatos em `## Conexões candidatas`, confirme e complete.
2. Use `WebSearch`/`WebFetch` para embasamento externo, agora capítulo a capítulo, com a profundidade que `/outline` deliberadamente não fez: dados, citações, referências acadêmicas, e — se o domínio for filosófico — as correntes e pensadores relevantes ao argumento. Parafraseie sempre, nunca reproduza trechos longos de fontes de terceiros.

## 2. Redigir com profundidade real

Escreva em `wiki/essays/<slug>.md` em Português do Brasil com profundidade e criatividade.

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

- **Frontmatter YAML**: `tags` (reuse do vocabulário controlado — cheque `tags_in_use` em `wiki/index.json`, rode `python scripts/build_index.py` primeiro se estiver desatualizado; só crie tag nova se nenhuma existente cobrir o tema), `summary` (resumo de uma linha, até 120 caracteres — usado por `build_index.py` para montar a entrada em `wiki/index.md`), `sources`, `created`, `updated`, `status: draft` (ver `## Status de essay` em `conventions/SKILL.md`)
- **Título** `# Título do Essay`, linha em branco, byline (`> Tipo`, `> Gustavo Zambrano · Mês de Ano`, sem `:`, sem `[[wikilinks]]`)
- **Sem resumo condensado dentro do essay** — vai direto da byline pro `## Sumário`; a introdução (primeira seção `##`) cumpre esse papel. Resumo de uma página é handout (`/handout`), nunca seção do essay.
- **`## Sumário`** logo após a byline, com links para cada seção `##` (exceto Referências e Conexões)
- **Corpo**: só links externos `[texto](url)` inline, nunca `[[wikilinks]]` fora de Conexões. **Mínimo 10 links externos**, cobrindo pensadores/correntes/obras (filosofia) ou normas/papers/conceitos técnicos (engenharia).
- **`## Referências`** (heading exato) com a bibliografia usada — cite a fonte sempre que possível, nunca afirme um dado ou claim sem verificação. Antes de escrever uma entrada nova, confira `wiki/references.md`: se a mesma obra já está catalogada (outro essay já cita), reuse a citação exata em vez de redigir uma versão nova — ver `## wiki/references.md e wiki/references.json` em `conventions/SKILL.md`. O formato de cada entrada é o de `## Formato de "## Referências" — padrão AIAA` em `conventions/SKILL.md`, e não é opcional:

  ```
  [1] Cheeseman, I. C., e Bennett, W. E., *The Effect of the Ground on a Helicopter Rotor in Forward Flight*, ARC R&M No. 3021, HMSO, London, 1955. — Nota curta opcional. [Link](https://…)
  [2] *Blade Element Momentum Theory*, Wikipedia, The Free Encyclopedia. [Link](https://…)
  ```

  Três erros que o corpus antigo acumulou e que **não** devem se repetir: título fora do itálico (todo título vai em itálico, inclusive verbete de enciclopédia e norma técnica); link em qualquer lugar que não seja a palavra `Link` no fim da entrada — nem no título, nem no periódico, nem envolvendo a citação inteira; e entrada que é só um link de glossário sem obra, autor nem container — se o alvo é um verbete, escreva-o como verbete (`*Título do verbete*, Wikipedia. [Link](url)`), e se não é fonte de nada, ele pertence ao corpo do texto, não à bibliografia.

  Confira com `python scripts/check_references.py --file <slug>` antes de encerrar.
- **`## Conexões`** como última seção, com wikilinks para essays/conceitos/entidades relacionados no formato de `## Regra de links` em `conventions/SKILL.md`

## 3. Criar/atualizar conceitos e entidades

Todo conceito, pensador, ou entidade central ao argumento que ainda não tem página própria ganha uma em `wiki/concepts/` ou `wiki/entities/`, linkada de volta ao essay (não no corpo do texto). Antes de criar, rode `python scripts/check_title.py "Título Do Conceito"` — evita nascer um quase-duplicado de página que já existe com outra grafia. Nenhum conceito relevante fica sem página só porque "nasceu" num essay criado agora.

## 4. Indexar e logar

- Feche com uma checagem de formato do essay recém-criado, sem acionar `/organize` inteiro (caro e desproporcional para um único arquivo):

  ```bash
  python scripts/check_wiki.py <slug>
  python scripts/fix_lint.py <slug>
  ```

  Aplique os achados mecânicos e reporte o restante. Só rode `/organize <slug>` se o Usuário pedir a auditoria completa daquele essay.
- Preencha `summary:` no frontmatter (resumo de uma linha, até 120 caracteres) e rode `python scripts/build_index.py` para regenerar `wiki/index.json`/`wiki/index.md` — nunca insira a entrada à mão (ver `## Formato do índice` em `conventions/SKILL.md`).
- Rode `python scripts/build_references.py` para regenerar `wiki/references.json`/`.md` a partir da `## Referências` do essay novo (mesmo padrão de `build_index.py` — artefato gerado, nunca editado à mão).
- `wiki/log.md`:

  ```
  ## [YYYY-MM-DD] essay | Título do Essay
  Tese: uma frase com a posição central defendida.
  Tipo: X. Conecta com: [[slug-do-essay|Essay Relacionado]], [[slug-do-conceito|Conceito]].
  ```

## 5. Oferecer exportação e handout

Depois de pronto, ofereça `/pdf` ou `/html` conforme o uso (imprimir/anexar vs. mandar link leve), e `/handout` se o Usuário for compartilhar um resumo com terceiros. Não gere nenhum dos dois automaticamente.

## Diferença em relação a `/import` e `/digest`

|                                  | `/import`                                        | `/digest`                        | `/essay`                                                 |
| -------------------------------- | -------------------------------------------------- | ---------------------------------- | ---------------------------------------------------------- |
| Ponto de partida                 | Arquivo em `raw/`, já pronto                     | Arquivo em `raw/`, de terceiro    | Esboço aprovado via `/outline`                           |
| Papel do Claude                  | Arquivista — processa fielmente                   | Leitor — resume, nunca gera essay | Coautor — pesquisa e escreve sobre o esboço já aprovado |
| Texto preservado?                | Sim, intacto                                       | N/A (não vira essay)              | Não aplicável — texto é gerado                         |
| Passa por `/outline`?           | Não — já é texto pronto, sem tese a estruturar | N/A — nunca vira essay            | Sim, sempre                                                |
| Pode expandir livremente depois? | Sim, via `/expand` etc.                           | N/A                                | Sim                                                        |

## Convenções

- Todo texto adicionado segue estilo e formatação em `conventions/SKILL.md`
- Nunca invente citações, dados, ou referências — se não pesquisou, não afirme como fato.
- Toda a wiki é em Português do Brasil.

## Skills relacionadas

- `/outline` — obrigatório antes deste skill, exceto quando a fonte é `/import`
- `/expand`, `/chapter`, `/proofread`, `/polish`, `/continuity`, `/linkify`, `/import`, `/digest`, `/absorb`, `/query`, `/organize`, `/sweep`, `/stats`, `/gaps`
- Se este essay veio de um item do plano (seção "Essays Futuros"), rode `/plan done` ao terminar
