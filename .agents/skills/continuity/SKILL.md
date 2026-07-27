---
name: continuity
description: >
  Audita a continuidade lógica e narrativa de um essay do início ao
  fim: conceitos usados antes de serem explicados, saltos abruptos
  entre seções, tese não sustentada de forma consistente, ou conclusão
  que não fecha o argumento aberto na introdução. Use quando o Usuário
  disser "verifica a continuidade", "faz sentido do início ao fim?",
  "a conclusão fecha bem o argumento?", ou depois de uma reorganização/
  adição, para confirmar que o essay ainda se sustenta.
allowed-tools: Bash Read Grep
---

# Continuity

Auditoria de coerência lógica e narrativa do essay do início ao fim. **Só diagnostica e reporta — não corrige silenciosamente.** A melhor solução geralmente depende de uma decisão editorial do Usuário (adicionar uma ponte, reordenar um bloco, cortar algo que não serve mais ao argumento), então o relatório vem antes de qualquer edição.

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

Se o Usuário aprovar as correções propostas, aplique-as usando `/expand` (conteúdo) ou `/chapter` (estrutura), conforme o caso — este skill não edita o essay diretamente. Log só se a auditoria motivou mudanças de fato:
```
## [YYYY-MM-DD] continuity | Título do Essay
Problemas encontrados e correções aplicadas (ou "nenhum problema encontrado").
```

## Convenções

Segue a regra de status (batch vs específico) de `## Status de essay` em `conventions/SKILL.md`.

## Skills relacionadas

- `/chapter` — para aplicar correções de reordenação apontadas aqui
- `/expand` — para aplicar pontes/transições de conteúdo apontadas aqui
- `/sweep` — roda `/continuity` como primeiro passo de cada essay, antes de proofread/polish/linkify
