# Newsletter — Kit

A newsletter é uma projeção do Second Brain, não uma segunda fonte editorial.

## Publicação

No front matter de um essay público:

```yaml
visibility: public
newsletter: true
```

Depois do build normal do site, gere o manifesto:

```bash
python scripts/build_newsletter_manifest.py
```

O arquivo `newsletter-manifest.json` contém apenas metadados públicos: slug, título, summary, updated e URL relativa. O corpo do essay e caminhos do repositório privado não entram no manifesto.

## GitHub Pages → Kit

O repositório `second-brain-site`, na mesma branch `feature/kit-newsletter`, contém o workflow pós-deploy e o cliente da API v4 do Kit.

Configuração necessária no repositório do site:

- Secret `KIT_API_KEY` — chave privada da API v4 do Kit.
- Variable `KIT_NEWSLETTER_ENABLED` — usar `true` somente depois dos testes; ausente ou diferente de `true` mantém dry-run.
- Variable `SITE_BASE_URL` — opcional; padrão `https://gitzambrano.github.io/second-brain-site`.
- Variable `KIT_EMAIL_TEMPLATE_ID` — opcional; ID do template de e-mail no Kit.

O workflow só roda depois de um deploy Pages bem-sucedido em `main`. Ele compara o manifesto atual com o commit anterior. Re-runs não duplicam envio: cada broadcast usa a chave `second-brain-newsletter:<slug>:<updated>` e o script verifica os broadcasts já existentes no Kit.

## Formulário de assinatura

Criar no Kit um Form do tipo **Inline**, manter double opt-in e copiar o embed JavaScript fornecido pelo próprio Kit. O embed é público; a API key nunca vai para o HTML.

A integração visual do formulário no template do site deve ser feita depois de criar esse Form, pois o código/UID do embed é específico da conta.
