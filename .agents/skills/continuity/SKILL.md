---
name: continuity
description: >
  Audita a coerência estrutural de um essay do início ao fim: conceitos
  usados antes de serem explicados, saltos abruptos entre seções, tese
  sustentada de forma consistente entre capítulos, ou conclusão que não
  fecha o argumento aberto na introdução. É o componente estrutural do
  peer review: /review invoca este skill como primeiro passo e foca a
  própria análise na força dos argumentos em si, não na organização.
  Use quando o Usuário disser "verifica a continuidade", "faz sentido
  do início ao fim?", "a conclusão fecha bem o argumento?", ou depois
  de uma reorganização/adição, para confirmar que o essay ainda se
  sustenta.
allowed-tools: Bash Read Grep
---

# Continuity

Auditoria de coerência **estrutural** do essay do início ao fim — a tese se mantém ao longo dos capítulos, cada seção prepara a seguinte, a conclusão fecha o que a introdução abriu. **Só diagnostica e reporta — não corrige silenciosamente.** A melhor solução geralmente depende de uma decisão editorial do Usuário (adicionar uma ponte, reordenar um bloco, cortar algo que não serve mais ao argumento), então o relatório vem antes de qualquer edição.

**Relação com `/review`**: este skill é o componente estrutural do peer review completo — `/review` o invoca como passo 2 e usa o resultado para alimentar seu próprio relatório, em vez de rechecar a mesma coisa. Quando chamado direto pelo Usuário (fora de `/review`), este skill se comporta exatamente como descrito abaixo, sem nenhuma etapa a menos.

## O que verificar

1. **Conceitos usados antes de serem explicados.** Um termo técnico ou ideia aparece num capítulo antes de ser definido/introduzido em outro.
2. **Saltos abruptos entre seções**, sem uma frase ou parágrafo de transição que conecte uma à outra.
3. **Progressão lógica**: a ordem das seções vai da introdução até a conclusão de modo que cada seção prepare o terreno para a próxima, ou existe uma seção fora de ordem?
4. **Sustentação da tese**: a tese central é mantida de forma consistente do início ao fim, sem a argumentação se desviar ou contradizer a própria conclusão?
5. **Fechamento**: a conclusão de fato fecha o argumento aberto na introdução, em vez de introduzir uma ideia nova que não foi preparada antes?

## Relatório

Para cada problema encontrado, indique a seção onde está, qual é exatamente o salto/inconsistência, e proponha a correção — mas não a aplique sem confirmação. Formato sugerido:

> **Capítulo 4 → 5**: o capítulo 5 usa "acomodação neural" sem que o termo tenha sido definido antes. Sugestão: uma frase de transição no início do capítulo 5, ou mover a definição do capítulo 6 para cá.

Se o essay passar limpo, diga isso também — não é preciso inventar problemas para justificar a auditoria.

## Depois

Se o Usuário aprovar as correções propostas, aplique-as usando `/expand` (conteúdo) ou `/chapter` (estrutura), conforme o caso — este skill não edita o essay diretamente (cada um deles já roda `check_wiki.py <slug>`/`fix_lint.py <slug>` no próprio fechamento). Log só se a auditoria motivou mudanças de fato:
```
## [YYYY-MM-DD] continuity | Título do Essay
Problemas encontrados e correções aplicadas (ou "nenhum problema encontrado").
```

## Convenções

Segue a regra de status (batch vs específico) de `## Status de essay` em `conventions/SKILL.md`.

## Skills relacionadas

- `/review` — invoca este skill como passo 2 (coerência estrutural); a análise crítica de conteúdo em si é do `/review`
- `/chapter`, `/expand` — aplicam as correções apontadas aqui
- `/sweep`
