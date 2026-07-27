---
name: stats
description: >
  Dashboard read-only de saúde da wiki: contagem de essays por tag/
  tipo/categoria, conceitos/entidades órfãos, sources sem entrada no
  manifesto ou na subpasta errada, sinais de travessão/formatação,
  contagem de handouts, itens do plano por seção, notas atômicas por
  maturidade. Pode também gerar o grafo visual de conexões
  (scripts/graph.py). Use quando o Usuário disser "como ta minha
  wiki", "dashboard", "stats da wiki", "quantos essays eu tenho",
  "quais sources não tem manifest", "mostra o grafo/mapa de conexões",
  ou quiser um retrato rápido de saúde sem rodar o lint completo.
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

2. Leia o output e apresente ao Usuário de forma resumida na conversa — não é necessário colar o relatório inteiro se ele for longo, destaque o que chama atenção (órfãos, sources sem manifest, essays com mais de 2 travessões).
3. Se o Usuário quiser um snapshot salvo (para comparar com uma stats anterior, por exemplo), rode com `--save`:

   ```bash
   python scripts/stats.py --save
   ```

   Isso grava em `output/stats/stats-YYYY-MM-DD.md` (ver `## Arquitetura` no AGENTS.md). Não salve por padrão — só quando pedido, já que é um artefato descartável na maioria das vezes.
4. Se o Usuário quiser **ver** as conexões, não só contá-las, rode o grafo:

   ```bash
   python scripts/graph.py
   ```

   Gera `output/graph/graph.html` (visualização interativa: zoom, arraste, clique num nó para destacar vizinhos, busca por título/tag) e `output/graph/graph.md` (versão Mermaid, sem precisar abrir navegador). É a forma mais rápida de enxergar clusters isolados — por exemplo, se os ensaios de filosofia nunca se conectam aos de engenharia, isso aparece visualmente como dois blocos separados no grafo. Ofereça isso sempre que o Usuário perguntar algo como "como as coisas se conectam" ou depois de um `/organize` substancial.

## O que o script cobre

- **Essays**: contagem total, por `Tipo` (Ensaio/White Paper/Estudo/etc), por categoria temática da byline, e distribuição de tags do vocabulário controlado.
- **Sinais de lint rápidos**: essays com `## Resumo Executivo` residual (não deveria existir mais, ver `conventions/SKILL.md`), essays com mais de 2 travessões, essays sem `## Sumário`/`## Referências`/`## Conexões`. Isso é uma varredura rasa (regex), não substitui `format_check.py` nem o julgamento humano do lint completo.
- **Órfãos**: concepts/entities em `wiki/concepts/` e `wiki/entities/` que não aparecem em nenhuma seção `## Conexões` de essay.
- **Sources**: total de arquivos em `wiki/sources/**`, distribuição por subpasta de tipo, quantos não têm entrada em `manifest.md`, quantos estão em uma subpasta fora do vocabulário controlado, quantas entradas do manifesto não têm `Tags:` preenchido, e a distribuição de tags em uso no manifesto — mesmo vocabulário controlado dos essays (ver `## Sources, Tags e Vocabulários Controlados` no AGENTS.md).
- **Handouts**: quantos existem em `wiki/handouts/`.
- **Plano**: quantos itens em `plan/plano.md`, por seção (Tarefas / Fontes para Ingerir / Revisões / Estudos / Essays Futuros) e por status.
- **Insights**: quantas páginas em `wiki/insights/`, por maturidade (solta / germinando / madura) — sinaliza quais estão maduras e prontas para `/insight promote`.

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
