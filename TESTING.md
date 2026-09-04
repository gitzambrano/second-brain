# 🧪 Testing and Repository Quality Gates

> Guia de qualidade, testes automatizados e proteção de integridade do **`second-brain-engine`**.

O engine público versionado **não contém corpus pessoal**. A suíte de testes do repositório foi desenhada para rodar de forma 100% isolada e reproduzível em qualquer ambiente de CI, sem depender de credenciais privadas ou do repositório `data/`.

---

## 🏛️ Isolamento e Resolução de Caminhos

Os testes e scripts resolvem caminhos através de `scripts/repo_paths.py`:

```text
CODE_ROOT   → Raiz do engine público (onde vive este repositório)
DATA_ROOT   → data/ (ou variável de ambiente SECOND_BRAIN_DATA_ROOT)
SITE_ROOT   → site/ (ou variável de ambiente SECOND_BRAIN_SITE_ROOT)
```

Durante a execução dos testes, o fixture sintético `tests/fixtures/mini-brain/` é copiado para um diretório temporário isolado do pytest (`tmp_path`). **Os testes nunca gravam no repositório real ou na pasta `data/` ativa.**

---

## 🚦 Portais de Qualidade (Quality Gates)

### 1. Diagnóstico do Repositório (`check_repo.py`)

O script `scripts/check_repo.py` é o ponto de entrada canônico para validar a saúde do ecossistema:

| Comando | Finalidade |
| :--- | :--- |
| `python scripts/check_repo.py` | **Diagnóstico completo** de ambiente, scripts, disciplina de caminhos e integridade. |
| `python scripts/check_repo.py --quick` | **Checagem rápida** (isolamento de git aninhado e disciplina de caminhos; ideal para pré-commit). |
| `python scripts/check_repo.py --wiki` | Validação estendida da wiki (frescor temporal e conformidade de publicação). |
| `python scripts/check_repo.py --exports` | Validação de exportações e paridade documental. |
| `python scripts/check_repo.py --site` | Sentinela de privacidade, auditoria visual e orçamento de tamanho do site. |
| `python scripts/check_repo.py --architecture` | Contratos estruturais: três Gits isolados, disciplina de caminhos e a cadeia `.agents/` → espelhos → adaptadores. |
| `python -m pytest -q -m browser` | Auditoria visual em Chromium real: home, essay e os dois mapas, em claro, escuro e mobile. Exige Chromium **e Pandoc**; pulada onde não há navegador. |

> [!NOTE]
> Em ambientes de CI ou clones novos sem a pasta `data/` populada, os grupos de teste que dependem de corpus real retornam status `SKIP` com elegância, sem falhar o build.

### 2. Contratos de Scripts e Skills

- **Defaults sem argumentos:** Todo script executável em `scripts/` deve executar uma tarefa útil ou diagnóstico seguro quando chamado sem argumentos:
  ```bash
  python scripts/check_script_defaults.py
  ```
- **Contratos de Skills:** Valida frontmatter, sintaxe e regras de isolamento em `.agents/`:
  ```bash
  python scripts/check_skills.py
  ```
- **Contrato de sincronização de agentes:** `.agents/` é a fonte editável; `.claude/skills/` e `.claude/agents/` são espelhos gerados por `scripts/sync_skills.py`. O contrato exige paridade byte a byte, nenhum arquivo órfão no espelho e reprodutibilidade integral a partir da fonte:
  ```bash
  python scripts/sync_skills.py --check
  python -m pytest tests/test_agent_sync_contract.py
  ```
  Um espelho editado à mão é drift, e o `--check` reprova. Para consertar, edite `.agents/` e rode `python scripts/sync_skills.py`.

---

## 🛡️ Sentinela de Privacidade do Site

A publicação pública possui uma barreira estrita e dedicada para impedir vazamento de notas e rascunhos:

```bash
python scripts/build_site.py --check
python scripts/check_site_privacy.py
```

O teste automatizado **`tests/test_site_privacy.py`** atua como sentinela:
- Cria um site sintético com um ensaio público e um ensaio privado com marcadores sentinela exclusivos.
- Comprova que corpos de texto privados, links de leitura restritos, slugs ou nós do grafo privado **nunca** chegam aos arquivos gerados em `site/`.
- **Nunca enfraqueça ou desative este teste.**

---

## 🏃 Executando a Suíte de Testes (pytest)

### Execução Rápida
```bash
python -m pytest -q -m "not html and not pdf and not slow and not browser"
```

Este é exatamente o comando do job `core` da CI. `python -m pytest -q` puro deixou
de ser rápido — e nem sempre passa — porque o marcador `browser` roda a auditoria
visual em Chromium real e exige navegador **e Pandoc** instalados. Rode a suíte
sem marcador só quando tiver o ambiente completo.

### Execução Seletiva por Marcadores
```bash
python -m pytest -m "not slow"   # Pula verificações demoradas de renderização
python -m pytest -m html         # Valida exports e visualização HTML
python -m pytest -m pdf          # Valida exportação e layout PDF
python -m pytest -m browser      # Auditoria visual em Chromium real (job site-browser)
```

---

## 📦 Dependências de Teste

| Ferramenta | Necessária Para | Instalação / Verificação |
| :--- | :--- | :--- |
| **PyYAML & pytest** | Suíte básica do engine | `pip install pyyaml pytest` |
| **Playwright (Chromium)** | Testes visuais de HTML e testes `browser` | `python -m playwright install chromium` |
| **Pandoc** | Exportação HTML e testes `browser` — o site da auditoria visual é construído com Pandoc | Binário de sistema no PATH |
| **Pandoc & LuaLaTeX** | Testes de exportação em PDF | Binários de sistema instalados no PATH |

---

## 🐛 Protocolo de Regressão para Bugs Mecânicos

Para qualquer correção mecânica determinística:
1. **Reprodução:** Crie uma mutação ou caso de teste no fixture sintético `tests/fixtures/mini-brain/`.
2. **Falha comprovada:** Escreva um teste que falha no comportamento incorreto.
3. **Correção:** Aplique o fix no código do engine.
4. **Verificação:** Confirme que o teste focado passa.
5. **Garantia:** Execute a suíte completa para prevenir efeitos colaterais.

> [!CAUTION]
> Nunca use ensaios reais do repositório privado como fixtures de regressão. Use sempre o mini-brain sintético.
