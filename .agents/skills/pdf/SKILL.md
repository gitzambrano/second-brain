---
name: pdf
description: >
  Exporta um ou todos os essays de wiki/essays/ para PDF via
  scripts/export_essay.py (Pandoc + LuaLaTeX). Use quando o
  usuário disser "exporta esse essay pra PDF", "gera o PDF de X",
  "exporta tudo pra PDF", ou quiser uma versão compartilhável/
  imprimível de um essay.
allowed-tools: Bash Read Glob
---
# PDF

Gera PDF a partir de um ou mais essays em `wiki/essays/`, via `scripts/export_essay.py` (Pandoc + LuaLaTeX). Este skill só invoca o script existente e interpreta o resultado — a lógica de conversão vive no script, não aqui.

## Quando usar

- "exporta [essay] pra PDF"
- "gera os PDFs de todos os essays"
- "manda esse ensaio pra alguém em PDF"

Para HTML, use `/html` em vez deste skill — não duplique lógica de exportação aqui.

## Pré-requisitos

O script depende de **Pandoc** com o engine **LuaLaTeX** (não XeLaTeX — ver `## Exportação para PDF` em `conventions/SKILL.md` para o motivo). Se o comando falhar com "Pandoc not found" ou erro de LaTeX, avise o usuário e não tente contornar reimplementando a conversão manualmente.

## Uso

```bash
# Listar essays disponíveis
python scripts/export_essay.py --list

# Exportar um essay específico (nome do arquivo, com ou sem .md)
python scripts/export_essay.py nome-do-essay

# Exportar todos os essays
python scripts/export_essay.py --all

# Diretório de saída customizado (padrão: output/pdf/)
python scripts/export_essay.py nome-do-essay --output caminho/custom
```

## O que o script já garante (não precisa reimplementar)

1. Remove a seção `## Conexões` (metadata interna, não vai para o PDF).
2. Preserva `## Sumário` e `## Referências`.
3. Converte frontmatter YAML + byline em bloco de título/subtítulo/autor no LaTeX.
4. Resolve caminhos relativos de imagem (`../assets/...`) para absolutos.
5. Remove `[[wikilinks]]` residuais, convertendo para texto puro.
6. Ativa hyperlinks clicáveis (`colorlinks`), matemática (`tex_math_dollars`), tabelas, código.

## Exportar um handout em vez de um essay

O mesmo script exporta handouts de `wiki/handouts/` com a flag `--handout`:

```bash
python scripts/export_essay.py <slug-do-essay> --handout --output output/handouts
```

Use quando o usuário quiser mandar o handout como PDF em vez de só o `.md` cru — ver skill `/handout` e `## Arquitetura` (bloco `output/`) no AGENTS.md. O handout não tem `## Conexões`/`## Referências`/`## Sumário`, então esses passos rodam como no-op; o resultado sai com a mesma tipografia dos essays, só mais curto.

## Depois de exportar

1. Confira o output do comando: cada essay reporta `OK: <arquivo>.pdf (<tamanho> KB)` ou `ERROR`. Se algum falhar, leia o `STDERR` reportado e diagnostique antes de tentar de novo (erro de LaTeX, imagem faltando, essay sem H1, etc.) — não ignore falhas silenciosamente num export em lote.
2. Avise o usuário do caminho final do(s) PDF(s).
3. Não é necessário atualizar `wiki/log.md` para exports — não é uma operação de ingestão/criação/edição de conteúdo da wiki, é uma exportação de leitura.

## Skills relacionadas

- `/html` — mesma essência, saída HTML standalone
- `/organize` e `/sweep` — o checklist de organize/sweep testa `export_essay.py --all` como parte do health-check
