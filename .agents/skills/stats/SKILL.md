---
name: stats
description: >
  Dashboard read-only de saúde da wiki: contagem de essays por tag/
  tipo/categoria, conceitos/entidades órfãos, sources sem entrada no
  manifesto ou na subpasta errada, sinais de travessão/formatação,
  contagem de handouts. Use quando o usuário disser "como ta minha
  wiki", "dashboard", "stats da wiki", "quantos essays eu tenho",
  "quais sources não tem manifest", ou quiser um retrato rápido de
  saúde sem rodar o lint completo.
allowed-tools: Bash Read
---

# Stats

Dashboard **read-only**. Só relata, nunca corrige — esse é o trabalho de `/organize` e `/sweep`. Inspirado no padrão `PROJECT_MAP.md` (um snapshot sempre atualizado do workspace): aqui o snapshot é de contagens e lacunas, não de árvore de arquivos.

## Quando usar

- "como está minha wiki", "dashboard da wiki", "quantos essays eu tenho por tag"
- "quais sources não têm manifest", "tem algum órfão?"
- Antes de decidir se vale rodar um `/organize` e `/sweep` completo (o stats é rápido e não corrige nada; se os números parecerem ruins, aí sim rode o lint)

## Passo a passo

1. Rode o script:

   ```bash
   python scripts/stats.py
   ```

2. Leia o output e apresente ao usuário de forma resumida na conversa — não é necessário colar o relatório inteiro se ele for longo, destaque o que chama atenção (órfãos, sources sem manifest, essays com mais de 2 travessões).
3. Se o usuário quiser um snapshot salvo (para comparar com uma stats anterior, por exemplo), rode com `--save`:

   ```bash
   python scripts/stats.py --save
   ```

   Isso grava em `output/stats/stats-YYYY-MM-DD.md` (ver `## Arquitetura` no AGENTS.md). Não salve por padrão — só quando pedido, já que é um artefato descartável na maioria das vezes.

## O que o script cobre

- **Essays**: contagem total, por `Tipo` (Ensaio/White Paper/Estudo/etc), por categoria temática da byline, e distribuição de tags do vocabulário controlado.
- **Sinais de lint rápidos**: essays com `## Resumo Executivo` residual (não deveria existir mais, ver `conventions/SKILL.md`), essays com mais de 2 travessões, essays sem `## Sumário`/`## Referências`/`## Conexões`. Isso é uma varredura rasa (regex), não substitui `deep_format_check.py` nem o julgamento humano do lint completo.
- **Órfãos**: concepts/entities em `wiki/concepts/` e `wiki/entities/` que não aparecem em nenhuma seção `## Conexões` de essay.
- **Sources**: total de arquivos em `wiki/sources/**`, distribuição por subpasta de tipo, quantos não têm entrada em `manifest.md`, e quantos estão em uma subpasta fora do vocabulário controlado (ver `## Sources, Tags e Vocabulários Controlados` no AGENTS.md).
- **Handouts**: quantos existem em `wiki/handouts/`.
- **Plano de estudos**: quantos itens pendentes em `plan/plano-estudos.md`, por tipo (Estudo / Essay Futuro).

## Diferença em relação ao lint

| | `/stats` | `/organize` e `/sweep` |
|---|---|---|
| Corrige algo? | Não, nunca | Sim, com aprovação |
| Velocidade | Rápido, um script | Mais lento, envolve leitura e julgamento |
| Granularidade | Contagens e sinais agregados | Achado por achado, com "onde" e "como corrigir" |
| Quando rodar | Frequentemente, sem custo | A cada 10 ingests / mensalmente |

Baixo risco de sobreposição por design: stats só lê e soma, nunca escreve em `wiki/`.

## Skills relacionadas

- `/organize` e `/sweep` — corrige o que o stats só reporta
- `/import`/`/digest`/`/absorb` — depois de vários ingests, `/stats` é uma forma rápida de ver se sources sem manifest estão acumulando
