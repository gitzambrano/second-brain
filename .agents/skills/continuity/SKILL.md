---
name: continuity
description: >
  Audita a coerência estrutural de um essay do início ao fim: conceitos
  usados antes de serem explicados, saltos abruptos entre seções, tese
  sustentada de forma consistente entre capítulos, ou conclusão que não
  fecha o argumento aberto na introdução. É o componente estrutural do
  peer review: /review invoca esta skill e reutiliza seus achados.
allowed-tools: Bash Read Grep
---
# Continuity

Auditoria estrutural do essay do início ao fim. **Diagnostica e reporta; não corrige silenciosamente.**

`/review` reutiliza esta análise para a dimensão estrutural do peer review.

## O que verificar

1. conceitos usados antes de serem explicados;
2. saltos abruptos entre seções;
3. progressão lógica e ordem dos capítulos;
4. sustentação consistente da tese;
5. conclusão que fecha o argumento sem introduzir ideia não preparada.

## Relatório

Para cada problema, informe:
- localização;
- inconsistência;
- impacto;
- correção sugerida.

Se não houver problema, diga que a continuidade passou limpa.

## Depois

Se o Usuário aprovar mudanças, use `/expand` para conteúdo ou `/chapter` para estrutura.

`/continuity` por si só não edita o essay e, portanto, não cria log. Se as correções forem executadas, a skill que fizer a edição registra o trabalho conforme sua própria regra.

## Convenções

Segue a regra de status de `conventions/SKILL.md`.

## Skills relacionadas

- `/review`
- `/chapter`, `/expand`
- `/sweep`
