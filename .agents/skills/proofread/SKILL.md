---
name: proofread
description: >
  Corrige português, pontuação e consistência terminológica sem mudar argumento
  ou registro. Use para revisão linguística de um essay; melhoria de estilo
  pertence a /polish.
metadata:
  second-brain-role: "language-editor"
  second-brain-mode: "write"
  second-brain-scope: "essay"
  second-brain-approval: "none"
  second-brain-closure: "single-essay"
allowed-tools: Bash Read Write Edit Glob Grep AskUserQuestion
---
# Proofread

Revisão de português: gramática, ortografia, concordância, pontuação e consistência terminológica. Não altera conteúdo ou argumento.

## Regra de abertura

Leia o essay inteiro. Prosa segue `## Estilo de prosa` em `conventions/SKILL.md`.

## O que corrigir

- concordância verbal e nominal;
- ortografia e acentuação;
- pontuação;
- ponto e vírgula: substituir por estrutura compatível com `conventions/SKILL.md`;
- parágrafos excessivamente longos quando a divisão melhora leitura sem mudar conteúdo;
- grafia inconsistente do mesmo termo técnico.

## O que não fazer

- não alterar argumento ou ordem das ideias;
- não mudar tom/registro — isso é `/polish`;
- não “corrigir” termo técnico legítimo por parecer incomum; em dúvida, preserve ou pergunte.

## Relatório

Resuma os tipos de correção. Não liste cada substituição salvo se o Usuário pedir.

## Depois

Feche com o `## Fechamento padrão de essay único` de `conventions/SKILL.md`.

Não altere `updated:`; a regra vive em `conventions/SKILL.md`. Correção pequena não precisa de log; passada extensa pode registrar:

```markdown
## [YYYY-MM-DD] proofread | Título do Essay
Resumo do que foi corrigido.
```

## Convenções

Segue a regra de status de `conventions/SKILL.md`.

## Skills relacionadas

- `/polish`
- `/sweep`
