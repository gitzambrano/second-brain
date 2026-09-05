---
name: sweep
description: >
  Orquestra revisão completa de um essay ou do corpus: manutenção mecânica,
  continuidade, português, estilo e links. Use para pente-fino amplo; corrige
  automaticamente o inequívoco e acumula decisões editoriais para o relatório.
metadata:
  second-brain-role: "review-orchestrator"
  second-brain-mode: "write"
  second-brain-scope: "essay-or-corpus"
  second-brain-approval: "conditional"
  second-brain-closure: "multi-essay"
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch AskUserQuestion
---
# Sweep

Orquestra, nessa ordem, `/organize <slug>` → `/continuity` → `/proofread` → `/polish` → `/linkify`.

A lógica de cada dimensão vive na skill correspondente. `/sweep` controla ordem, escopo, decisões e relatório.

## Escopo

```text
/sweep          → todos os essays elegíveis
/sweep <slug>   → essay específico
```

No corpus, siga a regra de status de `conventions/SKILL.md`: pule `revisao` e `finalizado`. Em essay nomeado, processe mesmo nesses estados e informe isso no resumo final.

## Execução

Processe um essay por vez.

1. Rode `/organize <slug>` para fixes mecânicos locais.
2. Rode `/continuity` e reutilize seus achados.
3. Para achado estrutural **inequívoco** que não muda tese nem exige escolha editorial, aplique a correção estrutural correspondente dentro do fluxo e registre-a.
4. Quando a correção exigir decidir tese, ordem argumentativa controversa, remoção de conteúdo ou interpretação entre alternativas, **não pare o batch**: marque o item como `decisão necessária` e continue o restante do essay e do corpus.
5. Rode `/proofread` e aplique as correções de língua.
6. Rode `/polish` e aplique as correções de estilo.
7. Rode `/linkify` e aplique links/referências que puderem ser verificados sem decisão editorial.

Não faça prompts de escala, estimativas de duração ou oferta de lotes. O escopo já foi definido pelo comando.

## Relatório

Entregue um único relatório consolidado:

```markdown
## Sweep — N essay(s)

### Resumo
- processados: N
- pulados por status: K
- fixes mecânicos: X
- continuidade corrigida: Y
- decisões editoriais pendentes: Z
- correções de português: W
- correções de estilo: V
- links/referências: U

### Decisões necessárias
- [essay] — [localização] — [decisão]

### Por essay
- [Título] — [resumo curto]
```

Não exponha cada microcorreção durante a execução.

## Fechamento

Registre uma entrada consolidada em `wiki/log.md` quando houver mudanças. Nenhuma etapa de `/sweep` altera `updated:` por revisão mecânica, linguística ou estilística; uma correção estrutural/substantiva aplicada no passo 3 segue a regra de data da skill que efetivamente mudou o corpo.

Depois do batch, ofereça o subagent `update` **somente** para regenerar derivados e executar commit/push após autorização explícita do Usuário. Ofereça `/status update` quando o trabalho for substancial.

## Limites

- Não duplica checklists das skills chamadas.
- Não bloqueia o corpus por uma decisão editorial de um único essay.
- Não escolhe silenciosamente entre alternativas substantivas.
- `/review` continua sendo a auditoria crítica profunda de argumento e evidência.
