---
name: sweep
description: >
  Orquestra a bateria completa de revisão num essay ou no corpus inteiro:
  /organize (passada mecânica) → /continuity → /proofread → /polish →
  /linkify, e produz um relatório consolidado. Aceita escopo corpus
  inteiro (/sweep) ou essay único (/sweep <slug>) — a lógica é idêntica,
  só o conjunto de arquivos processados muda. Use quando o Usuário disser
  "corrige todos os essays", "faz uma revisão geral", "passa o pente fino
  na wiki inteira", "passa o pente fino nesse essay", ou quiser a bateria
  completa de correções sem invocar cada skill manualmente. É um
  orquestrador: chama outros skills, não duplica a lógica deles.
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch AskUserQuestion
---

# Sweep

**[ambos]** Roda `/organize` (mecânico) → `/continuity` → `/proofread` → `/polish` → `/linkify` (leitura, cada um) em qualquer escopo, e consolida num único relatório. **Orquestrador**: a lógica de cada correção vive no skill correspondente, não aqui.

## É / não é

- **É**: pente fino completo de um essay ou de todos, cobrindo formatação, continuidade, português, estilo e links.
- **Não é**: `/organize` sozinho (saúde da wiki — índice, manifesto, órfãos; rode antes para decidir se vale um sweep). Não é `/review` (validade argumentativa e profundidade).

## Escopo

```
/sweep              → corpus inteiro: todos os essays em wiki/essays/
/sweep <slug>       → um essay específico
```

Mesma lógica nos dois casos, muda só o conjunto de arquivos. Argumento ambíguo (ex: `/sweep física` casando dois essays) → pergunte antes.

## Regras de status

Ver `conventions/SKILL.md`:

- **Corpus inteiro**: pula `finalizado`/`maduro`, sem perguntar nem avisar durante a execução. Informa quantos foram pulados no resumo final.
- **Essay específico**: executa normalmente mesmo se `finalizado`/`maduro`. Ao final, se estava `finalizado`, avisa: "Este essay estava marcado como finalizado; executei porque você pediu diretamente."

## Passo a passo

Execute na ordem para cada essay do escopo, um por vez (não paralelize).

1. **Aviso de escala** (corpus inteiro, mais de 5 essays): avise antes de começar — "são N essays, vou levar um tempo" — e ofereça processar em lotes.
2. **[script] `/organize <slug>`** (escopo essay único, sem as checagens de corpus). Corpus inteiro do sweep = `/organize <slug>` em sequência para cada essay; **nunca** chame `/organize` sem argumento aqui, repetiria as checagens de corpus por essay. Aplique fixes automáticos sem interação. Acumule issues restantes no relatório do essay.
3. **[leitura] `/continuity`**. Problema grave (contradição com a tese, conclusão que não fecha o argumento): reporte e pergunte se corrige agora ou depois; **pause só este essay**, continue os demais do batch. Achado estrutural menor (transição fraca, termo antecipado): registre no relatório sem interromper.
4. **[leitura] `/proofread`** — passada de português. Aplique direto.
5. **[leitura] `/polish`** — passada de estilo (bullets, travessões, elegância). Aplique direto.
6. **[leitura] `/linkify`** — checagem e adição de links externos. Aplique direto.
7. **Relatório consolidado**, ao final de todos os essays do escopo:

   ```
   ## Sweep — [N essay(s) processado(s)]

   ### Resumo
   - Essays processados: N
   - Essays pulados por status (finalizado/maduro): K
   - Issues de formato resolvidos automaticamente: X
   - Issues de formato restantes (não-automáticos): Y
   - Problemas de continuidade reportados: Z
   - Correções de português: W
   - Correções de estilo: V
   - Links adicionados/corrigidos: U

   ### Por essay
   **[Título]** (essays/slug.md)
   - [resumo do que foi corrigido ou reportado]
   ```

   Não exponha cada correção individual durante a execução — acumule e apresente só ao final.
8. **Fechamento**: sweep mexe em muita prosa de uma vez, então feche a sessão com os artefatos derivados em dia.
   - **[script]** Essay tocado → `python scripts/build_index.py`; `## Referências` mudou (passo 6 quase sempre muda) → `python scripts/build_references.py` também.
   - **[script]** qmd disponível (`qmd status`) → **ofereça** `qmd update && qmd embed` (não rode sozinho); sem qmd, pule sem avisar.
   - **[script]** `python scripts/sync_skills.py --check`; drift → `python scripts/sync_skills.py` direto.
   - Ofereça `/status update`, depois `/review`, `/expand`, `/chapter` ou `/connect` como próximos passos.

## Log

Uma entrada consolidada em `wiki/log.md`:

**Corpus inteiro:**

```
## [YYYY-MM-DD] sweep | N essays revisados
Formato: X auto-corrigidos, Y issues restantes. Continuidade: Z reportados.
Português: W correções. Estilo: V correções. Links: U adicionados. K pulados por status.
```

**Essay único:**

```
## [YYYY-MM-DD] sweep | [Título do Essay]
Formato: X auto-corrigidos, Y issues restantes. Continuidade: Z reportados.
Português: W correções. Estilo: V correções. Links: U adicionados.
```

Atualize `updated:` no frontmatter de cada essay tocado.

## Convenções

Prosa segue `## Estilo de prosa` em `conventions/SKILL.md`.

## Skills relacionadas

- `/organize` — passada mecânica (chamada no Passo 2, escopo essay único); em modo corpus inteiro decide se vale um sweep
- `/continuity`, `/proofread`, `/polish`, `/linkify` — chamados nos Passos 3–6
- `/review` — validade argumentativa e profundidade; complementar, não substituto
- `/stats` — dashboard de saúde; rode antes para visão geral
- `/connect` — fora da bateria automática; ofereça como próximo passo no fechamento
