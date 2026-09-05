---
name: outline
description: >
  Estrutura tese, tipo, domínio, capítulos e papel argumentativo antes da prosa.
  Use para preparar um essay novo em plan/drafts/; /essay consome o outline
  aprovado ou implicitamente resolvido.
metadata:
  second-brain-role: "planner"
  second-brain-mode: "write"
  second-brain-scope: "draft"
  second-brain-approval: "conditional"
  second-brain-closure: "draft"
allowed-tools: Bash Read Write Edit Glob Grep WebSearch WebFetch AskUserQuestion
---
# Outline

Estrutura um essay antes da redação. Produz notas de arquitetura, não prosa.

## 1. Resolver a tese

Tema não basta; o outline precisa de uma posição ou pergunta central que organize o argumento.

Se a tese já vier do Usuário, de `/study` ou do plano, não pergunte novamente.

Defina também:
- `tipo:` — `Ensaio | White Paper | Brainstorm | Estudo | Análise`;
- `dominio:` — `filosófico | técnico | misto`.

## 2. Pesquisa leve

Busque a wiki por páginas relacionadas e faça poucas buscas externas para confirmar correntes, objeções, fenômenos ou referências que a estrutura precisa contemplar.

Não pesquise cada capítulo em profundidade; isso é `/essay`.

## 3. Montar o esqueleto

Inclua:
- **Introdução** — problema + tese;
- **Desenvolvimento** — quantos capítulos forem necessários, cada um avançando um passo real;
- **Conclusão** — fecha a tese sem introduzir ideia nova.

Para cada capítulo:
- título;
- `Papel:` em uma frase, explicando o que estabelece e prepara;
- 3 a 6 bullets de conteúdo, fontes, exemplos, equações ou objeções.

Bullets são notas, não parágrafos.

## 4. Salvar

Use `plan/drafts/<slug>.md`:

```markdown
---
tese: uma frase
tipo: Ensaio | White Paper | Brainstorm | Estudo | Análise
dominio: filosófico | técnico | misto
status: rascunho
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Título

## Capítulo 1 — Título
Papel: ...
- ...
- ...

## Conexões candidatas
- [[slug|Página]] — motivo
```

`plan/drafts/` é planejamento, não conteúdo publicado; não coloque o esqueleto em `wiki/essays/`.

## 5. Iterar

Quando o Usuário pedir ajustes, edite o arquivo diretamente:
- reordenar/fundir/dividir capítulo;
- adicionar/remover bullets;
- mudar tese e reavaliar toda a cadeia argumentativa.

Após mudança estrutural, releia a sequência inteira. Mostre o outline completo atualizado quando isso ajudar o Usuário a aprovar o todo.

Atualize `updated:`.

## Esboço implicitamente aprovado

Se o pedido já trouxer tese, capítulos e direção suficientes para não exigir decisão adicional, grave o outline e prossiga para `/essay` sem criar uma rodada artificial de confirmação.

Pare apenas se houver ambiguidade substantiva.

## Retomar um esboço em andamento

Se o draft tiver `escritos:`, altere somente os capítulos ainda não escritos.

Mudança em capítulo já publicado pertence a `/chapter`, não `/outline`.

## Entrega para `/essay`

Quando aprovado, `/essay` usa o draft como brief.

- Mantenha o draft enquanto houver capítulo pendente.
- O próprio `/essay` remove o arquivo somente quando todo o outline estiver incorporado.
- Se ficar para outra sessão, `/plan` pode registrar a pendência apontando para o draft.

## Limites

- Não escreva prosa de essay.
- Não aprofunde pesquisa além do necessário para validar a arquitetura.
- Texto completo já escrito pelo autor é `/import`, não `/outline`.
