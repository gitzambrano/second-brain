---
name: linkify
description: >
  Adiciona e valida links externos no corpo de um essay e corrige
  referências bibliográficas que exigem pesquisa. Não reescreve prosa
  nem altera wikilinks internos.
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch
---
# Linkify

Trata links externos do corpo e qualidade bibliográfica de `## Referências`. Formatos canônicos vivem em `conventions/SKILL.md`.

## Escopo

- Corpo do essay: links externos `[texto](url)` na primeira ocorrência relevante.
- `## Conexões`: não tocar; wikilinks internos pertencem a `/connect`.
- `## Referências`: validar e corrigir segundo o padrão canônico.

## 1. Adicionar links externos

1. Leia o essay inteiro.
2. Identifique termos, pensadores, obras, normas e conceitos relevantes sem link.
3. Escolha fonte adequada:
   - conceito geral → fonte enciclopédica confiável;
   - filosofia → SEP quando aplicável;
   - engenharia → paper, norma ou fonte institucional;
   - ferramenta/produto → site oficial.
4. Linke a primeira ocorrência útil, não todas as repetições.

O alvo prático de cerca de 10 links externos é orientação de cobertura, não motivo para inserir link irrelevante.

## 2. Validar links existentes

Use `WebFetch` quando houver dúvida sobre destino, disponibilidade ou relevância.

Substitua link quebrado/desatualizado por fonte equivalente quando a intenção estiver clara. Não altere o texto do argumento para acomodar o link.

## 3. Validar referências

Execute:

```bash
python scripts/check_references.py --file <slug>
```

Depois aplique o fixer mecânico:

```bash
python scripts/fix_lint.py <slug>
```

O fixer resolve apenas transformações inequívocas. Para achados que exigem conhecer a fonte real:

1. procure primeiro em `wiki/references.md`;
2. se não houver citação canônica, pesquise a obra;
3. confirme título, autores, container e URL;
4. escreva a entrada conforme a seção `Formato de ## Referências — padrão AIAA` de `conventions/SKILL.md`.

Regras de decisão:
- referência sem link pode permanecer assim se não houver versão digital confiável;
- obra citável no corpo sem bibliografia → adicione a referência; não remova o link do corpo;
- não promova URL de glossário para URL da obra sem verificar;
- não invente metadados bibliográficos.

## 4. Fechar

Se algo mudou:
- rode o `## Fechamento padrão de essay único` de `conventions/SKILL.md`;
- se `## Referências` mudou, rode `python scripts/build_references.py`.

Para passada grande, registre:

```markdown
## [YYYY-MM-DD] linkify | Título
N links adicionados, M corrigidos.
```

## Limites

- Não reescreva prosa; isso é `/polish`.
- Não modifique wikilinks internos.
- Não adicione link apenas para atingir contagem.
- Não altere `updated:`; a regra vive em `conventions/SKILL.md`.
- Respeite a regra de status de `conventions/SKILL.md`.
