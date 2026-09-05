---
name: insight
description: >
  Captura, desenvolve, lista e promove ideias em wiki/insights/. Use para uma
  ideia ainda sem essay-pai; promoção encaminha para /essay, /expand ou /chapter
  conforme o destino.
metadata:
  second-brain-role: "knowledge-capture"
  second-brain-mode: "mixed"
  second-brain-scope: "insight"
  second-brain-approval: "conditional"
  second-brain-closure: "page"
allowed-tools: Bash Read Write Edit Glob Grep AskUserQuestion
---
# Insight

Guarda uma ideia única que ainda não exige a estrutura de um essay. Pode ser semente, síntese, observação, intuição ou mini-argumento.

Formato canônico: `## Formato de páginas em wiki/insights/` em `conventions/SKILL.md`.

## Maturidade

| Estado | Critério |
| --- | --- |
| `solta` | ideia curta ou ainda sem conexão |
| `germinando` | corpo desenvolvido + ao menos uma conexão genuína |
| `madura` | ideia central clara, densa e bem conectada; pronta para promoção |
| `absorvida` | conteúdo já incorporado a essay/capítulo |

Tamanho sozinho não aumenta maturidade.

## `/insight add`

Registre primeiro; converse depois.

1. Capture a ideia sem exigir conversa prévia. Desenvolva apenas o suficiente para torná-la inteligível; até 4–5 parágrafos quando houver material, menos quando a ideia for pontual.
2. Busque relações na wiki com `qmd query`; use `python scripts/find_text.py "termo" --ignore-case` como fallback.
3. Antes de nomear o arquivo:

```bash
python scripts/check_title.py "Título Da Ideia"
```

4. Defina `maturidade:`:
   - `germinando` se já houver corpo desenvolvido e conexão real;
   - `solta` caso contrário.
5. Reuse `tags_in_use` conforme `conventions/SKILL.md`.
6. Salve em `wiki/insights/<slug>.md`. `## Conexões` pode ficar vazio quando não houver relação genuína.
7. Não escreva no `wiki/log.md`.
8. Depois de salvar, ofereça brevemente desenvolver mais; não force continuação.

## `/insight develop <nota>`

1. Leia a nota inteira e suas conexões.
2. Converse com o Usuário sobre a direção antes de reescrever.
3. Integre o material novo à prosa existente; não apenas anexe texto.
4. Atualize conexões e `updated:`.
5. Reavalie maturidade:
   - `solta` → `germinando` quando ganhar corpo + conexão;
   - `germinando` → `madura` quando houver ideia central clara e densidade suficiente.
6. Em caso de dúvida sobre promoção de maturidade, mantenha o estado atual ou pergunte.

## `/insight list`

Liste todos os insights agrupados por maturidade. Mostre `madura` primeiro. Read-only.

## `/insight promote <nota>`

Promoção não é automática.

- **Essay novo:** use `/essay`; o insight fornece a ideia/tese, não substitui o outline.
- **Essay existente:** use `/expand` se couber numa seção ou `/chapter` se exigir seção própria.

Para `solta` ou `germinando`, confirme antes de promover.

Depois que o conteúdo existir no destino:

1. mantenha a nota;
2. mude para `maturidade: absorvida`;
3. registre no corpo: `> Absorvida em [[slug-do-essay|Essay Resultante]] em YYYY-MM-DD.`;
4. registre:

```markdown
## [YYYY-MM-DD] insight-promote | Título → [[slug-do-essay|Essay Resultante]]
```

## Limites

- Não use insight como etapa obrigatória antes de `/essay`.
- Não force `solta` a evoluir; pode permanecer assim indefinidamente.
- `/connect` pode criar conexão, mas não muda `maturidade:`.
- Não duplique aqui as regras gerais de frontmatter, tags, links ou nomenclatura; use `conventions/SKILL.md`.
