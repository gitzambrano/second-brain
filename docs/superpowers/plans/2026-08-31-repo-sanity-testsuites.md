# Repo Sanity Testsuites Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply the supplied repo-sanity overlay to `testsuites` and prove the tracked skeleton, scripts, exports, and test suite work without touching personal wiki content.

**Architecture:** Apply the bundle only after selecting `testsuites`. The new test harness uses `tests/fixtures/mini-brain/`; commands that could write are exercised in disposable copies or through the test suite, never against the populated ignored corpus. Compare each replaced script with its pre-overlay `main` version and retain externally visible behavior unless a test-backed correction is needed.

**Tech Stack:** Python 3, pytest, Ruff, Pandoc/LuaLaTeX, Playwright Chromium, PowerShell, Git.

**Spec:** User request in this task and `C:\Users\gusta\Downloads\second-brain-testsuites-final.zip`.

## Global Constraints

- Work directly on branch `testsuites`, never `main`.
- Do not add personal wiki, plan, raw, or output files to Git.
- Use only `tests/fixtures/mini-brain/` as test corpus data.
- Keep tests strict; repair production code or the test harness rather than weakening assertions.
- A skeleton with no essays or generated exports must return documented skips, not failures.

---

### Task 1: Safely apply the overlay

**Files:**
- Create/modify: paths supplied under `files/` in the ZIP
- Modify: narrow patches to `AGENTS.md`, `README.md`, `.gitignore`, and skill documents

- [ ] **Step 1: Inspect branch, ignored workspace data, and bundle manifest.**
- [ ] **Step 2: Create or select `testsuites` from the requested baseline without staging ignored files.**
- [ ] **Step 3: Run `apply_repo_sanity_v1.py` against the repository root and record its changed-file list.**
- [ ] **Step 4: Confirm `git status --short --ignored` does not expose personal content for staging.**

### Task 2: Establish compatibility coverage

**Files:**
- Create/modify: `tests/`, `scripts/`, and configuration files only when a verified failure requires it
- Reference: pre-overlay versions available at `main:<path>`

- [ ] **Step 1: Run the focused sanity and default-contract tests; record every failure.**
- [ ] **Step 2: For each failure, add a fixture-only regression test that fails before a production correction when one is absent.**
- [ ] **Step 3: Implement the minimal compatible correction and rerun the focused test.**
- [ ] **Step 4: Compare every replaced legacy script against `main` for removed CLI options, defaults, outputs, or helpers.**

### Task 3: Execute full verification

**Files:**
- Modify: only test-backed fixes identified in Task 2

- [ ] **Step 1: Install missing testable dependencies, including Playwright Chromium and PDF tooling when available.**
- [ ] **Step 2: Run all pytest markers: core, HTML/browser, PDF, and export parity.**
- [ ] **Step 3: Run `check_repo.py`, each executable script's zero-argument contract, Ruff, and `compileall` in safe fixture/skeleton contexts.**
- [ ] **Step 4: Run the complete suite again after fixes and record only unavoidable skips with their missing external dependency.**
