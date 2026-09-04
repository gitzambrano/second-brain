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
allowed-tools: Bash Read Write Edit Glob AskUserQuestion
---
# Status

`wiki/status.md` é um snapshot vivo, não um log cronológico. Cada seção é sobrescrita no lugar; `wiki/log.md` continua append-only.

## Comandos

### `/status`

Leia `wiki/status.md` e mostre o estado atual. Não edita nada, com uma única exceção: se o arquivo ainda não existir, crie-o com o template abaixo e avise que é a primeira inicialização.

### `/status update`

1. Releia `wiki/status.md`.
2. Recalcule as **Pendências**:
   - itens em `raw/`;
   - itens `Status: Pendente` em cada seção de `plan/plano.md`;
   - entradas de `wiki/sources/manifest.md` com `Verificação: não verificado`,
     exceto quando `Virou:` for `None`, `nenhum`, `nenhuma`, `-` ou `—`.
     Esses valores registram uma decisão explícita de não converter a fonte e
     não entram na pendência, mesmo sem verificação bibliográfica;
   - contradições ainda não resolvidas registradas na sessão.
3. Atualize, a partir da conversa ou perguntando apenas quando necessário:
   - **Foco atual**;
   - **Perguntas em aberto**;
   - **Decisões recentes**.
4. Reescreva `wiki/status.md` inteiro com `Atualizado:` na data atual.
5. Se a sessão editou muitas páginas, ofereça o subagent `update` — ele regenera derivados e faz commit e push em `./` e em `data/`.
6. Não registre `/status update` em `wiki/log.md`.

Decisões recentes pertencem ao status enquanto forem úteis entre sessões. Regras permanentes de estrutura/estilo só entram em `conventions/SKILL.md` quando representam o comportamento normativo atual; não mantenha histórico de decisões lá.

## Template

```markdown
# Status

Atualizado: YYYY-MM-DD

## Foco atual
- [projeto/essay/tema] — [estado em uma frase] — próxima ação: [...]

## Perguntas em aberto
- [pergunta] (desde YYYY-MM-DD)

## Decisões recentes
- [decisão] (YYYY-MM-DD) — [justificativa breve]

## Pendências
- raw/: N item(ns) aguardando triagem
- plan/plano.md: N tarefa(s), N fonte(s) para ingerir, N revisão(ões), N estudo(s), N essay(s) futuro(s) pendente(s)
- sources com Verificação: não verificado: N
```

Seção sem conteúdo real recebe `- (nenhuma)`.

## Quando outras skills devem tocar `/status`

Após trabalho substancial em `/essay`, `/import`, `/digest`, `/absorb`, `/organize`, `/sweep`, `/study` ou `/plan work`, ofereça `/status update`.

Não rode automaticamente sem avisar.

## Skills relacionadas

- `/plan` — pendências de longo prazo
- `/organize` — saúde estrutural e de sources
- `conventions` — somente regras normativas atuais
