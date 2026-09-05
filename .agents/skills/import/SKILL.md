---
name: import
description: >
  Ingere um essay/white paper completo escrito pelo próprio Usuário: arquiva o
  original sem alteração e cria um essay derivado preservando a prosa. Use para
  texto autoral pronto; fontes de terceiros pertencem a /digest.
metadata:
  second-brain-role: "author-source-ingestion"
  second-brain-mode: "write"
  second-brain-scope: "source-and-essay"
  second-brain-approval: "conditional"
  second-brain-closure: "single-essay"
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch AskUserQuestion
---
# Import

Transforma um texto autoral já pronto em um essay da wiki. O agente atua como **arquivista**, não coautor.

## Contratos

| Artefato | Regra |
| --- | --- |
| `wiki/sources/<tipo>/<nome-original>` | cópia do original; nunca editar |
| `wiki/essays/<slug>.md` | derivado que preserva frase, ordem, argumento e vocabulário, salvo transformações permitidas |

Transformações permitidas sem nova autorização no derivado:

- frontmatter canônico;
- H1/byline;
- `## Sumário` derivado dos H2 existentes;
- conversão fiel para Markdown, incluindo tabelas, equações, notas e imagens;
- links externos úteis;
- bibliografia original normalizada em `## Referências`;
- `## Conexões`.

Não corrija gramática, não condense, não acrescente argumento, não crie seção de conteúdo e não reescreva estilo durante a ingestão.

## Decisão de entrada

Use `/import` somente quando estiver claro que o texto completo é do próprio Usuário. Se a autoria ou o grau de completude forem realmente ambíguos, confirme antes de prosseguir. Fonte de terceiro → `/digest`; autoria nova → `/outline` → `/essay`.

Se o original não estiver em Português do Brasil, pergunte se o derivado deve permanecer no idioma original ou ser traduzido. Tradução exige escolha explícita e deve ficar registrada na referência/manifesto conforme `conventions/SKILL.md`.

## Fluxo

1. Leia a fonte inteira.
2. Classifique o source pelo vocabulário de `conventions/SKILL.md`.
3. Arquive o original preservando nome e conteúdo.
4. Crie `wiki/essays/<slug>.md` aplicando apenas as transformações permitidas.
5. Defina `status: finalizado` por padrão; use `draft` quando o original for claramente rascunho.
6. Escreva `summary:` e tags segundo `conventions/SKILL.md`.
7. Normalize a bibliografia original. Confirme metadados bibliográficos antes de completar o que não estiver explícito.
8. Crie/atualize concept/entity apenas quando houver valor independente e sem reescrever o essay para justificar a página de apoio.
9. Atualize `wiki/sources/manifest.md` e `wiki/sources/map.md`.
10. Valide e regenere derivados necessários.

Comandos mínimos para referências/índice:

```bash
python scripts/check_references.py --file <slug>
python scripts/build_index.py
python scripts/build_references.py
```

Depois use o `## Fechamento padrão de essay único` de `conventions/SKILL.md`.

Registre:

```markdown
## [YYYY-MM-DD] import | Título do Essay
Tese: <uma frase>.
```

## Depois

Edição substantiva posterior exige pedido explícito e usa `/expand`, `/chapter`, `/proofread` ou `/polish`. O arquivo arquivado em `wiki/sources/` permanece intocado em qualquer cenário.
