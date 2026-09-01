---
name: gaps
description: >
  Identifica lacunas mecânicas, léxicas e semânticas entre essays,
  concepts, entities e insights. Aceita corpus, página, pasta ou tema.
  É read-only; /connect age sobre os candidatos encontrados.
allowed-tools: Bash Read Glob Grep
---
# Gaps

Camada de **identificação**. Não cria página, não insere link e não corrige nada.

## Escopo

```text
/gaps
/gaps <slug ou lista>
/gaps concepts/ | entities/ | insights/ | essays/
/gaps <tema ou tag>
```

Se o argumento for ambíguo, resolva antes. Em corpus grande, amostragem semântica é aceitável se declarada.

## Camadas

1. **Mecânica** — wikilink morto ou fora do formato canônico.
2. **Léxica** — termo recorrente sem página ou página existente citada sem link.
3. **Semântica** — páginas tematicamente próximas sem menção literal.

## 1. Mecânica

Rode `check_wiki.py` no escopo possível:

```bash
python scripts/check_wiki.py --json
```

ou, por página:

```bash
python scripts/check_wiki.py <slug> --json
```

Extraia apenas achados de wikilink/formatação. Marque typo óbvio como alta confiança, mas não corrija.

## 2. Léxica

Rode:

```bash
python scripts/check_gaps.py --skip-tags
```

O script opera no corpus; filtre a saída quando o pedido tiver escopo menor.

Interprete:
- termo sem página → candidato a `concepts/` ou `entities/`;
- página existente mencionada sem link → candidato a conexão.

É heurístico; falso positivo não é erro do fluxo.

## 3. Semântica

Use `qmd query` quando disponível; fallback para `find_text.py`.

Procure relações fortes que a camada léxica não captura, especialmente entre pages com vocabulário diferente. Em corpus grande, priorize páginas do escopo e amostra representativa.

## 4. Classificar

- **Alta:** alvo exato já aparece ou typo mecânico inequívoco.
- **Média:** relação forte, mas interpretativa.
- **Baixa:** descarte como ruído.

## 5. Reportar

Agrupe:
- link quebrado/mal formatado;
- candidato a página nova;
- página existente que deveria ser conectada;
- conexão temática sem menção literal.

Não cole output bruto dos scripts.

Quando chamado diretamente, ofereça `/connect` para agir. Quando chamado por `/connect`, apenas devolva a lista.

## Limites

- Read-only em todos os casos.
- Balanço de tags pertence a `/organize`.
- Não ajuste thresholds heurísticos sem evidência de que estão inadequados ao corpus.
- Não rode automaticamente dentro de `/organize` ou `/sweep`.
