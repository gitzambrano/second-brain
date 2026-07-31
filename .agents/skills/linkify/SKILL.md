---
name: linkify
description: >
  Adiciona links externos a conceitos e termos técnicos ao longo do
  corpo de um essay, e checa os links existentes quanto a validade/
  relevância. Use quando o Usuário disser "adiciona mais links", "essa
  seção não tem nenhum link", "checa se os links ainda funcionam", ou
  depois de escrever/editar uma seção que introduz conceitos,
  pensadores ou termos técnicos novos sem hyperlink na primeira
  menção.
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch
---

# Linkify

Garante que todo conceito, termo técnico, pensador, ou obra citada no corpo de um essay tem um link externo na primeira ocorrência, e que os links existentes ainda apontam para algo relevante e correto.

## Regra de escopo

Só o **corpo do essay** (texto corrido) recebe links externos `[texto](url)`. `[[wikilinks]]` ficam exclusivamente em `## Conexões` — nunca misture os dois formatos fora dessa seção (ver `## Regra de links — exportabilidade para PDF` em `conventions/SKILL.md`).

## Adicionar links

1. Leia o essay inteiro e liste os conceitos, termos técnicos, pensadores, correntes filosóficas, obras, normas técnicas, ou entidades mencionados sem link.
2. Para cada um, busque a referência mais apropriada: Wikipedia para conceitos gerais, Stanford Encyclopedia of Philosophy (SEP) para filosofia, paper original ou norma técnica para conceitos de engenharia, site oficial para ferramentas/produtos.
3. Adicione o link na **primeira ocorrência** do termo no essay (não em toda repetição — isso poluiria o texto).
4. Mínimo de 10 links externos por essay (ver `## Regra de links — exportabilidade para PDF` em `conventions/SKILL.md`) — se o essay estiver abaixo disso, esse é o sinal de que faltam links, não que o mínimo é opcional.

## Checar links existentes

1. Para cada link externo já presente, avalie se a URL parece plausível e se o texto-âncora corresponde ao que o link deveria mostrar.
2. Se houver dúvida sobre um link estar quebrado ou desatualizado, use `WebFetch` para confirmar.
3. Links para páginas que claramente mudaram de conteúdo ou saíram do ar devem ser substituídos por uma fonte equivalente, nunca deixados apontando para o lugar errado.

## Checar e reformatar `## Referências`

Além dos links inline do corpo, `/linkify` é a skill dona do formato das entradas de `## Referências` — o padrão AIAA de `## Formato de "## Referências" — padrão AIAA` em `conventions/SKILL.md`. Quem valida é `scripts/linkify_check.py`:

```bash
python scripts/linkify_check.py --file <slug>
```

Os códigos que ele emite:

| Código                        | Severidade | Significado                                                       |
| ----------------------------- | ---------- | ----------------------------------------------------------------- |
| `REFERENCIA_FORMATO_INVALIDO` | ERROR      | entrada fora de `[N] ...`, sem título em itálico, ou fora de ordem |
| `DUPLICATE_REFERENCIA`        | ERROR      | duas entradas com a mesma URL normalizada no mesmo essay          |
| `LINK_NOT_IN_REFERENCIAS`     | ERROR      | URL de obra citável usada no corpo, sem entrada na bibliografia   |
| `REFERENCIA_SEM_LINK`         | WARNING    | entrada sem link                                                   |
| `REFERENCIA_NAO_USADA`        | WARNING    | entrada `[N]` nunca citada no corpo                                |

`NO_REFERENCIAS` (a seção não existe) é de `format_check.py`, não deste script.

**Escopo desta seção: só a seção `## Referências`, no fim do arquivo.** Numa passada de bibliografia, os links inline do corpo não se tocam — nem para reescrever, nem para reposicionar, nem para remover. Isso vale inclusive quando um check aponta para o corpo: `LINK_NOT_IN_REFERENCIAS` significa que **falta uma entrada na bibliografia**, nunca que o link do corpo esteja sobrando. Adicionar links novos ao corpo é a seção `## Adicionar links` acima, e só acontece quando o Usuário pede isso explicitamente.

A parte mecânica da migração do formato antigo (bullet `- Autor. *Título.* ...`) sai sozinha:

```bash
python scripts/linkify_check.py --fix-format
```

Ele renumera para `[N]`, normaliza o itálico do título, repõe a vírgula separadora e **move qualquer link da citação para a palavra `Link` no fim da entrada** — venha ele do título, do periódico ou de um envelope em volta da citação inteira. **Ele não escolhe URL de fonte**: no formato antigo os links de uma entrada costumam ser de glossário, dentro da nota, e não o endereço da própria obra — promovê-los inventaria bibliografia. O que sobrar sai como `REFERENCIA_SEM_LINK`, e aí sim é trabalho seu:

1. Para cada `REFERENCIA_SEM_LINK`, primeiro confira `wiki/references.md` — a mesma obra pode já estar catalogada com link em outro essay, e nesse caso reuse a citação existente em vez de buscar de novo. Só se não estiver, busque o endereço da obra seguindo a ordem de preferência de `conventions/SKILL.md`: DOI ou link permanente do editor, depois site institucional primário (NASA/NTRS, AIAA, ARC/NACA, universidade, GitHub do projeto), depois SEP para verbete filosófico, e Wikipedia só para conceito geral.
2. O link entra como a palavra `Link`, clicável, **depois do ponto final**, como última coisa da entrada. Nunca no título nem no periódico.
3. Se a fonte for genuinamente sem edição digital confiável (livro impresso antigo), deixe sem link: o WARNING é aceitável, não um erro a maquiar.
4. Para `LINK_NOT_IN_REFERENCIAS`, a obra citada no corpo precisa virar entrada na bibliografia — não remova o link do corpo para calar o check.

Ao final, rode `python scripts/references_index.py` para regenerar `wiki/references.json`/`.md`.

## O que não fazer

Não adicione um link só para atingir o mínimo de 10 — o link deve ser genuinamente relevante ao termo.

Não linke a mesma entidade duas vezes no mesmo parágrafo.

Não transforme isso numa desculpa para reescrever a prosa (isso é `/polish`) — a única mudança de texto aqui é a inserção do markdown do link.

## Depois

Atualize `updated:` no frontmatter se algum link foi adicionado/corrigido. Log só se for uma passada grande (essay com poucos links recebendo vários):
```
## [YYYY-MM-DD] linkify | Título do Essay
N links adicionados, M links corrigidos.
```

Se `## Referências` também foi tocada nesta passada, rode `python scripts/references_index.py` para regenerar `wiki/references.json`/`.md`.

## Convenções

Segue a regra de status (batch vs específico) de `## Status de essay` em `conventions/SKILL.md`.

## Skills relacionadas

- `/expand` — se o processo de linkificar revelar que um conceito citado de passagem merece uma explicação melhor no corpo, isso é `/expand`, não `/linkify`
- `/sweep` — roda `/linkify` em todos os essays de uma vez
