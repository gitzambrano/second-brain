---
name: study
description: >
  Conduz estudo ativo com fontes externas, comparação crítica e perguntas
  socráticas. Use quando o objetivo é compreender ou formar posição; /scout faz
  apenas curadoria, e persistência fica com /insight, /digest ou /essay.
metadata:
  second-brain-role: "research"
  second-brain-mode: "read"
  second-brain-scope: "conversation-and-web"
  second-brain-approval: "none"
  second-brain-closure: "none"
allowed-tools: Bash Read Glob Grep WebSearch WebFetch AskUserQuestion
---
# Study

Sessão de exploração ativa. O objetivo é melhorar entendimento e posição do Usuário, não apenas listar fontes.

## Fluxo

### 1. Ancorar o ponto de partida

Descubra o que o Usuário já sabe ou quer decidir.

Busque material relacionado na wiki com `qmd query`; use `scripts/find_text.py` como fallback.

Não repita pergunta cuja resposta já esteja clara na conversa ou na wiki.

### 2. Ler fontes

Comece com poucas fontes relevantes.

Para cada fonte:
- leia o conteúdo, não apenas snippet;
- resuma em palavras próprias;
- identifique claim principal, evidência e limitações;
- mantenha o link junto da síntese.

Se o objetivo virar apenas curadoria ampla, use `/scout`.

Fonte que merece preservação permanente pode ser encaminhada para `/digest`.

### 3. Comparar criticamente

Cruze as fontes:
- convergências;
- divergências;
- pressupostos;
- evidência fraca;
- questões ainda abertas.

Não trate consenso aparente como prova automática.

### 4. Fazer perguntas socráticas

Use perguntas que ajudem o Usuário a testar a própria posição, especialmente onde a evidência muda uma hipótese anterior.

Não transforme a sessão numa sequência obrigatória de perguntas; intercale explicação, síntese e questionamento conforme o ritmo da conversa.

### 5. Conectar com a wiki

Aponte relações úteis com essays, concepts, entities e insights existentes. Não force conexão temática fraca.

### 6. Encerrar com destino

Quando o Usuário quiser fechar:
- ideia atômica nova → `/insight add`;
- fonte a preservar → `/digest`;
- fonte já processada que deve enriquecer páginas → `/absorb`;
- tese pronta → `/outline` → `/essay`;
- estudo ainda aberto → `/plan add` ou atualize o item existente.

## Limites

- `/study` não é `/query`: pode trazer material novo de fora da wiki.
- `/study` não é `/scout`: lê e confronta fontes, não apenas seleciona.
- Não force transformação em essay.
- Não declare um estudo “concluído” sem o Usuário encerrar ou mudar de objetivo.
