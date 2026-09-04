# Diagnóstico Confiável e Conexões do Corpus Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tornar o diagnóstico padrão rápido e finito, reduzir ruído de gaps, ligar páginas de apoio a essays e normalizar finais de linha.

**Architecture:** `check_repo.py` encaminha o navegador apenas com `--visual`; `check_site_pages.py` recebe prazo total monotônico; `check_gaps.py` exige sinal semântico para nomes próprios; ligações explícitas são espelhadas em `## Conexões`.

**Tech Stack:** Python, pytest, Playwright, Markdown e Git attributes.

**Spec:** `docs/superpowers/specs/2026-09-04-reliable-diagnostics-design.md`

## Global Constraints

- `/publish` continua chamando `check_site_pages.py` diretamente, sem pulo de navegador.
- Não mudar corpo, `updated:` ou `visibility:` dos essays.
- Não reescrever `wiki/sources/`.

### Task 1: Diagnóstico visual explícito

**Files:** `scripts/check_repo.py`, `tests/test_repo_sanity.py`

- [ ] Escrever teste falho que chama `site(CheckResult("repository"), visual=False)` e verifica que `check_site_pages.py` não entra em `run_status_command`; outro com `visual=True` verifica que entra.
- [ ] Rodar `python -m pytest tests/test_repo_sanity.py -k visual -v`; esperar falha porque `site()` ainda não aceita `visual`.
- [ ] Adicionar `visual: bool = False` a `site()` e `audit()`. Declarar `--visual` fora do grupo exclusivo de modos. Executar privacidade e orçamento sempre; inserir `check_site_pages.py --allow-skip-browser` apenas se `visual` for verdadeiro. Gravar `meta["visual"]`.
- [ ] Rodar o teste focal e esperar PASS.

### Task 2: Orçamento da auditoria visual

**Files:** `scripts/check_site_pages.py`, `tests/test_site_browser_audit.py`

- [ ] Escrever teste falho para `audit(max_seconds=0)` que espera issue `AUDIT_TIME_BUDGET_EXCEEDED`.
- [ ] Rodar `python -m pytest tests/test_site_browser_audit.py -k budget -v`; esperar falha por argumento inexistente.
- [ ] Usar `time.monotonic()` para calcular `deadline`. Antes de cada página, mapa e probe de geometria/capa, encerrar o restante com `result.error("AUDIT_TIME_BUDGET_EXCEEDED", ...)` quando esgotado. Acrescentar CLI `--max-seconds` com default 300 e metadados de páginas verificadas/puladas. Converter timeout do Playwright em `PAGE_TIMEOUT`, nunca suprimi-lo.
- [ ] Rodar o teste focal e esperar PASS.

### Task 3: Gaps com sinal semântico

**Files:** `scripts/check_gaps.py`, novo `tests/test_gaps.py`

- [ ] Escrever testes falhos para `is_gap_candidate("Engenheiro", {"nome-proprio"})` e `is_gap_candidate("Esses", {"nome-proprio"})` retornarem falso, enquanto expressão capitalizada de duas palavras e negrito retornam verdadeiro.
- [ ] Rodar `python -m pytest tests/test_gaps.py -v`; esperar falha por função inexistente.
- [ ] Implementar `is_gap_candidate(term, kinds)`: âncora externa ou negrito são sinal suficiente; nome próprio isolado precisa ter duas palavras e não pertencer à stoplist de palavras funcionais e profissões genéricas. Aplicar na construção de `ranked`, preservando os limiares existentes.
- [ ] Rodar o teste focal e esperar PASS.

### Task 4: LF no fixer e no repositório privado

**Files:** `scripts/fix_lint.py`, `tests/test_fix_lint.py`, novo `data/.gitattributes`

- [ ] Escrever teste falho que passa `"uma\\r\\nduas\\r\\n"` a `save_file_content` e espera bytes `b"uma\\nduas\\n"`.
- [ ] Rodar `python -m pytest tests/test_fix_lint.py -k crlf -v`; esperar falha.
- [ ] Normalizar CRLF/CR para LF em `save_file_content`, escrever UTF-8 com LF, e adicionar atributos LF para `*.md`, `*.json`, `*.yaml`, `*.yml` e `*.txt` em `data/.gitattributes`.
- [ ] Rodar o teste focal e esperar PASS.

### Task 5: Conexões dos órfãos

**Files:** essays e páginas de apoio sob `data/wiki/`, somente `## Conexões`

- [ ] Estabelecer baseline com `python scripts/check_wiki.py --json`; esperar 21 `ORPHAN_NO_ESSAY`.
- [ ] Espelhar backlinks já declarados: Diagrama de Coleman ↔ `rotores-e-giroscopios`; Einstein ↔ `cerebros-de-boltzmann`, `forma-do-universo`, `simular-e-instanciar-sobre-as-leis-da-natureza`; Church ↔ seus dois essays já listados; Rutan e X-29 ↔ comparação de dinâmica.
- [ ] Para cada outro órfão, pesquisar o termo e acrescentar somente relações que o essay já trata diretamente; manter a ligação bidirecional.
- [ ] Rodar `python scripts/check_wiki.py <slug>` para cada página alterada e repetir o JSON do corpus; esperar zero órfãos tratados.

### Task 6: Verificação e commits separados

- [ ] Rodar `python -m pytest -q`, `python scripts/check_repo.py --json`, `python scripts/check_repo.py --visual --json`, `python scripts/check_wiki.py --json` e `python scripts/check_site_privacy.py`.
- [ ] Reconstruir somente derivados necessários (`build_graph.py` se conexões mudarem), conferir os três Git statuses e commitar engine e `data/` separadamente.
