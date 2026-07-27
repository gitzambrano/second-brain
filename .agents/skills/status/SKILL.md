---
name: status
description: >
  Mantém wiki/status.md, o snapshot do estado atual da wiki: foco corrente,
  perguntas em aberto, decisões recentes fechadas, e pendências (raw/,
  plan/, sources sem manifest). É o que conecta uma sessão à próxima —
  use "/status" para ver o estado atual no início de uma sessão, e
  "/status update" para atualizá-lo ao fechar uma sessão com trabalho
  substancial. Use também quando o Usuário perguntar "onde eu parei",
  "o que falta fazer", ou "atualiza o status".
allowed-tools: Bash Read Write Edit Glob
---

# Status

`wiki/status.md` é um snapshot vivo, não um log cronológico — cada seção é sobrescrita no lugar, ao contrário de `wiki/log.md` (append-only). Ele existe para responder, em segundos, "onde eu parei" no início de uma sessão nova.

## Comandos

### `/status` (sem argumento)

Leia `wiki/status.md` e mostre o conteúdo ao Usuário, tal como está. Read-only, não modifica nada. Se o arquivo não existir ainda, crie-o vazio com o template abaixo e avise que é a primeira vez.

### `/status update`

1. Releia `wiki/status.md` atual.
2. Recalcule as **Pendências** automaticamente, sem perguntar:
   - Quantos itens há em `raw/` aguardando triagem.
   - Quantos itens pendentes (`Status: Pendente`) há em `plan/plano.md`, por seção (Tarefas / Fontes para Ingerir / Revisões / Estudos / Essays Futuros).
   - Quantas entradas em `wiki/sources/manifest.md` estão com `Verificação: não verificado`.
   - Qualquer contradição entre fontes ainda não resolvida (ver regra de contradição em `conventions/SKILL.md`) que tenha ficado em aberto na sessão.
3. Pergunte ao Usuário (ou infira da conversa corrente) o que mudou em:
   - **Foco atual**: no que ele está trabalhando agora, por projeto/essay/tema.
   - **Perguntas em aberto**: dúvidas ainda não resolvidas que vão precisar de decisão futura.
   - **Decisões recentes**: qualquer decisão de conteúdo ou estilo fechada nesta sessão (se for uma decisão de estilo/formatação, ofereça também registrá-la em `## Decisões fechadas` de `conventions/SKILL.md`).
4. Reescreva `wiki/status.md` inteiro (sobrescreva, não faça append) com `Atualizado:` na data de hoje.
5. Não é necessário logar a atualização em `wiki/log.md` — `/status` é meta-operação sobre o estado da wiki, não uma operação de conteúdo.

## Template

```markdown
# Status

Atualizado: YYYY-MM-DD

## Foco atual
- [projeto/essay/tema] — [estado em uma frase] — próxima ação: [...]

## Perguntas em aberto
- [pergunta] (desde YYYY-MM-DD)

## Decisões recentes (fechadas — não reabrir sem evidência nova)
- [decisão] (YYYY-MM-DD) — [justificativa breve]

## Pendências
- raw/: N item(ns) aguardando triagem
- plan/plano.md: N tarefa(s), N fonte(s) para ingerir, N revisão(ões), N estudo(s), N essay(s) futuro(s) pendente(s)
- sources com Verificação: não verificado: N
```

Seções sem conteúdo real ficam com um traço único `- (nenhuma)` em vez de bullet vazio ou template residual.

## Quando outras skills devem tocar `/status`

- Ao final de `/essay`, `/import`, `/digest`, `/absorb`, `/organize`, `/study`, `/plan work` — se o trabalho foi substancial (não uma correção pontual), ofereça rodar `/status update` antes de encerrar a sessão.
- Nunca rode `/status update` automaticamente sem avisar — é rápido, mas quem decide o que é "foco atual" é o Usuário, não uma inferência silenciosa.

## Skills relacionadas

- `/plan` — pendências de `plan/plano.md` alimentam a seção Pendências.
- `/organize` — pendências de sources sem manifest/verificação alimentam a seção Pendências.
- `conventions` — decisões de estilo fechadas na sessão podem migrar para a lista de decisões fechadas lá.
