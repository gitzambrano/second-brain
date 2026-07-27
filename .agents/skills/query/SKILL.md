---
name: query
description: >
  Responde perguntas usando a base de conhecimento centrada em essays.
  Use quando o usuário fizer uma pergunta sobre seus essays, quiser
  explorar conexões entre temas, disser "o que eu já escrevi sobre X",
  "resume meu ensaio sobre Y", ou quiser buscar na wiki.
allowed-tools: Bash Read Write Edit Glob Grep
---

# Query

Responde perguntas buscando e sintetizando conhecimento da wiki. **Essays são a unidade primária de resposta** — conceitos e entidades existem para aprofundar, não para substituir os essays.

## Estratégia de busca

### 1. Comece pelo índice

Leia `wiki/index.md` — ele contém **apenas essays**, organizados por categoria temática. Identifique os essays mais relevantes para a pergunta.

### 2. Use qmd para wikis grandes

Se `qmd` estiver instalado (`command -v qmd`), use para buscar em todo o conteúdo, não só nos títulos do index:

```bash
qmd search "termos da busca" --path wiki/
```

Especialmente útil quando a wiki passa de ~100 páginas.

### 3. Leia os essays relevantes e aprofunde via Conexões

Leia os essays identificados. Siga os `[[wikilinks]]` da seção `## Conexões` de cada um para puxar contexto de conceitos e entidades relacionados. Leia o suficiente para responder bem, sem ler a wiki inteira.

### 4. Consulte o acervo original só como último recurso

`wiki/sources/` guarda os **arquivos originais** (PDFs, DOCX, HTML) que geraram os essays — não são páginas de resumo. Se os essays não cobrirem algo que você sabe que está na fonte, leia o original diretamente ali (pode exigir extração de PDF/DOCX). Prefira sempre responder a partir do essay já processado — ele já vem sintetizado, traduzido e cruzado.

## Sintetizar a resposta

### Formato

Combine com o tipo de pergunta:
- **Factual** → resposta direta com citação
- **Comparação** → tabela ou comparação estruturada
- **Exploração** → narrativa com conceitos linkados
- **Lista/catálogo** → lista com descrições breves

### Citações

Cite sempre o essay de origem via `[[wikilink]]`:

> Segundo [[Mente Aumentada]], o padrão LLM Wiki resolve o problema clássico do second brain fazendo a manutenção da malha de conexões automática. Isso se conecta ao que [[Autopoiese, Consciência e os Limites do Vivo]] discute sobre sistemas que se auto-mantêm.

### Ofereça salvar respostas valiosas

Se a resposta gerar algo que vale a pena guardar — uma comparação, uma síntese nova, uma conexão que não estava explícita — ofereça:

> "Essa síntese pode valer a pena guardar. Quer que eu salve como um novo essay, ou é mais uma nota de síntese curta?"

- **Se for profunda o bastante para ser um essay**: siga o fluxo completo de `/essay` (frontmatter, byline, Sumário, mínimo 10 links externos, Referências, Conexões) e salve em `wiki/essays/`.
- **Se for uma comparação/nota curta entre coisas que já existem na wiki**: salve em `wiki/synthesis/` com `tipo: comparacao` no frontmatter (ver `conventions/SKILL.md`).
- **Se a resposta revelar uma ideia nova, ainda sem tese própria** (não é comparação do que já existe, é um insight novo que a pergunta provocou): isso não é `/query` — é `/atom add`. A diferença: comparação organiza conhecimento existente; nota atômica é conhecimento novo que ainda não tem lugar.
- Em ambos os casos: atualize `wiki/index.md` (se for essay) e registre em `wiki/log.md`:
  ```
  ## [YYYY-MM-DD] query | Resumo da pergunta
  ```

## Convenções

- **Cite sempre.** Toda afirmação factual deve linkar o essay de onde veio.
- Use `[[wikilinks]]` para toda referência interna. Nunca caminhos de arquivo crus.

## Skills relacionadas

- `/import`, `/digest`, ou `/absorb` — processar novas fontes em essays
- `/essay` — criar um essay novo do zero
- `/atom` — quando a resposta revela uma ideia nova, não uma comparação do que já existe
- `/organize` — auditar e organizar a wiki
