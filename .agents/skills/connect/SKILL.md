---
name: connect
description: >
  Repara e expande ## Conexões entre essays, concepts, entities e
  insights. Invoca /gaps para identificar candidatos e age sobre eles:
  corrige links mecânicos, aplica conexões de alta confiança, propõe
  relações ambíguas e cria stub de concept/entity somente com aprovação.
allowed-tools: Bash Read Write Edit Glob Grep AskUserQuestion
---
# Connect

Camada de **ação** do grafo interno. `/gaps` faz a identificação; `/connect` age exclusivamente sobre a lista retornada.

## Escopo

```text
/connect
/connect <slug ou lista>
/connect concepts/ | entities/ | insights/ | essays/
/connect <tema ou tag>
```

Passe o mesmo escopo para `/gaps`. Se for ambíguo, resolva antes de editar.

## 1. Obter candidatos

Invoque `/gaps` com o escopo recebido. Não rode uma segunda identificação paralela.

Se `wiki/index.json` estiver desatualizado e for necessário para nomes/tags, rode `python scripts/build_index.py`.

## 2. Corrigir links mecânicos

Para candidatos mecânicos de `/gaps`:

- typo óbvio apontando para página existente → corrija;
- formato fora de `[[slug|Título]]` → normalize preservando alvo/display;
- alvo inexistente sem correspondência clara → pergunte;
- link válido mas semanticamente suspeito → leia contexto e proponha correção; não troque silenciosamente.

## 3. Conectar páginas existentes

- **Alta confiança:** nome exato/alvo inequívoco já está no contexto → aplique.
- **Média confiança:** relação temática forte, mas interpretativa → apresente lote curto para confirmação.
- **Baixa confiança:** descarte.

### Bidirecionalidade

Nova conexão é bidirecional por padrão.

Antes de adicionar muitos backlinks a uma página-hub, use `find_backlinks.py` para avaliar volume. Se o retorno deixaria `## Conexões` da hub ruidosa, adicione o lado de origem e pergunte sobre o backlink em massa.

## 4. Propor página inexistente

Somente para candidato que realmente pede `concepts/` ou `entities/`.

1. Rode:

```bash
python scripts/check_title.py "Título Proposto"
```

2. Escolha a pasta pela tabela canônica de `conventions/SKILL.md`.
3. Mostre a proposta e peça aprovação.
4. Se aprovado, crie stub mínimo com frontmatter, um parágrafo denso e `## Conexões` de volta às páginas de origem.

Nunca crie essay ou insight dentro de `/connect`.

## 5. Validar e fechar

Para cada página alterada:

```bash
python scripts/check_wiki.py <slug>
python scripts/fix_lint.py <slug>
```

Se criou página, rode `python scripts/build_index.py`.

Em escopo de corpus, reconstrua o grafo no fechamento apropriado.

Registre:

```markdown
## [YYYY-MM-DD] connect | Escopo
N links corrigidos, M conexões novas, K páginas novas.
```

## Relatório

Agrupe apenas o que importa:
- corrigido automaticamente;
- conexões aguardando confirmação;
- páginas novas propostas;
- links semanticamente suspeitos.

Não cole o output bruto de `/gaps`.

## Limites

- Não enriqueça prosa além do necessário para justificar uma conexão.
- Não crie página sem aprovação.
- Não refaça a lógica de `/gaps`.
