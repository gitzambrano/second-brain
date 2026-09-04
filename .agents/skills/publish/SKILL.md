---
name: publish
description: >
  Compila o site estático público, valida a privacidade com a sentinela
  check_site_privacy.py e publica no repositório site/ via GitHub Pages.
allowed-tools: Bash Read Glob
---
# Publish

Executa a publicação do **Second Brain Atlas** no repositório público `site/` (GitHub Pages). A publicação é um ato deliberado e explícito do Usuário — nenhuma outra skill constrói ou publica o site.

## Pré-requisitos

1. Os essays destinados à leitura pública devem conter `visibility: public` no frontmatter. Se necessário alterar a visibilidade de algum essay antes de publicar, use `scripts/set_visibility.py`.
2. O repositório `site/` deve estar inicializado (com `.second-brain-site`).

## Fluxo Obrigatório

Execute a sequência estrita:

```bash
# 1. Auditar visibilidade e conformidade
python scripts/set_visibility.py
python scripts/check_visibility_field.py

# 2. Compilar o site estático
python scripts/build_site.py

# 3. Sentinela de privacidade (OBRIGATÓRIO)
python scripts/check_site_privacy.py

# 4. Como o leitor vê: abre cada página do site num navegador real,
#    incluindo graph.html e sphere.html (OBRIGATÓRIO)
python scripts/check_site_pages.py

# 5. Orçamento de tamanho dos artefatos públicos
python scripts/check_site_budget.py

# 6. Selo: roda os gates de novo e carimba a prova no artefato (OBRIGATÓRIO)
python scripts/seal_publication.py
```

O selo é o que liga os dois repositórios. Sem ele, o `site/` publicava qualquer
coisa que chegasse na branch — o deploy podia ficar verde com a CI do engine
vermelha, porque nenhum dos dois olhava para o outro. `seal_publication.py`
roda os gates ele mesmo e só então grava, no `site-manifest.json`, quais
passaram, o commit do engine e uma impressão do conteúdo publicado. A portaria
do site recalcula essa impressão antes do deploy: publicação sem selo é
recusada, e selar e editar depois invalida.

Se `seal_publication.py` avisar que o engine tinha mudanças não commitadas,
commite antes de publicar — senão o selo aponta para um commit que não contém o
código que gerou o site.

Sem Chromium a auditoria visual **falha**, não pula: "não foi auditado" não
pode passar por "passou". Instale com `python -m playwright install chromium`.
`--allow-skip-browser` existe só para diagnóstico local e **não** vale neste
fluxo.

### Regra da Sentinela de Privacidade

Se `check_site_privacy.py` reportar **qualquer erro bloqueante** (corpo de essay não autorizado, link para essay privado, ou vazamento de caminhos internos de `data/`):
- **Pare imediatamente.**
- **Não prossiga** para o commit/push no `site/`.
- Reporte os erros exatos encontrados ao Usuário.

### 7. Deploy no Git de `site/`

Somente com a sentinela reportando `PASS`:

```bash
git -C site status --short
git -C site add .
git -C site commit -m "Publicação do site: YYYY-MM-DD"
git -C site push
```

## Regras

- **Nunca publique sem o gate:** `check_site_privacy.py` deve sempre passar antes de qualquer commit em `site/`.
- `check_site_pages.py` é o gate visual **obrigatório**: overflow horizontal, imagem quebrada, âncora morta, erro de console e Markdown vazando na página renderizada, mais uma auditoria própria de `graph.html` e `sphere.html` (canvas, dados, controles, tema, resize e interação). Falha aqui não é vazamento de privacidade, mas também não se publica: reporte e corrija antes do deploy.
- **Ausência de navegador é falha, não SKIP.** Publicar sem a auditoria visual é publicar às cegas.
- **Git é isolado:** Esta skill faz commit e push **exclusivamente** no repositório `site/`. Nunca faça commit em `./` ou em `data/` dentro deste fluxo.
- **Não altere visibilidade automaticamente:** Alterações de `visibility:` são decididas exclusivamente pelo Usuário.

## Gate do lado do site

O repositório `site/` tem portaria própria — `check_artifact.py`, sob o
`.github/` de lá — executada pelo workflow antes do deploy: confere a allowlist contra as páginas
presentes, recusa corpo de texto no `search-index.json`, procura caminho de
`data/` ou caminho absoluto de máquina vazando, e aplica o orçamento de tamanho.
É auto-suficiente — biblioteca padrão, sem acesso ao repositório privado — e
existe porque um push manual chega ao ar pelo mesmo caminho que uma publicação
legítima.

**Pendência manual, fora do alcance de qualquer script:** ligar branch
protection em `second-brain-site/main` exigindo esse workflow, para que só o
fluxo validado atualize a branch. É configuração de repositório no GitHub e
precisa ser feita pelo Usuário, uma vez.
