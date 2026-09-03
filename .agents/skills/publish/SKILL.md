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
```

### Regra da Sentinela de Privacidade

Se `check_site_privacy.py` reportar **qualquer erro bloqueante** (corpo de essay não autorizado, link para essay privado, ou vazamento de caminhos internos de `data/`):
- **Pare imediatamente.**
- **Não prossiga** para o commit/push no `site/`.
- Reporte os erros exatos encontrados ao Usuário.

### 4. Deploy no Git de `site/`

Somente com a sentinela reportando `PASS`:

```bash
git -C site status --short
git -C site add .
git -C site commit -m "Publicação do site: YYYY-MM-DD"
git -C site push
```

## Regras

- **Nunca publique sem o gate:** `check_site_privacy.py` deve sempre passar antes de qualquer commit em `site/`.
- **Git é isolado:** Esta skill faz commit e push **exclusivamente** no repositório `site/`. Nunca faça commit em `./` ou em `data/` dentro deste fluxo.
- **Não altere visibilidade automaticamente:** Alterações de `visibility:` são decididas exclusivamente pelo Usuário.
