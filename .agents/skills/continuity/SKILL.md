---
name: continuity
description: >
  Audita a progressão estrutural de um essay sem editar. Use para detectar
  conceitos antecipados, saltos entre seções, tese inconsistente ou conclusão
  que não fecha o argumento; /review reutiliza estes achados.
metadata:
  second-brain-role: "structure-auditor"
  second-brain-mode: "read"
  second-brain-scope: "essay"
  second-brain-approval: "none"
  second-brain-closure: "none"
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
