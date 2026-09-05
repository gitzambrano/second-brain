---
name: status
description: >
  Lê ou atualiza wiki/status.md, o snapshot entre sessões. Use para “onde parei?”
  e para registrar foco, perguntas, decisões recentes e pendências recalculadas
  de raw/, plano, sources não verificados e contradições abertas.
metadata:
  second-brain-role: "session-state"
  second-brain-mode: "mixed"
  second-brain-scope: "status"
  second-brain-approval: "none"
  second-brain-closure: "status"
allowed-tools: Bash Read Write Edit Glob AskUserQuestion
---
# Status

`wiki/status.md` é um snapshot vivo. `wiki/log.md` é o histórico append-only.

## `/status`

Leia e mostre o estado atual. Não edite. Se o arquivo ainda não existir, crie o template canônico e informe que foi inicializado.

## `/status update`

1. Releia `wiki/status.md`.
2. Recalcule **Pendências**:
   - itens em `raw/`;
   - itens `Status: Pendente` em cada seção de `plan/plano.md`;
   - entries de `wiki/sources/manifest.md` com `Verificação: não verificado`, exceto fontes cuja decisão explícita de não converter esteja registrada em `Virou:` como `None`, `nenhum`, `nenhuma`, `-` ou `—`;
   - contradições ainda abertas na sessão.
3. Atualize **Foco atual**, **Perguntas em aberto** e **Decisões recentes** com base no trabalho efetivamente realizado. Pergunte somente quando faltar informação necessária.
4. Reescreva o snapshot inteiro e atualize `Atualizado:`.
5. Não escreva entrada de log para `/status update`.

Template:

```markdown
# Status

Atualizado: YYYY-MM-DD

## Foco atual
- [projeto/essay/tema] — [estado] — próxima ação: [...]

## Perguntas em aberto
- [pergunta] (desde YYYY-MM-DD)

## Decisões recentes
- [decisão] (YYYY-MM-DD) — [justificativa breve]

## Pendências
- raw/: N item(ns) aguardando triagem
- plan/plano.md: N tarefa(s), N fonte(s), N revisão(ões), N estudo(s), N essay(s) futuro(s) pendente(s)
- sources com Verificação: não verificado: N
```

Se uma seção não tiver conteúdo real, use `- (nenhuma)`.

## Relação com outras skills

Após trabalho substancial em `/essay`, `/import`, `/digest`, `/absorb`, `/organize`, `/sweep`, `/study` ou `/plan work`, ofereça `/status update`; não rode automaticamente.

Se a sessão alterou muitas páginas, pode oferecer `update` separadamente para derivados/Git. O remoto continua sujeito à autorização própria do `update`.

Regras permanentes pertencem a `conventions/SKILL.md`; `status.md` guarda apenas estado útil entre sessões.
