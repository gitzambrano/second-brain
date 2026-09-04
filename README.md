# 🧠 Second Brain Engine

> Motor computacional e infraestrutura de agentes para uma wiki pessoal centrada em **ensaios (*essays*), artigos (*white papers*) e estudos aprofundados** em Português do Brasil.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-Pytest-green.svg)](TESTING.md)
[![Atlas](<https://img.shields.io/badge/Atlas-Live%20Site-orange.svg>)](https://gitzambrano.github.io/second-brain-site/)

🔗 **Atalhos rápidos:**

- **[Atlas ao Vivo](https://gitzambrano.github.io/second-brain-site/)** — o site público do Second Brain: o ideário de essays, white papers e estudos, com o catálogo completo, o grafo de conexões entre essays, conceitos, entidades e referências, e o globo, que é o mesmo mapa numa esfera. O catálogo e os mapas cobrem a base inteira; o texto só abre para o que foi explicitamente autorizado.

- **[`AGENTS.md`](./AGENTS.md)** — regras operacionais, routing e convenções de agentes.
- **[`conventions/SKILL.md`](./.agents/skills/conventions/SKILL.md)** — especificação normativa de formato, estilo e frontmatter.
- **[`TESTING.md`](./TESTING.md)** — suíte de testes, fixtures e quality gates do repositório.

---

## 🏛️ Arquitetura de Repositórios

O projeto separa estritamente o **motor de código** do **conhecimento pessoal** e da **publicação web**. Três repositórios Git independentes convivem no mesmo workspace sem submodules:

| Repositório | Caminho | Visibilidade | Responsabilidade |
| :-------------------------------- | :------------ | :----------------- | :------------------------------------------------------------------------------------------------------------------------------ |
| **`second-brain-engine`** | `./` (raiz) | **Público** | Agentes (`.agents/`), scripts de automação, testes, templates do site e pipelines de qualidade. |
| **`second-brain-data`** | `data/` | **Privado** | O cofre de conhecimento: ensaios, conceitos, entidades, fontes, insights, plano e notas no Obsidian. |
| **`second-brain-site`** | `site/` | **Público** | Projeção estática gerada via GitHub Pages contendo o [Second Brain Atlas](https://gitzambrano.github.io/second-brain-site/). |

> [!NOTE]
> `data/` e `site/` são integralmente ignorados pelo Git do engine. O engine funciona de forma 100% autônoma para desenvolvimento e testes usando o corpus sintético (`tests/fixtures/mini-brain/`).

---

## 🚀 Início Rápido

### 1. Clonar e configurar ambiente

```bash
git clone https://github.com/gitzambrano/second-brain-engine.git second-brain
cd second-brain

# Dependências essenciais do engine
python -m pip install pyyaml pytest
```

### 2. Validar a instalação

```bash
python scripts/check_repo.py --quick   # validação rápida de ambiente e integridade
python -m pytest -q                    # executa a suíte de testes
```

### 3. (Opcional) Inicializar os repositórios complementares

Se desejar inicializar os esqueletos de `data/` (privado) e `site/` (público):

```bash
python scripts/bootstrap_repositories.py --create --init-git
```

---

## 🤖 Agentes e Skills

O engine é a **fonte única** (`.agents/`) de habilidades operacionais e editoriais consumidas por agentes de IA (Claude Code, Gemini, Antigravity, etc.).

Fonte única significa fonte única **editável**, não cópia única. Cada harness lê de um lugar diferente, então os espelhos são gerados:

```text
.agents/                 fonte única editável
    ↓ scripts/sync_skills.py
.claude/skills/          espelho gerado
.claude/agents/          espelho gerado
.codex/agents/*.toml     adaptadores específicos do Codex
```

Nunca edite `.claude/skills/` ou `.claude/agents/` à mão: o conteúdo é sobrescrito no próximo sync. O hook `SessionStart` de `.claude/settings.json` roda `python scripts/sync_skills.py --quiet` na abertura da sessão, e `--check` reprova drift em `check_repo.py --quick` e nos testes.

### Catálogo de Skills por Fase

| Fase                   | Skill           | Finalidade                                                                                                     |
| :--------------------- | :-------------- | :------------------------------------------------------------------------------------------------------------- |
| **Ideação**    | `/insight`    | Captura ideias atômicas sem essay-pai em`wiki/insights/`.                                                   |
|                        | `/outline`    | Estrutura tese, capítulos e bullets antes de redigir prosa.                                                   |
|                        | `/essay`      | Redige o essay completo a partir de um outline aprovado.                                                       |
| **Iteração**   | `/expand`     | Adiciona ou ajusta conteúdo substantivo, teses e exemplos.                                                    |
|                        | `/chapter`    | Adiciona, move, funde ou divide seções/capítulos.                                                           |
|                        | `/continuity` | Audita coerência estrutural, fechamento de tese e transições.                                               |
|                        | `/proofread`  | Revisão ortográfica, gramatical e pontuação.                                                               |
|                        | `/polish`     | Aperfeiçoamento de ritmo e estilo literário/ensaístico.                                                     |
|                        | `/linkify`    | Enriquecimento e validação de links e citações externas.                                                   |
|                        | `/review`     | Peer review crítico de argumentos, premissas e rigor conceitual.                                              |
| **Fontes**       | `/import`     | Ingere ensaio pronto do próprio autor preservando o texto.                                                    |
|                        | `/digest`     | Resume fontes de terceiros (papers, livros) e arquiva em`wiki/sources/`.                                     |
|                        | `/absorb`     | Incorpora fonte já arquivada a páginas existentes da wiki.                                                   |
|                        | `/study`      | Sessão socrática de estudo sobre fontes com conexões à wiki.                                               |
|                        | `/scout`      | Curadoria e busca na web por fontes candidatas a ingestão.                                                    |
| **Manutenção** | `/organize`   | Auditoria mecânica de metadados, tags, links internos e índice.                                              |
|                        | `/sweep`      | Bateria completa sequencial:`/organize` ➔ `/continuity` ➔ `/proofread` ➔ `/polish` ➔ `/linkify`. |
|                        | `/gaps`       | Identificação de lacunas mecânicas, léxicas e conceituais (read-only).                                     |
|                        | `/connect`    | Ação resolutiva sobre lacunas identificadas por`/gaps`.                                                    |
|                        | `/merge`      | Fusão de duas páginas do mesmo tipo redirecionando wikilinks.                                                |
|                        | `/delete`     | Remoção segura de página com reparo de links e log.                                                         |
|                        | `/plan`       | Gestão do roadmap de longo prazo em`plan/plano.md`.                                                         |
|                        | `/stats`      | Dashboard rápido de métricas e saúde da wiki.                                                               |
|                        | `/status`     | Snapshot contextual que conecta uma sessão de trabalho à próxima.                                           |
|                        | `/doctor`     | Diagnóstico de integridade do repositório em modo read-only.                                                 |
| **Saída**       | `/handout`    | Sumário executivo de uma página com tese e conclusões.                                                      |
|                 | `/html`       | Exportação de essays em HTML standalone com tipografia refinada.                                             |
|                 | `/pdf`        | Exportação de essays em PDF tipográfico via Pandoc + LuaLaTeX.                                              |
|                 | `/publish`    | Publicação deliberada do Second Brain Atlas no GitHub Pages com validação de privacidade.                   |
|                 | `/query`      | Consulta e exploração da base de conhecimento da wiki.                                                       |
|                 | `/synthesize` | Busca e identificação de padrões emergentes entre temas.                                                    |

### Subagents Especializados

- **`update`**: Encerra sessões de trabalho substanciais através de pre-flight, correção mecânica, rebuild dos derivados e commit transacional isolado por repositório.
- **`lint-report`**: Diagnóstico consolidado de qualidade agrupando avisos em Crítico, Atenção e Informativo.

---

## 🛠️ Scripts Mais Utilizados

Todos os scripts executáveis em `scripts/` possuem defaults úteis quando executados sem argumentos (consulte o catálogo completo em **[`SCRIPTS.md`](./SCRIPTS.md)**):

```bash
# Diagnóstico e Qualidade
python scripts/check_repo.py                 # Diagnóstico global do repositório
python scripts/check_repo.py --quick         # Checagem ultrarrápida para commits (isolamento git e caminhos)
python scripts/check_repo.py --site          # Validação estrita da sentinela de privacidade do site
python scripts/check_skills.py               # Valida contratos e integridade de todas as skills

# Publicação do Atlas (site/)
python scripts/set_visibility.py             # Lista ensaios por visibilidade (public/private/hidden)
python scripts/set_visibility.py allow <slug> # Autoriza publicação de um ensaio
python scripts/check_visibility_field.py     # Valida o campo de visibilidade no frontmatter
python scripts/build_site.py                 # Compila os ensaios públicos e os mapas interativos
python scripts/check_site_privacy.py         # Sentinela de privacidade (zero vazamento de dados privados)
python scripts/serve_site.py                 # Servidor local de pré-visualização do site

# Exportações Standalone
python scripts/export_essay_html.py <slug>   # Gera versão HTML standalone com MathJax local
python scripts/export_essay_pdf.py <slug>    # Gera versão PDF tipográfica via LuaLaTeX
python scripts/check_html_structure.py       # Auditoria estrutural do HTML exportado
python scripts/check_html_browser.py         # Teste headless de renderização no navegador
```

---

## 🌐 Publicação em Duas Camadas

O site público opera sob um modelo de **Atlas Aberto + Texto por Autorização**:

- **Catálogo & Topologia:** O índice completo e os mapas interativos (Grafo 2D e Esfera 3D) mapeiam todo o universo conceitual — revelando como ensaios, conceitos, fontes e entidades se conectam.
- **Corpo do Ensaio:** Apenas essays com `visibility: public` no frontmatter têm o corpo renderizado e linkável. Ensaios em rascunho ou notas pessoais aparecem no catálogo e mapas marcados como **privados**, impedindo leitura indevida.
- **Busca:** a busca da capa filtra os cartões já presentes na página por **título, resumo e tags** — nunca pelo corpo. O `search-index.json` é um catálogo, não um corpus: ele não carrega o texto de essay nenhum, nem dos publicados.

---

## 🧪 Testes e Qualidade

O engine conta com suíte de testes automatizados via `pytest` que rodam sobre ambientes isolados em `tmp_path`, garantindo total proteção do corpus real.

```bash
python -m pytest -q                        # Executa a suíte rápida
python -m pytest tests/test_site_privacy.py # Sentinela estrita de privacidade
```

Consulte o arquivo **[`TESTING.md`](./TESTING.md)** para instruções completas sobre os quality gates, dependências opcionais (Pandoc, Playwright) e regras de regressão.
