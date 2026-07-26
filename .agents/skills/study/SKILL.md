ois

---

name: study
description: >
  Mantém plan/plano-estudos.md, o to-do do que Usuário quer estudar ou
  escrever no futuro. Comandos: add (ingerir uma ideia de estudo/essay
  futuro, com ou sem fonte), done (marcar como estudado e tirar do
  plano), list (mostrar o plano atual). Use quando o usuário disser
  "quero estudar X", "anota isso pra estudar depois", "já estudei X",
  "tira isso do plano", ou "o que falta estudar".
allowed-tools: Bash Read Write Edit Glob
---

# Study

`plan/plano-estudos.md` é o to-do e log do que Usuário quer estudar ou transformar em essay no futuro — organizado por tópico, com índice. Não é a wiki em si: é a lista de pendências que alimenta a wiki mais tarde, via `/essay`, `/import`, `/digest` ou `/absorb` quando o item for de fato trabalhado.

## Formato de `plan/plano-estudos.md`

```markdown
# Plano de Estudos

## Índice
- [Tópico A](#tópico-a)
- [Tópico B](#tópico-b)

## Tópico A

### Título da ideia
- Tipo: Estudo | Essay Futuro
- Status: Pendente
- Adicionado: YYYY-MM-DD
- Fonte: [[Nome do Source]] | link externo | (sem fonte — ideia solta)
- Nota: descrição breve do que se quer estudar/escrever e por quê.
```

- **Tipo** distingue algo que é só para estudar/ler (`Estudo`) de algo que já é uma ideia de essay futuro (`Essay Futuro`) — o plano cobre os dois.
- Um tópico pode ter múltiplos itens; a ordem dentro do tópico não importa, mas o índice sempre lista todos os tópicos com conteúdo pendente.

## Comandos

### `/study add`

1. Colete: título curto da ideia, tópico (reuse um existente em vez de criar um novo, mesma lógica das tags — ver `AGENTS.md`), tipo (`Estudo` ou `Essay Futuro`), fonte (se houver: um `[[wikilink]]` para algo já em `wiki/sources/` ou `wiki/concepts/`, um link externo, ou nenhuma), e uma nota breve.
2. Se o tópico já existe em `plan/plano-estudos.md`, adicione o item sob ele. Se não existe, crie a seção `## Tópico` e adicione ao Índice.
3. Aceita ideias **genéricas, sem fonte nenhuma** — um insight solto, uma pergunta que o Usuário quer investigar depois — tanto quanto ideias já ancoradas numa fonte específica.
4. Não dispara `/essay`, `/import` nem `/digest` — só registra a intenção. O trabalho de fato acontece depois, quando o item for retomado.

### `/study done <item>`

1. Localize o item pelo título (pergunte se houver ambiguidade entre tópicos).
2. Remova o item da seção do tópico em `plan/plano-estudos.md`. Se o tópico ficar sem itens, remova também a entrada correspondente do Índice (mas pode manter o heading `## Tópico` vazio se for provável que volte a ter itens — use julgamento).
3. Registre a conclusão em `wiki/log.md`:

   ```
   ## [YYYY-MM-DD] estudo-concluído | Título da ideia
   Descrição breve do que foi estudado e, se aplicável, para onde foi (essay/concept/entity resultante).
   ```

4. Se o item virou um essay, concept ou entity concreto, pergunte se deve linkar isso na entrada do log (`[[Essay Resultante]]`).

### `/study list`

Leia `plan/plano-estudos.md` e mostre um resumo agrupado por tópico (título + tipo + status), sem reescrever o arquivo. Read-only.

## Regras

1. **Reuse tópicos antes de criar um novo** — mesma disciplina do vocabulário de tags (ver `AGENTS.md`), para o plano não fragmentar em tópicos quase-duplicados.
2. **Nunca gera conteúdo de wiki sozinho.** `/study` só gerencia a lista de intenções; a produção de conteúdo é sempre via `/essay`, `/import`, `/digest` ou `/absorb`, quando o Usuário decidir puxar o item.
3. Ao adicionar um item, ofereça rodar `/scout` se o item não tiver fonte ainda e parecer que precisa de uma para avançar.

## Skills relacionadas

- `/scout` — pesquisa e sugere fontes candidatas para um item do plano.
- `/status` — pendências de `plan/plano-estudos.md` (quantos itens, por tipo) aparecem na seção Pendências de `wiki/status.md`.
- `/essay`, `/import`, `/digest`, `/absorb` — onde o item do plano vira conteúdo de fato, quando retomado.
