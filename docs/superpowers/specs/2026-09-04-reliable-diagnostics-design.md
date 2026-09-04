# Diagnóstico Confiável e Conexões do Corpus

## Objetivo

Manter `check_repo.py` útil como diagnóstico local sem tornar o navegador um custo implícito, preservar a auditoria visual como requisito de publicação, reduzir ruído em `check_gaps.py` e integrar páginas de apoio que já têm relação inequívoca com essays.

## Gate de repositório e auditoria visual

O modo padrão `check_repo.py` continuará executando os verificadores estáticos do site: privacidade, páginas estruturais e orçamento. Ele não abrirá Chromium. Um novo argumento `--visual` solicitará explicitamente `check_site_pages.py`; o `/publish` e `seal_publication.py` continuam chamando o verificador visual diretamente, sem esse atalho.

`check_site_pages.py` aceitará um orçamento total configurável. A auditoria medirá tempo monotônico antes de cada página e interromperá o restante com um erro identificável quando não houver orçamento disponível. As navegações terão timeout finito e falhas por página serão registradas no resultado, não poderão deixar o processo em espera indefinida. O relatório inclui páginas verificadas e páginas puladas pelo orçamento.

## Heurística de gaps

Termos vindos de nomes próprios só são candidatos se tiverem sinal específico: expressão com duas ou mais palavras capitalizadas, sigla, termo destacado ou texto-âncora externo. Uma lista de palavras funcionais e rótulos profissionais genéricos exclui casos como “Esses”, “Substituindo”, “Engenheiro” e “Físico”. O filtro não se aplica a âncoras externas ou negrito; estes continuam sendo sinais explícitos de intenção conceitual.

## Conexões de apoio

O trabalho limita-se a `## Conexões`. Para cada concept ou entity órfão, a ligação só será adicionada quando o próprio arquivo ou o essay já estabelecerem relação direta e verificável. A ligação será bidirecional, sem alterar corpo, datas `updated:` ou `visibility:`. Relações sem evidência direta ficam fora desta rodada.

## Finais de linha

O repositório privado `data/` ganha `.gitattributes` com LF para Markdown, JSON, YAML e arquivos de texto gerados. O fixer mecânico normaliza para LF somente os arquivos que já reescreve e nunca toca documentos originais em `wiki/sources/`.

## Testes e aceitação

- O gate padrão não inicia auditoria visual; `--visual` a inclui.
- O orçamento visual encerra o restante com erro observável.
- Os falsos positivos listados deixam de aparecer, mas um candidato legítimo com sinal forte permanece elegível.
- Os links adicionados passam em `check_wiki.py` e eliminam os órfãos relacionados.
- Arquivos reescritos pelo fixer usam LF.
