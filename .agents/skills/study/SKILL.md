---
name: study
description: >
  Conduz uma sessão de estudo de verdade sobre um tema: busca fontes,
  lê e sintetiza, faz perguntas socráticas pro Usuário desenvolver o
  próprio raciocínio, e gera conexões com o que já existe na wiki.
  Não gerencia pendências de longo prazo (isso é /plan) — é o trabalho
  de estudar em si, na sessão atual. Use quando o Usuário disser
  "quero estudar X agora", "me explica Y", "vamos explorar esse
  assunto", "não entendo bem Z, me ajuda a entender", ou quando /plan
  estiver retomando um item da seção Estudos.
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch
---

# Study

Estudar não é ler passivamente — é o ciclo de buscar material, confrontar com o que o Usuário já pensa, e deixar a compreensão ficar mais precisa a cada volta. Essa skill conduz esse ciclo dentro da sessão atual. Ela não decide sozinha quando um assunto "acabou de ser estudado" e virou conteúdo de wiki — isso é decisão do Usuário, geralmente via `/atom` (se virou uma ideia atômica) ou `/essay` (se já virou uma tese completa).

## O ciclo

1. **Ancore o ponto de partida.** O que o Usuário já sabe ou já pensa sobre isso? Pergunte antes de despejar informação — estudar em cima do que já existe na cabeça da pessoa rende mais do que uma exposição do zero. Se o tema já toca algo na wiki (`wiki/index.md`, `wiki/concepts/`, `wiki/entities/`), mencione e pergunte se aquilo é o ponto de partida.

2. **Busque material.** Use `WebSearch`/`WebFetch` diretamente para uma exploração rápida, ou rode `/scout` se o objetivo é levantar uma lista mais extensa e curada de fontes candidatas antes de aprofundar. Não é preciso decidir de antemão — comece pequeno (2-3 buscas) e escale se o tema pedir.

3. **Leia com ceticismo produtivo.** Ao trazer o que encontrou, não apenas resuma — aponte onde as fontes discordam entre si, onde o argumento é fraco, onde falta evidência. Isso é o que diferencia "estudar" de "resumir".

4. **Faça perguntas socráticas.** Em vez de só entregar a resposta, devolva perguntas que levem o Usuário a articular a própria posição: "isso bate com o que você pensava sobre X?", "e se Y estiver errado, o que muda no seu argumento?", "como isso se conecta com [[Essay Já Existente]]?". O objetivo é o Usuário sair da sessão com uma posição mais clara, não só mais informação.

5. **Gere conexões ativamente.** Ao longo da sessão, aponte explicitamente onde o que está sendo estudado ecoa (ou contradiz) algo já na wiki — um essay, um concept, uma entity, ou até uma nota atômica em `wiki/synthesis/`. Não espere o fim da sessão para fazer isso; conexões encontradas no meio do processo costumam ser as mais interessantes.

6. **Feche com uma decisão sobre o que fazer com o que foi estudado.** No fim (ou quando o Usuário quiser parar), pergunte o que fazer com o material:
   - Virou uma ideia solta, ainda sem tese? → `/atom add`.
   - Virou uma fonte específica que vale preservar? → `/digest` ou `/absorb`, dependendo do uso.
   - Já virou uma tese completa? → `/essay`.
   - Ainda não deu pra concluir nada, mas vale continuar depois? → deixe (ou crie, via `/plan add`) o item na seção Estudos do plano, com uma `Nota:` atualizada sobre até onde chegou.

## Exemplo

> **Usuário:** quero estudar mais sobre dynamic stall models pra decidir qual usar no zBEMT.
>
> **Claude:** Você já tem o modelo de Øye implementado — a dúvida é se vale trocar, ou se é sobre entender melhor as alternativas antes de decidir? [pergunta socrática de ancoragem]
>
> **Usuário:** É mais sobre entender as alternativas, tipo Leishman-Beddoes.
>
> **Claude:** [busca "Leishman-Beddoes dynamic stall model", "Øye vs Leishman-Beddoes comparison"] Encontrei três fontes relevantes — uma delas (Leishman & Beddoes 1989, o paper original) é bem mais complexa que Øye: modela histerese com múltiplos estados internos em vez de uma única constante de tempo. Isso pode valer a fidelidade extra pro seu caso de uso, ou pode ser complexidade desnecessária — dado que seu GUI já roda em near-real-time via QThread, um modelo mais pesado computacionalmente muda esse trade-off? [pergunta que conecta ao que já existe no projeto]
>
> **Usuário:** boa pergunta, não tinha pensado nisso.
>
> **Claude:** [ao final] Isso virou uma posição clara o suficiente pra virar uma nota atômica — "Leishman-Beddoes tem fidelidade maior mas o custo computacional pode não valer a pena dado o uso em near-real-time do zBEMT GUI" é uma ideia com tese própria. Quer que eu capture isso via `/atom add`?

## O que não fazer

Não decida sozinho quando "encerrar" o estudo de um tema — isso é sempre negociado com o Usuário no fechamento do ciclo. Não pule direto pra `/essay` só porque o tema é rico — a maioria das sessões de estudo não produz um essay inteiro, e forçar isso é pior do que deixar a ideia decantar como nota atômica ou item de plano. Não confunda `/study` com `/query` — `/query` responde uma pergunta pontual usando o que **já está** na wiki; `/study` é uma sessão de exploração que pode trazer material **novo**, de fora da wiki.

## Skills relacionadas

- `/plan` — quem decide chamar `/study` ao retomar um item da seção Estudos, e quem registra se ficou pendente
- `/scout` — busca mais extensa e curada de fontes, quando `WebSearch` direto não é suficiente
- `/atom` — destino natural de um insight que emergiu da sessão mas ainda não é uma tese completa
- `/essay` — destino de uma sessão que já produziu uma tese completa
- `/digest`, `/absorb` — destino de uma fonte específica encontrada durante o estudo
- `/query` — para responder uma pergunta pontual com o que já está na wiki, sem sair buscando material novo
