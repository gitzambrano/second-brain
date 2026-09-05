---
name: polish
description: >
  Melhora clareza, concisão, tom e naturalidade sem mudar conteúdo ou argumento.
  Use para revisão de estilo; as regras normativas de prosa vivem em
  conventions/SKILL.md e devem prevalecer sobre heurísticas desta passada.
metadata:
  second-brain-role: "style-editor"
  second-brain-mode: "write"
  second-brain-scope: "essay"
  second-brain-approval: "none"
  second-brain-closure: "single-essay"
allowed-tools: Bash Read Write Edit Glob Grep
---
# Polish

Melhora clareza, concisão, tom e naturalidade sem alterar conteúdo. Aplica `## Estilo de prosa` de `conventions/SKILL.md`.

## Regra de abertura

Leia o essay inteiro antes de reescrever. Avalie padrões no contexto do documento, não frases isoladas.

## O que corrigir

### Clareza e concisão

1. **Frases sobrecarregadas:** mantenha uma proposição principal por frase.
2. **Parágrafos sem foco:** mantenha um tema principal por parágrafo.
3. **Conectores excessivos:** remova transições que não acrescentem relação lógica, mas preserve conectores necessários para explicitar causa, contraste, condição ou consequência.
4. **Bullets artificiais:** converta em prosa quando apenas fragmentarem um argumento; preserve listas reais.
5. **Filler:** remova `é importante observar que`, `vale destacar que`, `cabe mencionar que` e equivalentes.
6. **Verbos indiretos e nominalizações:** prefira a ação direta: `possui a capacidade de representar` → `representa`; `realiza o cálculo de` → `calcula`; `constitui-se como` → `é`.
7. **Hedge excessivo:** preserve incerteza real, mas simplifique construções como `pode potencialmente vir a indicar`.
8. **Concisão excessiva:** não transforme prosa em estilo telegráfico. Preserve sujeito, verbo, artigos, preposições, conectores e modificadores quando necessários para a sintaxe ou para a relação lógica. Evite sequências como `Aumento de RPM. Maior rigidez. Menor flapping.` quando a relação entre as ideias deve ser explicitada.
9. **Travessões:** respeite o limite de `conventions/SKILL.md`; reescreva excedentes.
10. **Ponto e vírgula:** elimine; prefira frases autônomas.
11. **Atalhos tipográficos:** evite barras, til, remissões abreviadas e intervalos com hífen na prosa quando prejudicarem clareza.

### Padrões artificiais

12. **Gerúndio ornamental:** revise `demonstrando`, `evidenciando`, `ressaltando`, `reforçando`, `refletindo` quando apenas repetirem ou dramatizarem a frase anterior.
13. **Metadiscurso:** evite `vamos agora entender`, `vejamos a seguir`, `é aqui que entra`. Explique diretamente.
14. **Repetição do heading:** não abra uma seção repetindo o título em outras palavras.
15. **Paralelismos e tríades artificiais:** evite `não apenas X, mas também Y` e grupos de três criados apenas por efeito retórico.
16. **Falsa profundidade:** revise `no fundo`, `em essência`, `a verdadeira questão`, `insight profundo` quando não acrescentarem conteúdo.
17. **Aforismos artificiais:** evite fórmulas como `X é a linguagem de Y` ou `X não é apenas uma ferramenta, é...` sem necessidade conceitual.
18. **Objeções inexistentes:** não introduza `isso não significa que...` se essa interpretação não surgiu no argumento.
19. **Alternativas fictícias:** não invente uma opção apenas para criar contraste e rejeitá-la.
20. **Histórico editorial residual:** remova explicações que só existem por causa de prompts, steers, correções ou versões anteriores. Escreva o estado final do argumento; não diga `não é X, mas Y` ou `a formulação correta é Y` quando X ou o erro não aparecem no texto.
21. **Fontes vagas:** revise `estudos mostram`, `especialistas afirmam`, `a literatura demonstra`, `é amplamente reconhecido` sem fonte identificável.
22. **Finais genéricos:** remova `isso abre novas possibilidades`, `aponta para um futuro promissor` e equivalentes sem consequência concreta.
23. **Restos de chatbot:** elimine `vamos explorar`, `como podemos ver`, `espero que isso ajude` e equivalentes.

### Inflação retórica, marketing e dramatização

Evite atribuir importância, profundidade, novidade, qualidade ou dramaticidade sem demonstrá-las.

**Gatilhos frequentes:** `fundamental`, `crucial`, `central`, `profundo`, `rigoroso`, `notável`, `inovador`, `avançado`, `sofisticado`, `robusto`, `poderoso`, `elegante`, `revolucionário`, `transformador`, `impressionante`, `extraordinário`.

Revise também:

- **marketing:** `solução poderosa`, `abordagem inovadora`, `arquitetura elegante`, `método sofisticado`, `grande avanço`, `potencial transformador`;
- **superlativos e absolutos:** `o mais importante`, `o melhor`, `um dos maiores`, `sem precedentes`, `definitivo`, `único`, `de toda a ciência`;
- **dramatização não técnica:** `explosivo`, `catastrófico`, `devastador`, `brutal`, `dramático`, `radical`, `extremo`, `severo`;
- **prestígio vazio:** `com rigor matemático`, `análise rigorosa`, `visão profunda`, `resultado central`, `fato notável`, `para compreender plenamente`.

Prefira descrever a propriedade concreta: mecanismo, magnitude, taxa, condição de validade, vantagem ou consequência física.

Esses termos são gatilhos, não proibições. Preserve usos técnicos reais, como `frequência fundamental`, `estabilidade robusta`, `nível de significância` ou classificações formais de severidade. O acúmulo de qualificadores próximos é sinal mais forte que uma ocorrência isolada.

### Essays técnicos

24. Não antropomorfize código, modelos ou teorias.
25. Prefira voz ativa quando o agente for conhecido.
26. Simplifique cadeias longas de `de/da/do`.
27. Preserve grafia única para termos, siglas, unidades e variáveis.
28. Não sacrifique causalidade, sintaxe natural ou precisão técnica para encurtar a frase.

## Não corrigir mecanicamente

Uma ocorrência isolada não constitui erro.

Preserve voz do autor, terminologia técnica, repetição deliberada, ritmo intencional e cautela epistemológica necessária.

O objetivo é remover padrões mecânicos e ornamentais, não uniformizar a escrita.

## O que preservar

Não adicione nem remova ideias. Não altere argumento ou ordem lógica sem necessidade estilística clara.

## Relatório

Resuma categorias de ajustes em vez de listar cada troca, salvo se o Usuário pedir diff.

## Depois

Feche com o `## Fechamento padrão de essay único` de `conventions/SKILL.md`.

Não altere `updated:`; a regra vive em `conventions/SKILL.md`. Logue apenas quando a passada for extensa:

```markdown
## [YYYY-MM-DD] polish | Título do Essay
Resumo do ajuste de estilo.
```

## Convenções

Segue a regra de status de `conventions/SKILL.md`.

## Skills relacionadas

- `/proofread`
- `/sweep`
