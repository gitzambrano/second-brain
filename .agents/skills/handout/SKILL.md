---
name: handout
description: >
  Gera um handout de uma página para um essay existente, em
  wiki/handouts/: linha de tese, 3 a 5 conclusões em prosa, e link de
  volta para o essay completo. Use quando o Usuário disser "gera um
  handout desse essay", "resume isso numa página para eu mandar pro
  fulano", ou quiser uma versão executiva rápida de um essay para
  alguém que não vai ler o texto inteiro.
allowed-tools: Bash Read Write Edit Glob AskUserQuestion
---

# Handout

Gera `wiki/handouts/<slug-do-essay>.md`: uma versão de uma página do essay, para o Usuário mandar rápido para alguém que não vai ler o white paper inteiro.

## Quando usar

- **Nunca automático.** Só quando pedido explicitamente ("gera um handout de X", "resume esse ensaio para mandar pro fulano").
- Normalmente oferecido (não executado direto) pelos skills `/essay`, `/expand`, `/chapter`, `/proofread` e `/polish` quando o essay parece algo que será compartilhado com terceiros.

## Passo a passo

1. **Leia o essay completo** em `wiki/essays/<slug>.md` — não há `## Resumo Executivo` interno para atalhar essa leitura, então o handout vem de ler de fato o `## Sumário`, a introdução e a conclusão, não de um resumo genérico do tema.
2. A partir dessa leitura, escreva a linha de tese (uma frase com a ideia central) — a única "compressão" que este skill faz, sem seção pronta para copiar.
3. Extraia **3 a 5 conclusões principais** em prosa curta corrida, não bullets (mesma regra do `## Estilo de prosa` em `conventions/SKILL.md`).
4. Monte o arquivo em `wiki/handouts/<slug>.md`:

```markdown
---
essay: <slug-do-essay>
created: YYYY-MM-DD
---

# <Título do Essay>

<Uma frase com a tese central.>

<Conclusão 1 em prosa curta.>

<Conclusão 2 em prosa curta.>

<Conclusão 3 a 5, conforme necessário.>

Leia o essay completo: [<Título do Essay>](../essays/<slug>.md)
```

5. **Não inclua** `## Sumário`, `## Referências` ou `## Conexões` — essas seções pertencem ao essay completo, não ao handout.
6. Se já existir um handout para esse essay (de uma edição anterior do essay), leia-o primeiro e regenere em vez de duplicar — sobrescreva com o conteúdo atualizado.
7. Não é necessário atualizar `wiki/index.md` (que contém apenas essays) nem `wiki/log.md` — handout é um artefato leve, gerado sob demanda, não uma operação de conteúdo da wiki que precise de rastro no log.

## Handout como output

`wiki/handouts/<slug>.md` é a fonte de verdade, versionada e atualizada quando o essay muda. O que o Usuário manda para alguém é um output, igual ao PDF/HTML de um essay. Depois de gerar ou atualizar o handout:

1. Copie o arquivo para `output/handouts/<slug>.md`.
2. Pergunte se o Usuário quer também `.pdf` e/ou `.html`, mais apresentáveis para anexar ou mandar por link:

   ```bash
   python scripts/export_essay.py <slug> --handout --output output/handouts
   python scripts/export_essay_html.py <slug> --handout --output output/handouts
   ```

3. Não gere `.pdf`/`.html` automaticamente — só quando o Usuário confirmar que vai usar. O `.md` em `output/handouts/` pode ser copiado sempre, é barato.

## Depois de gerar

Avise o Usuário do caminho do handout (em `wiki/handouts/` e em `output/handouts/`) e pergunte se ele quer o essay completo exportado também (`/pdf` ou `/html`) para anexar junto, caso o destinatário queira aprofundar.

## Skills relacionadas

- `/essay` — cria o essay que o handout resume
- `/expand`, `/chapter`, `/proofread`, `/polish` — se o essay mudar depois, o handout existente pode precisar ser regenerado
- `/pdf` / `/html` — para exportar o essay completo, não o handout
