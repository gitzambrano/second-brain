---
tags: [Teste, Engenharia]
sources: []
created: 2026-08-31
updated: 2026-08-31
status: draft
summary: "Essay sintético de qualificação do pipeline que reúne estrutura, matemática, tabela, código, imagem, links, referências e conexões em um documento pequeno. Ele existe exclusivamente para testes determinísticos de regressão e nunca representa conteúdo pessoal ou uma conclusão factual do usuário."
---
# Qualification Essay

> Estudo
> Gustavo Zambrano · Agosto de 2026

## Sumário

- [[#1. Introdução]]
- [[#2. Estruturas suportadas]]
- [[#3. Caixa que enquadra a seção]]
- [[#4. Callout no meio da prosa]]
- [[#5. Conclusão]]

---

## 1. Introdução

Este documento é uma fixture sintética. Um [termo de teste](https://example.com/term) fornece um link externo e a energia de teste obedece a $E=mc^2$ apenas como exemplo de renderização matemática [1].

## 2. Estruturas suportadas

### 2.1 Tabela e código

| Parâmetro | Valor | Fórmula na célula |
| --- | ---: | --- |
| alfa | 1 | $C_T/\sigma = \theta_0 (V\cos\alpha)(V\sin\alpha + v_i)/4$ |
| beta | 2 | $\lambda_i = \sqrt{C_T/2}$ |

```python
matrix = [[1, 2], [3, 4]]
print(matrix[0])
```

### 2.2 Figura

![Figura sintética](../assets/test-image.png)

A figura acima é deliberadamente simples para permitir um teste de presença no HTML e no PDF.

## 3. Caixa que enquadra a seção

> **Ideia 01**

Rótulo que abre a seção enquadra a seção inteira, subseções incluídas. Este parágrafo e o que vem depois dele pertencem ao quadro.

### 3.1 Subseção dentro do quadro

Bloco de código dentro da caixa precisa manter as linhas em branco do original e ganhar o mesmo recuo dos parágrafos:

```text
primeira linha do bloco

linha depois de uma linha em branco
```

## 4. Callout no meio da prosa

Prosa antes do rótulo, para que ele não abra a seção e valha como callout pontual.

> **⚠ Atenção**

Somente este parágrafo pertence ao callout.

### 4.1 Fora do quadro

Esta subseção fica fora da caixa: um callout no meio da prosa fecha no primeiro
heading que encontra, em vez de engolir o resto do capítulo.

## 5. Conclusão

A conclusão contém a frase sentinela **PIPELINE-SENTINEL-ALPHA** para verificar preservação semântica entre formatos.

## Índice de Casos de Teste

Um capítulo cujo título apenas *começa* com uma palavra de aparato. Ele existe
para provar que o exportador não o confunde com o `## Sumário` gerado e apaga
o seu título.

I Tabela e código — estruturas de bloco
II Figura — presença de imagem no HTML e no PDF

## Referências

[1] Doe, J., *Synthetic Reference for Pipeline Qualification*, Example Technical Press, 2026. — Referência completamente fictícia usada apenas por esta fixture. [Link](https://example.com/source)

## Conexões

- [[segundo-essay|Segundo Essay]]
