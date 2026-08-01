---
name: outline
description: >
  Gera o esqueleto de um essay futuro — título, tipo, e
  cada capítulo com uma frase de papel argumentativo e bullets do
  conteúdo que entra — sem escrever texto corrido. Salva como
  artefato próprio em plan/drafts/ para o Usuário aprovar e iterar
  em rodadas (reordenar capítulo, fundir, adicionar, remover bullet)
  antes de qualquer prosa. Passo obrigatório antes de /essay para todo
  essay novo — a única exceção é /import (essay já pronto do autor,
  sem tese a estruturar). Use quando o Usuário disser "esboça um essay
  sobre X", "quero ver a estrutura antes de escrever", "monta o
  esqueleto/outline desse essay", ou já tiver uma tese e quiser
  aprovar a arquitetura do argumento antes do texto em si — ou quando
  /essay for acionado sem um esboço existente ainda.
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch AskUserQuestion
---

# Outline

Produz e itera o esqueleto de um essay — nunca prosa. `/essay` agora exige esse esboço aprovado antes de escrever qualquer texto corrido (única exceção: `/import`, que ingere um essay já pronto do autor, sem tese nova a estruturar). `/outline` separa essa fase, salva como arquivo próprio, e permite quantas rodadas de revisão o Usuário quiser, em sessões diferentes se for o caso, antes de qualquer capítulo ser escrito de fato.

## 1. Tese primeiro

Se a tese central ainda não está clara, pergunte antes de propor qualquer esqueleto: tema não é tese — "quero escrever sobre livre-arbítrio" é tema, "quero argumentar que o compatibilismo dissolve o problema, não o resolve" é tese. Se a tese já emergiu de uma sessão de `/study` ou já está no plano (`plan/plano.md`, seção Essays Futuros), use isso como ponto de partida em vez de perguntar de novo.

Confirme rapidamente: **Tipo** (`Ensaio` | `White Paper` | `Brainstorm` | `Estudo` | `Análise`), **Domínio** (filosófico | técnico | misto) — `/essay` depende desses dois campos para saber que seção de redação aplicar, então ficam gravados no frontmatter do esboço.

## 2. Pesquisa leve — o suficiente para estruturar, não para redigir

1. Busque na wiki (`wiki/index.md`, `wiki/concepts/`, `wiki/entities/`) por essays/conceitos relacionados — mencione o que encontrou, vai virar candidato a `## Conexões` depois.
2. Uma varredura curta de `WebSearch`/`WebFetch` (poucas buscas) só para confirmar que a estrutura de capítulos cobre as correntes/objeções principais do tema — não é hora de aprofundar cada capítulo, isso é trabalho de `/essay` depois.

## 3. Montar o esqueleto

Estrutura mínima, sempre:

- **Introdução** — situa o problema e apresenta a tese, não só o tema.
- **Capítulos de desenvolvimento** — sem teto artificial de quantidade. Um tema denso pode passar de 10 capítulos; o que importa é que cada um avance um passo real do argumento e prepare o seguinte. Prefira mais capítulos focados a poucos capítulos genéricos: divida quando um capítulo tenta cobrir mais de uma ideia central.
- **Conclusão** — fecha o argumento aberto na introdução, não introduz ideia nova não preparada antes.

Cada capítulo deve se encadear logicamente com o anterior e com o seguinte — nunca uma sequência de seções independentes sob o mesmo título. Se o esboço crescer para muitos capítulos, releia a cadeia inteira antes de apresentar; se ficou longa e complexa o bastante para dúvida, ofereça `/continuity` depois que `/essay` gerar a prosa, para confirmar que a progressão sobreviveu à redação.

Para cada capítulo:

- **Título do capítulo**.
- **Papel argumentativo em uma frase**: o que ele estabelece e o que prepara para o capítulo seguinte — essa cadeia explícita é o motivo de existir do esboço, não um parágrafo de passagem dentro de um texto maior.
- **3 a 6 bullets** do conteúdo que entra: um argumento, uma fonte/pensador a citar, um experimento mental, um dado técnico — o suficiente para o Usuário avaliar se aquele capítulo é o que ele quer, sem precisar ler prosa para descobrir.

Não escreva nenhuma frase de prosa corrida nos bullets — eles são notas telegráficas, não rascunho de parágrafo. Se um bullet já está saindo como parágrafo, é sinal de que virou prosa antes da hora; corte de volta para nota.

## 4. Salvar como artefato próprio

Escreva em `plan/drafts/<slug>.md`:

```markdown
---
tese: uma frase com a posição central
tipo: Ensaio | White Paper | Brainstorm | Estudo | Análise
dominio: filosófico | técnico | misto
status: rascunho
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Título do Essay (provisório)

## Capítulo 1 — Título
Papel: o que este capítulo estabelece e prepara para o próximo.
- bullet
- bullet
- bullet

## Capítulo 2 — Título
Papel: ...
- bullet
...

## Conexões candidatas
- [[Essay ou Concept já existente]] — por quê
```

`plan/drafts/` é rascunho de estrutura, não wiki de verdade — por isso fica em `plan/`, fora do escopo de `/organize`, `/sweep` e `/gaps` — essas skills tratam `wiki/essays/` como conteúdo publicado, e um esqueleto de bullets ali quebraria a expectativa de prosa completa que elas assumem. (O mesmo vale para o script `python scripts/check_wiki.py`, que não é uma skill invocável por `/`, mas segue a mesma lógica de escopo.)

## 5. Apresentar e iterar

Mostre o esqueleto inteiro (é curto, cabe numa resposta) e pergunte o que ajustar. Rodadas de iteração são o ponto central desta skill — trate cada uma como edição direta do arquivo, não como conversa que se perde:

- Reordenar, fundir, dividir, adicionar ou remover capítulo → edite a estrutura, renumere se necessário, releia a cadeia de papéis para confirmar que a transição ainda faz sentido (mesmo cuidado de `/chapter` ao mover seção).
- Adicionar/remover/ajustar bullet dentro de um capítulo → edição pontual.
- Mudar a tese → releia se a estrutura inteira ainda serve a essa tese nova, não só o capítulo onde ela foi mencionada.

Depois de cada rodada, reapresente o esqueleto completo atualizado (não um diff) — o Usuário precisa ver o todo para continuar ajustando. Atualize `updated:` no frontmatter a cada rodada.

## 6. Aprovado — entregar para `/essay`

Quando o Usuário confirmar que o esqueleto está pronto para virar texto, ofereça `/essay` explicitamente. `/essay` lê `plan/drafts/<slug>.md` como brief de escrita, usando os capítulos e bullets já aprovados em vez de propor um esboço novo do zero. Só quando **todos** os capítulos do esboço estiverem escritos, `/essay` apaga o arquivo — o conteúdo já está incorporado ao essay e ao `wiki/log.md`. Se o essay ficar parcialmente escrito entre sessões, o draft continua vivo (veja `## Retomar um esboço em andamento` abaixo).

Se o Usuário preferir deixar para depois em vez de escrever agora, ofereça `/plan add` (seção Essays Futuros) com `Nota:` apontando para `plan/drafts/<slug>.md`, para retomar em outra sessão sem perder o esqueleto.

## Esboço implicitamente aprovado

Se o pedido do Usuário já trouxer tese e capítulos com detalhe suficiente (título, papel de cada um, conteúdo que dá para virar bullets sem inventar nada), não force uma rodada de aprovação separada. Monte o esqueleto (passo 4), mostre-o rapidamente numa única mensagem confirmando o que foi capturado, e já ofereça `/essay` na mesma resposta, em vez de esperar o Usuário aprovar antes de seguir. Só pare para perguntar se algo ficou genuinamente ambíguo — capítulo sem direção clara, tese ainda soando como tema. Pedidos curtos ou vagos continuam pelo fluxo normal dos passos 5 e 6.

## Retomar um esboço em andamento

Se `plan/drafts/<slug>.md` ainda existir mas o essay em `wiki/essays/` já tiver capítulos escritos (sessão anterior parou no meio), `/outline` pode ser chamado de novo para reestruturar só os capítulos ainda não escritos — reordenar, fundir, dividir, adicionar ou remover, como no passo 5. Não toque nos capítulos já marcados como escritos (`escritos:` no frontmatter do draft) nem no texto já publicado no essay: se a mudança pedida afeta um capítulo já escrito, isso é `/chapter`, não `/outline`. Reapresente só a parte pendente do esqueleto ao final.

## O que não fazer

Não escreva prosa em nenhum bullet, nem "só uma frase de exemplo" — isso antecipa decisões de redação que são trabalho de `/essay`.

Não pesquise a fundo cada capítulo aqui — a pesquisa detalhada por capítulo é de `/essay`; `/outline` só pesquisa o suficiente para validar a arquitetura.

Não crie o arquivo em `wiki/essays/` — isso confundiria `/organize`, `/stats` e `/gaps`, que tratam tudo em `wiki/essays/` como conteúdo publicado.

## Depois

Sem entrada em `wiki/log.md` — esboço não é conteúdo publicado. Se o esboço nasceu de um item do plano, atualize a `Nota:` desse item apontando para o arquivo.

## Skills relacionadas

- `/essay` — consome o esqueleto aprovado e escreve o texto corrido; apaga o esboço ao final
- `/study` — sessão anterior que pode ter produzido a tese que `/outline` estrutura
- `/plan` — guarda a pendência de "esboço pronto, falta escrever" entre sessões
- `/chapter` — reestruturação de capítulos depois que o essay já existe em prosa; `/outline` é a mesma operação, mas antes de qualquer prosa existir
